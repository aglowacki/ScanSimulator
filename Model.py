'''
Arthur Glowacki
APS ANL
10/17/2014
'''

import vtk
import math

class Model:
	def __init__(self):
		self.translate = [0.0, 0.0, 0.0]
		self.scale = [1.0, 1.0, 1.0]
		self.rotate = [0.0, 0.0, 0.0]
		self.source = None
		self.locator = vtk.vtkCellLocator()
		self.mapper = vtk.vtkPolyDataMapper()
		self.actor = vtk.vtkActor()
	 	self.density = 1.0

	def Update(self):
		if not self.source == None:
			self.locator.SetDataSet(self.source.GetOutput())
			self.locator.BuildLocator()	
			self.mapper.SetInputConnection(self.source.GetOutputPort())
			self.actor.SetMapper(self.mapper)
	
	def intersect_line( self, L0, L1 ):
		dist = 0.0
		tolerance = 0.00001
		tmut = vtk.mutable(0)
		p0 = [0.0, 0.0, 0.0]
		p1 = [0.0, 0.0, 0.0]
		pcoords = [0.0, 0.0, 0.0]
		subId = vtk.mutable(0)
		i = 0
		i += self.locator.IntersectWithLine(L0, L1, tolerance, tmut, p0, pcoords, subId)
		i += self.locator.IntersectWithLine(L1, L0, tolerance, tmut, p1, pcoords, subId)
		if i == 2:
			#print p0, p1
			distSquared = vtk.vtkMath.Distance2BetweenPoints(p0,p1)
			dist = math.sqrt(distSquared)
			#print 'dist',dist
		return dist * self.density

