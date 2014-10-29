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
from Volumizer import Volumizer

import random, time
 
class MainWindow(QtGui.QMainWindow):
 
	def __init__(self, parent = None):
		QtGui.QMainWindow.__init__(self, parent)
 
		self.frame = QtGui.QFrame()

		self.scan = Scanner()
		self.scan.notifyProgress.connect(self.onScanProgress)
		self.scan.notifyFinish.connect(self.onScanFinish)

		self.volumizer = Volumizer()

		self.isSceneGenerated = False
		self.baseModels = []
		self.elementModels = []

		self.vl = QtGui.QHBoxLayout()
		self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
		self.vl.addWidget(self.vtkWidget)
		
		vBox = QtGui.QVBoxLayout()
		vBox.addWidget(self.createGenPropsWidget())
		vBox.addWidget(self.createScanPropsWidget())
		self.vl.addLayout(vBox)

		self.genTask = GenerateWithCubesAndSphereThread()
		self.genTask.notifyProgress.connect(self.onGenProgress)
		self.genTask.notifyFinish.connect(self.onGenFinish)

		self.ren = vtk.vtkRenderer()
		self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
		self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

		self.ren.ResetCamera()
 
		self.frame.setLayout(self.vl)
		self.setCentralWidget(self.frame)
 
		self.show()
		self.iren.Initialize()

	def createGridInputWidget(self):
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

		gridGroup = QtGui.QGroupBox('Grid Size')
		gridGroup.setLayout(hBox)

		return gridGroup

	def createElementTableWidget(self):
		print 'TODO: create '

	def createGenPropsWidget(self):
		DsetStartVal = '1000'
		vBox0 = QtGui.QVBoxLayout()
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
		self.ElementsPerFaceIn.setText('1')

		baseGroup = QtGui.QGroupBox("Base Material")
		vBox1 = QtGui.QVBoxLayout()
		hBox0 = QtGui.QHBoxLayout()
		hBox0.addWidget(QtGui.QLabel("From:"))
		hBox0.addWidget(self.BaseScaleStart)
		hBox0.addWidget(QtGui.QLabel("To:"))
		hBox0.addWidget(self.BaseScaleEnd)
		vBox1.addWidget(QtGui.QLabel("Scale:"))
		vBox1.addLayout(hBox0)

		hBox1 = QtGui.QHBoxLayout()
		hBox1.addWidget(QtGui.QLabel("From:"))
		hBox1.addWidget(self.BaseRotateStart)
		hBox1.addWidget(QtGui.QLabel("To:"))
		hBox1.addWidget(self.BaseRotateEnd)
		vBox1.addWidget(QtGui.QLabel("Rotate (degrees):"))
		vBox1.addLayout(hBox1)

		baseGroup.setLayout(vBox1)

		elementGroup = QtGui.QGroupBox("Element Material")
		vBox2 = QtGui.QVBoxLayout()
		hBox2 = QtGui.QHBoxLayout()
		hBox2.addWidget(QtGui.QLabel("# Per Suface face:"))
		hBox2.addWidget(self.ElementsPerFaceIn)
		vBox2.addLayout(hBox2)

		hBox3 = QtGui.QHBoxLayout()
		hBox3.addWidget(QtGui.QLabel("From:"))
		hBox3.addWidget(self.ElementScaleStart)
		hBox3.addWidget(QtGui.QLabel("To:"))
		hBox3.addWidget(self.ElementScaleEnd)
		vBox2.addWidget(QtGui.QLabel("Scale:"))
		vBox2.addLayout(hBox3)

		elementGroup.setLayout(vBox2)

		self.btnGenScan = QtGui.QPushButton('Generate')
		self.btnGenScan.clicked.connect(self.generateScan)

		self.genProgressBar = QtGui.QProgressBar(self)
		self.genProgressBar.setRange(0,100)

		vBox0.addWidget(self.createGridInputWidget())
		vBox0.addWidget(baseGroup)
		vBox0.addWidget(elementGroup)
		vBox0.addWidget(self.genProgressBar)
		vBox0.addWidget(self.btnGenScan)

		self.genGroup = QtGui.QGroupBox("Generate Properties")
		self.genGroup.setLayout(vBox0)

		return self.genGroup

	def createScanTypeWidget(self):
		print 'TODO: create '

	def createDatasetWidget(self):
		DsetStartVal = '1000'
		hBox = QtGui.QHBoxLayout()
		self.DsetXIn = QtGui.QLineEdit()
		self.DsetYIn = QtGui.QLineEdit()

		self.DsetXIn.setText(DsetStartVal)
		self.DsetYIn.setText(DsetStartVal)

		hBox.addWidget(QtGui.QLabel("Width"))
		hBox.addWidget(self.DsetXIn)
		hBox.addWidget(QtGui.QLabel("Height"))
		hBox.addWidget(self.DsetYIn)

		datasetGroup = QtGui.QGroupBox("Dataset Size")
		datasetGroup.setLayout(hBox)

		return datasetGroup

	def createTomoScanWidget(self):
		self.NumImagesIn = QtGui.QLineEdit()
		self.StartRotIn = QtGui.QLineEdit()
		self.StopRotIn = QtGui.QLineEdit()
		hBox1 = QtGui.QHBoxLayout()
		hBox2 = QtGui.QHBoxLayout()
		vBox = QtGui.QVBoxLayout()

		self.NumImagesIn.setText('100')
		self.StartRotIn.setText('0.0')
		self.StopRotIn.setText('180.0')

		hBox1.addWidget(QtGui.QLabel('Number Of Images:'))
		hBox1.addWidget(self.NumImagesIn)
		
		hBox2.addWidget(QtGui.QLabel('Start Rotation (degreees):'))
		hBox2.addWidget(self.StartRotIn)
		hBox2.addWidget(QtGui.QLabel('Stop Rotation:'))
		hBox2.addWidget(self.StopRotIn)

		vBox.addLayout(hBox1)
		vBox.addLayout(hBox2)

		tomoGroup = QtGui.QGroupBox("Tomo Scan")
		tomoGroup.setLayout(vBox)

		return tomoGroup


	def createScanPropsWidget(self):
		self.btnStartScan = QtGui.QPushButton('Start Scan')
		self.btnStartScan.clicked.connect(self.runScan)

		self.btnStopScan = QtGui.QPushButton('Stop Scan')
		self.btnStopScan.clicked.connect(self.stopScan)

		hBox3 = QtGui.QHBoxLayout()
		self.fileNameIn = QtGui.QLineEdit()
		self.fileNameIn.setText('TestScan.h5')
		hBox3.addWidget(QtGui.QLabel('FileName:'))
		hBox3.addWidget(self.fileNameIn)

		self.scanProgressBar = QtGui.QProgressBar(self)
		self.scanProgressBar.setRange(0,100)

		hBox2 = QtGui.QHBoxLayout()
		hBox2.addWidget(self.btnStartScan)
		hBox2.addWidget(self.btnStopScan)

		vBox = QtGui.QVBoxLayout()
		vBox.addLayout(hBox3)
		vBox.addWidget(self.createDatasetWidget())
		vBox.addWidget(self.createTomoScanWidget())
		vBox.addWidget(self.scanProgressBar)
		vBox.addLayout(hBox2)

		self.scanGroup = QtGui.QGroupBox("Scan Properties")
		self.scanGroup.setLayout(vBox)

		self.scanGroup.setEnabled(False)

		return self.scanGroup

	def addElementActors(self):
		print 'TODO: add actors'

	def removeElementActors(self):
		print 'TODO: remove actors'

	def clearScene(self):
		if self.isSceneGenerated:
			print 'Override current scene?'
			for m in self.baseModels:
				self.ren.RemoveActor(m.actor)
				print 'del m'
				del m
			self.baseModels = []
			for e in self.elementModels:
				self.ren.RemoveActor(e.actor)
				del e
			self.elementModels = []
			self.iren.Render()

	def onScanProgress(self, i):
		self.scanProgressBar.setValue(i)

	def onScanFinish(self):
		self.genGroup.setEnabled(True)
		self.btnStartScan.setEnabled(True)
		print 'Scan Finished'

	def onGenProgress(self, i):
		self.genProgressBar.setValue(i)

	def onGenFinish(self, baseList, elementList):
		for m in baseList:
			self.ren.AddActor(m.actor)
			self.baseModels += [m]
		for e in elementList:
			self.ren.AddActor(e.actor)
			self.elementModels += [e]
		self.ren.ResetCamera()
		self.iren.Render()
		self.isSceneGenerated = True
		self.btnGenScan.setEnabled(True)
		self.scanGroup.setEnabled(True)
		print 'Finished generating scene'

	def generateScan(self):
		self.btnGenScan.setEnabled(False)
		self.scanGroup.setEnabled(False)
		self.genTask.gridX = int(self.GridXIn.text())
		self.genTask.gridY = int(self.GridYIn.text())
		self.genTask.gridZ = int(self.GridZIn.text())
		self.genTask.startBaseScale = float(self.BaseScaleStart.text())
		self.genTask.endBaseScale = float(self.BaseScaleEnd.text())
		self.genTask.startBaseRotate = float(self.BaseRotateStart.text())
		self.genTask.endBaseRotate = float(self.BaseRotateEnd.text())
		self.genTask.elementsPerFace = int(self.ElementsPerFaceIn.text())
		self.genTask.startElementScale = float(self.ElementScaleStart.text())
		self.genTask.endElementScale = float(self.ElementScaleEnd.text())
		self.clearScene()
		#print 'generating scene with grid size',self.gridX, self.gridY, self.gridZ
		self.genProgressBar.setRange(0, self.genTask.gridX * self.genTask.gridY * self.genTask.gridZ)
		self.genProgressBar.setValue(0)
		#self.generateWithCubesAndSpheres()
		self.genTask.start()

	def stopScan(self):
		print 'Trying to stop the scan'
		self.scan.Stop = True

	def runVolumizer(self):
		self.volumizer.export('myVol', self.baseModels, self.elementModels)

	def runScan(self):
		dimX = int(self.DsetXIn.text())
		dimY = int(self.DsetYIn.text())
		numImages = int(self.NumImagesIn.text())
		startRot = float(self.StartRotIn.text())
		stopRot = float(self.StopRotIn.text())
		#scene
		if self.isSceneGenerated:
			self.genGroup.setEnabled(False)
			self.btnStartScan.setEnabled(False)
			#self.scan.exportSceneToHDF('test.h5', self.baseModels, self.elementModels, dimX, dimY)
			#self.scan.exportTomoScanToHDF('testTomo.h5', self.baseModels, self.elementModels, dimX, dimY, 0.0, 180.0, 180)
			#self.scan.exportTomoScanToHDF('testTomo.h5', self.baseModels, self.elementModels, dimX, dimY, 45.0, 46.0, 1)
			self.scan.filename = str(self.fileNameIn.text())
			self.scan.baseModels = self.baseModels
			self.scan.elementModels = self.elementModels
			self.scan.dimX = dimX
			self.scan.dimY = dimY
			self.scan.startRot = startRot
			self.scan.stopRot = stopRot
			self.scan.numImages = numImages
			self.scanProgressBar.setRange(0, numImages)
			self.scanProgressBar.setValue(0)
			self.scan.start()
		else:
			print 'Please generate a scene first'

