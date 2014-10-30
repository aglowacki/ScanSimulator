'''
Arthur Glowacki
APS ANL
10/30/2014
'''
from PyQt4 import QtCore
import random, time, math
from PrimitiveModels import CubeModel, SphereModel

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
		self.allModelList = []
		self.elementsPerFace = 1
		self.Stop = False
		self.numElements = 1

	def genRandRange(self, start, stop):
		return start + ( random.random() * (stop - start) )

	def genColor(self):
		r = random.random()
		g = random.random()
		b = random.random()
		if r + g + b < 1.0:
			r+= 0.2
			g+= 0.2
			b+= 0.2
		return (r,g,b)

	def run(self):
		bounds = [0.,0.,0.,0.,0.,0.]
		self.Stop = False
		random.seed(time.time())
		maxTrans = 0.0
		baseScales = []
		self.allModelList = [list()]
		colorList = [(1., 1., 1.), (1., 0.2, 0.2), (0.2, 0.2, 1.), (0.2, 1., 0.2), (1., 1., 0.2), (0.5, 0.0, 1.0), (1.0, 0.2, 1.0) ]
		addColorCnt = self.numElements - (len(colorList) - 1)
		for i in range(addColorCnt):
			colorList += [self.genColor()]
		if self.elementsPerFace == 0 or self.numElements == 0:
			self.elementsPerFace = 0
			self.numElements == 0

		for i in range(self.numElements):
			self.allModelList.append(list())
		#print 'colorlist ',colorList
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
					bnds = m.transformFilter.GetOutput().GetBounds()
					bounds[0] = min(bounds[0], bnds[0])
					bounds[1] = max(bounds[1], bnds[1])
					bounds[2] = min(bounds[2], bnds[2])
					bounds[3] = max(bounds[3], bnds[3])
					bounds[4] = min(bounds[4], bnds[4])
					bounds[5] = max(bounds[5], bnds[5])
					self.allModelList[0] += [m]
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
							
							element = random.randrange(1, self.numElements +1)
							s.density = element + 1
							#local transform
							s.translate(sXTran, sYTran, sZTran ) 
							s.scale(sScale, sScale, sScale)
							s.setColorT(colorList[element])
							#self.ren.AddActor(s.actor)
							#print 'gen element',element
							bnds = s.transformFilter.GetOutput().GetBounds()
							bounds[0] = min(bounds[0], bnds[0])
							bounds[1] = max(bounds[1], bnds[1])
							bounds[2] = min(bounds[2], bnds[2])
							bounds[3] = max(bounds[3], bnds[3])
							bounds[4] = min(bounds[4], bnds[4])
							bounds[5] = max(bounds[5], bnds[5])
							self.allModelList[element] += [s]
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
		xd = bounds[1] - bounds[0]
		zd = bounds[5] - bounds[4]
		offset = math.sqrt( (xd * xd) + (zd * zd) )
		#print 'xd',xd,'zd',zd,'offset',offset
		offset = (offset - xd) * 0.5
		bounds[0] -= offset
		bounds[1] += offset
		bounds[2] -= offset
		bounds[3] += offset
		bounds[4] -= offset
		bounds[5] += offset
		#print 'offset',offset
		self.notifyFinish.emit(self.allModelList, bounds)
		


