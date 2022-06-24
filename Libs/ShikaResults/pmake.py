import sys,os,math
from numpy import *
import time
import datetime,time

#sys.path.append("/Users/kuntaro/00.Develop/Prog/02.Python/Libs/")
sys.path.append("/md1/work/Prog/02.Python/Libs")
from ReflWidthStill import *
from ReadMtz import *
from GaussFitXY import *

import iotbx.mtz
from libtbx import easy_mp
import scipy.spatial

class ProfileMaker:
	def __init__(self,still_mtz):
		self.still_mtz=still_mtz
		self.isGauss=False

	def init(self):
		start_time=time.time()
		## Open MOSFLM MTZ file
		self.smtz=ReadMtz(self.still_mtz)
		self.smtz.getSymmOption()

		## Extract intensity related cctbx.array
		self.stiI = self.smtz.getIntensityArray()

		## M/ISYMM
		self.s_isyms=self.smtz.getColumn("M_ISYM").data()%256

		## resolution
		self.s_d=self.stiI.d_spacings().data()

		## Batch number
		self.s_ba=self.smtz.getColumn("BATCH").data()

		# Detector area
		self.s_xa=self.smtz.getColumn("XDET").data()
		self.s_ya=self.smtz.getColumn("YDET").data()

		# If neede, make it possible 140129 KH
		# Detector area setting
		#self.da=DetectorArea(3072,8,4)
		#self.da.init()

		print "%10d reflections were read from %s"%(len(self.s_ba),self.still_mtz)
		self.nrefl=len(self.s_ba)
		end_time=time.time()
		print "Init: %10.1f sec"%(end_time-start_time)

	def isSameRefl(self,i1,i2):
		# HKL information of the first index
		hkl1=self.HKL[i1]
		isym1=self.ISYM[i1]
		# HKL information of the second index
		hkl2=self.HKL[i2]
		isym2=self.ISYM[i2]

		if hkl1==hkl2 and isym1==isym2:
			return True
		else:
			return False

	def prepInfo(self,matfile,startphi=35.0,stepphi=0.1,
		wl=1.24,divv=0.02,divh=0.02,mosaic=0.3,dispersion=0.0002):

		self.matfile=matfile
		self.wl=wl
		self.divv=0.02
		self.divh=0.02
		self.mosaic=0.3
		self.dispersion=0.0002

		start_time=time.time()

		# PHISTART and PHISTEP
		phi0=startphi

		# List of parameters
		self.HKL=[]
		self.PHI=[]
		self.I=[]
		self.SIGI=[]
		self.ISYM=[]
		self.BATCH=[]
		self.PINFO=[]

		idx=0
		for (hkl1,sI,ssigI),isym,batch,d in zip(self.stiI,
								self.s_isyms,self.s_ba,self.s_d):
			# Initial batch number
			if idx==0:
				batch0=batch

			# Convertion HKL -> original HKL in MOSFLM
			ohkl=self.smtz.getOriginalIndex(hkl1,isym)
			self.HKL.append(ohkl)
			self.I.append(sI)
			self.SIGI.append(ssigI)
			self.ISYM.append(isym)
			self.BATCH.append(batch)

			# Rotation angle
			phi1=phi0+(batch-batch0)*stepphi

			idx+=1

			# Collect info to array
			pinfo=ohkl,phi1,sI,ssigI
			self.PINFO.append(pinfo)

	def doProcess(self,missx,missy,missz):
		self.calcXYZQL(missx,missy,missz)

	def calcXYZQL(self,rx,ry,rz): # developed on 19th Feb 2014
		self.Q=[]
		self.RLP=[]
		self.Lorentz=[]
		self.XYZQL=[]
		idx=0

		# Apply miss-setting angle
		self.misx=rx
		self.misy=ry
		self.misz=rz
		
		## Lap time
		start_time=time.time()

		self.XYZQL=easy_mp.pool_map(
			fixed_func=self.getRefInfo,
			args=self.PINFO,
			processes=8)

		print "XYZQL=%5d"%len(self.XYZQL)
		#print "LEN(I)=%d"%len(self.I)

		idx=0
		for xyzql in self.XYZQL:
			xyz,q,l=xyzql
			self.RLP.append(xyz)
			self.Q.append(q)
			self.Lorentz.append(l)
			self.I[idx]=l*self.I[idx]
			idx+=1

		print "Processed %5d reflections"%len(self.Lorentz)
		end_time=time.time()
		print "Prep %10.1f sec"%(end_time-start_time)

	def getRefInfo(self,pinfo):
		# Required class for RLP coodrinate calculation
		rws=ReflWidthStill(self.matfile,self.divv,self.divh,self.mosaic,self.dispersion,self.wl)
		ohkl,phi1,sI,ssigI=pinfo

		# Missetting angle give in calcXYZQL
		rws.setMisset(self.misx,self.misy,self.misz)
		rws.setHKL(ohkl,phi1)
		rws.calcDELEPS()
		rws.calcLorentz()
		# RLP coordinate
		rlp=rws.getRLP()
		q=rws.calcQ()
		lorentz=rws.getLorentz()
		return rlp,q,lorentz

	def bunch(self):
		start_time=time.time()
		# independent reflection list
		self.reflist_i=[]

		# Working list
		lwork=[]

		# Initial condition
		save_i=0

		# Count reflections
		n_alone=0

		# Processing
		for i in range(1,self.nrefl):
			# check if saved reflection and this one is 'same' reflection
			# (not including 'equivalent'
			# DEBUGGING
			#print i,self.HKL[i],self.ISYM[i]

			if self.isSameRefl(i,save_i):
				lwork.append(i)
			else:
				if len(lwork)==1:
					#print "HKL is one",save_i,self.HKL[save_i]
					n_alone+=1

				# Reflection which fills conditions to estimate
				# intensity profile
				#else:
					#self.makeProfile(lwork)
					#print lwork

			# save information
				save_i=i
				self.reflist_i.append(lwork)
				lwork=[]
				lwork.append(i)

		print "%10d reflections are stored."%len(self.reflist_i)
		print "%10d reflections are rejected because observation was once"%n_alone
		end_time=time.time()
		print "Bunch %10.1f sec"%(end_time-start_time)

	def calcRLPdist(self,rlp1,rlp2):
		#print rlp1,rlp2
		vector=rlp1-rlp2
		dist=linalg.norm(vector)
		return dist

	def process_multi_gravity(self,dstar_thresh,nproc):
		# In order to make a 'tree' for fast calculation
		# Firstly, this routine makes the numpy array of RLP 
		# codes for each reflection
		# Each reflection is stored into self.reflist_i as indices
		# grouped from MTZ file
		# Ex) in self.reflist_i 
		# [0] 1,2,3,4,5
		# [1] 6,7,8
		# [2] 9
		# [3] 10,11,12
		# ...
		# ...
		# each index in each component represents the index
		# of reflections sorted in MTZ file

		start_time=time.time()

		# Finaly this list will be converted to numpy array
		rlp3d_list=[]

		###############
		# self.Grav is a list for storing Gravity
		###############
		print "calcGrav fitting starts: %s"%datetime.datetime.now()
		self.Grav=easy_mp.pool_map(
			fixed_func=self.calcGrav,
			args=self.reflist_i,
			processes=nproc)
		print "calcGrav ends: %s"%datetime.datetime.now()


		end_time=time.time()
		print "ProcessMulti %10.1f sec"%(end_time-start_time)

	def mon(self):
		tmp=[]
		# Selection
		for v in self.Grav:
			if v == -11111 or v == -99999:
				continue
			elif v <= 1.0 and v >= -1.0:
				#print "GOOD: %12.5f"%v
				tmp.append(fabs(v))

		ta=array(tmp)
		avv=average(ta)
		stt=std(ta)
		ndata=len(ta)

		return (avv,stt,ndata)

	def process_multi_gauss(self,nproc):
		# In order to make a 'tree' for fast calculation
		# Firstly, this routine makes the numpy array of RLP 
		# codes for each reflection
		# Each reflection is stored into self.reflist_i as indices
		# grouped from MTZ file
		# Ex) in self.reflist_i 
		# [0] 1,2,3,4,5
		# [1] 6,7,8
		# [2] 9
		# [3] 10,11,12
		# ...
		# ...
		# each index in each component represents the index
		# of reflections sorted in MTZ file

		start_time=time.time()

		###############
		# Multi-processing Guassian fitting of each reflection
		# self.Profile is a list for stroring Gaussian function
		# parameters (index is same with self.reflist_i)
		###############
		print "Gauss fitting starts: %s"%datetime.datetime.now()
		self.Profile=easy_mp.pool_map(
			fixed_func=self.gaussFit,
			args=self.reflist_i,
			processes=nproc)
		print "Gauss fitting ends: %s"%datetime.datetime.now()
		end_time=time.time()
		self.isGauss=True

	def monitorGauss(self):
		# Dummy Gaussian class for gauss value
		x=[0.0]
		y=[0.0]
		dmG=GaussFitXY(x,y)

		if self.isGauss == False:
			return -1
		
		gfile=open("gaus.dat","w")
		rfile=open("refi.dat","w")

		cnt_good=0
		cnt_bad=0
		for gauss,reflist in zip(self.Profile,self.reflist_i):
			A,mean,sigma=gauss
			if A==-9999:
				cnt_bad+=1
				continue
			else:
				cnt_good+=1


			gfile.write("GAUSS: %12.5f %12.5f %12.5f\n"%(A,mean,sigma))
			for idx in reflist:
				q=self.Q[idx]
				I=self.I[idx]

				# Value estimated from this gaussian function
				value=dmG.gaussian(q,A,mean,sigma)

				# Logging
				rfile.write("REFI %12.5f %12.5f %12.5f\n"%(q,I,value))
				gfile.write("REFI %12.5f %12.5f %12.5f\n"%(q,I,value))

			rfile.write("\n")

		print "GOOD: %5d BAD: %5d"%(cnt_good,cnt_bad)

		gfile.close()
		rfile.close()

			#print gauss,reflist

	def averageProfile(self,dstar_thresh):
		print "averageProfile starts: %s"%datetime.datetime.now()
		start_time=time.time()

		# Finaly this list will be converted to numpy array
		rlp3d_list=[]
		###############
		# processing each reflection to extract RLP coordinate
		# of the first index
		###############
		num_ng=0
		for each_refl in self.reflist_i:
			rlp_code=self.RLP[each_refl[0]]
			rlp3d_list.append(rlp_code)

		# Convertion of the list to numpy.array
		rlp3d=array(rlp3d_list)

		print len(self.Profile),len(rlp3d),len(self.reflist_i)

		# Making the tree for all RLPs
		self.tree=scipy.spatial.cKDTree(rlp3d)

		#print num_ng,num_ok  #s10.mtz Results = 5759 8534 140204
		self.Neighbors=[]

		# Grouping near reflection list
		for rlp in rlp3d: # For all of independent reflections
			proclist=[]
			dist,idx=self.tree.query(
				rlp,k=300,p=1,distance_upper_bound=dstar_thresh)
			# Bunch of processing
			for (d,i) in zip(dist,idx):
				if d==float('inf'):
					break
				else:
					proclist.append(i)
			self.Neighbors.append(proclist)

		# self.Neighbors has a same reflection index with
		# self.reflist_i

		# self.Neighbors, self.reflist_i, self.Profile 
		# Length of these list is equal

		ofile=open("profile.dat","w")
		for neighbor_bunch,intensity_array in zip(self.Neighbors,self.reflist_i):
			ofile.write("####\n")
			sumA=0.0
			sumMean=0.0
			sumSig=0.0
			num=0
			for refi in neighbor_bunch:
				A,mean,sigma=self.Profile[refi]
				if A != -9999 and A != -1111:
					sumA+=A
					sumMean+=mean
					sumSig+=sigma
					num+=1
					ofile.write("%20.5f %20.5f %20.5f\n"%(A,mean,sigma))
				if num!=0.0:
					#print sumA/num,sumMean/num,sumSig/num
					aveA=sumA/num
					aveMean=sumMean/num
					aveSig=sumSig/num
			#for idx in intensity_array:
				#print self.HKL[idx],self.I[idx]

		end_time=time.time()
		print "averageProfile starts: %s"%datetime.datetime.now()
		contime=end_time-start_time
		print "averageProfile %5.2f sec"%contime

	def calcGrav(self,iwork):
		# if a number of reflections is 2
		# Gravity fitting failed # Error code : -11111
		if len(iwork) <= 2:
			#print "Gravity calculation cannot be done #refls=%5d!"%len(iwork)
			grav=-11111
			return grav

		# Lorentz correction should be neglected
		# Gravity calculation
		tot_I=0.0
		tot_IQ=0.0

		for i in iwork:
			I=self.I[i]
			tot_I+=I
			tot_IQ=I*self.Q[i]

		try:
			grav=tot_IQ/tot_I
		except:
			grav=-99999

		return grav

	def gaussFit(self,iwork):
		xlist=[]
		ylist=[]

		# Number of reflections for gaussian fitting
		#print "DEBUG0: nref = %5d\n"%len(iwork)

		# if a number of reflections is 2
		# Gauss fitting is not conducted
		# Error code : -11111
		if len(iwork) <= 2:
			#print "Gaussian fitting cannot be done #refls=%5d!"%len(iwork)
			A,mean,sigma=-11111,-11111,-11111

		for i in iwork:
			xlist.append(self.Q[i])
			ylist.append(self.I[i])
			#print "GAUSS_SOURCE: ",self.Q[i],icorr,i
		#print "\n\n"

		# Gaussian fitting
		g=GaussFitXY(xlist,ylist)

		# Gaussian fitting
		# When the fitting fails, an error code of -9999 is set
		try:
			params=g.fit_without_base()
			A,mean,sigma=params
		except:
			A,mean,sigma=-9999,-9999,-9999

		#print "========"
		#print "GaussFit End"
		#print "========"
		
		return A,mean,sigma

if __name__ == "__main__":

	print len(sys.argv)

	if len(sys.argv)!=6:
		print "Usage MTZFILE MATFILE NPROC PHISTART DELTAPHI"
		sys.exit(1)

	mtzfile=sys.argv[1]
	matfile=sys.argv[2]
	nproc=int(sys.argv[3])
	phistart=float(sys.argv[4])
	deltaphi=float(sys.argv[5])

	# Doudemoii parameters now
	divv=0.02
	divh=0.02
	mosaic=0.3
	dispersion=0.0002

	# Missetting parameters for s5.mtz
	mx=0.0000
	my=0.06
	mz=0.24

	#mx=my=mz=0.0

	starttime=time.time()
	# ARG1 = MOSFLM MTZ file
	h=ProfileMaker(mtzfile)

	h.init()
	#h.prepInfo(matfile,startphi=0.0,stepphi=0.1)
	h.prepInfo(matfile,phistart,deltaphi)
	h.bunch()

	h.calcXYZQL(mx,my,mz)
	h.process_multi_gauss(nproc)

	#h.monitorGauss()
	# Profile making
	h.averageProfile(0.035)

	endtime=time.time()
	print endtime-starttime