class GenerateWithCubesAndSphereThread(QtCore.QThread):
	notifyProgress = QtCore.pyqtSignal(int)
	notifyFinish = QtCore.pyqtSignal(list, list)

	def __init__(self):
		QtCore.QObject.__init__(self)
		self.gridX = 0
		self.gridY = 0
		self.gridZ = 0
		self.startBaseScale = 1.0
		self.endBaseScale = 2.0
		self.startElementScale = 0.2
		self.endElementScale = 0.5
		self.startBaseRotate = 0.0
		self.endBaseRotate = 180.0
		self.baseModels = []
		self.elementModels = []
		self.elementsPerFace = 1
		self.Stop = False

	def genRandRange(self, start, stop):
		return start + ( random.random() * (stop - start) )

	def run(self):
		self.Stop = False
		random.seed(time.time())
		maxTrans = 0.0
		baseScales = []
		self.baseModels = []
		self.elementModels = []
		#generate scales for base elements
		for z in range(self.gridZ):
			bScaleY = []
			for y in range(self.gridY):
				bScaleX = []
				for x in range(self.gridX):
					val = self.genRandRange(self.startBaseScale, self.endBaseScale)
					maxTrans = max(maxTrans, val)
					bScaleX += [val]
				bScaleY += [bScaleX]
			baseScales += [bScaleY]
		trans = maxTrans * 2.0
		xTrans = -(self.gridX * 0.5 * trans * 0.5)
		yTrans = -(self.gridY * 0.5 * trans * 0.5)
		zTrans = -(self.gridZ * 0.5 * trans * 0.5)
		allBaseItems = self.gridZ * self.gridY * self.gridX
		print 'transes', xTrans, yTrans, zTrans, trans
		curBaseCnt = 0
		numFacesOnBase = 6
		for z in range(self.gridZ):
			yTrans = -(self.gridY * 0.5 * trans * 0.5)
			for y in range(self.gridY):
				xTrans = -(self.gridX * 0.5 * trans * 0.5)
				for x in range(self.gridX):
					if self.Stop:
						print 'Generator Stopped!'
						self.notifyFinish.emit([], [])
					rScale = baseScales[z][y][x]
					m = CubeModel()
					m.translate(xTrans,  yTrans, zTrans)
					xRot = self.genRandRange(self.startBaseRotate, self.endBaseRotate )
					yRot = self.genRandRange(self.startBaseRotate, self.endBaseRotate )
					zRot = self.genRandRange(self.startBaseRotate, self.endBaseRotate )
					m.rotate(xRot, yRot, zRot)
					#print 'rScale', rScale
					m.scale(rScale, rScale, rScale)
					#self.ren.AddActor(m.actor)
					self.baseModels += [m]
					for i in range(numFacesOnBase):
						for j in range(self.elementsPerFace):
							sScale = self.genRandRange( self.startElementScale, self.endElementScale ) 
							sRadius = 0.5 * sScale
							sTrans = [ [-((0.5 * rScale) + sRadius), 0.0, 0.0], [(0.5 * rScale) + sRadius, 0.0, 0.0], [0.0, -((0.5 * rScale)+sRadius), 0.0], [0.0, (0.5 * rScale)+sRadius, 0.0], [0.0, 0.0, -((0.5 * rScale)+sRadius)], [0.0, 0.0, (0.5 * rScale+sRadius)] ]
							s = SphereModel()
							s.density = 2.0
							#parent model transform
							s.translate(xTrans, yTrans, zTrans)
							s.rotate(xRot, yRot, zRot)
							#random parent suface local transform
							sXTran = sTrans[i][0]
							sYTran = sTrans[i][1]
							sZTran = sTrans[i][2]
							
							#randomize where on the face we put it
							if random.random() > 0.5:
								op1 = 1
							else:
								op1 = -1
							if random.random() > 0.5:
								op2 = 1
							else:
								op2 = -1
							if not sTrans[i][0] == 0.0:
								sYTran += random.random() * sTrans[1][0] * op1
								sZTran += random.random() * sTrans[1][0] * op2
							elif not sTrans[i][1] == 0.0:
								sXTran += random.random() * sTrans[1][0] * op1
								sZTran += random.random() * sTrans[1][0] * op2
							elif not sTrans[i][2] == 0.0:
								sYTran += random.random() * sTrans[1][0] * op1
								sXTran += random.random() * sTrans[1][0] * op2
							
							#local transform
							s.translate(sXTran, sYTran, sZTran ) 
							s.scale(sScale, sScale, sScale)
							s.setColor(0.8, 0.2, 0.2)
							#self.ren.AddActor(s.actor)
							self.elementModels += [s]
						#for j
					#for i
					xTrans += trans
					curBaseCnt += 1
					print 'created item',curBaseCnt, ' of',allBaseItems
					self.notifyProgress.emit(curBaseCnt)
				#end for X
				yTrans += trans
			#end for Y
			zTrans += trans
		#end for Z
		self.notifyFinish.emit(self.baseModels, self.elementModels)
		


