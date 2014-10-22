'''
Arthur Glowacki
APS ANL
10/17/2014
'''

import sys
import math
from PyQt4 import QtCore, QtGui, QtOpenGL
from Model import Model
from Scanner import Scanner
import numpy as np
import math, time

try:
	from OpenGL import GL
except ImportError:
	app = QtGui.QApplication(sys.argv)
	QtGui.QMessageBox.critical(None, "OpenGL hellogl",
			"PyOpenGL must be installed to run this example.")
	sys.exit(1)

class Window(QtGui.QWidget):
	def __init__(self):
		super(Window, self).__init__()

		self.glWidget = GLWidget()
		self.scan = Scanner()

		self.xSlider = self.createSlider()
		self.ySlider = self.createSlider()
		self.zSlider = self.createSlider()

		self.xSlider.valueChanged.connect(self.glWidget.setXRotation)
		self.glWidget.xRotationChanged.connect(self.xSlider.setValue)
		self.ySlider.valueChanged.connect(self.glWidget.setYRotation)
		self.glWidget.yRotationChanged.connect(self.ySlider.setValue)
		self.zSlider.valueChanged.connect(self.glWidget.setZRotation)
		self.glWidget.zRotationChanged.connect(self.zSlider.setValue)

		self.exportBtn = QtGui.QPushButton('Export')
		self.exportBtn.clicked.connect(self.exportToHDF)
		self.loadModelBtn = QtGui.QPushButton('Load Model')
		self.loadModelBtn.clicked.connect(self.loadModel)

		mainLayout = QtGui.QHBoxLayout()
		mainLayout.addWidget(self.glWidget)
		mainLayout.addWidget(self.xSlider)
		mainLayout.addWidget(self.ySlider)
		mainLayout.addWidget(self.zSlider)
		m2Layout = QtGui.QVBoxLayout()
		m2Layout.addLayout(self.createGridInput())
		m2Layout.addLayout(mainLayout)
		m2Layout.addWidget(self.loadModelBtn)
		m2Layout.addWidget(self.exportBtn)
		self.setLayout(m2Layout)

		self.xSlider.setValue(15 * 16)
		self.ySlider.setValue(345 * 16)
		self.zSlider.setValue(0 * 16)


		self.setWindowTitle("Model2HDF")

	def createGridInput(self):
		GridStartVal = '10'
		hBox = QtGui.QHBoxLayout()
		self.GridXIn = QtGui.QLineEdit()
		self.GridYIn = QtGui.QLineEdit()
		self.GridZIn = QtGui.QLineEdit()

		self.GridXIn.setText(GridStartVal)
		self.GridYIn.setText(GridStartVal)
		self.GridZIn.setText(GridStartVal)

		hBox.addWidget(QtGui.QLabel("X"))
		hBox.addWidget(self.GridXIn)
		hBox.addWidget(QtGui.QLabel("Y"))
		hBox.addWidget(self.GridYIn)
		hBox.addWidget(QtGui.QLabel("Z"))
		hBox.addWidget(self.GridZIn)

		vBox = QtGui.QVBoxLayout()
		vBox.addWidget(QtGui.QLabel("Grid Size"))
		vBox.addLayout(hBox)

		return vBox

	def createSlider(self):
		slider = QtGui.QSlider(QtCore.Qt.Vertical)

		slider.setRange(0, 360 * 16)
		slider.setSingleStep(16)
		slider.setPageStep(15 * 16)
		slider.setTickInterval(15 * 16)
		slider.setTickPosition(QtGui.QSlider.TicksRight)

		return slider

	def exportToHDF(self):
		dimX = 100
		dimY = 100
		dimZ = 1
		self.scan.exportToHDF(self.glWidget.model, dimX, dimY)

	def loadModel(self, a):
		filename = QtGui.QFileDialog.getOpenFileName( self, "Open Mesh", ".", "Mesh Files (*.obj)")
		print 'loading model', filename
		self.glWidget.model = Model(filename, True)
		self.glWidget.updateGL()


