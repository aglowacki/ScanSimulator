'''
Arthur Glowacki
APS ANL
10/17/2014
'''

from Model import Model
import numpy as np
import math, time, sys
import h5py
from PyQt4 import QtCore
from vtk import *
import Optics

class Scanner(QtCore.QThread):
	notifyProgress = QtCore.pyqtSignal(int)
	notifyFinish = QtCore.pyqtSignal()

	def __init__(self):
		QtCore.QObject.__init__(self)
		self.baseModels = []
		self.datasetName = ''
		self.dimX = 1000
		self.dimY = 1000
		self.startRot = 0.0
		self.stopRot = 0.0
		self.numImages = 180
		self.Stop = False
		self.dsetLock = None
		self.hfile = None
		self.bSaveTheta = False
		self.bounds = []
		self.objectives = []
		self.calc = Optics.Optics()
		self.hdfFiles = []

	def initLocator(self):
		polys = vtkAppendPolyData()
		
		for m in self.baseModels:
			polys.AddInput(m.transformFilter.GetOutput())

		polys.Update()
		locator = vtkCellLocator()
		locator.SetDataSet(polys.GetOutput())
		locator.BuildLocator()

		return locator, polys.GetOutput().GetBounds()
		

	def exportTomoScanToHDF(self):
		print self.datasetName,' exporting tomo scan'

		self.obj_dsets = []
		self.dsetLock.lock()
		self.dset = self.hfile.create_dataset(self.datasetName, (self.numImages, self.dimX, self.dimY))
		for i in range(len(self.hdfFiles)):
			self.obj_dsets += [ self.hdfFiles[i].create_dataset(self.datasetName, (self.numImages, self.dimX, self.dimY)) ]
		self.dsetLock.unlock()

		wdata = np.zeros((self.numImages, self.dimX, self.dimY), dtype=np.float32)
		if self.bSaveTheta:
			thetaDset = np.zeros((self.numImages), dtype=np.float32)
			#create theta rotation dataset
			self.dsetLock.lock()
			thetaH5 = self.hfile.create_dataset('exchange/theta', (self.numImages,))
			self.obj_thetas = [  ]
			for i in range(len(self.hdfFiles)):
				self.obj_thetas += [ self.hdfFiles[i].create_dataset('exchange/theta', (self.numImages,)) ]
			self.dsetLock.unlock()

		baseLocator, nbounds = self.initLocator()

		xItr = (self.bounds[1] - self.bounds[0]) / float(self.dimX)
		yItr = (self.bounds[3] - self.bounds[2]) / float(self.dimY)
		#if starting from 0 we want to go backwards
		angle = math.radians(self.startRot)
		delta = (math.radians(self.stopRot) - math.radians(self.startRot)) / float(self.numImages) 
		#print 'angle',angle,'delta', delta
		cntr = 1
		zStart = self.bounds[4] - 100
		zEnd = self.bounds[5] + 100

		tolerance = 0.00001
		tmut = mutable(0)
		subId = mutable(0)

		for n in range(self.numImages):
			startTime = time.time()
			if self.bSaveTheta:
				thetaDset[n] = angle
			print self.datasetName,'Image number',n+1,'of',self.numImages
			yStart = self.bounds[2]
			for y in range(self.dimY):
				#print 'scan line', y
				if self.Stop:
					print self.datasetName,'Scan Stopped!'
					self.notifyFinish.emit()
					return
				xStart = self.bounds[0] 
				for x in range(self.dimX):
					L0RotX = (zStart * math.sin(angle)) + (xStart * math.cos(angle))
					L0RotZ = (zStart * math.cos(angle)) - (xStart * math.sin(angle))
					L1RotX = (zEnd * math.sin(angle)) + (xStart * math.cos(angle))
					L1RotZ = (zEnd * math.cos(angle)) - (xStart * math.sin(angle))
					L0 = [L0RotX, yStart, L0RotZ]
					L1 = [L1RotX, yStart, L1RotZ]
					
					p0 = [0.0, 0.0, 0.0]
					pcoords = [0.0, 0.0, 0.0]
					if baseLocator.IntersectWithLine(L0, L1, tolerance, tmut, p0, pcoords, subId) > 0:
						#print 'L0',L0,'L1',L1
						for m in self.baseModels:
							wdata[n][x][y] += m.intersect_line(L0, L1)
					xStart += xItr
				yStart += yItr
			self.notifyProgress.emit(cntr)
			cntr += 1
			'''
			#perform optics
			for objIndex in self.objectives:
				calc.coherent(wdata[n], 
				#then save
			'''
			self.dsetLock.lock()
			self.dset[n] = wdata[n]
			for i in range(len(self.obj_dsets)):
				self.obj_dsets[i][n] = self.calc.coherent(wdata[n], self.objectives[i])
			self.dsetLock.unlock()

			angle += delta
			endTime = time.time()
			print self.datasetName, ' ',int(endTime - startTime),'seconds per image'
		if self.bSaveTheta:
			self.dsetLock.lock()
			thetaH5[:] = thetaDset[:]
			for i in range(len(self.hdfFiles)):
				self.obj_thetas[i][:] = thetaDset[:]
		self.dsetLock.unlock()
		self.notifyFinish.emit()
		print self.datasetName,' finished exporting'

	def run(self):
		self.Stop = False
		self.exportTomoScanToHDF()

