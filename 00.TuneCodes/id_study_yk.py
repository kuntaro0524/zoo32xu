#!/bin/env python 
import sys
import socket
import time
import datetime

# My library
from FES import *
from ID import *
from Mono import *
from File import *
from TCS import *
#from Count import *

def SearchPoint(fname,max):
  ratio = 0.8
  i = 0
  flag = 0
  detune0=[0]*2
  detune1=[0]*2
  val0=[0]*2
  val1=[0]*2

  cols=[]
  f = open(fname,"r")
  lines = f.readlines()
  f.close()
  for line in lines:
        if line.strip().find("#")==0:
                continue
        new=[]
        new=line.replace(","," ").strip().split()

        cols.append(new)

        ncols=len(cols)
        #print self.ncols

  xdat=[]
  ydat=[]

  for idx in range(0,ncols):
        xdat.append(float(cols[idx][1]))
        ydat.append(float(cols[idx][2]))

  xd=pylab.array(xdat)
  yd=pylab.array(ydat)

  print "ncols ,max, threshold = %d %d %f\n" % (ncols, max, max * ratio)

  while i < ncols:
#	print "loop i = %d" % i
#	print xd[i],yd[i]
#	print "\n"
	if (flag == 0) and (yd[i] >= max * ratio):
		if (i == 0):
			detune0 = [xd[i],xd[i+1]]
			val0 = [yd[i],yd[i+1]]
		else: 
			detune0 = [xd[i-1],xd[i]]
			val0 = [yd[i-1],yd[i]]
		print "i = %d, threshold = %f, val0= %s\n" %(i,max * ratio,val0)
		flag = 1
	if (flag == 1) and (yd[i] <= max * ratio):
		detune1 = [xd[i-1],xd[i]]
		val1 = [yd[i-1],yd[i]]
		print "i = %d, threshold = %f, val1= %s\n" %(i,max * ratio,val1)
		break
	i += 1

  print "detune0 = %s, detune1 = %s \n" %(detune0, detune1)
  return detune0, detune1

	
if __name__=="__main__":
 host = '172.24.242.41'
 port = 10101
 s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 s.connect((host,port))

 while True:

# Energy range
#    en_start=8.3
    en_start=13.1
    en_end=13.2
    en_step=0.1

#    en_start=12.4
#    en_end=12.5
    en_step=0.1

# Intesity decay ratio for ID detune
    ratio=0.8

# Filename
    #en_list=[8.0,8.1,8.2,13.1,20.3,20.4,20.5]
    #en_list=[8.5,10.0,11.0,12.0,12.398,14.0,15.0,16.0,17.0,18.0,19.0,20.0]
    #en_list=[12.398]

# Rough scan
    idch1=3
    rough_step=0.10
    fine_step=0.01
    sfine_step=0.001

# Devices
    id=ID(s)
    mono=Mono(s)
    fes=FES(s)
    f=File("./")
    tcs=TCS(s)

    tcs.setApert(5.0,5.0)
    tcs.setPosition(-0.6601,0.0642)

    index=0
   
    # log file
    logf=open("id.log","w")
    logfc=open("id_close.log","w")
    logfo=open("id_open.log","w")

    # Energy range
    width=en_end-en_start
    npoint=int(width/en_step)+1

    for idx in range(0,npoint) :

	# energy
	en=en_start+float(idx)*float(en_step)

	# file prefix
	enstr="%fkev"%(en)

	#moving the fisrt position
	mono.changeE(en)
	id.moveE(en)

#	if en==8.3:
	if en==9.5:
		print "wainting"
		time.sleep(3600)

# dtheta1 tune
	prefix="%03d_%s_dt1"%(f.getNewIdx3(),enstr)
	mono.scanDt1PeakConfig(prefix,"DTSCAN_FULLOPEN",tcs)

# Rough scan
	prefix="%03d_%s_coarse"%(f.getNewIdx3(),enstr)
	current_id=id.getE(en)
	start=current_id-rough_step*10
	end=current_id+rough_step*10

	if start<=7.4:
		start=7.4
	else:
		id.move(start - 0.1)

	print "Rough Scan start for ID = %f mm\n" % current_id
	id.move(start)
	max1=id.scanID(prefix,start,end,rough_step,idch1,0,0.2)

	id.move(max1[0] - 0.1)
	id.move(max1[0])
	counter=Count(s,3,0)
	IntPin=counter.getCount(0.2)
	#print "Pin Count = \n" % IntPin
	print IntPin

	detune0,detune1 = SearchPoint(prefix+"_id.scn",IntPin[0])

# Fine scan
	prefix="%03d_%s_fine"%(f.getNewIdx3(),enstr)
	current_id=max1[0]
	start=current_id-fine_step*10.0
	end=current_id+fine_step*10.0

	if start<=7.4:
		start=7.4
	else:
		id.move(start - 0.1)
		

	print "Fine Scan start for ID = %f mm\n" % current_id
	id.move(start)
	max2=id.scanID(prefix,start,end,fine_step,idch1,0,0.2)

	id.move(max2[0] - 0.1)
	id.move(max2[0])
	counter=Count(s,3,0)
	IntPin=counter.getCount(0.2)

# Fine scan for search Detune ID Position (close)
	prefix="%03d_%s_fine_close"%(f.getNewIdx3(),enstr)
	start = detune0[0] + (detune0[0] - detune0[1])
	end = detune0[1] - (detune0[0] - detune0[1])

	print "scan range is "
	print start, end , fine_step
	print "\n"

	if start<=7.4:
		start=7.4
	else:
		id.move(start - 0.1)

	print "\nFine Scan Detune Close ID from %f to %f\n" % (start, end)
	id.move(start)
	id.scanID(prefix,start,end,fine_step,idch1,0,0.2)
	detune0,tmp= SearchPoint(prefix+"_id.scn",IntPin[0])

