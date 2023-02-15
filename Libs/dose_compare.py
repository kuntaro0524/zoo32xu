import sys,os,math,time,tempfile,datetime
import Raddose

if __name__=="__main__":
    e=Raddose.Raddose()

    # 160509 wl=1.0A 10x15 um
    en=12.3984

    #density=1.4E12 # photons/um^2/s
    beam_h=10
    beam_v=10
    flux=2E10
    exptime = 1.0

    pf_en = 12.3984 / 3.0
    numoto_en = 12.3984/1.1
    en_list=[pf_en,numoto_en,12.3984,13.0]

    for en in en_list:
        dose=e.getDose(beam_h,beam_v,flux,exptime,energy=en)
        exptime_for_10MGy = 10.0 / dose
        photons_for_10MGy = exptime_for_10MGy * flux
        density_for_10MGy = photons_for_10MGy / beam_h / beam_v
        print("%8.1f %8.3f MGy density for 10MGy: %6.3e"%(en,dose,density_for_10MGy))
