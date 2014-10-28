'''
Arthur Glowacki
APS ANL
10/17/2014
'''

import vtk
import math

class Model:
	def __init__(self):
		self.source = None
		self.locator = vtk.vtkCellLocator()
		self.mapper = vtk.vtkPolyDataMapper()
		self.actor = vtk.vtkActor()
	 	self.density = 1.0
		self.transform = vtk.vtkTransform()
		self.transformFilter=vtk.vtkTransformPolyDataFilter()
		self.transformFilter.SetTransform(self.transform)
		self.tolerance = 0.00001
		self.tmut = vtk.mutable(0)
		self.subId = vtk.mutable(0)

	def Update(self):
		if not self.source == None:
			self.transformFilter.SetInputConnection(self.source.GetOutputPort())
			self.transformFilter.Update()
			#self.locator.SetDataSet(self.source.GetOutput())
			self.locator.SetDataSet(self.transformFilter.GetOutput())
			self.locator.BuildLocator()	
			#self.mapper.SetInputConnection(self.source.GetOutputPort())
			self.mapper.SetInputConnection(self.transformFilter.GetOutputPort())
			self.actor.SetMapper(self.mapper)

	def setColor(self, r, g, b):
		self.actor.GetProperty().SetColor(r, g, b)

	def translate(self, x, y, z):
		self.transform.Translate(x,y,z)
		self.Update()

	def scale(self, x, y, z):
		self.transform.Scale(x,y,z)
		self.Update()

	def rotate(self, x, y, z):
		self.transform.RotateWXYZ(x,1,0,0)
		self.transform.RotateWXYZ(y,0,1,0)
		self.transform.RotateWXYZ(z,0,0,1)
		self.Update()

	def getBounds(self):
		return self.transformFilter.GetOutput().GetBounds()
	
	def intersect_line( self, L0, L1 ):
		dist = 0.0
		p0 = [0.0, 0.0, 0.0]
		p1 = [0.0, 0.0, 0.0]
		pcoords = [0.0, 0.0, 0.0]
		i = 0
		i += self.locator.IntersectWithLine(L0, L1, self.tolerance, self.tmut, p0, pcoords, self.subId)
		i += self.locator.IntersectWithLine(L1, L0, self.tolerance, self.tmut, p1, pcoords, self.subId)
		if i == 2:
			#print p0, p1
			distSquared = vtk.vtkMath.Distance2BetweenPoints(p0,p1)
			dist = math.sqrt(distSquared)
			#print 'dist',dist
		return dist * self.density

