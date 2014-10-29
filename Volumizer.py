'''
Arthur Glowacki
APS ANL
10/26/2014
'''

from vtk import *
import math, time
from H5Exporter import H5Exporter
import numpy as np
from PyQt4 import QtCore

class Volumizer(QtCore.QThread):
	notifyProgress = QtCore.pyqtSignal(int)
	notifyFinish = QtCore.pyqtSignal()

	def __init__(self):
		QtCore.QObject.__init__(self)
		self.filename = 'Volume.h5'
		self.baseModels = []
		self.elementModels = []
		self.dimX = 1000
		self.dimY = 1000
		self.dimZ = 1000

	def __export__(self, filename, pd, bounds, dim):
		whiteImage = vtkImageData()
		wdata = np.zeros((dim[2], dim[0], dim[1]), dtype=np.float32)
		#bounds = pd.GetBounds()
		spacing = []
		spacing += [abs( bounds[1] - bounds[0] ) / dim[0] ]
		spacing += [abs( bounds[3] - bounds[2] ) / dim[1] ]
		spacing += [abs( bounds[5] - bounds[4] ) / dim[2] ]
		print 'spacing', spacing

		whiteImage.SetSpacing(spacing)

		print 'dim',dim
		whiteImage.SetDimensions(dim)
		whiteImage.SetExtent(0, dim[0] - 1, 0, dim[1] - 1, 0, dim[2] - 1)

		origin = [ bounds[0] + spacing[0] / 2 , bounds[2] + spacing[1] / 2, bounds[4] + spacing[2] / 2 ]
		whiteImage.SetOrigin(origin)


		#whiteImage.SetScalarTypeToUnsignedChar()
		whiteImage.SetScalarTypeToFloat()
		whiteImage.AllocateScalars()
		#whiteImage.AllocateScalars(VTK_UNSIGNED_CHAR,1);
		# fill the image with foreground voxels:
		inval = 1.0
		outval = 0.0
		count = whiteImage.GetNumberOfPoints()
		print 'count',count
		for i in range(count):
			whiteImage.GetPointData().GetScalars().SetTuple1(i, inval)

		# polygonal data -. image stencil:
		pol2stenc = vtkPolyDataToImageStencil()
		pol2stenc.SetInput(pd)
		pol2stenc.SetOutputOrigin(origin)
		pol2stenc.SetOutputSpacing(spacing)
		pol2stenc.SetOutputWholeExtent(whiteImage.GetExtent())
		pol2stenc.Update()
 
		# cut the corresponding white image and set the background:
		imgstenc = vtkImageStencil()
		imgstenc.SetInput(whiteImage)
		imgstenc.SetStencil(pol2stenc.GetOutput())
		imgstenc.ReverseStencilOff()
		imgstenc.SetBackgroundValue(outval)
		imgstenc.Update()

		d = imgstenc.GetOutput().GetPointData().GetArray(0)
		#print p
		#d = whiteImage.GetPointData().GetArray(0)
		c = 0
		for z in range(dim[2]):
			zOf = dim[2] - z - 1
			for y in range(dim[1]):
				yOf = dim[1] - y - 1
				for x in range(dim[0]):
					wdata[zOf][x][yOf] = d.GetTuple1(c)
					c+=1

		#writer = vtkMetaImageWriter()
		#writer.SetFileName(filename+'.mhd')
		#writer.SetInput(imgstenc.GetOutput())
		#writer.Write()
		return wdata

	def export(self, filename, baseModels, elementModels, dimX, dimY, dimZ):
		print 'Starting export'
		startTime = time.time()

		datasetNames = ['baseVolume']
		elementData = []
		#for i in range(len(elementModels)):
		for i in range(1):
			datasetNames += ['elementVolume'+str(i)]

		saver = H5Exporter()
		h5st = saver.H5_Start(filename, datasetNames, dimX, dimY, dimZ)

		addPolys = vtkAppendPolyData()
		for m in baseModels:
			addPolys.AddInput(m.transformFilter.GetOutput())
		addPolys.Update()
		
		nbounds = addPolys.GetOutput().GetBounds()
		bounds = []
		
		offset = 2.0
		bounds += [nbounds[0] - offset]
		bounds += [nbounds[1] + offset]
		bounds += [nbounds[2] - offset]
		bounds += [nbounds[3] + offset]
		bounds += [nbounds[4] - offset]
		bounds += [nbounds[5] + offset]
		print 'bounds', bounds

		print 'Saving Base'
		wdata = self.__export__('base', addPolys.GetOutput(), bounds, [dimX, dimY, dimZ])
		del addPolys

		for z in range(dimZ):
			saver.H5_SaveSlice(h5st, datasetNames[0], wdata, z)
		del wdata


		#todo for loop for elements
		addPolys2 = vtkAppendPolyData()
		for m in elementModels:
			addPolys2.AddInput(m.transformFilter.GetOutput())
		addPolys2.Update()
		print 'Saving Elements'
		wdata = self.__export__('element', addPolys2.GetOutput(), bounds, [dimX, dimY, dimZ])

		for z in range(dimZ):
			saver.H5_SaveSlice(h5st, datasetNames[1], wdata, z)
		del wdata

		saver.H5_End(h5st)
		print 'Finished export in', int(time.time() - startTime),' seconds'
		self.notifyFinish.emit()

	def run(self):
		self.export(self.filename, self.baseModels, self.elementModels, self.dimX, self.dimY, self.dimZ)

