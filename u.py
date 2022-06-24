import sys,os,math,cv2,socket,time
import numpy as np
sys.path.append("/isilon/BL32XU/BLsoft/PPPP/10.Zoo/Libs/")
from MyException import * 
import Centering
import RasterSchedule
import SummarySHIKA
import Zoo
import Light
import Colli
import MultiCrystal
import AttFactor
import Beamsize
import GonioVec
import RDprop
import ScheduleBSS_HS
import AnaShika
import LoopMeasurement

if __name__ == "__main__":
	ms = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ms.connect(("192.168.163.1", 10101))
	skip=True

	root_dir="/isilon/users/target/target/Staff/2016A/160617/lysdose/"
	prefix="lys-1dps5-1201-05"
	trayid=1
	pinid=1
	beamsize=10.0

	lm=LoopMeasurement.LoopMeasurement(ms,root_dir,prefix)
	scan_id="2d"
	raster_path="%s/%s/scan/%s/"%(root_dir,prefix,scan_id)
	R_tmp=(0,0,0)
	phi=0.0
	R_final=lm.shikaSingleEdges(R_tmp,phi,raster_path,scan_id,thresh_nspots=10,margin=0.005,crysize=0.016)