# Fine scan for search Detune ID Position (open)
	prefix="%03d_%s_fine_open"%(f.getNewIdx3(),enstr)
	start = detune1[0] + (detune1[0] - detune1[1])
	end = detune1[1] - (detune1[0] - detune1[1])

	if start<=7.4:
		start=7.4
	else:
		id.move(start - 0.1)

	print "\nFine Scan Detune Open ID from %f to %f\n" % (start, end)
	id.move(start)
	id.scanID(prefix,start,end,fine_step,idch1,0,0.2)
	tmp,detune1 = SearchPoint(prefix+"_id.scn",IntPin[0])

# Superfine scan
	prefix="%03d_%s_superfine"%(f.getNewIdx3(),enstr)
	current_id=max2[0]
	start=current_id-sfine_step*10.0
	end=current_id+sfine_step*10.0

	if start<=7.4:
		start=7.4
	else:
		id.move(start - 0.1)

	id.move(start)
	print "\nSuper Fine Scan start for ID = %f mm\n" % current_id
	max3=id.scanID(prefix,start,end,sfine_step,idch1,0,0.2)

	print "\nMax Intensity ID gap by SuperFine Scan"
	print max3

	id.move(max3[0] - 0.1)
	id.move(max3[0])

	# dtheta1 tune @ TCS 5.0,5.0
	prefix="%03d_%s_max"%(f.getNewIdx3(),enstr)
	mono.scanDt1PeakConfig(prefix,"DTSCAN_FULLOPEN",tcs)

	# Writing log file
	counter=Count(s,3,0)
	pin_value=counter.getPIN(6)
	IntPin=counter.getCount(0.2)
	logf.write("%8.3f keV ID %8.5f PIN: %8s uA\n"%(en,max3[0],pin_value))
	logf.flush()

	# TCS scan
	prefix="%03d_%s"%(f.getNewIdx3(),enstr)
	vcenter,hcenter=tcs.scanBoth(prefix,0.05,0.5,-1.0,1.0,0.05,idch1,0,0.2)
	tcs.setApert(5.0,5.0)
	tcs.setPosition(-0.6601,0.0642)
	print "TCS scan finished in Max Int\n"


# Super Fine scan for search Detune ID Position (close)
	prefix="%03d_%s_superfine_close"%(f.getNewIdx3(),enstr)
	start = detune0[0] + (detune0[0] - detune0[1])
	end = detune0[1] - (detune0[0] - detune0[1])

	if start<=7.4:
		start=7.4
	else:
		id.move(start - 0.1)

	print "\nSuperFine Scan Detune Close ID from %f to %f\n" % (start, end)
	id.move(start)
	id.scanID(prefix,start,end,sfine_step,idch1,0,0.2)
	detune0,tmp= SearchPoint(prefix+"_id.scn",IntPin[0])

	id.move(detune0[0] - 0.1)
	id.move(detune0[0])

	# dtheta1 tune @ TCS 3.0,3.0
	prefix="%03d_%s_close"%(f.getNewIdx3(),enstr)
	mono.scanDt1PeakConfig(prefix,"DTSCAN_FULLOPEN",tcs)

	# Writing log file
	counter=Count(s,3,0)
	pin_valuec=counter.getPIN(6)
	logfc.write("%8.3f keV ID %8.5f PIN: %8s uA\n"%(en,detune0[0],pin_valuec))
	logfc.flush()

	# TCS scan
	prefix="%03d_%s"%(f.getNewIdx3(),enstr)
	vcenter,hcenter=tcs.scanBoth(prefix,0.05,0.5,-1.0,1.0,0.05,idch1,0,0.2)
	tcs.setApert(5.0,5.0)
	tcs.setPosition(-0.6601,0.0642)
	print "TCS scan finished in Detune to Closer ID pos\n"

# Super Fine scan for search Detune ID Position (open)
	prefix="%03d_%s_superfine_open"%(f.getNewIdx3(),enstr)
	start = detune1[0] + (detune1[0] - detune1[1])
	end = detune1[1] - (detune1[0] - detune1[1])

	if start<=7.4:
		start=7.4
	else:
		id.move(start - 0.1)

    	id.move(start)
	print "\nSuperFine Scan Detune Open ID from %f to %f\n" % (start, end)
	id.scanID(prefix,start,end,sfine_step,idch1,0,0.2)
	tmp,detune1 = SearchPoint(prefix+"_id.scn",IntPin[0])

	id.move(detune1[0] - 0.1)
	id.move(detune1[0])

	# dtheta1 tune @ TCS 5.0,5.0
	prefix="%03d_%s_open"%(f.getNewIdx3(),enstr)
	mono.scanDt1PeakConfig(prefix,"DTSCAN_FULLOPEN",tcs)

	# Writing log file
    	counter=Count(s,3,0)
    	pin_valueo=counter.getPIN(6)
	logfo.write("%8.3f keV ID %8.5f PIN: %8s uA\n"%(en,detune1[0],pin_valueo))
	logfo.flush()

	# TCS scan
	prefix="%03d_%s"%(f.getNewIdx3(),enstr)
	vcenter,hcenter=tcs.scanBoth(prefix,0.05,0.5,-1.0,1.0,0.05,idch1,0,0.2)
	tcs.setApert(5.0,5.0)
	tcs.setPosition(-0.6601,0.0642)
	print "TCS scan finished in Detune to Open ID pos\n"

	

    s.close()

    break

  en = 12.3984
  mono.changeE(en)
  id.moveE(en)

