'''
Arthur Glowacki
APS ANL
10/17/2014
'''

from Model import Model
import numpy as np
import math, time, sys
from H5Exporter import H5Exporter
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

class Scanner:
	def __inti__(self):
		print 'init scanner'

	def exportModelToHDF(self, model, dimX, dimY ):
		dimZ = 1
		print 'exporting'
		saveVal = 1
		rDir = [0.0, 0.0, 1.0]

		wdata = np.zeros((dimZ, dimY, dimX), dtype=np.float32)
		saver = H5Exporter()
		h5st = saver.H5_Start('test.h5', dimX, dimY, dimZ)

		print 'bounding box minX',model.minX,'maxX',model.maxX,'minY',model.minY,'maxY',model.maxY,'minZ',model.minZ,'maxZ',model.maxZ
		xItr = (model.maxX - model.minX) / float(dimX)
		yItr = (model.maxY - model.minY) / float(dimY)
		#if starting from 0 we want to go backwards
		for y in range(dimY):
			print y
			for x in range(dimX):
				L0 = [model.minX + (xItr * x), model.minY + (yItr * y), model.minZ - 10]
				L1 = [model.minX + (xItr * x), model.minY + (yItr * y), model.maxZ + 10]
				#print 'L0',L0, 'L1',L1
				#i = model.intersect_line(L0, L1)
				i = model.intersect_l(L0, rDir)
				if not i == None:
					nInters = len(i)
					#if nInters > 0:
					#	print 'nInters',nInters
					if nInters == 1: 
						print i
					if nInters > 2: 
						print i
					if nInters == 2: 
						#write to wdata 
						#print 'inters',i
						#hdfI = math.sqrt( (i[0][0] * i[0][0]) + (i[0][1] * i[0][1]) + (i[0][2] * i[0][2]) )
						hdfI = np.linalg.norm( np.subtract(i[0]  , i[1] ))
						#print 'hdfL', hdfI
						wdata[0][y][x] = hdfI
		saver.H5_SaveSlice(h5st, wdata, 0)
		saver.H5_End(h5st)
		print 'finished exporting'


	def exportSceneToHDF(self, baseModels, elementModels, dimX, dimY, toThread ):
		dimZ = 1
		print 'exporting'
		saveVal = 1
		rDir = [0.0, 0.0, 1.0]

		wdata = np.zeros((dimZ, dimY, dimX), dtype=np.float32)
		saver = H5Exporter()
		h5st = saver.H5_Start('test.h5', dimX, dimY, dimZ)

		maxX = sys.float_info.min
		minX = sys.float_info.max
		maxY = sys.float_info.min
		minY = sys.float_info.max
		maxZ = sys.float_info.min
		minZ = sys.float_info.max
		for m in baseModels:
			b = m.source.GetOutput().GetBounds()
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
			#if starting from 0 we want to go backwards
			for y in range(dimY):
				print y
				for x in range(dimX):
					L0 = [minX + (xItr * x), minY + (yItr * y), minZ - 10]
					L1 = [L0[0], L0[1],  maxZ + 10]
					#L1 = [minX + (xItr * x), minY + (yItr * y), maxZ + 10]
					#print 'L0',L0, 'L1',L1
					#i = scene.intersect_line(L0, L1)
					for m in baseModels:
						wdata[0][y][x] += m.intersect_line(L0, L1)
		saver.H5_SaveSlice(h5st, wdata, 0)
		saver.H5_End(h5st)
		print 'finished exporting'


