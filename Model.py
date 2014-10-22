from OpenGL.GL import *
import math
import numpy as np

class Model:
	triangles = []
	normals = []
	listname = 0
	def __init__(self,filepath, genList):
		self.maxX = 0.0
		self.maxY = 0.0
		self.maxZ = 0.0
		self.minX = 0.0
		self.minY = 0.0
		self.minZ = 0.0
		self.loadObj(filepath)
		self.makeNormals()
		if genList == True:
			self.createList()

	def createList(self):
		self.listname = glGenLists(1)
		glNewList(self.listname,GL_COMPILE)
		self.rawDraw()
		glEndList()
	
	def loadObj(self,filepath):
		modelFile = open(filepath,"r")
		triangles = []
		vertices = []
		for line in modelFile.readlines():
			line = line.strip()
			if len(line)==0 or line.startswith("#"):
				continue
			data = line.split(" ")
			if data[0]=="v":
				x = float(data[1])
				y = float(data[2])
				z = float(data[3])
				vertices.append((x, y, z))
				self.maxX = max(self.maxX, x)
				self.maxY = max(self.maxY, y)
				self.maxZ = max(self.maxZ, z)
				self.minX = min(self.minX, x)
				self.minY = min(self.minY, y)
				self.minZ = min(self.minZ, z)
			if data[0]=="f":
				vertex1 = vertices[int(data[1].split("/")[0])-1]
				vertex2 = vertices[int(data[2].split("/")[0])-1]
				vertex3 = vertices[int(data[3].split("/")[0])-1]
				triangles.append((vertex1,vertex2,vertex3))
		self.triangles = triangles
	
	def normalize3(self, v1):
		l = math.sqrt( (v1[0] * v1[0]) + (v1[1] * v1[1]) + (v1[2] * v1[2]) ) 
		return (v1[0] / l, v1[1] / l, v1[2] / l)

	def makeNormals(self):
		normals = []
		for triangle in self.triangles:
			arm1 = np.subtract(triangle[1],triangle[0])
			arm2 = np.subtract(triangle[2],triangle[0])
			normals.append(self.normalize3(np.cross(arm1,arm2)))
		self.normals = normals
	
	def draw(self):
		glCallList(self.listname)
	
	def rawDraw(self):
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
		intersects = []
		for t in self.triangles:
			i = self.intersect3D_RayTriangle(L0, L1, t[0], t[1], t[2])
			if not i == None:
				intersects += [i]
		return intersects

	def intersect_l( self, L0, rDir ):
		intersects = []
		for t in self.triangles:
			i = self.intersectionTest(L0, rDir, t[0], t[1], t[2])
			if not i == None:
				intersects += [i]
		return intersects

	def intersectionTest(self, L0, rDir, v1, v2, v3):
		# structure for holding the result of the test
		edge1 = np.subtract(v2, v1)
		edge2 = np.subtract(v3, v1)
	
		# Find the cross product of edge2 and the ray direction
		s1 = np.cross(rDir, edge2)
	
		# Find the divisor, if its zero, return false as the triangle is
		# degenerated
		divisor = np.dot(s1, edge1)
		if divisor == 0.0:
			return None
	
		# A inverted divisor, as multipling is faster then division
		invDivisor = 1/ divisor
	
		# Calculate the first barycentic coordinate. Barycentic coordinates
		# are between 0.0 and 1.0
		distance = np.subtract(L0 , v1)
		barycCoord_1 = np.dot(distance, s1) * invDivisor
		if  barycCoord_1 < 0.0 or barycCoord_1 > 1.0:
			return None
	
		# Calculate the second barycentic coordinate
		s2 = np.cross(distance, edge1)
		barycCoord_2 = np.dot(rDir, s2) * invDivisor
		if barycCoord_2 < 0.0 or (barycCoord_1 + barycCoord_2) > 1.0:
			return None
	
		# After doing the barycentic coordinate test we know if the ray hits or 
		# not. If we got this far the ray hits.
		# Calculate the distance to the intersection point
		intersectionDistance = np.dot(edge2, s2) * invDivisor
	
		return np.add(L0, np.multiply( intersectionDistance , rDir ) )
	

	def intersect3D_RayTriangle( self, L0, L1, V0, V1, V2 ):
		'''
		converted to python from:
		// Copyright 2001 softSurfer, 2012 Dan Sunday
		// This code may be freely used and modified for any purpose
		// providing that this copyright notice is included with it.
		// SoftSurfer makes no warranty for this code, and cannot be held
		// liable for any real or imagined damage resulting from its use.
		// Users of this code must verify correctness for their application.
		'''
		SMALL_NUM = 0.00001

		# get triangle edge vectors and plane normal
		u = np.subtract(V1, V0)
		v = np.subtract(V2, V0)
		# cross product
		n = np.cross(u,  v) 
		# ray rayDirection vector
		rayDir = np.subtract(L1, L0)
		w0 = np.subtract(L0, V0)
		a = -np.dot(n, w0)
		b = np.dot(n, rayDir)
		if abs(b) < SMALL_NUM: # ray is  parallel to triangle plane
			if a == 0:#	 ray lies in triangle plane
				print '---------------------------'
				return 2
			else:
				return None

		# get intersect point of ray with triangle plane
		r = a / b
		if r < 0.0: # ray goes away from triangle
			return None
		#for a segment, also test if (r > 1.0) => no intersect
		#outP = L0 + r * rayDir # intersect point of ray and plane
		outP = np.add( L0 , np.multiply(rayDir, r)) # intersect point of ray and plane
		# is I inside T?
		uu = np.dot(u, u)
		uv = np.dot(u, v)
		vv = np.dot(v, v)
		w = np.subtract(outP, V0)
		wu = np.dot(w, u)
		wv = np.dot(w, v)
		D = (uv * uv) - (uu * vv)

		# get and test parametric coords
		s = (uv * wv - vv * wu) / D
		# I is outside T
		if s < 0.0 or s > 1.0:	
			return None
		t = (uv * wu - uu * wv) / D
		# I is outside T
		if t < 0.0 or (s + t) > 1.0:
				return None

		return outP


if __name__ == '__main__':
	m = Model('sphere.obj', False)
	#print m.intersect_line((0.3, 0.3, -10), (0.3, 0.3, 10))
	print len(m.triangles) , len(m.normals)
