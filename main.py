'''
Arthur Glowacki
APS ANL
10/17/2014
'''

import sys
from MainWindow import MainWindow
from PyQt4 import QtCore, QtGui

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())

