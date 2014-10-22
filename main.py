'''
Arthur Glowacki
APS ANL
10/17/2014
'''

from PyQt4 import QtCore, QtGui, QtOpenGL
from QtWin import Window
import sys

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	window = Window()
	window.show()
	sys.exit(app.exec_())

