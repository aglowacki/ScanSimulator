'''
Arthur Glowacki
APS ANL
10/26/2014
'''

from vtk import *
import math, time
import h5py
import numpy as np
from PyQt4 import QtCore

class Volumizer(QtCore.QThread):
	notifyProgress = QtCore.pyqtSignal(int)
	notifyFinish = QtCore.pyqtSignal()

	def __init__(self):
		QtCore.QObject.__init__(self)
		self.filename = 'Volume.h5'
		self.allModelList = []
		self.dimX = 1000
		self.dimY = 1000
		self.dimZ = 1000
		self.bounds = []

	def __export__(self, pd, dim, hfile, datasetName):
		whiteImage = vtkImageData()
		wdata = np.zeros((dim[2], dim[0], dim[1]), dtype=np.float32)
		#bounds = pd.GetBounds()
		spacing = []
		spacing += [abs( self.bounds[1] - self.bounds[0] ) / dim[0] ]
		spacing += [abs( self.bounds[3] - self.bounds[2] ) / dim[1] ]
		spacing += [abs( self.bounds[5] - self.bounds[4] ) / dim[2] ]
		print 'spacing', spacing

		whiteImage.SetSpacing(spacing)

		print 'dim',dim
		whiteImage.SetDimensions(dim)
		whiteImage.SetExtent(0, dim[0] - 1, 0, dim[1] - 1, 0, dim[2] - 1)

		origin = [ self.bounds[0] + spacing[0] / 2 , self.bounds[2] + spacing[1] / 2, self.bounds[4] + spacing[2] / 2 ]
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

		dset = hfile.create_dataset(datasetName, (dim[2], dim[0], dim[1]))
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
			#dset[zOf] = d.GetTuple1(c)
		#end
		for z in range(dim[2]):
			dset[z] = wdata[z]
		del dset

	def export(self):
		print 'Starting export'
		startTime = time.time()

		count = len(self.allModelList)
		datasetNames = ['baseVolume']
		for i in range(count - 1):
			datasetNames += ['elementVolume'+str(i)]

		hfile = h5py.File(self.filename, 'w')

		count = len(self.allModelList)
		for i in range(count):
			#dset = hfile.create_dataset(datasetNames[i], (self.dimX, self.dimY, self.dimZ))
			addPolys = vtkAppendPolyData()
			for m in self.allModelList[i]:
				addPolys.AddInput(m.transformFilter.GetOutput())
			addPolys.Update()
			print 'Exporting',i+1,'of',count
			startExport = time.time()
			self.__export__(addPolys.GetOutput(), [self.dimX, self.dimY, self.dimZ], hfile, datasetNames[i])
			del addPolys
			print 'Finished export in', int(time.time() - startExport),'seconds'
		hfile.close()
		del hfile
		print 'Finished whole volume in', int(time.time() - startTime),' seconds'
		self.notifyFinish.emit()

	def run(self):
		self.export()

