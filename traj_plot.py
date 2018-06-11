#!/APSshare/anaconda3/BlueSky/bin/python3 

import sys
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QInputDialog, QLineEdit, QFileDialog, QAction, QTextEdit, QLabel, QTabWidget
from PyQt5 import QtGui
#from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import numpy as np
from numpy import genfromtxt
import math

import epics
import os

#temp data storage
import tempData as tdat

def getData(fileAndPath):
	data = genfromtxt(fileAndPath, delimiter=',')
	tdat.x_ref = data[:,0]
	tdat.y_ref = data[:,1]
	tdat.x_act = data[:,2]
	tdat.y_act = data[:,3]
	tdat.det_v = data[:,4]
	tdat.fileAndPath(fileAndPath)
	tdat.local_files = getFiles(fileAndPath)
#	tdat.index = #where tdat.local_files == tdat_filename OR do this in getFiles

def getFiles(fileAndPath):
	fname_array = fileAndPath.split('/')
	fNasize = len(fname_array)
	tdat.filename = fname_array[-1]
	csvDir = '/'.join(fname_array[0:fNasize-1])
	tdat.fileDir = csvDir
	
	list_of_files = [f for f in os.listdir(csvDir) if f.endswith(".csv")]

	try:
		tdat.local_files = list_of_files.index(tdat.filename)
	except:
		print('Error processing file -- csv file to be displayed not found in csv directory')
		
	return list_of_files

class QPlotter(QWidget):
	def __init__(self, parent = None):		
		super(QPlotter, self).__init__()
    	
		# a figure instance to plot on
		self.figure1 = plt.figure()
		self.figure2 = plt.figure()

		self.x_lim = [-5000,5000]
		self.y_lim = [-5000,5000]
		self.t_lim = [0,2.5e4]
		
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
				
		#self.fileDisplayLabel = QLabel(self)
		#self.fileDisplayLabel.setText('File plotted: ')
		#self.fileDisplay = QLineEdit()
		#self.fileDisplay.setText('<filename.csv>')
		#self.fileDisplay.setReadOnly(True)
		#self.fileDisplay.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
		#filePlotted = QHBoxLayout()
		#filePlotted.addStretch(1)
		#filePlotted.addWidget(self.fileDisplayLabel)
		#filePlotted.addWidget(self.fileDisplay)
		
		# buttons on bottom
#		self.button = QPushButton('Plot Loaded Data')
#		self.button.clicked.connect(self.plot)
		self.button3 = QPushButton('Plot Previous Traj')
		self.button3.clicked.connect(self.loadTraj(inc = 'Prev'))
		self.button4 = QPushButton('Plot Next Traj')
		self.button4.clicked.connect(self.loadTraj(inc = 'Next'))
		self.button2 = QPushButton('Load Latest Scan')
		self.button2.clicked.connect(self.loadTraj(inc = 'Latest'))
		self.button1 = QPushButton('Clear Plot')
		self.button1.clicked.connect(self.clear_plot)

		buttons = QHBoxLayout()
		buttons.addStretch(1)
#		buttons.addLayout(filePlotted)
		buttons.addWidget(self.button2)
		buttons.addWidget(self.button3)
		buttons.addWidget(self.button4)
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
		
	def loadLatest(self):
		dest_PV = epics.PV('2iddVELO:VP:Destination_Dir')
		destPath = dest_PV.get(as_string=True)
		filename_PV = epics.PV('2iddVELO:VP:Last_Filename')
		posFile = filename_PV.value

		destFilePath = os.path.join(destPath, posFile)		

		getData(destFilePath) 

		self.plot()

	def loadTraj(self, inc = 'Latest'):
		if ((inc == 'Prev') or (inc == 'Next') and (tdat.fileDir == []):
			destPath = tdat.fileDir
			trajFile = tdat.local_files[tdat.indes + (1 if (inc == 'Next') else -1)]
		else:
			destPath_PV = epics.PV('2iddVELO:VP:Destination_Dir')
			destPath = dest_PV.get(as_string=True)
			filename_PV = epics.PV('2iddVELO:VP:Last_Filename')
			trajFile = filename_PV.value

		trajFilePath = os.path.join(destPath, trajFile)
		getData(trajFilePath)
		
		self.plot() 

	def plot(self):
		self.figure1.clear()

		self.x_lim = [int(self.xmin.text()), int(self.xmax.text())]
		self.y_lim = [int(self.ymin.text()), int(self.ymax.text())]
		self.t_lim = [float(self.tmin.text()), float(self.tmax.text())]

		if tdat.fileAndPath == '':
			getData('arch_spiral_4500x30_3kHz_traces.csv', delimiter=',')

		# create an axis
		self.figure1.suptitle(tdat.fileAndPath)

		ax = self.figure1.add_subplot(121)
		bx = self.figure1.add_subplot(122)
		
		ax.set_xlim((self.x_lim[0], self.x_lim[1]))
		ax.set_ylim((self.y_lim[0], self.y_lim[1]))
		
		bx.set_xlim((self.t_lim[0], len(tdat.x_ref)))
		bx.set_ylim((min((self.x_lim[0],self.y_lim[0])),max((self.x_lim[1],self.y_lim[1]))))

		ax.set_ylabel('y (nm)')
		ax.set_xlabel('x (nm)')
	
		bx.set_ylabel('x, y (nm)')
		bx.set_xlabel('Time ')

		ax.set_title('XY Trajectories')
		bx.set_title('X(t), Y(t)')
	
		lineA1, = ax.plot(tdat.x_ref,tdat.y_ref,lw=1, color = 'xkcd:azure', 
						  alpha = 0.9, label = 'reference trajectory')
		lineA2, = ax.plot(tdat.x_act,tdat.y_act,lw=1, color = 'xkcd:orange', 
						  alpha = 0.5, label = 'measured trajectory')

		lineB1a, = bx.plot(tdat.x_ref, lw=1, color = 'xkcd:azure', 
						  alpha = 0.9, label = 'x-reference')
		lineB1b, = bx.plot(tdat.x_act, lw=1, color = 'xkcd:orange', 
						  alpha = 0.5, label = 'x-actual')

		lineB2a, = bx.plot(tdat.y_ref, lw=1, color = 'xkcd:azure', 
						  alpha = 0.9, label = 'y-reference', linestyle = '-.')
		lineB2b, = bx.plot(tdat.y_act, lw=1, color = 'xkcd:orange', 
						  alpha = 0.5, label = 'y-actual', linestyle = '-.')

		ax.legend(loc = 1)
		bx.legend()

		# refresh canvas
		self.canvas1.draw()	
		
class App(QMainWindow):
	def __init__(self, parent=None):
		super().__init__()
		self.title = 'Velociprobe Trajectory Plotter'
		self.left = 10
		self.top = 10
		self.width = 1350
		self.height = 850
		self.initUI()

	def initUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		self.plotter = QPlotter()
		self.setCentralWidget(self.plotter)
	
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
			tdat.fileAndPath = fname[0]
			getData(tdat.fileAndPath)
			self.plotter.plot()

	def close_application(self):
		sys.exit()
			

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())
