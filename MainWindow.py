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
from Scanner import Scanner
from Volumizer import Volumizer
from H5Exporter import H5Exporter
from Generator import GenerateWithCubesAndSphereThread
import random, time
 
class MainWindow(QtGui.QMainWindow):
 
	def __init__(self, parent = None):
		QtGui.QMainWindow.__init__(self, parent)
 
		self.frame = QtGui.QFrame()

		self.scanMutex = QtCore.QMutex()

		self.volumizer = Volumizer()
		self.volumizer.notifyFinish.connect(self.onFinishVolume)

		self.isSceneGenerated = False

		self.vl = QtGui.QHBoxLayout()
		self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
		self.vl.addWidget(self.vtkWidget)

		tab_widget = QtGui.QTabWidget()
		tab_widget.addTab(self.createGenPropsWidget(), "Generate")
		tab_widget.addTab(self.createScanPropsWidget(), "Scan")
		tab_widget.addTab(self.createVolumePropsWidget(), "Volume")
		self.vl.addWidget(tab_widget)

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
		self.NumElementsIn = QtGui.QLineEdit()

		self.BaseScaleStart.setText('4.0')
		self.BaseScaleEnd.setText('7.0')
		self.BaseRotateStart.setText('0.0')
		self.BaseRotateEnd.setText('180.0')
		self.ElementScaleStart.setText('0.2')
		self.ElementScaleEnd.setText('0.2')
		self.ElementsPerFaceIn.setText('1')
		self.NumElementsIn.setText('1')

		'''
		self.BaseScaleStart.setFixedWidth(32)
		self.BaseScaleEnd.setFixedWidth(32)
		self.BaseRotateStart.setFixedWidth(32)
		self.BaseRotateEnd.setFixedWidth(32)
		self.ElementScaleStart.setFixedWidth(32)
		self.ElementScaleEnd.setFixedWidth(32)
		self.ElementsPerFaceIn.setFixedWidth(32)
		self.NumElementsIn.setFixedWidth(32)
		'''

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
		hBox2.addWidget(QtGui.QLabel("Num of different elements:"))
		hBox2.addWidget(self.NumElementsIn)
		hBox2.addWidget(QtGui.QLabel("Num Per Suface:"))
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

	def createVolDatasetWidget(self):
		DsetStartVal = '1000'
		hBox = QtGui.QHBoxLayout()
		self.volDsetXIn = QtGui.QLineEdit()
		self.volDsetYIn = QtGui.QLineEdit()
		self.volDsetZIn = QtGui.QLineEdit()

		self.volDsetXIn.setText(DsetStartVal)
		self.volDsetYIn.setText(DsetStartVal)
		self.volDsetZIn.setText(DsetStartVal)

		hBox.addWidget(QtGui.QLabel("Width"))
		hBox.addWidget(self.volDsetXIn)
		hBox.addWidget(QtGui.QLabel("Height"))
		hBox.addWidget(self.volDsetYIn)
		hBox.addWidget(QtGui.QLabel("Depth"))
		hBox.addWidget(self.volDsetZIn)

		datasetGroup = QtGui.QGroupBox("Volume Size")
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

	def createVolumePropsWidget(self):
		self.btnStartVolume = QtGui.QPushButton('Export Volume')
		self.btnStartVolume.clicked.connect(self.runVolumizer)

		self.btnStopVolume = QtGui.QPushButton('Stop')
		#self.btnStopVolume.clicked.connect(self.stopScan)

		hBox3 = QtGui.QHBoxLayout()
		self.volFileNameIn = QtGui.QLineEdit()
		self.volFileNameIn.setText('Volume.h5')
		hBox3.addWidget(QtGui.QLabel('FileName:'))
		hBox3.addWidget(self.volFileNameIn)

		#self.volProgressBar = QtGui.QProgressBar(self)
		#self.volProgressBar.setRange(0,100)

		hBox2 = QtGui.QHBoxLayout()
		hBox2.addWidget(self.btnStartVolume)
		#hBox2.addWidget(self.btnStopVolume)

		vBox = QtGui.QVBoxLayout()
		vBox.addLayout(hBox3)
		vBox.addWidget(self.createVolDatasetWidget())
		#vBox.addWidget(self.volProgressBar)
		vBox.addLayout(hBox2)

		self.volGroup = QtGui.QGroupBox("Volume Properties")
		self.volGroup.setLayout(vBox)

		self.volGroup.setEnabled(False)

		return self.volGroup

	def addElementActors(self):
		print 'TODO: add actors'

	def removeElementActors(self):
		print 'TODO: remove actors'

	def clearScene(self):
		if self.isSceneGenerated:
			print 'Override current scene?'
			for mList in self.allModelList:
				for m in mList:
					self.ren.RemoveActor(m.actor)
					print 'del m'
					del m
			self.allModelList = []
			self.iren.Render()

	def onScanProgress(self, i):
		self.scanMutex.lock()
		v = self.scanProgressBar.value()
		self.scanProgressBar.setValue(v+1)
		self.scanMutex.unlock()

	def onScanFinish(self):
		#if all finished then save file
		self.scanMutex.lock()
		self.finishedScans += 1
		if self.finishedScans >= len(self.allModelList):
			self.saver.H5_End(self.h5st)
			self.genGroup.setEnabled(True)
			self.volGroup.setEnabled(True)
			self.btnStartScan.setEnabled(True)
			print 'Scan finished in ',int(time.time() - self.startScanTime),' seconds'
		self.scanMutex.unlock()

	def onGenProgress(self, i):
		self.genProgressBar.setValue(i)

	def onGenFinish(self, allModelList, bounds):
		for mList in allModelList:
			for m in mList:
				self.ren.AddActor(m.actor)
		self.sceneBounds = bounds
		self.allModelList = allModelList
		self.ren.ResetCamera()
		self.iren.Render()
		self.isSceneGenerated = True
		self.btnGenScan.setEnabled(True)
		self.scanGroup.setEnabled(True)
		self.volGroup.setEnabled(True)
		print 'Finished generating scene'

	def generateScan(self):
		self.btnGenScan.setEnabled(False)
		self.scanGroup.setEnabled(False)
		self.volGroup.setEnabled(False)
		self.genTask.gridX = int(self.GridXIn.text())
		self.genTask.gridY = int(self.GridYIn.text())
		self.genTask.gridZ = int(self.GridZIn.text())
		self.genTask.numElements = int(self.NumElementsIn.text())
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
		for s in self.scanners:
			s.Stop = True

	def onFinishVolume(self):
		self.btnStartVolume.setEnabled(True)
		self.genGroup.setEnabled(True)
		self.scanGroup.setEnabled(True)

	def runVolumizer(self):
		self.genGroup.setEnabled(False)
		self.scanGroup.setEnabled(False)
		self.btnStartVolume.setEnabled(False)
		self.volumizer.bounds = self.sceneBounds
		self.volumizer.dimX = int(self.volDsetXIn.text())
		self.volumizer.dimY = int(self.volDsetYIn.text())
		self.volumizer.dimZ = int(self.volDsetZIn.text())
		self.volumizer.filename = str(self.volFileNameIn.text())
		self.volumizer.allModelList = self.allModelList
		self.volumizer.start()

	def runScan(self):
		self.startScanTime = time.time()
		dimX = int(self.DsetXIn.text())
		dimY = int(self.DsetYIn.text())
		numImages = int(self.NumImagesIn.text())
		startRot = float(self.StartRotIn.text())
		stopRot = float(self.StopRotIn.text())
		#scene
		if self.isSceneGenerated:
			self.genGroup.setEnabled(False)
			self.volGroup.setEnabled(False)
			self.btnStartScan.setEnabled(False)

			scanCount = len(self.allModelList)
			#create hdf5 file
			filename = str(self.fileNameIn.text())
			datasetNames = ['exchange/data']
			for i in range(scanCount - 1): 
				datasetNames += ['exchange/element'+str(i)]
			self.saver = H5Exporter()
			self.h5st = self.saver.H5_Start(filename, datasetNames, dimX, dimY, numImages)

			self.scanProgressBar.setRange(0, numImages * scanCount )
			self.scanProgressBar.setValue(0)

			self.finishedScans = 0

			self.scanners = []
			for i in range(scanCount):
				self.scanners += [Scanner()]
				self.scanners[i].saver = self.saver
				self.scanners[i].h5st = self.h5st
				self.scanners[i].datasetName = datasetNames[i]
				self.scanners[i].baseModels = self.allModelList[i]
				self.scanners[i].bounds = self.sceneBounds
				self.scanners[i].dimX = dimX
				self.scanners[i].dimY = dimY
				self.scanners[i].startRot = startRot
				self.scanners[i].stopRot = stopRot
				self.scanners[i].numImages = numImages
				self.scanners[i].notifyProgress.connect(self.onScanProgress)
				self.scanners[i].notifyFinish.connect(self.onScanFinish)
				#We only want the first scanner to save theta
				self.scanners[0].bSaveTheta = True
				self.scanners[i].start()
		else:
			print 'Please generate a scene first'


