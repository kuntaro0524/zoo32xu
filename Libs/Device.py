#!/bin/env python
import sys
import os
import socket
import time
import datetime
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs")

from numpy import *

# My library
import Singleton
import File
import TCS
import BM
import Capture
import Count
import Mono
import ConfigFile
import Att
import BeamCenter
import Stage
import Zoom
import BS
import Shutter
import Cryo
import ID
import ExSlit1
import Light
import AnalyzePeak
import Gonio
import Colli
import Cover
import CCDlen
import CoaxPint
import MBS
import DSS
import BeamsizeConfig
import Flux

class Device(Singleton.Singleton):
    """
    def __init__(self,server_address):
        self.isInit=False
            host = server_address
            port = 10101
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((host,port))
    """
    def __init__(self,server):
        print server
        self.s=server

    def readConfig(self):
        conf=ConfigFile.ConfigFile()
        # Reading config file
        try :
            ## Dtheta 1
            self.scan_dt1_ch1=int(conf.getCondition2("DTSCAN","ch1"))
            self.scan_dt1_ch2=int(conf.getCondition2("DTSCAN","ch2"))
            self.scan_dt1_start=int(conf.getCondition2("DTSCAN","start"))
            self.scan_dt1_end=int(conf.getCondition2("DTSCAN","end"))
            self.scan_dt1_step=int(conf.getCondition2("DTSCAN","step"))
            self.scan_dt1_time=conf.getCondition2("DTSCAN","time")

            ## Fixed point parameters
            self.fixed_ch1=int(conf.getCondition2("FIXED_POINT","ch1"))
            self.fixed_ch2=int(conf.getCondition2("FIXED_POINT","ch2"))
            self.block_time=conf.getCondition2("FIXED_POINT","block_time")
            self.total_num=conf.getCondition2("FIXED_POINT","total_num")
            self.count_time=conf.getCondition2("FIXED_POINT","time")

        except MyException,ttt:
            print ttt.args[0]
            print "Check your config file carefully.\n"
            sys.exit(1)

    def init(self):
        # settings
        print "Initialization starts"
        self.mono=Mono.Mono(self.s)
        self.tcs=TCS.TCS(self.s)
        self.bm=BM.BM(self.s)
        self.f=File.File("./")
        self.capture=Capture.Capture()
        self.slit1=ExSlit1.ExSlit1(self.s)
        self.att=Att.Att(self.s)
        self.stage=Stage.Stage(self.s)
        self.zoom=Zoom.Zoom(self.s)
        self.bs=BS.BS(self.s)
        self.cryo=Cryo.Cryo(self.s)
        self.id=ID.ID(self.s)
        self.light=Light.Light(self.s)
        self.gonio=Gonio.Gonio(self.s)
        #self.gonio.prepprep()
        self.colli=Colli.Colli(self.s)
        self.coax_pint=CoaxPint.CoaxPint(self.s)
        self.clen=CCDlen.CCDlen(self.s)
        self.covz=Cover.Cover(self.s)
        self.shutter=Shutter.Shutter(self.s)
        # Optics
        self.mbs=MBS.MBS(self.s)
        self.dss=DSS.DSS(self.s)

        print "Device. initialization finished"
        self.isInit=True

    def tuneDt1(self,logpath):
        if os.path.exists(logpath)==False:
            os.makedirs(logpath)
        self.f=File.File(logpath)
        prefix="%s/%03d"%(logpath,self.f.getNewIdx3())
        self.mono.scanDt1PeakConfig(prefix,"DTSCAN_NORMAL",self.tcs)
        dtheta1=int(self.mono.getDt1())
        print "Final dtheta1 = %d pls"%dtheta1

    def changeEnergy(self,en,isTune=True,logpath="/isilon/BL32XU/BLsoft/Logs/Zoo/"):
        # Energy change
        self.mono.changeE(en)
        # Gap
        self.id.moveE(en)
        if isTune==True:
            self.tuneDt1(logpath)

    def measureFlux(self):
        en=self.mono.getE()
        # Prep scan
        self.prepScan()
        # Measurement
        ipin,iic=self.countPin(pin_ch=3)
        pin_uA=ipin/100.0
        iic_nA=iic/100.0
        # Photon flux estimation
        ff=Flux.Flux(en)
        phosec=ff.calcFluxFromPIN(pin_uA)
        self.finishScan(cover_off=True)
        print "PHOSEC: %e"%phosec
        return phosec

    def getBeamsize(self,config_dir="/isilon/blconfig/bl32xu/"):
        tcs_vmm,tcs_hmm=self.tcs.getApert()
        bsf=BeamsizeConfig.BeamsizeConfig(config_dir)
        hbeam,vbeam=bsf.getBeamsizeAtTCS_HV(tcs_hmm,tcs_vmm)
        return hbeam,vbeam

    def bsOff(self):
        if self.isInit==False:
            self.init()
        self.bs.off()

    def prepCentering(self,zoom_out=False):
        if zoom_out==True:
            self.zoom.zoomOut()
            # 2020/01/24 This must be stupid code.
            # It is very dangerous code.
            # 2021/01/22 This must be stupid code.
            # It is very dangerous code.
            self.coax_pint.move(20367)
        self.bs.on()
        self.colli.off()
        self.light.on()

    def prepCenteringBackCamera(self,zoom_out=True):
        if zoom_out==True:
            self.zoom.zoomOut()
        self.bs.evacLargeHolderWait()
        #self.bs.off()
        self.cryo.on()
        self.colli.off()
        self.light.on()

    def prepCenteringSideCamera(self,zoom_out=True):
        if zoom_out==True:
            self.zoom.zoomOut()
        self.bs.off()
        self.cryo.on()
        self.colli.off()
        self.light.on()

    def prepCenteringLargeHolderCam1(self,zoom_out=True):
        if zoom_out==True:
            self.zoom.zoomOut()
        #self.bs.evacLargeHolder()
        self.bs.evacLargeHolderWait()
        self.cryo.on()
        self.colli.off()
        self.light.on()

    def prepCenteringLargeHolderCam2(self,zoom_out=True):
        if zoom_out==True:
            self.zoom.zoomOut()
        self.bs.on()
        self.cryo.on()
        self.colli.off()
        self.light.on()

    def prepScan(self):
        # Prep scan
        self.clen.evac()
        ## Cover on
        self.covz.on()
        time.sleep(2.0)
        ## Cover check
        self.covz.isCover()
        self.light.off()
        self.shutter.open()
        self.slit1.openV()
        ## Attenuator
        self.att.setAttThick(0)
        # collimator on
        self.colli.on()
        # Beamstopper on
        self.bs.off()

    def finishScan(self,cover_off=True):
        self.slit1.closeV()
        self.shutter.close()
        # collimator on
        self.colli.off()
        if cover_off==True:
            ## Cover off
            self.covz.off()

    def closeAllShutter(self):
        self.shutter.close()
        self.slit1.closeV()

    def countPin(self,pin_ch=3):
        counter=Count.Count(self.s,pin_ch,0)
        i_pin,i_ion=counter.getCount(1.0)
        return i_pin,i_ion

    def setAttThick(self,thick):
        if self.isInit==False:
            self.init()
        self.att.setAttThick(thick)
    
    def calcAttFac(self,wl,thickness):
        self.att.calcAttFac(wl,thickness)
    
    def prepView(self):
        if self.isInit==False:
            self.init()
        self.closeShutters()
        self.light.on()
    
    def moveGonioXYZ(self,x,y,z):
        self.gonio.moveXYZmm(x,y,z)

