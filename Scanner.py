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
		self.filename = 'testScan.h5'
		self.baseModels = []
		self.elementModels = []
		self.dimX = 1000
		self.dimY = 1000
		self.startRot = 0.0
		self.stopRot = 0.0
		self.numImages = 180
		self.Stop = False

	def initLocator(self, models):
		polys = vtkAppendPolyData()
		
		for m in models:
			polys.AddInput(m.transformFilter.GetOutput())

		polys.Update()
		locator = vtkCellLocator()
		locator.SetDataSet(polys.GetOutput())
		locator.BuildLocator()

		return locator, polys.GetOutput().GetBounds()
		

	def exportTomoScanToHDF(self, filename, baseModels, elementModels, dimX, dimY, startRot, stopRot, numImages):
		print 'exporting tomo scan'
		saveVal = 1

		datasetNames = ['exchange/data']
		elementData = []
		#for i in range(len(elementModels)):
		for i in range(1):
			datasetNames += ['exchange/element'+str(i)]
			elementData.append( np.zeros((numImages, dimX, dimY), dtype=np.float32) )
		wdata = np.zeros((numImages, dimX, dimY), dtype=np.float32)
		thetaDset = np.zeros((numImages), dtype=np.float32)
		saver = H5Exporter()
		h5st = saver.H5_Start(filename, datasetNames, dimX, dimY, numImages)
		#create theta rotation dataset
		thetaH5st = saver.H5_Gen1DDataset(h5st.fid, 'exchange/theta', numImages)

		baseLocator, nbounds = self.initLocator(baseModels)
		elementLocator, ebounds = self.initLocator(elementModels)

		bounds = []
		
		offset = 2.0
		bounds += [nbounds[0] - offset]
		bounds += [nbounds[1] + offset]
		bounds += [nbounds[2] - offset]
		bounds += [nbounds[3] + offset]
		bounds += [nbounds[4] - offset]
		bounds += [nbounds[5] + offset]
		print 'bounds', bounds
		
		xItr = (bounds[1] - bounds[0]) / float(dimX)
		yItr = (bounds[3] - bounds[2]) / float(dimY)
		#if starting from 0 we want to go backwards
		angle = math.radians(startRot)
		delta = (math.radians(stopRot) - math.radians(startRot)) / float(numImages) 
		print 'angle',angle,'delta', delta
		cntr = 1
		zStart = bounds[4] - 100
		zEnd = bounds[5] + 100

		tolerance = 0.00001
		tmut = mutable(0)
		subId = mutable(0)

		for n in range(numImages):
			startTime = time.time()
			thetaDset[n] = angle
			print 'Image number',n+1,'of',numImages
			yStart = bounds[2]
			for y in range(dimY):
				if self.Stop:
					print 'Scan Stopped!'
					saver.H5_End(h5st)
					self.notifyFinish.emit()
					return
				xStart = bounds[0] 
				for x in range(dimX):
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
						for m in baseModels:
							wdata[n][x][y] += m.intersect_line(L0, L1)
					if elementLocator.IntersectWithLine(L0, L1, tolerance, tmut, p0, pcoords, subId) > 0:
						for e in range(len(elementModels)):
							elementData[0][n][x][y] += elementModels[e].intersect_line(L0, L1)
					xStart += xItr
				yStart += yItr
			self.notifyProgress.emit(cntr)
			cntr += 1
			saver.H5_SaveSlice(h5st, datasetNames[0], wdata, n)
			saver.H5_SaveSlice(h5st, datasetNames[1], elementData[0], n)
			angle += delta
			endTime = time.time()
			print int(endTime - startTime),'seconds per image'
			#for e in range(len(elementModels)):
			#	print 'Saving element', e
			#	saver.H5_SaveSlice(h5st, datasetNames[e+1], elementData[e], n)
		saver.H5_SaveDset(thetaH5st, 'exchange/theta', thetaDset)
		saver.H5_End(h5st)
		self.notifyFinish.emit()
		print 'finished exporting'

	def run(self):
		self.Stop = False
		self.exportTomoScanToHDF(self.filename, self.baseModels, self.elementModels, self.dimX, self.dimY, self.startRot, self.stopRot, self.numImages)

'''

import multiprocessing
import threading

class scanThread(threading.Thread):
	def __init__(self, dimX, dimY, startX, endX, startY, endY, xItr, yItr, scene):
		super(scanThread, self).__init__()
		self.dimX = dimX
		self.dimY = dimY
		self.startX = startX
		self.endX = endX
		self.startY = startY
		self.endY = endY
		self.xItr = xItr
		self.yItr = yItr
		self.scene = scene
		self.data = np.zeros((1, dimY, dimX), dtype=np.float32)
	def run(self):
		rDir = [0.0, 0.0, 1.0]
		for y in range(self.startY, self.endY):
			print y
			for x in range(self.startX, self.endX):
				L0 = [self.scene.minX + (self.xItr * x), self.scene.minY + (self.yItr * y), self.scene.minZ - 100]
				L1 = [self.scene.minX + (self.xItr * x), self.scene.minY + (self.yItr * y), self.scene.maxZ + 100]
				#print 'L0',L0, 'L1',L1
				#i = scene.intersect_line(L0, L1)
				self.data[0][y][x] = self.scene.intersect_baseModels(L0, rDir)




		if toThread == True:
			threads = []
			cpus = multiprocessing.cpu_count()
			yCut = dimY / cpus
			startY = 0
			endY = yCut
			for i in range (cpus):
				t = scanThread(dimX, dimY, 0, dimX, startY, endY, xItr, yItr, scene )
				t.start()
				threads += [t]
				startY += yCut
				endY += yCut
			for t in threads:
				t.join()
				for y in dimY:
					for x in dimX:
						wdata[0][y][x] += t.data[0][y][x]
		else:
'''
