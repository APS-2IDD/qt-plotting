#!/APSshare/anaconda3/BlueSky/bin/python3 

import sys
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QInputDialog, QLineEdit, QFileDialog, QAction, QTextEdit, QLabel, QTabWidget
from PyQt5.QtGui import QIcon
from PyQt5 import QtGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import numpy as np
import math
from mda import *
import h5py

import epics
import os
import re
import math

#temp data storage
import temp_mdaData as mdat
import temp_h5Data as hdat

data1_name = b'dp_eiger:Stats1:Total_RBV'
data2_name = b'dp_eiger:Stats1:CentroidX_RBV'
data3_name = b'dp_eiger:Stats1:CentroidY_RBV'
h5_data_tree = 'entry/data/data'

tot_cmap = 'hot'
cX_cmap = 'hot'
cY_cmap = 'hot'
h5_cmap = 'hot'

def getHDFdata(h5Dir_Path, h5pref, scanNum, scanX, scanY):

	h5file_name = h5pref+'_data_'+str(scanX+1).zfill(6)+'.h5'
	h5file_path = h5Dir_Path+'/'+h5file_name

	hdat.scanX = scanX
	hdat.scanY = scanY

	f = h5py.File(h5file_path, 'r')
	data = f[h5_data_tree].value  #Returns 3-d array of (ScanY, DataY, DataX)
	
	return  h5file_path, data 

        
class QPlotter(QWidget):
	def __init__(self, parent=None):		
		super(QPlotter, self).__init__(parent)
    	
		# a figure instance to plot on
		self.figure1 = plt.figure()
		self.figure2 = plt.figure()

		self.x_lim = [-500,500]
		self.y_lim = [-500,500]
		self.t_lim = [0,1e4]
		
		self.canvas1 = FigureCanvas(self.figure1)
		self.toolbar1 = NavigationToolbar(self.canvas1, self)

		# coordinate display on bottom
		self.coordLabel = QLabel(self)
		self.coordLabel.resize(200, 40)

		# buttons on bottom
		self.button = QPushButton('Re-Plot Loaded Data')
		self.button.clicked.connect(self.plot)
		self.button2 = QPushButton('Load Latest Scan')
		self.button2.clicked.connect(self.loadLatest)
		self.button1 = QPushButton('Clear Plot')
		self.button1.clicked.connect(self.clear_plot)

		buttons = QHBoxLayout()
		buttons.addStretch(1)
		buttons.addWidget(self.coordLabel)
		buttons.addWidget(self.button2)
		buttons.addWidget(self.button)
		buttons.addWidget(self.button1)
		
		controls = QHBoxLayout()
		controls.addStretch(1)
		controls.addLayout(buttons)

		layout = QVBoxLayout()
		layout.addWidget(self.toolbar1)
		layout.addWidget(self.canvas1)
		layout.addLayout(controls)
		self.setLayout(layout)

		self.setMouseTracking(True)

	def mouseMoveEvent(self, event):
		self.coordLabel.setText('Mouse coords: ( %d : %d )' % (event.x(), event.y()))

#	def mousePressEvent(self, QMouseEvent):
#		print(QMouseEvent.pos())

