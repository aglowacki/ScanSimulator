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
		self.source = vtk.vtkAppendPolyData()
		for i in range(amt):
			opX = 1.0
			opY = 1.0
			opZ = 1.0
			if random() > 0.5:
				opX *= -1.0
			if random() > 0.5:
				opY *= -1.0
			if random() > 0.5:
				opZ *= -1.0
			sRad = 0.25 + ( random() * 0.25 )
			x = float(random() * radius) * opX
			y = float(random() * radius) * opY
			z = float(random() * radius) * opZ
			s = vtk.vtkSphereSource()
			s.SetCenter(x,y,z)
			s.SetRadius(float(sRad))
			s.Update()
			self.source.AddInput(s.GetOutput())
		#add center
		s = vtk.vtkSphereSource()
		s.SetCenter(0.0, 0.0, 0.0)
		s.SetRadius(0.5)
		s.Update()
		self.source.AddInput(s.GetOutput())
		self.Update()

