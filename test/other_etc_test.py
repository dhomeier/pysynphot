import sys
import os
import tempfile

from pysynphot import spectrum,observationmode
from pysynphot import newobservation as observation
from pysynphot import ObsBandpass
from pysynphot import locations
from pysynphot import spparser as P
from pysynphot import units, planck
from pysynphot import newetc as etc

from pytools import testutil 


## TO RUN IN A SINGLE TEST IN DEBUG MODE:
## import v0.2_test
## v0.2_test.FileTestCase('testwave').debug()



#Places used by test code
userdir   = os.environ['PYSYN_USERDATA']
testdata  = os.path.join(locations.rootdir,'calspec','feige66_002.fits')

#Freeze the version of the comptable so tests are not susceptible to
# updates to CDBS
cmptb_name = os.path.join('mtab','r1j2146sm_tmc.fits')
observationmode.COMPTABLE = observationmode._refTable(cmptb_name)
print "%s:"%os.path.basename(__file__)
print "  Tests are being run with %s"%observationmode.COMPTABLE
print "  Synphot comparison results were computed with r1j2146sm_tmc.fits"
#Synphot comparison results are identified with the varname synphot_ref.

accuracy = 1.0e-5    # default floating point comparison accuracy
etc.debug = 0        # supress messages from ETC-support tasks

testindex = 0
# spectrum values @ testindex
values = {'flam':           2.79979E-11,
          'flam z=2.5':     6.53011E-13,
          'fnu':            1.23037E-23,
          'photlam':        1.61773E+00,
          'photlam z=1.0':  4.04432E-01,
          'photlam z=2.5':  1.32060E-01,
          'photnu':         7.10915E-13,
          'jy':             1.23037E+00,
          'mjy':            1.23037E+03,
          'abmag':          8.67490E+00,
          'stmag':          5.28218E+00,
          'obmag':          -1.23590E+01,
          'v=0.0':          4.38149E-07,
          'v=5.0':          4.38149E-09,
          'vegamag':        1.81443E+00,
          'counts':         8.78177E+04,
          'angstrom':       1.14780E+03,
          'angstrom z=1.0': 2.29560E+03,
          'angstrom z=2.5': 4.01730E+03,
          'hz':             2.61189E+15,
          'nm':             1.14780E+02,
          'micron':         1.14780E-01,
          'mm':             1.14780E-04,
          'cm':             1.14780E-05,
          'm':              1.14780E-07,
          'integral':       1.65862E+03,
          'sp_npoints':     5.11000E+03,
          'thru_npoints':   1.1E+04,
          'thru_5000':      1.22327E-01,
          'obsmode':        'acs,hrc,f555w',
          'hstarea':        4.52389E+04,
          'countrate':      8.30680E+05,
          'efflam':         5328.12
          }

format_spec = '%.5E'    # floating point precision in assert
format_offset = {'win32':1,'sunos5':0,'linux2':0}

def format(value):
    ''' Formats scientific notation according to platform.    
    '''
    str = format_spec%(value)

    index1 = str.index('E') + 2
    index2 = index1 + format_offset[sys.platform]

    str1 = str[0:index1]
    str2 = str[index2:len(str)]

    return str1+str2




class ObsmodeTestCase(testutil.FPTestCase):

    def test1(self):
        obsmode = observationmode.ObservationMode(values['obsmode'])
        self.assertApproxFP(obsmode.area, values['hstarea'])
        throughput = obsmode.Throughput().throughputtable
        self.assertEqual(len(throughput), 11003)
        self.assertApproxFP(throughput[5000], 0.12232652011958853)

    #Moved test2 to other_etc_ticket_cases: ticket #21
    #Moved test3 to other_etc_ticket_cases: ticket #21

    def test4(self):
        obsmode = observationmode.ObservationMode("acs,sbc,F125LP")
        wave = obsmode.Throughput().GetWaveSet()
        throughput = obsmode.Throughput().throughputtable
        self.assertApproxFP(throughput[500], 3.983354E-15)

    def test5(self):
        obsmode = observationmode.ObservationMode("stis,ccd")
        wave = obsmode.Throughput().GetWaveSet()
        throughput = obsmode.Throughput().throughputtable
        self.assertApproxFP(throughput[500], 0.1451186)

    #Moved test6 to other_etc_ticket_cases: ticket #21

    def test7(self):
        obsmode = observationmode.ObservationMode("acs,wfc1,G800L")
        wave = obsmode.bandWave()
        throughput = obsmode.Throughput().throughputtable
        self.assertApproxFP(throughput[5000], 0.389376)


    def test8(self):
        obsmode = observationmode.ObservationMode("stis,g750m,c8825")
        wave = obsmode.bandWave()
        throughput = obsmode.Throughput().throughputtable
        self.assertApproxFP(throughput[7500], 0.0681207)

    def test9(self):
        obsmode = observationmode.ObservationMode("stis,fuvmama,g140l,s52x2")
        wave = obsmode.Throughput().GetWaveSet()
        throughput = obsmode.Throughput().throughputtable
        self.assertApproxFP(throughput[200], 0.0297475)


    def test10(self):
        obsmode = observationmode.ObservationMode("acs,hrc,PR200L")
        wave = obsmode.Throughput().GetWaveSet()
        throughput = obsmode.Throughput().throughputtable
        self.assertApproxFP(throughput[5000], 0.266238)


    def test11(self):
        obsmode = observationmode.ObservationMode("stis,nuvmama,e230h,c2263,s02x02")
        wave = obsmode.Throughput().GetWaveSet()
        throughput = obsmode.Throughput().throughputtable
        self.assertApproxFP(throughput[1500], 0.0048806)