class GLWidget(QtOpenGL.QGLWidget):
	xRotationChanged = QtCore.pyqtSignal(int)
	yRotationChanged = QtCore.pyqtSignal(int)
	zRotationChanged = QtCore.pyqtSignal(int)

	def __init__(self, parent=None):
		super(GLWidget, self).__init__(parent)

		self.xRot = 0
		self.yRot = 0
		self.zRot = 0

		self.gridList = None
		self.gridX = 10
		self.gridY = 10
		self.gridZ = 10

		self.model = None
		self.models = []

		self.orthoLeft = -10.5
		self.orthoRight = 10.5
		self.orthoTop = -10.5
		self.orthoBottom = 10.5
		self.orthoNear = 4.0
		self.orthoFar = 150.0

		self.fbo = None
		self.lastPos = QtCore.QPoint()

		self.trolltechGreen = QtGui.QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
		self.trolltechPurple = QtGui.QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)

	def minimumSizeHint(self):
		return QtCore.QSize(50, 50)

	def sizeHint(self):
		return QtCore.QSize(400, 400)

	def setXRotation(self, angle):
		angle = self.normalizeAngle(angle)
		if angle != self.xRot:
			self.xRot = angle
			self.xRotationChanged.emit(angle)
			self.updateGL()

	def setYRotation(self, angle):
		angle = self.normalizeAngle(angle)
		if angle != self.yRot:
			self.yRot = angle
			self.yRotationChanged.emit(angle)
			self.updateGL()

	def createFrameBuffs(self, dimX, dimY):
		if self.fbo == None:
			self.fbo = GL.glGenFramebuffers(1)
			print 'Created frame buffer',self.fbo
			GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo)
			self.fbTex = GL.glGenTextures(1)
			print 'Created frame buffer texture', self.fbTex
			GL.glBindTexture( GL.GL_TEXTURE_2D, self.fbTex )
			GL.glTexImage2D( GL.GL_TEXTURE_2D, 0, GL.GL_DEPTH_COMPONENT, dimX, dimY, 0, GL.GL_DEPTH_COMPONENT, GL.GL_UNSIGNED_SHORT, None ) 
			GL.glFramebufferTexture2D( GL.GL_FRAMEBUFFER, GL.GL_DEPTH_ATTACHMENT, GL.GL_TEXTURE_2D, self.fbTex, 0 )
			if sys.platform in ('win32','darwin'):
				print 'Creating render buffer'
				self.rbo = GL.glGenRenderbuffers(1)
				GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, self.rbo)
				GL.glRenderbufferStorage(GL.GL_RENDERBUFFER, GL.GL_RGBA, dimX, dimY, )
				GL.glFramebufferRenderbuffer(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_RENDERBUFFER, self.rbo )
				#GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, 0 )
				#GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0 )
		else:
			print 'Frame buffer already created ',self.fbo
			GL.glBindRenderbuffer(GL.GL_RENDERBUFFER, self.rbo )
			GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.fbo )
			GL.glBindTexture( GL.GL_TEXTURE_2D, self.fbTex )

	def saveToTexture(self):
		self.createFrameBuffs(dimX, dimY)
		self.updateGL()
		img = GL.glGetTexImage(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, GL.GL_UNSIGNED_SHORT)
		print img

	def setFrameSlice(self, val):
		GL.glMatrixMode(GL.GL_PROJECTION)
		GL.glLoadIdentity()
		self.orthoNear = val
		# left , right , bottom , top , near , far 
		GL.glOrtho(self.orthoLeft, self.orthoRight, self.orthoBottom, self.orthoTop, self.orthoNear, self.orthoFar)
		GL.glMatrixMode(GL.GL_MODELVIEW)
		self.updateGL()

	def setZRotation(self, angle):
		angle = self.normalizeAngle(angle)
		if angle != self.zRot:
			self.zRot = angle
			self.zRotationChanged.emit(angle)
			self.updateGL()

	def initializeGL(self):
		self.qglClearColor(self.trolltechPurple.dark())
		GL.glShadeModel(GL.GL_FLAT)
		GL.glEnable(GL.GL_DEPTH_TEST)
		GL.glEnable(GL.GL_CULL_FACE)

		#self.genGrid(self.gridX, self.gridY, self.gridZ)

		mat_specular = [ 1.0, 1.0, 1.0, 1.0 ]
		mat_shininess = [ 50.0 ]
		light_position = [ 1.0, -1.0, -1.0, 0.0 ]

		GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, mat_specular)
		GL.glMaterialfv(GL.GL_FRONT, GL.GL_SHININESS, mat_shininess)
		GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, light_position)
		GL.glEnable(GL.GL_LIGHTING)
		GL.glEnable(GL.GL_LIGHT0)


	def genGrid(self, xSize, ySize, zSiz):
		x0 = -(xSize / 2)
		x1 = -x0
		y0 = -(ySize / 2)
		y1 = -y0
		z0 = -(zSize / 2)
		z1 = -z0
		self.gridList = GL.glGenLists(1)
		GL.glNewList(self.gridList, GL.GL_COMPILE)
		GL.glDisable(GL.GL_LIGHTING)
		GL.glBegin(GL.GL_LINES)
		GL.glColor(0.0, 0.0, 0.0)

		#draw X lines
		for z in range(z0, z1):
			for y in range(y0, y1):
				GL.glVertex3f(x0, y, z)
				GL.glVertex3f(x1, y, z)

		#draw Y lines
		for z in range(z0, z1):
			for x in range(x0, x1):
				GL.glVertex3f(x, y0, z)
				GL.glVertex3f(x, y1, z)

		#draw Z lines
		for y in range(y0, y1):
			for x in range(x0, x1):
				GL.glVertex3f(x, y, z0)
				GL.glVertex3f(x, y, z1)

		GL.glEnd()
		GL.glEnable(GL.GL_LIGHTING)
		GL.glEndList()

	def paintGL(self):
		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
		GL.glLoadIdentity()
		GL.glTranslated(0.0, 0.0, -20.0)
		GL.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
		GL.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
		GL.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
		#if not self.gridList == None:
		#	GL.glCallList(self.gridList)
		for m in self.models:
			m.draw()
		if not self.model == None:
			self.model.draw()

	def resizeGL(self, width, height):
		side = min(width, height)
		if side < 0:
			return

		GL.glViewport((width - side) / 2, (height - side) / 2, side, side)

		GL.glMatrixMode(GL.GL_PROJECTION)
		GL.glLoadIdentity()
		GL.glOrtho(self.orthoLeft, self.orthoRight, self.orthoBottom, self.orthoTop, self.orthoNear, self.orthoFar)
		#GL.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
		GL.glMatrixMode(GL.GL_MODELVIEW)

	def mousePressEvent(self, event):
		self.lastPos = event.pos()

	def mouseMoveEvent(self, event):
		dx = event.x() - self.lastPos.x()
		dy = event.y() - self.lastPos.y()

		if event.buttons() & QtCore.Qt.LeftButton:
			self.setXRotation(self.xRot + 8 * dy)
			self.setYRotation(self.yRot + 8 * dx)
		elif event.buttons() & QtCore.Qt.RightButton:
			self.setXRotation(self.xRot + 8 * dy)
			self.setZRotation(self.zRot + 8 * dx)

		self.lastPos = event.pos()

	def makeObjectFromVerts(self, vertList):
		genList = GL.glGenLists(1)
		GL.glNewList(genList, GL.GL_COMPILE)

		GL.glBegin(GL.GL_TRIANGLES)

		self.qglColor(self.trolltechGreen)

		for v in vertList:
			self.qglColor(self.trolltechGreen)
			GL.glVertex3d(v[0][0], v[0][1], v[0][2])
			GL.glVertex3d(v[1][0], v[1][1], v[1][2])
			GL.glVertex3d(v[2][0], v[2][1], v[2][2])

		GL.glEnd()
		GL.glEndList()

		return genList

	def normalizeAngle(self, angle):
		while angle < 0:
			angle += 360 * 16
		while angle > 360 * 16:
			angle -= 360 * 16
		return angle