################################
# Last modified 120607
# for XYZ stage implemtented to the monitor
################################
    def prepCapture(self):
        if self.isInit==False:
            self.init()
        ## Zoom in
        self.zoom.go(0)
    
        ## Cryo go up
        self.cryo.off()
    
        ## BM on
        self.bm.onPika()
    
        ## BS on
        self.bs.on()

    def closeCapture(self):
        self.capture.disconnect()

    ###########################
    # Last modified 120607
    # for XYZ stage implemtented to the monitor
    ###########################
    def finishCapture(self):
        if self.isInit==False:
            self.init()
        ## BM off
        self.bm.offXYZ()
        ## BS off
        self.bs.off()
    
    def captureBM(self,prefix,isTune=True):
        if self.isInit==False:
            self.init()
    
        # Attenuator setting
        if isTune==True:
            # Tune gain
            gain=self.cap.tuneGain()
    
        print "##### GAIN %5d\n"%gain
    
        ### averaging center x,y
        path=os.path.abspath("./")
        prefix="%s/%s"%(path,prefix)
        x,y=self.cap.aveCenter(prefix,gain,5)
    
        return x,y
    
    def checkRingCurrent(self,current_threshold=50.0):
        self.get_current_str="get/bl_dbci_ringcurrent/present"
        self.s.sendall(self.get_current_str)
        recbuf = self.s.recv(8000)
        strs=recbuf.split("/")
        ring_current=float(strs[len(strs)-2].replace("mA",""))
    
        if ring_current > current_threshold:
            print "Ring current %5.1f"%ring_current
            return True
        else:
            print "Ring aborted."
            print "Ring current %5.1f"%ring_current
            return False

if __name__=="__main__":
    host = '172.24.242.41'
    port = 10101
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))

    dev=Device(s)
    dev.init()

    logpath="/isilon/users/target/target/Staff/2016B/161003/03.Test/"

    """
        if os.path.exists(logpath)==False:
                os.makedirs(logpath)
    print "%e"%dev.measureFlux(logpath,tune=False,config_dir="/isilon/blconfig/bl32xu/bss/")
    """
    #phosec=dev.measureFlux()
    #hbeam,vbeam=dev.getCurrentBeamsize(config_dir="/isilon/blconfig/bl32xu/")

    #print phosec,hbeam,vbeam

    dev.prepCentering()

#dev.closeAllShutter()

#print proc.gonio.getXYZmm()
#proc.setAttThick(0)
#proc.bsOff()
#print proc.captureBM("TEST")
#en_list=arange(19.5,8.0,-0.5)
#print en_list,len(en_list)

#en_list=[19.5,15.5,12.5,11.5,11.0,10.5,10.4,10.3,10.2,10.1,10.0,9.9,9.8,9.7,9.6,9.5,8.5]
#en_list=[19.5,15.5,12.3984,11.5,10.5,9.5,8.5]
#en_list=[8.5,9.5,10.5,11.5,12.3984,15.5,19.5]
#en_list=arange(8.5,11.0,0.1)
#print en_list
#print len(en_list)

#while(1):
#for en in en_list:
#proc.makeTable(en)

# Analyze knife
#print proc.analyzeKnife("049_stagey.scn")

# Energy table check
#proc.moveEtable(8.5)
