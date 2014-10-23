'''
Arthur Glowacki
APS ANL
10/17/2014
'''

import vtk
from Model import Model

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