class ObsmodeWFC3TestCase(testutil.FPTestCase):
    def test1(self):
        obsmode = observationmode.ObservationMode("wfc3,ir,f160w")
        wave = obsmode.Throughput().GetWaveSet()
        throughput = obsmode.Throughput().throughputtable


class ETCTestCase_Imag1(testutil.FPTestCase):

    def setUp(self):
        self.oldpath=os.path.abspath(os.curdir)
        self.expr = "(earthshine.fits*0.5)%2brn(spec(Zodi.fits),band(V),22.7,vegamag)%2b(el1215a.fits*0.5)%2b(el1302a.fits*0.5)%2b(el1356a.fits*0.5)%2b(el2471a.fits*0.5)"
        os.chdir(locations.specdir)
       
    def tearDown(self):
        os.chdir(self.oldpath)

    def test1cr(self):
        sp = etc.parse_spec(self.expr)
        bp = ObsBandpass('acs,hrc,f220w')
        obs = observation.Observation(sp, bp)
        countrate = obs.countrate()
        self.assertApproxFP(countrate, 0.115697)

    def test2lam(self):
        spectrum = "spectrum=" + self.expr
        obsmode = "obsmode=acs,hrc,f220w"
        parameters = [spectrum, obsmode]
        efflam = etc.calcphot(parameters)
        self.assertApproxFP(efflam, 2499.47)

    def test3cr(self):
        spectrum = "spectrum=" + self.expr
        instrument = "instrument=acs,hrc,f220w"
        parameters = [spectrum, instrument]
        countrate = etc.countrate(parameters)
        self.assertApproxFP(countrate[0], 0.115697)

    #Removed test 4cr1 to other_etc_ticket_cases: ticket #21
    #Removed test 4cr2 to other_etc_ticket_cases: ticket #71

    def test5cr(self):
        spectrum = "spectrum=rn(icat(k93models,5770,0.0,4.5),band(johnson,v),20.0,vegamag)"
        instrument = "instrument=acs,sbc,F125LP"
        parameters = [spectrum, instrument]
        countrate = etc.countrate(parameters)
        self.assertApproxFP(countrate[0], 0.00015431)


