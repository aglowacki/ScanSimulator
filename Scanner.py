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

	def exportSceneToHDF(self, filename, baseModels, elementModels, dimX, dimY ):
		dimZ = 1
		print 'exporting'
		saveVal = 1

		datasetNames = ['base']
		elementData = []
		#for i in range(len(elementModels)):
		for i in range(1):
			datasetNames += ['element'+str(i)]
			elementData.append( np.zeros((dimZ, dimY, dimX), dtype=np.float32) )
		wdata = np.zeros((dimZ, dimY, dimX), dtype=np.float32)
		saver = H5Exporter()
		h5st = saver.H5_Start(filename, datasetNames, dimX, dimY, dimZ)

		maxX = sys.float_info.min
		minX = sys.float_info.max
		maxY = sys.float_info.min
		minY = sys.float_info.max
		maxZ = sys.float_info.min
		minZ = sys.float_info.max
		for m in baseModels:
			b = m.getBounds()
			print 'bounds', b
			minX = min(minX, b[0])
			maxX = max(maxX, b[1])
			minY = min(minY, b[2])
			maxY = max(maxY, b[3])
			minZ = min(minZ, b[4])
			maxZ = max(maxZ, b[5])
		print 'bounding box minX',minX,'maxX',maxX,'minY',minY,'maxY',maxY,'minZ',minZ,'maxZ',maxZ
		xItr = (maxX - minX) / float(dimX)
		yItr = (maxY - minY) / float(dimY)
		#if starting from 0 we want to go backwards
		for y in range(dimY):
			print 'Scan line',y+1,'of',dimY
			for x in range(dimX):
				L0 = [minX + (xItr * x), minY + (yItr * y), minZ - 10]
				L1 = [L0[0], L0[1],  maxZ + 10]
				for m in baseModels:
					wdata[0][y][x] += m.intersect_line(L0, L1)
				for e in range(len(elementModels)):
					elementData[0][0][y][x] += elementModels[e].intersect_line(L0, L1)
		saver.H5_SaveSlice(h5st, datasetNames[0], wdata, 0)
		#for e in range(len(elementModels)):
		#	print 'Saving element', e
		#	saver.H5_SaveSlice(h5st, datasetNames[e], elementData[e], 0)
		saver.H5_SaveSlice(h5st, datasetNames[1], elementData[0], 0)
		saver.H5_End(h5st)
		print 'finished exporting'

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
		saver = H5Exporter()
		h5st = saver.H5_Start(filename, datasetNames, dimX, dimY, numImages)

		maxX = sys.float_info.min
		minX = sys.float_info.max
		maxY = sys.float_info.min
		minY = sys.float_info.max
		maxZ = sys.float_info.min
		minZ = sys.float_info.max
		for m in baseModels:
			b = m.getBounds()
			print 'bounds', b
			minX = min(minX, b[0])
			maxX = max(maxX, b[1])
			minY = min(minY, b[2])
			maxY = max(maxY, b[3])
			minZ = min(minZ, b[4])
			maxZ = max(maxZ, b[5])
		offset = 2.0
		minX -= offset
		minY -= offset
		minZ -= offset
		maxX += offset
		maxY += offset
		maxZ += offset
		#maxZ = max(maxX, maxZ) + 100
		#minZ = min(minX, minZ) + 100
		print 'bounding box minX',minX,'maxX',maxX,'minY',minY,'maxY',maxY,'minZ',minZ,'maxZ',maxZ
		xItr = (maxX - minX) / float(dimX)
		yItr = (maxY - minY) / float(dimY)
		#if starting from 0 we want to go backwards
		angle = math.radians(startRot)
		delta = (math.radians(stopRot) - math.radians(startRot)) / float(numImages)
		print 'angle',angle,'delta', delta
		cntr = 1
		L0Z = minZ - 100
		L1Z = maxZ + 100
		for n in range(numImages):
			startTime = time.time()
			print 'Image number',n+1,'of',numImages 
			for y in range(dimY):
				if self.Stop:
					print 'Scan Stopped!'
					saver.H5_End(h5st)
					self.notifyFinish.emit()
					return
				#print 'Scan line',y+1,'of',dimY
				L0Y = minY + (yItr * y)
				L1Y = L0Y
				for x in range(dimX):
					L0X = minX + (xItr * x)
					L1X = L0X
					L0RotX = (L0Z * math.sin(angle)) + (L0X * math.cos(angle))
					L0RotZ = (L0Z * math.cos(angle)) - (L0X * math.sin(angle))
					L1RotX = (L1Z * math.sin(angle)) + (L1X * math.cos(angle))
					L1RotZ = (L1Z * math.cos(angle)) - (L1X * math.sin(angle))
					L0 = [L0RotX, L0Y, L0RotZ]
					L1 = [L1RotX, L1Y, L1RotZ]
					#if y == 49 and x == 49:
					#	print 'L0',L0,'L1',L1
					for m in baseModels:
						wdata[n][x][y] += m.intersect_line(L0, L1)
					for e in range(len(elementModels)):
						elementData[0][n][x][y] += elementModels[e].intersect_line(L0, L1)
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
		saver.H5_End(h5st)
		self.notifyFinish.emit()
		print 'finished exporting'

	def exportTomoScanToHDF2(self, filename, baseModels, elementModels, dimX, dimY, startRot, stopRot, numImages):
		print 'exporting tomo scan'
		saveVal = 1

		datasetNames = ['exchange/data']
		elementData = []
		#for i in range(len(elementModels)):
		for i in range(1):
			datasetNames += ['exchange/element'+str(i)]
			elementData.append( np.zeros((numImages, dimX, dimY), dtype=np.float32) )
		wdata = np.zeros((numImages, dimX, dimY), dtype=np.float32)
		saver = H5Exporter()
		h5st = saver.H5_Start(filename, datasetNames, dimX, dimY, numImages)

		addPolys = vtkAppendPolyData()
		
		maxX = sys.float_info.min
		minX = sys.float_info.max
		maxY = sys.float_info.min
		minY = sys.float_info.max
		maxZ = sys.float_info.min
		minZ = sys.float_info.max
		for m in baseModels:
			addPolys.AddInput(m.transformFilter.GetOutput())
			b = m.getBounds()
			print 'bounds', b
			minX = min(minX, b[0])
			maxX = max(maxX, b[1])
			minY = min(minY, b[2])
			maxY = max(maxY, b[3])
			minZ = min(minZ, b[4])
			maxZ = max(maxZ, b[5])

		addPolys.Update()
		locator = vtkCellLocator()
		locator.SetDataSet(addPolys.GetOutput())
		locator.BuildLocator()	

		offset = 2.0
		minX -= offset
		minY -= offset
		minZ -= offset
		maxX += offset
		maxY += offset
		maxZ += offset
		#maxZ = max(maxX, maxZ) + 100
		#minZ = min(minX, minZ) + 100
		print 'bounding box minX',minX,'maxX',maxX,'minY',minY,'maxY',maxY,'minZ',minZ,'maxZ',maxZ
		xItr = (maxX - minX) / float(dimX)
		yItr = (maxY - minY) / float(dimY)
		#if starting from 0 we want to go backwards
		angle = math.radians(startRot)
		delta = (math.radians(stopRot) - math.radians(startRot)) / float(numImages)
		print 'angle',angle,'delta', delta
		cntr = 1
		L0Z = minZ - 100
		L1Z = maxZ + 100

		tolerance = 0.00001
		tmut = mutable(0)
		subId = mutable(0)

		for n in range(numImages):
			startTime = time.time()
			print 'Image number',n+1,'of',numImages 
			for y in range(dimY):
				if self.Stop:
					print 'Scan Stopped!'
					saver.H5_End(h5st)
					self.notifyFinish.emit()
					return
				#print 'Scan line',y+1,'of',dimY
				L0Y = minY + (yItr * y)
				L1Y = L0Y
				for x in range(dimX):
					L0X = minX + (xItr * x)
					L1X = L0X
					L0RotX = (L0Z * math.sin(angle)) + (L0X * math.cos(angle))
					L0RotZ = (L0Z * math.cos(angle)) - (L0X * math.sin(angle))
					L1RotX = (L1Z * math.sin(angle)) + (L1X * math.cos(angle))
					L1RotZ = (L1Z * math.cos(angle)) - (L1X * math.sin(angle))
					L0 = [L0RotX, L0Y, L0RotZ]
					L1 = [L1RotX, L1Y, L1RotZ]
					
					p0 = [0.0, 0.0, 0.0]
					pcoords = [0.0, 0.0, 0.0]
					if locator.IntersectWithLine(L0, L1, tolerance, tmut, p0, pcoords, subId) > 0:
						#print 'L0',L0,'L1',L1
						for m in baseModels:
							wdata[n][x][y] += m.intersect_line(L0, L1)
						for e in range(len(elementModels)):
							elementData[0][n][x][y] += elementModels[e].intersect_line(L0, L1)
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
		saver.H5_End(h5st)
		self.notifyFinish.emit()
		print 'finished exporting'

	def run(self):
		self.Stop = False
		self.exportTomoScanToHDF2(self.filename, self.baseModels, self.elementModels, self.dimX, self.dimY, self.startRot, self.stopRot, self.numImages)

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
