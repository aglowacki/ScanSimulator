'''
Arthur Glowacki
APS ANL
10/17/2014
'''

from Model import Model
import numpy as np
import math, time
from H5Exporter import H5Exporter


class Scanner:
	def __inti__(self):
		print 'init scanner'

	def exportToHDF(self, model, dimX, dimY ):
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


