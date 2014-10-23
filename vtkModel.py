from OpenGL.GL import *
import math
import numpy as np
import copy
import vtk

class Model:
	polyData = vtk.vtkPolyData()
	triangles = vtk.vtkCellArray()
	listname = 0
	def __init__(self, filepath, genList):
		self.maxX = 0.0
		self.maxY = 0.0
		self.maxZ = 0.0
		self.minX = 0.0
		self.minY = 0.0
		self.minZ = 0.0
		self.tris = []
		self.listname = None
		self.translate = [0.0, 0.0, 0.0]
		self.scale = [1.0, 1.0, 1.0]
		self.rotate = [0.0, 0.0, 0.0]
		if not filepath == None:
			self.loadObj(filepath)
		#finalState is when all transformation have been done
		self.finalState = False
		if genList == True:
			self.createList()

	def createList(self):
		if not self.listname == None:
			glDeleteLists(self.listname, 1)
		self.listname = glGenLists(1)
		glNewList(self.listname,GL_COMPILE)
		self.rawDraw()
		glEndList()

	def getCopy(self):
		m = Model(None, False)
		m.triangles = copy.copy(self.triangles)
		m.normals = copy.copy(self.normals)
		return m
	
	def loadObj(self,filepath):
		#cleanPolyData = vtk.vtkCleanPolyData()
		#cleanPolyData.SetInput(self.polyData)
		#cleanPolyData.SetTolerance(0.005)
		#smooth_loop = vtk.vtkLoopSubdivisionFilter()
		#smooth_loop.SetNumberOfSubdivisions(3)
		#smooth_loop.SetInputConnection(cleanPolyData.GetOutputPort())
		self.c = vtk.vtkSphereSource()
		self.c.SetRadius(50)
		self.c.SetThetaResolution(100)
		self.c.SetPhiResolution(100)
		self.locator = vtk.vtkCellLocator()
		self.locator.SetDataSet(self.c.GetOutput())
		self.locator.BuildLocator()
	
	def normalize3(self, v1):
		l = math.sqrt( (v1[0] * v1[0]) + (v1[1] * v1[1]) + (v1[2] * v1[2]) ) 
		return (v1[0] / l, v1[1] / l, v1[2] / l)

	def identity_transform(self):
		self.translate = [0.0, 0.0, 0.0]
		self.scale = [1.0, 1.0, 1.0]
		self.rotate = [0.0, 0.0, 0.0]

	#trasform verticies from unit to final form
	def finalize(self):
		if self.finalState == False:
			#rotate
			#scale
			#translate
			for t in self.triangles:
				t[0] += self.translate[0]
				t[1] += self.translate[1]
				t[2] += self.translate[2]
			self.finalState = True
			#self.identity_transform()
		else:
			print 'Model already in final state'
	
	def draw(self):
		glCallList(self.listname)
	
	def rawDraw(self):
		glRotate(self.rotate[2], 0.0, 0.0, 1.0)
		glRotate(self.rotate[1], 0.0, 1.0, 0.0)
		glRotate(self.rotate[0], 1.0, 0.0, 0.0)
		glTranslate(self.translate[0], self.translate[1], self.translate[2])
		glScale(self.scale[0], self.scale[1], self.scale[2])
		glBegin(GL_TRIANGLES)
		i = 0
		for triangle in self.triangles:
			glNormal3f(self.normals[i][0],self.normals[i][1],self.normals[i][2])
			glVertex3f(triangle[0][0],triangle[0][1],triangle[0][2])
			glVertex3f(triangle[1][0],triangle[1][1],triangle[1][2])
			glVertex3f(triangle[2][0],triangle[2][1],triangle[2][2])
			i+=1
		glEnd()

	def intersect_line( self, L0, L1 ):
		# Setup actor and mapper
		mapper = vtk.vtkPolyDataMapper()
		if vtk.VTK_MAJOR_VERSION <= 5:
			mapper.SetInputConnection(self.polyData.GetProducerPort())
		else:
			mapper.SetInputData(self.c.GetOutput())

		actor = vtk.vtkActor()
		actor.SetMapper(mapper)
		actor.GetProperty().SetPointSize(10)

		# Setup render window, renderer, and interactor
		renderer = vtk.vtkRenderer()
		renderWindow = vtk.vtkRenderWindow()
		renderWindow.AddRenderer(renderer)
		renderWindowInteractor = vtk.vtkRenderWindowInteractor()
		renderWindowInteractor.SetRenderWindow(renderWindow)
		renderer.AddActor(actor)

		renderWindow.Render()
		renderWindowInteractor.Start()
		return
		tolerance = 0.00001
		tmut = vtk.mutable(0)
		x = [0.0, 0.0, 0.0]
		pcoords = [0.0, 0.0, 0.0]
		subId = vtk.mutable(0)
		intersects = []
		i = self.locator.IntersectWithLine(L0, L1, tolerance, tmut, x, pcoords, subId)
		if i == 1:
			intersects += [x]
		return intersects
		'''
		for t in self.tris:
			i = t.IntersectWithLine(L0, L1, tolerance, tmut, x, pcoords, subId)
			if i == 1:
				intersects += [x]
		return intersects
		'''

if __name__ == '__main__':
	#m = Model('meshes/sphere.obj', False)
	m = Model('meshes/cube.obj', False)
	print m.intersect_line((0.3, 0.3, -10), (0.3, 0.3, 10))
	#print len(m.triangles) 
