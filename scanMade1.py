import os,sys,math,numpy,socket,datetime,time
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
import IboINOCC
import Zoo
import Gonio,BS
import Device
import LoopMeasurement
import StopWatch
import MyException

if __name__ == "__main__":
        blanc = '172.24.242.41'
        b_blanc = 10101
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((blanc,b_blanc))

        gonio=Gonio.Gonio(s)
        bs=BS.BS(s)
        inocc=IboINOCC.IboINOCC(gonio)

	# ROOT DIRECTORY
	root_dir="/isilon/BL32XU/BLsoft/PPPP/10.Zoo/TEST/"

	# Zoo progress report
        zooprog=open("%s/zoo_large.log"%root_dir, "a")

        # preparation
	dev=Device.Device(s)
	dev.init()
       	dev.prepCenteringLargeHolderCam1()

	"""
	# Dismount current pin
	zoo.dismountCurrentPin()
	zoo.waitTillReady()

       	dev.prepCenteringLargeHolderCam1()
        inocc.getImage("back1.png")

        # preparation
        dev.prepCenteringLargeHolderCam2()
        inocc.getCam2Image("back2.png")
	"""

	# Conditions (normally cond.####)
	trayid="HRC1010"
	pinid=2

	h_beam=10.0
	v_beam=15.0
	shika_minscore=10
	shika_maxhits=100
	osc_width=0.1
	total_osc=5.0
	exp_henderson=0.45
	exp_time=0.02
	distance=300.0
	sample_name="holder1"
	prefix="data2"
	scan_mode="2D"
	scanv_um=2500
	scanh_um=2500
	vstep_um=15.0
	hstep_um=10.0
	att_idx=0
	raster_exp=0.02
        stopwatch=StopWatch.StopWatch()

        sx,sy,sz=dev.gonio.getXYZmm()
	sphi=dev.gonio.getPhi()

        endtime=datetime.datetime.now()
        #time_sec= (endtime-starttime).seconds

	#print time_sec

	################# Loop measurement
	lm=LoopMeasurement.LoopMeasurement(s,root_dir,prefix)
        cxyz=sx,sy,sz
	scan_id="2d"

	lm.prepDataCollection()

        raster_schedule,raster_path=lm.rasterMaster(scan_id,scan_mode,v_beam,h_beam,scanv_um,
                scanh_um,vstep_um,hstep_um,cxyz,sphi,att_idx=att_idx,distance=distance,exptime=raster_exp)

        # Raster scan results
        try:
                glist=[]
                #scan_id=lm.prefix
                # Crystal size setting
                if h_beam > v_beam:
                        crysize=h_beam/1000.0+0.0001
                else:
                        crysize=v_beam/1000.0+0.0001

                glist=lm.shikaSumSkipStrongMulti(cxyz,sphi,raster_path,
                        scan_id,thresh_nspots=shika_minscore,crysize=crysize,max_ncry=shika_maxhits,
                        mode="peak")

                n_crystals=len(glist)

                # Time calculation
                t_for_mount=stopwatch.getDsecBtw("start","mount_finished")/60.0
                t_for_center=stopwatch.getDsecBtw("mount_finished","centering_finished")/60.0
                t_for_raster=stopwatch.getDsecBtw("raster_start","raster_end")/60.0
                logstr="%20s %20s %5d crystals MCRD[min]:%5.2f %5.2f %5.2f"%(
                        stopwatch.getTime("start"),prefix,n_crystals,t_for_mount,t_for_center,t_for_raster)

        except MyException, tttt:
                print "Skipping this loop!!"
                # Disconnecting capture in this loop's 'capture' instance
                print "Disconnecting capture"
                lm.closeCapture()
		sys.exit(1)
