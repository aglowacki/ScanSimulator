'''
Arthur Glowacki
APS ANL
10/17/2014
'''

from vtk import *
import math, time

class Volumizer:
	def __init__(self):
		print 'init'

	def __export__(self, filename, pd, spacing):
		whiteImage = vtkImageData()
		bounds = pd.GetBounds()

		whiteImage.SetSpacing(spacing)

		# compute dimensions
		dim = []
		for i in range(3):
			dim += [ int(math.ceil((bounds[i * 2 + 1] - bounds[i * 2]) / spacing[i])) ]

		whiteImage.SetDimensions(dim)
		whiteImage.SetExtent(0, dim[0] - 1, 0, dim[1] - 1, 0, dim[2] - 1)

		origin = [ bounds[0] + spacing[0] / 2 , bounds[2] + spacing[1] / 2, bounds[4] + spacing[2] / 2 ]
		whiteImage.SetOrigin(origin)


		whiteImage.SetScalarTypeToUnsignedChar()
		whiteImage.AllocateScalars()
		#whiteImage.AllocateScalars(VTK_UNSIGNED_CHAR,1);
		# fill the image with foreground voxels:
		inval = 255
		outval = 0
		count = whiteImage.GetNumberOfPoints()
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
 
		writer = vtkMetaImageWriter()
		writer.SetFileName(filename+'.mhd')
		writer.SetInput(imgstenc.GetOutput())
		writer.Write()


	def export(self, filename, baseModels, elementModels):
		print 'Starting export'
		startTime = time.time()
		addPolys = vtkAppendPolyData()
		for m in baseModels:
			addPolys.AddInput(m.transformFilter.GetOutput())
		addPolys.Update()
		print 'Saving Base'
		self.__export__('base', addPolys.GetOutput(), [0.5, 0.5, 0.5])
		del addPolys

		addPolys2 = vtkAppendPolyData()
		for m in elementModels:
			addPolys2.AddInput(m.transformFilter.GetOutput())
		addPolys2.Update()
		print 'Saving Elements'
		self.__export__('element', addPolys2.GetOutput(), [0.5, 0.5, 0.5])

		print 'Finished export in', int(time.time() - startTime),' seconds'


