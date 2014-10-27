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
import random, time
 
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
		self.vl.addLayout(self.createDatasetInput())
		self.vl.addLayout(self.createGenProps())
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

	def createDatasetInput(self):
		DsetStartVal = '1000'
		hBox = QtGui.QHBoxLayout()
		self.DsetXIn = QtGui.QLineEdit()
		self.DsetYIn = QtGui.QLineEdit()
		self.DsetZIn = QtGui.QLineEdit()

		self.DsetXIn.setText(DsetStartVal)
		self.DsetYIn.setText(DsetStartVal)
		self.DsetZIn.setText('1')

		hBox.addWidget(QtGui.QLabel("X"))
		hBox.addWidget(self.DsetXIn)
		hBox.addWidget(QtGui.QLabel("Y"))
		hBox.addWidget(self.DsetYIn)
		#hBox.addWidget(QtGui.QLabel("Z"))
		#hBox.addWidget(self.DsetZIn)

		vBox = QtGui.QVBoxLayout()
		vBox.addWidget(QtGui.QLabel("Dataset Size"))
		vBox.addLayout(hBox)

		return vBox

	def createGenProps(self):
		DsetStartVal = '1000'
		self.BaseScaleStart = QtGui.QLineEdit()
		self.BaseScaleEnd = QtGui.QLineEdit()
		self.BaseRotateStart = QtGui.QLineEdit()
		self.BaseRotateEnd = QtGui.QLineEdit()
		self.ElementScaleStart = QtGui.QLineEdit()
		self.ElementScaleEnd = QtGui.QLineEdit()
		self.ElementsPerFaceIn = QtGui.QLineEdit()

		self.BaseScaleStart.setText('4.0')
		self.BaseScaleEnd.setText('7.0')
		self.BaseRotateStart.setText('0.0')
		self.BaseRotateEnd.setText('180.0')
		self.ElementScaleStart.setText('0.2')
		self.ElementScaleEnd.setText('0.2')
		self.ElementsPerFaceIn.setText('10')

		vBox = QtGui.QVBoxLayout()
		hBox0 = QtGui.QHBoxLayout()
		hBox0.addWidget(QtGui.QLabel("From:"))
		hBox0.addWidget(self.BaseScaleStart)
		hBox0.addWidget(QtGui.QLabel("To:"))
		hBox0.addWidget(self.BaseScaleEnd)
		vBox.addWidget(QtGui.QLabel("Base Material Scale:"))
		vBox.addLayout(hBox0)

		hBox1 = QtGui.QHBoxLayout()
		hBox1.addWidget(QtGui.QLabel("From:"))
		hBox1.addWidget(self.BaseRotateStart)
		hBox1.addWidget(QtGui.QLabel("To:"))
		hBox1.addWidget(self.BaseRotateEnd)
		vBox.addWidget(QtGui.QLabel("Base Material Rotate (degrees):"))
		vBox.addLayout(hBox1)

		hBox2 = QtGui.QHBoxLayout()
		hBox2.addWidget(QtGui.QLabel("Elements Per Suface face:"))
		hBox2.addWidget(self.ElementsPerFaceIn)
		vBox.addLayout(hBox2)

		hBox3 = QtGui.QHBoxLayout()
		hBox3.addWidget(QtGui.QLabel("From:"))
		hBox3.addWidget(self.ElementScaleStart)
		hBox3.addWidget(QtGui.QLabel("To:"))
		hBox3.addWidget(self.ElementScaleEnd)
		vBox.addWidget(QtGui.QLabel("Element Material Scale:"))
		vBox.addLayout(hBox3)

		return vBox

	def addElementActors(self):
		print 'TODO: add actors'

	def removeElementActors(self):
		print 'TODO: remove actors'

	def clearScene(self):
		if self.isSceneGenerated:
			print 'Override current scene?'
			for m in self.baseModels:
				self.ren.RemoveActor(m.actor)
				del m
			self.baseModels = []
			for e in self.elementModels:
				self.ren.RemoveActor(e.actor)
				del e
			self.elementModels = []


	def generateScan(self):
		gridX = int(self.GridXIn.text())
		gridY = int(self.GridYIn.text())
		gridZ = int(self.GridZIn.text())
		self.startBaseScale = float(self.BaseScaleStart.text())
		self.endBaseScale = float(self.BaseScaleEnd.text())
		self.startBaseRotate = float(self.BaseRotateStart.text())
		self.endBaseRotate = float(self.BaseRotateEnd.text())
		self.elementsPerFace = int(self.ElementsPerFaceIn.text())
		self.startElementScale = float(self.ElementScaleStart.text())
		self.endElementScale = float(self.ElementScaleEnd.text())
		self.clearScene()
		print 'generating scene with grid size',gridX, gridY, gridZ
		self.generateWithCubesAndSpheres(gridX, gridY, gridZ)
		self.ren.ResetCamera()
		self.iren.Render()
		self.isSceneGenerated = True
		print 'Finished generating scene'

	def genRandRange(self, start, stop):
		return start + ( random.random() * (stop - start) )

	def generateWithCubesAndSpheres(self, gridX, gridY, gridZ):
		random.seed(time.time())
		#sRadius = 0.5 * 0.2 //when scale is 0.2
		maxTrans = 0.0
		baseScales = []
		for z in range(gridZ):
			bScaleY = []
			for y in range(gridY):
				bScaleX = []
				for x in range(gridX):
					val = self.genRandRange(self.startBaseScale, self.endBaseScale)
					maxTrans = max(maxTrans, val)
					bScaleX += [val]
				bScaleY += [bScaleX]
			baseScales += [bScaleY]
		#rScale = self.genRandRange(self.startBaseScale, self.endBaseScale)
		#sTrans = [ [-((0.5 * rScale) + sRadius), 0.0, 0.0], [(0.5 * rScale) + sRadius, 0.0, 0.0], [0.0, -((0.5 * rScale)+sRadius), 0.0], [0.0, (0.5 * rScale)+sRadius, 0.0], [0.0, 0.0, -((0.5 * rScale)+sRadius)], [0.0, 0.0, (0.5 * rScale+sRadius)] ]
		#trans = rScale * 2.0
		trans = maxTrans * 2.0
		xTrans = 0.0
		yTrans = 0.0
		zTrans = 0.0
		allBaseItems = gridZ * gridY * gridX
		curBaseCnt = 0
		numFacesOnBase = 6
		for z in range(gridZ):
			yTrans = 0.0
			for y in range(gridY):
				xTrans = 0.0
				for x in range(gridX):
					#rev1 sScale = self.genRandRange( self.startElementScale, self.endElementScale ) 
					#rev1 sRadius = 0.5 * sScale
					#Rev0 rScale = self.genRandRange(self.startBaseScale, self.endBaseScale)
					#rev0 sTrans = [ [-0.5 - rScale, 0.0, 0.0], [0.5 + rScale, 0.0, 0.0], [0.0, -0.5 - rScale, 0.0], [0.0, 0.5 + rScale, 0.0], [0.0, 0.0, -0.5 - rScale], [0.0, 0.0, 0.5 + rScale] ]
					rScale = baseScales[z][y][x]
					#rev1 sTrans = [ [-((0.5 * rScale) + sRadius), 0.0, 0.0], [(0.5 * rScale) + sRadius, 0.0, 0.0], [0.0, -((0.5 * rScale)+sRadius), 0.0], [0.0, (0.5 * rScale)+sRadius, 0.0], [0.0, 0.0, -((0.5 * rScale)+sRadius)], [0.0, 0.0, (0.5 * rScale+sRadius)] ]
					m = CubeModel()
					m.translate(xTrans,  yTrans, zTrans)
					#xRot = random.random() * 180.0 
					#yRot = random.random() * 180.0 
					#zRot = random.random() * 180.0 
					xRot = self.genRandRange(self.startBaseRotate, self.endBaseRotate )
					yRot = self.genRandRange(self.startBaseRotate, self.endBaseRotate )
					zRot = self.genRandRange(self.startBaseRotate, self.endBaseRotate )
					m.rotate(xRot, yRot, zRot)
					#print 'rScale', rScale
					m.scale(rScale, rScale, rScale)
					self.ren.AddActor(m.actor)
					self.baseModels += [m]
					for i in range(numFacesOnBase):
						for j in range(self.elementsPerFace):
							sScale = self.genRandRange( self.startElementScale, self.endElementScale ) 
							sRadius = 0.5 * sScale
							sTrans = [ [-((0.5 * rScale) + sRadius), 0.0, 0.0], [(0.5 * rScale) + sRadius, 0.0, 0.0], [0.0, -((0.5 * rScale)+sRadius), 0.0], [0.0, (0.5 * rScale)+sRadius, 0.0], [0.0, 0.0, -((0.5 * rScale)+sRadius)], [0.0, 0.0, (0.5 * rScale+sRadius)] ]
							s = SphereModel()
							#parent model transform
							s.translate(xTrans, yTrans, zTrans)
							s.rotate(xRot, yRot, zRot)
							#random parent suface local transform
							sXTran = sTrans[i][0]
							sYTran = sTrans[i][1]
							sZTran = sTrans[i][2]
							
							#randomize where on the face we put it
							if random.random() > 0.5:
								op = 1
							else:
								op = -1
							if not sTrans[i][0] == 0.0:
								sYTran += random.random() * sTrans[1][0] * op
								sZTran += random.random() * sTrans[1][0] * op
							elif not sTrans[i][1] == 0.0:
								sXTran += random.random() * sTrans[1][0] * op
								sZTran += random.random() * sTrans[1][0] * op
							elif not sTrans[i][2] == 0.0:
								sYTran += random.random() * sTrans[1][0] * op
								sXTran += random.random() * sTrans[1][0] * op
							
							#local transform
							#s.translate(sTrans[i][0], sTrans[i][1], sTrans[i][2] ) 
							s.translate(sXTran, sYTran, sZTran ) 
							s.scale(sScale, sScale, sScale)
							s.setColor(0.8, 0.2, 0.2)
							self.ren.AddActor(s.actor)
							self.elementModels += [s]
						#for j
					#for i
					xTrans += trans
					curBaseCnt += 1
					print 'created item',curBaseCnt, ' of',allBaseItems
				#end for X
				yTrans += trans
			#end for Y
			zTrans += trans
		#end for Z
		

	def runScan(self):
		dimX = int(self.DsetXIn.text())
		dimY = int(self.DsetYIn.text())
		dimZ = int(self.DsetZIn.text())
		dimZ = 1
		#scene
		if self.isSceneGenerated:
			self.scan.exportSceneToHDF(self.baseModels, self.elementModels, dimX, dimY)
		else:
			print 'Please generate a scene first'


