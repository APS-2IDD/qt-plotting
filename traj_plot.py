import sys
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QInputDialog, QLineEdit, QFileDialog, QAction, QTextEdit, QLabel, QTabWidget
from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import numpy as np
from numpy import genfromtxt
import math

#temp data storage
import tempData as tdat

class QPlotter(QWidget):
	def __init__(self, parent=None):		
		super(QPlotter, self).__init__(parent)
    	
		# a figure instance to plot on
		self.figure1 = plt.figure()
		self.figure2 = plt.figure()

		self.x_lim = [-500,500]
		self.y_lim = [-500,500]
		self.t_lim = [0,1e6]
		
		self.canvas1 = FigureCanvas(self.figure1)
		self.toolbar1 = NavigationToolbar(self.canvas1, self)

		# Plot settings on bottom
		self.xmin = QLineEdit()
		self.xmin.setText(str(self.x_lim[0]))
		self.xminLabel = QLabel(self)
		self.xminLabel.setText('x_min (nm): ')
		self.xmax = QLineEdit()
		self.xmax.setText(str(self.x_lim[1]))
		self.xmaxLabel = QLabel(self)
		self.xmaxLabel.setText('x_max (nm): ')

		self.ymin = QLineEdit()
		self.ymin.setText(str(self.y_lim[0]))
		self.yminLabel = QLabel(self)
		self.yminLabel.setText('y_min (nm): ')
		self.ymax = QLineEdit()
		self.ymax.setText(str(self.y_lim[1]))
		self.ymaxLabel = QLabel(self)
		self.ymaxLabel.setText('y_max (nm): ')

		self.tmin = QLineEdit()
		self.tmin.setText(str(self.t_lim[0]))
		self.tminLabel = QLabel(self)
		self.tminLabel.setText('t_min (nm): ')
		self.tmax = QLineEdit()
		self.tmax.setText(str(self.t_lim[1]))
		self.tmaxLabel = QLabel(self)
		self.tmaxLabel.setText('t_max (nm): ')

		plotXSettings = QHBoxLayout()
		plotXSettings.addStretch(1)
		plotXSettings.addWidget(self.xminLabel)
		plotXSettings.addWidget(self.xmin)
		plotXSettings.addWidget(self.xmaxLabel)
		plotXSettings.addWidget(self.xmax)

		plotYSettings = QHBoxLayout()
		plotYSettings.addStretch(1)
		plotYSettings.addWidget(self.yminLabel)
		plotYSettings.addWidget(self.ymin)
		plotYSettings.addWidget(self.ymaxLabel)
		plotYSettings.addWidget(self.ymax)

		plotTSettings = QHBoxLayout()
		plotTSettings.addStretch(1)
		plotTSettings.addWidget(self.tminLabel)
		plotTSettings.addWidget(self.tmin)
		plotTSettings.addWidget(self.tmaxLabel)
		plotTSettings.addWidget(self.tmax)
		
		plotSettings = QVBoxLayout()
		plotSettings.addLayout(plotXSettings)
		plotSettings.addLayout(plotYSettings)
		plotSettings.addLayout(plotTSettings)
		
		# buttons on bottom
		self.button = QPushButton('Plot')
		self.button.clicked.connect(self.plot)
		self.button1 = QPushButton('Clear Plot')
		self.button1.clicked.connect(self.clear_plot)

		buttons = QHBoxLayout()
		buttons.addStretch(1)
		buttons.addWidget(self.button)
		buttons.addWidget(self.button1)

		controls = QHBoxLayout()
		controls.addLayout(plotSettings)
		controls.addStretch(1)
		controls.addLayout(buttons)

		layout = QVBoxLayout()
		layout.addWidget(self.toolbar1)
		layout.addWidget(self.canvas1)
		layout.addLayout(controls)
		self.setLayout(layout)

	def clear_plot(self):
		self.figure1.clear()
		self.canvas1.draw()

	def plot(self):
		# instead of ax.hold(False)
		self.figure1.clear()