class ETCTestCase_Imag2(testutil.FPTestCase):
    
    def setUp(self):
        self.oldpath=os.path.abspath(os.curdir)
        os.chdir(locations.specdir)
       
    def tearDown(self):
        os.chdir(self.oldpath)



    def thermback1(self):
        obsmode = "obsmode="
        calculator = etc.Thermback([obsmode])
        countrate = calculator.run()
        self.assertEqual(countrate,'NaN')

    def thermback2(self):
        obsmode = "obsmode=null"
        calculator = etc.Thermback([obsmode])
        countrate = calculator.run()
        self.assertEqual(countrate,'NaN')

    def thermback3(self):
        obsmode = "obsmode=nicmos,1,F090M"
        calculator = etc.Thermback([obsmode])
        countrate = calculator.run()
        synphot_ref=1.98635725923e-12
        self.assertApproxFP(float(countrate), synphot_ref)

    def thermback4(self):
        obsmode = "obsmode=nicmos,1,f190n"
        calculator = etc.Thermback([obsmode])
        countrate = calculator.run()
        synphot_ref=0.0142158651724
        self.assertApproxFP(float(countrate), synphot_ref)

    def thermback5(self):
        obsmode = "obsmode=wfc3,ir,f110w"
        calculator = etc.Thermback([obsmode])
        countrate = calculator.run()
        synphot_ref=0.0342143550515
        self.assertApproxFP(float(countrate), synphot_ref)

        
    def test6(self):
        spectrum = "spectrum=((earthshine.fits*0.5)%2brn(spec(Zodi.fits),band(V),22.7,vegamag)%2b(el1215a.fits*0.5)%2b(el1302a.fits*0.5)%2b(el1356a.fits*0.5)%2b(el2471a.fits*0.5))"
        instrument = "instrument=acs,sbc,F140LP"
        parameters = [spectrum, instrument]
        countrate = etc.countrate(parameters)
        self.assertApproxFP(float(countrate[0]), 0.0834405)

    #Moved test7 to other_etc_ticket_cases: ticket #21
    #Deleted test8: it's an obsolete case.
    

    def test9(self):
        spectrum = "spectrum= rn(unit(1,flam),band(johnson,v),15.0,vegamag)"
        instrument = "instrument=stis,ccd"
        parameters = [spectrum, instrument]
        countrate = etc.countrate(parameters)
        self.assertApproxFP(float(countrate[0]), 36130.9)

    def test10(self):
        spectrum = "spectrum=rn(unit(1,flam),band(johnson,v),15.0,vegamag)"
        instrument = "instrument=wfc3,ir,F110W"
        parameters = [spectrum, instrument]
        countrate = etc.countrate(parameters)
        self.assertApproxFP(float(countrate[0]), 134832)

    def test11(self):
        spectrum = "spectrum=rn(bb(5000.0),band(johnson,v),28.0,vegamag)"
        instrument = "instrument=wfc3,uvis1,F606W"
        parameters = [spectrum, instrument]
        countrate = etc.countrate(parameters)
        self.assertApproxFP(float(countrate[0]), 0.175573)

    def test12(self):
        spectrum = "spectrum=((earthshine.fits*0.5)%2brn(spec(Zodi.fits),band(V),22.7,vegamag)%2b(el1215a.fits*0.5)%2b(el1302a.fits*0.5)%2b(el1356a.fits*0.5)%2b(el2471a.fits*0.5))"
        instrument = "instrument=wfc3,uvis1,F606W"
        parameters = [spectrum, instrument]
        countrate = etc.countrate(parameters)
        self.assertApproxFP(float(countrate[0]), 31.9866)


class ETCTestCase(testutil.FPTestCase):

    def setUp(self):
        self.oldpath=os.path.abspath(os.curdir)
        os.chdir(locations.specdir)
        self.sp=etc.parse_spec(self.spectrum)
        self.bp=ObsBandpass(self.obsmode)
        self.obs=observation.Observation(self.sp,self.bp)
        self.parameters=["spectrum=%s"%self.spectrum,
                         "instrument=%s"%self.obsmode]
        self.obs.convert('counts')
       
    def tearDown(self):
        os.chdir(self.oldpath)

class ETCTestCase_Spec1a(ETCTestCase):
    def setUp(self):

        self.spectrum = "(earthshine.fits*0.5)%2brn(spec(Zodi.fits),band(V),22.7,vegamag)"
        self.obsmode = "acs,hrc,PR200L"
        ETCTestCase.setUp(self)
        
    def testrate(self):
        countrate = etc.specrate(self.parameters)
        self.assertApproxFP(float(countrate.split(';')[0]), 13.7853)

    def testflux(self):
        self.assertApproxFP(float(self.obs.binflux[-1]), 5.01883)

class ETCTestCase_Spec1b(ETCTestCase):
    def setUp(self):
        self.spectrum = "rn((unit(1,flam)),band(johnson,v),15.0,vegamag)"
        self.obsmode = "acs,wfc1,G800L"
        ETCTestCase.setUp(self)
        
    def testrate(self):
        countrate = etc.specrate(self.parameters)
        self.assertApproxFP(float(countrate.split(';')[0]), 73770.3)

    def testflux(self):
        self.assertApproxFP(float(self.obs.binflux[50]), 915.203)

class ETCTestCase_Spec1c(ETCTestCase):
    def setUp(self):
        self.spectrum = "em(4000.0,10.0,1.0000000168623835E-16,flam)"
        self.obsmode = "acs,hrc,PR200L"
        ETCTestCase.setUp(self)

    def testrate(self):
        countrate = etc.specrate(self.parameters)
        self.assertApproxFP(float(countrate.split(';')[0]), 0.163706)

class ETCTestCase_Spec1d(ETCTestCase):
    def setUp(self):
        self.spectrum = "rn((unit(1,flam)),band(johnson,v),15.0,vegamag)"
        self.obsmode="acs,hrc,PR200L"
        ETCTestCase.setUp(self)

    def testrate(self):
        countrate = etc.specrate(self.parameters)
        self.assertApproxFP(float(countrate.split(';')[0]),15658.6)

    def testflux(self):
        self.assertApproxFP(float(self.obs.binflux[80]), 79.8567)