#	def mouseReleaseEvent(self, QMouseEvent):
#		cursor = QtGui.QCursor()
#		print(cursor.pos())  

	def clear_plot(self):
		self.figure1.clear()
		self.canvas1.draw()
		
	def loadLatest(self):
		dest_PV = epics.PV('2iddVELO:VP:Destination_Dir')
		destPath = dest_PV.get(as_string=True)
		filename_PV = epics.PV('2iddVELO:VP:Last_Filename')
		posFile = filename_PV.value

		destFilePath = os.path.join(destPath, posFile)		

		data = genfromtxt(destFilePath, delimiter=',')

		tdat.filename = posFile
		tdat.x_ref = data[:,0]
		tdat.y_ref = data[:,1]
		tdat.x_act = data[:,2]
		tdat.y_act = data[:,3]
		tdat.det_v = data[:,4]
		
		self.plot()

	def plot_h5(self, h5Axis):
		h5Axis.set_title(hdat.filename)
		h5data = hdat.data[hdat.scanY,:,:]
		h5Axis.imshow(h5data, cmap = h5_cmap)
		
		self.canvas1.draw()

	def plot(self):
		self.figure1.clear()

		#self.x_lim = [int(self.xmin.text()), int(self.xmax.text())]
		#self.y_lim = [int(self.ymin.text()), int(self.ymax.text())]
		#self.t_lim = [float(self.tmin.text()), float(self.tmax.text())]

		if mdat.filename != '':
			#create grid for subplots
			gs = gridspec.GridSpec(3,4)
			
			ax = self.figure1.add_subplot(gs[0,0])
			bx = self.figure1.add_subplot(gs[1,0])
			cx = self.figure1.add_subplot(gs[2,0])
			dx = self.figure1.add_subplot(gs[:,1:])
	
			#ax.set_xlim((self.x_lim[0], self.x_lim[1]))
			#ax.set_ylim((self.y_lim[0], self.y_lim[1]))
			
			#bx.set_xlim((self.t_lim[0], min((self.t_lim[1],len(tdat.x_ref)))))
			#bx.set_ylim((min((self.x_lim[0],self.y_lim[0])),max((self.x_lim[1],self.y_lim[1]))))
	
			if mdat.filename != '':
				self.figure1.suptitle(mdat.filename, x = 0.1, ha='left')

			ax.set_title('Total Counts')
			bx.set_title('Centroid X')
			cx.set_title('Centroid Y')
			
			ax.tick_params(axis='x', which='both', bottom=False, top=False,         
				labelbottom=False) 

			bx.tick_params(axis='x', which='both', bottom=False, top=False,         
				labelbottom=False) 

			dx.tick_params(axis='y', which='both', right=True, left=False, 
				labelleft=False, labelright=True) 
						
			ax.imshow(mdat.total_dat.T, cmap = tot_cmap)
			bx.imshow(mdat.centroidX_dat.T, cmap = cX_cmap)
			cx.imshow(mdat.centroidY_dat.T, cmap = cY_cmap)

			if hdat.filename == '':
				dx.set_title('<No hdf5 file selected/found>')
			else:
				self.plot_h5(dx)

			def onclick(event):
				if (((event.dblclick is False) and (event.button == 1)) and 
				(ax.in_axes(event) or bx.in_axes(event) or cx.in_axes(event))):
					scanX = math.floor(event.xdata)
					scanY = math.floor(event.ydata)
					if scanX != hdat.scanX:
						hdat.filename, hdat.data = getHDFdata(hdat.h5Path, 
													hdat.h5Prefix, mdat.scanNum, 
													scanX, scanY)
						self.plot_h5(dx)
					else:
						if scanY != hdat.scanY:
							hdat.scanY = scanY
							self.plot_h5(dx)
					print('xdata=%d, ydata=%d'%(math.floor(event.xdata), 
						math.floor(event.ydata)))
				else:
					print('x=%f, y=%f'%(event.x, event.y))
				
			cid = self.canvas1.mpl_connect('button_press_event', onclick)
			
			# refresh canvas
			self.canvas1.draw()	

class App(QMainWindow):
	def __init__(self, parent=None):
		super().__init__()
		self.title = 'MDA/H5 Viewer'
		#when run @sec2idd, need to change default dir to /mnt/micdata2/velociprobe
		self.default_dir = '/net/micdata/data2/velociprobe/2018-2/Jun_comm'
		self.mdaFilename = ''
		self.mdaDir = ''
		self.h5Filename = ''
		self.h5Files = []
		self.h5Dir = ''
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
	
		mainMenu = self.menuBar()
		fileMenu = mainMenu.addMenu('&File')
		helpMenu = mainMenu.addMenu('Help')

		openFile = QAction("&Open MDA File", self)
		openFile.setShortcut("Ctrl+O")
		openFile.setStatusTip('Open MDA File')
		openFile.triggered.connect(self.file_open)
		fileMenu.addAction(openFile)

		extractAction = QAction("&Quit", self)
		extractAction.setShortcut("Ctrl+Q")
		extractAction.setStatusTip('Leave The App')
		extractAction.triggered.connect(self.close_application)
		fileMenu.addAction(extractAction)

		self.show()

	def file_open(self):
		fname = QFileDialog.getOpenFileName(self, 'Open File',self.default_dir)
		if fname[0]:
			fname_array = fname[0].split('/')
			fNasize = len(fname_array)
			self.mdaFilename = fname_array[-1]
			self.mdaDir = '/'.join(fname_array[0:fNasize-1])
			fileName = self.mdaFilename.split('.')
			fileNum = fileName[0].split('_')
			fNum = int(fileNum[-1])
			mdat.scanNum = fNum
			mdat.filename = self.mdaFilename

			dim = readMDA(fname[0], verbose = 0)

			data1_loc = [i for i in range(len(dim[2].d)) if dim[2].d[i].name == data1_name]
			data2_loc = [i for i in range(len(dim[2].d)) if dim[2].d[i].name == data2_name]
			data3_loc = [i for i in range(len(dim[2].d)) if dim[2].d[i].name == data3_name]

			mdat.total_dat = dim[2].d[data1_loc[0]].data
			mdat.centroidX_dat = dim[2].d[data2_loc[0]].data
			mdat.centroidY_dat = dim[2].d[data3_loc[0]].data
		
			hdat.h5Prefix = 'scan'+str(mdat.scanNum).zfill(3)
			hdat.h5Path = '/'.join(fname_array[0:fNasize-2])+'/ptycho/'+hdat.h5Prefix
			hdat.filename, hdat.data = getHDFdata(hdat.h5Path, hdat.h5Prefix, fNum, 0, 0)
			
			self.plotter.plot()

	def close_application(self):
		sys.exit()
			

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = App()
	sys.exit(app.exec_())
