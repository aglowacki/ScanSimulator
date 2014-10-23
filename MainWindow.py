'''
Arthur Glowacki
APS ANL
10/17/2014
'''
 
import sys
import vtk
import math
from PyQt4 import QtCore, QtGui
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PrimitiveModels import CubeModel, SphereModel
from Scanner import Scanner
 
class MainWindow(QtGui.QMainWindow):
 
	def __init__(self, parent = None):
		QtGui.QMainWindow.__init__(self, parent)
 
		self.frame = QtGui.QFrame()

		self.scan = Scanner()
		self.isSceneGenerated = False
		self.baseModels = []
		self.elementModels = []

		self.btnGenScan = QtGui.QPushButton('Generate')
		self.btnGenScan.clicked.connect(self.generateScan)
		self.btnScan = QtGui.QPushButton('Start Scan')
		self.btnScan.clicked.connect(self.runScan)
 
		self.vl = QtGui.QVBoxLayout()
		self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
		self.vl.addWidget(self.vtkWidget)
		hbox2 = QtGui.QHBoxLayout()
		hbox3 = QtGui.QHBoxLayout()
		hbox3.addWidget(self.btnGenScan)
		hbox3.addWidget(self.btnScan)
		self.vl.addLayout(self.createGridInput())
		self.vl.addLayout(hbox2)
		self.vl.addLayout(hbox3)
 
		self.ren = vtk.vtkRenderer()
		self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
		self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
 

		self.ren.ResetCamera()
 
		self.frame.setLayout(self.vl)
		self.setCentralWidget(self.frame)
 
		self.show()
		self.iren.Initialize()

	def createGridInput(self):
		GridStartVal = '2'
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

	def generateScan(self):
		gridX = int(self.GridXIn.text())
		gridY = int(self.GridYIn.text())
		gridZ = int(self.GridZIn.text())
		if self.isSceneGenerated:
			print 'Override current scene?'
		print 'generating scene with grid size',gridX, gridY, gridZ
		'''
		c0 = CubeModel()
		self.ren.AddActor(c0.actor)
		self.baseModels += [c0]
 
		c1 = CubeModel()
		c1.source.SetCenter(0.5, 0.5, 1.5)
		c1.source.Update()
		c1.Update()
		self.ren.AddActor(c1.actor)
		self.baseModels += [c1]
 		'''
		sphereModel = SphereModel()
		#sphereModel.source.SetCenter(0., 0., 0.)
		#sphereModel.source.Update()
		#sphereModel.Update()
		self.ren.AddActor(sphereModel.actor)
		self.baseModels += [sphereModel]

		sphereModel1 = SphereModel()
		sphereModel1.source.SetCenter(0.5, 0.5, 0.)
		sphereModel1.source.Update()
		sphereModel1.Update()
		self.ren.AddActor(sphereModel1.actor)
		self.baseModels += [sphereModel1]

		#self.baseModels += [cubeModel]
		#self.elementModels += [sphereModel]
		'''
		trans = 2.0
		xTrans = 0.0
		yTrans = 0.0
		zTrans = 0.0
		for z in range(gridZ):
			yTrans = 0.0
			for y in range(gridY):
				xTrans = 0.0
				for x in range(gridX):
					m = self.glWidget.baseModel.getCopy()
					m.translate = [ xTrans,  yTrans, zTrans ]
					m.createList()
					#self.glWidget.scene.addBaseModel(m)
					xTrans += trans
				yTrans += trans
			zTrans += trans
		'''
		self.ren.ResetCamera()
		self.isSceneGenerated = True

	def runScan(self):
		dimX = 100
		dimY = 100
		dimZ = 1
		#scene
		if self.isSceneGenerated:
			self.scan.exportSceneToHDF(self.baseModels, self.elementModels, dimX, dimY, False)
		else:
			print 'Please generate a scene first'