class ETCTestCase_Spec1e(ETCTestCase):
    def setUp(self):
        self.spectrum = "rn((spec(crcalspec$gd71_mod_005.fits))*ebmvx(0.1,gal1),box(5500.0,1),1.0E-16,flam)"
        self.obsmode = "acs,hrc,PR200L"
        ETCTestCase.setUp(self)

    def testrate(self):
        countrate = etc.specrate(self.parameters)
        self.assertApproxFP(float(countrate.split(';')[0]), 1472.035)

    def testflux(self):
        self.assertApproxFP(float(self.obs.binflux[50]), 7.03327)

class ETCTestCase_Spec2a(ETCTestCase):
    def setUp(self):
        self.spectrum = "(spec(crcalspec$grw_70d5824_stis_001.fits))"
        self.obsmode = "stis,fuvmama,g140l,s52x2"
        ETCTestCase.setUp(self)

    def testrate(self):
        countrate = etc.specrate(self.parameters)
        self.assertApproxFP(float(countrate.split(';')[0]), 28935.7)

    def testflux(self):
        self.assertApproxFP(float(self.obs.binflux[500]), 35.5329)

class ETCTestCase_Spec2b(ETCTestCase):
    def setUp(self):
        self.spectrum = "rn((icat(k93models,44500,0.0,5.0)),band(johnson,v),10.516,vegamag)"
        self.obsmode = "stis,nuvmama,e230h,c2263,s02x02"
        ETCTestCase.setUp(self)

    def testrate(self):
        countrate = etc.specrate(self.parameters)
        self.assertApproxFP(float(countrate.split(';')[0]), 35412)

    def testflux(self):
        self.assertApproxFP(float(self.obs.binflux[500]), 1.1851)

class ETCTestCase_Spec2c(ETCTestCase):
    def setUp(self):
        self.spectrum ="rn((spec(crcalspec$bd_28d4211_stis_001.fits)),box(2000.0,1),1.0E-12,flam)"
        self.obsmode="stis,nuvmama,e230h,c2263,s02x02"
        ETCTestCase.setUp(self)

    def testrate(self):
        countrate = etc.specrate(self.parameters)
        self.assertApproxFP(float(countrate.split(';')[0]), 4221.47)

    def testflux(self):
        self.assertApproxFP(float(self.obs.binflux[500]), 0.143323)

class ETCTestCase_Spec2d(ETCTestCase):
    def setUp(self):
        self.spectrum = "(spec(crcalspec$agk_81d266_stis_001.fits))"
        self.obsmode = "stis,ccd,g230lb,s52x2"
        ETCTestCase.setUp(self)

    def testrate(self):
        countrate = etc.specrate(self.parameters)
        self.assertApproxFP(float(countrate.split(';')[0]), 183608.)

    def testflux(self):
        self.assertApproxFP(float(self.obs.binflux[500]), 245.078)


class ETCTestCase_Spec3a(ETCTestCase):
    def setUp(self):
        self.spectrum = "em(4300.0,1.0,9.999999960041972E-13,flam)"
        self.obsmode = "stis,ccd,g430l"
        ETCTestCase.setUp(self)

    def testrate(self):
        countrate = etc.specrate(self.parameters)
        self.assertApproxFP(float(countrate.split(';')[0]), 924.085)


class ETCTestCase_Spec3b:
    def setUp(self):
        self.spectrum = "rn((icat(k93models,5770,0.0,4.5)),band(johnson,v),20.0,vegamag)"
        self.obsmode = "acs,hrc,PR200L"
        ETCTestCase.setUp(self)

    def testrate(self): 
        countrate = etc.specrate(self.parameters)
        self.assertApproxFP(float(countrate.split(';')[0]), 119.709)

class ETCTestCase_Spec3c:
    def setUp(self):
        self.spectrum = "((earthshine.fits*0.5)%2brn(spec(Zodi.fits),band(V),22.7,vegamag)%2b(el1215a.fits*0.5)%2b(el1302a.fits*0.5)%2b(el1356a.fits*0.5)%2b(el2471a.fits*0.5))"
        self.obsmode = "stis,fuvmama,g140l"
        ETCTestCase.setUp(self)

    def testrate(self):
        countrate = etc.specrate(parameters)
        self.assertApproxFP(float(countrate.split(';')[0]), 11.68605)

class ETCTestCase_Spec3d:
    def setUp(self):
        self.spectrum = "((earthshine.fits*0.5)%2brn(spec(Zodi.fits),band(V),22.7,vegamag)%2b(el1215a.fits*0.5)%2b(el1302a.fits*0.5)%2b(el1356a.fits*0.5)%2b(el2471a.fits*0.5))"
        self.obsmode = "cos,fuv,g130m,c1309"
        ETCTestCase.setUp(self)

    def testrate(self):
        countrate = etc.specrate(parameters)
        self.assertApproxFP(float(countrate.split(';')[0]), 26.5409)

        

if __name__ == '__main__':
    if 'debug' in sys.argv:
        testutil.debug(__name__)
    else:
        testutil.testall(__name__)










