'''
Arthur Glowacki
APS ANL
10/17/2014
'''

import vtk
from Model import Model
from random import random

class CubeModel(Model):
	def __init__(self):
		Model.__init__(self)
		self.source = vtk.vtkCubeSource()
		self.source.SetCenter(0.0, 0.0, 0.0)
		self.source.SetXLength(1.0)
		self.source.SetYLength(1.0)
		self.source.SetZLength(1.0)
		self.source.Update()
		self.Update()

class SphereModel(Model):
	def __init__(self):
		Model.__init__(self)
		self.source = vtk.vtkSphereSource()
		self.source.SetCenter(0.0, 0.0, 0.0)
		self.source.SetRadius(0.5)
		self.source.Update()
		self.Update()

class MultiSphereModel(Model):
	def __init__(self, amt, radius):
		Model.__init__(self)
		self.source = vtkAppendPolyData()
		halfRad = radius * 0.5
		for i in range(amt):
			s = vtk.vtkSphereSource()
			s.SetCenter(random() * halfRad, random() * halfRad, random * halfRad)
			s.SetRadius(0.5)
			s.Update()
			self.source.AddImput(s.GetOutput())
		#add center
		s = vtk.vtkSphereSource()
		s.SetCenter(0.0, 0.0, 0.0)
		s.SetRadius(0.5)
		s.Update()
		self.source.AddImput(s.GetOutput())
		self.Update()

