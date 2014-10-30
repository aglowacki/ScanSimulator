'''
Arthur Glowacki
APS ANL
10/17/2014
'''

from Model import Model
import numpy as np
import math, time, sys
from H5Exporter import H5Exporter
from PyQt4 import QtCore
from vtk import *

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
		self.saver = None
		self.h5st = None
		self.bSaveTheta = False

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

		wdata = np.zeros((self.numImages, self.dimX, self.dimY), dtype=np.float32)
		if self.bSaveTheta:
			thetaDset = np.zeros((self.numImages), dtype=np.float32)
			#create theta rotation dataset
			thetaH5st = self.saver.H5_Gen1DDataset(self.h5st.fid, 'exchange/theta', self.numImages)

		baseLocator, nbounds = self.initLocator()
		bounds = []
		offset = 2.0
		bounds += [nbounds[0] - offset]
		bounds += [nbounds[1] + offset]
		bounds += [nbounds[2] - offset]
		bounds += [nbounds[3] + offset]
		bounds += [nbounds[4] - offset]
		bounds += [nbounds[5] + offset]
		#print 'bounds', bounds
		
		xItr = (bounds[1] - bounds[0]) / float(self.dimX)
		yItr = (bounds[3] - bounds[2]) / float(self.dimY)
		#if starting from 0 we want to go backwards
		angle = math.radians(self.startRot)
		delta = (math.radians(self.stopRot) - math.radians(self.startRot)) / float(self.numImages) 
		#print 'angle',angle,'delta', delta
		cntr = 1
		zStart = bounds[4] - 100
		zEnd = bounds[5] + 100

		tolerance = 0.00001
		tmut = mutable(0)
		subId = mutable(0)

		for n in range(self.numImages):
			startTime = time.time()
			if self.bSaveTheta:
				thetaDset[n] = angle
			print self.datasetName,'Image number',n+1,'of',self.numImages
			yStart = bounds[2]
			for y in range(self.dimY):
				#print 'scan line', y
				if self.Stop:
					print self.datasetName,'Scan Stopped!'
					self.notifyFinish.emit()
					return
				xStart = bounds[0] 
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
			self.saver.H5_SaveSlice(self.h5st, self.datasetName, wdata, n)
			angle += delta
			endTime = time.time()
			print self.datasetName, ' ',int(endTime - startTime),'seconds per image'
		if self.bSaveTheta:
			self.saver.H5_SaveDset(thetaH5st, 'exchange/theta', thetaDset)
		self.notifyFinish.emit()
		print self.datasetName,' finished exporting'

	def run(self):
		self.Stop = False
		self.exportTomoScanToHDF()