#		self.figure2.clear()

		self.x_lim = [int(self.xmin.text()), int(self.xmax.text())]
		self.y_lim = [int(self.ymin.text()), int(self.ymax.text())]
		self.t_lim = [float(self.tmin.text()), float(self.tmax.text())]

		if tdat.filename == '':
			tdat.filename = 'arch_spiral_4500x30_3kHz_traces.csv'
			data = genfromtxt(tdat.filename, delimiter=',')
			tdat.x_ref = data[:,0]
			tdat.y_ref = data[:,1]
			tdat.x_act = data[:,2]
			tdat.y_act = data[:,3]
			tdat.det_v = data[:,4]
	 
		# create an axis
		ax = self.figure1.add_subplot(121)
		bx = self.figure1.add_subplot(122)
#		bx2 = self.figure2.add_subplot(312)
#		bx3 = self.figure2.add_subplot(313)
		
		ax.set_xlim((self.x_lim[0], self.x_lim[1]))
		ax.set_ylim((self.y_lim[0], self.y_lim[1]))

		ax.set_ylabel('y (nm)')
		ax.set_xlabel('x (nm)')
	
		bx.set_ylabel('x, y (nm)')
		bx.set_xlabel('Time ')

		ax.set_title('XY Trajectories')
		bx.set_title('X(t), Y(t)')

#		self.setWindowTitle(tdat.filename)
	
		lineA1, = ax.plot(tdat.x_ref,tdat.y_ref,lw=1, color = 'b',label = 'reference trajectory')
		lineA2, = ax.plot(tdat.x_act,tdat.y_act,lw=1, color = 'g',label = 'measured trajectory')

		lineB1a, = bx.plot(tdat.x_ref, lw=1, color = 'b', label = 'x-reference')
		lineB1b, = bx.plot(tdat.x_act, lw=1, color = 'g', label = 'x-actual')

		lineB2a, = bx.plot(tdat.y_ref, lw=1, color = 'r', label = 'y-reference')
		lineB2b, = bx.plot(tdat.y_act, lw=1, color = 'm', label = 'y-actual')

#		lineB3, = bx.plot(tdat.det_v, lw=1, color = 'k', label = 'detector V')

#		traj_legend = plt.legend(handles=[lineA1, lineA2])
#		ax.add_legend(traj_legend)
		
#		trace_legend = plt.legend(handles=[lineB1a, lineB1b, lineB2a, lineB2b])
#		bx.add_legend(trace_legend)
		
		ax.legend()
		bx.legend()

#		self.figure1.legend()
#		self.figure2.legend()

		# refresh canvas
		self.canvas1.draw()	
#		self.canvas2.draw()	

class App(QMainWindow):
	def __init__(self, parent=None):
		super().__init__()
		self.title = 'Velociprobe Trajectory Plotter'
		self.left = 10
		self.top = 10
		self.width = 1350
		self.height = 900
		self.initUI()
 
	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		plotter = QPlotter()
		self.setCentralWidget(plotter)
	
		#temporarily using old file
#		self.csvFile = 'arch_spiral_4500x30_3kHz_traces.csv'

		mainMenu = self.menuBar()
		fileMenu = mainMenu.addMenu('&File')
		helpMenu = mainMenu.addMenu('Help')

		openFile = QAction("&Open File", self)
		openFile.setShortcut("Ctrl+O")
		openFile.setStatusTip('Open File')
		openFile.triggered.connect(self.file_open)
		fileMenu.addAction(openFile)

		extractAction = QAction("&Quit", self)
		extractAction.setShortcut("Ctrl+Q")
		extractAction.setStatusTip('Leave The App')
		extractAction.triggered.connect(self.close_application)
		fileMenu.addAction(extractAction)

		self.show()
		
	def file_open(self):
		fname = QFileDialog.getOpenFileName(self, 'Open File')
		if fname[0]:
			tdat.filename = fname[0]
			print(tdat.filename)
			data = genfromtxt(tdat.filename, delimiter=',')
			tdat.x_ref = data[:,0]
			tdat.y_ref = data[:,1]
			tdat.x_act = data[:,2]
			tdat.y_act = data[:,3]
			tdat.det_v = data[:,4]

	def close_application(self):
		sys.exit()
			

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())
