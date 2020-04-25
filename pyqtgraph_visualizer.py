# import pyqtgraph.examples
# pyqtgraph.examples.run()
# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import pyaudio
import wave
import struct
import sys
import time

class Datastream:
    def __init__(self, wavfile):
        self.CHUNK = 1024
        self.slinter = 2 
        self.wf = wave.open(wavfile, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                channels=self.wf.getnchannels(),
                rate=self.wf.getframerate(),
                output=True)

    def nextchunk(self):
        data = self.wf.readframes(self.CHUNK)
        if len(data) < 1:
            raise BufferError("end of WAV.")
        self.stream.write(data)

        data_int = struct.unpack(str(2*self.CHUNK)+'h', data)
        return np.array(data_int, dtype=np.int8)[::self.slinter]
        
datastream = Datastream("02-Nangs.wav")

# while True:
#     datastream.nextchunk()


#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

win = pg.GraphicsWindow(title="Music Visualizer")
win.resize(1000,600)
win.setWindowTitle('Window for Visualizer')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# p5 = pg.PlotItem()
# p5.plot(np.random.normal(size=(1000)))
# p5v = p5.getViewBox()
# p5v.setRange(xRange=(0,1000), yRange=(-128,128))
# p5v.setMouseEnabled(x=False, y=False)
# # p5v.setLimits(xMin=0, xMax=1000, yMin=-128, yMax=128)
# win.addItem(p5)

# win.nextRow()

p6 = win.addPlot(title="Audio Channel")
p6v = p6.getViewBox()
p6v.setRange(xRange=(0,1000), yRange=(-128,128))
p6v.setMouseEnabled(x=False, y=False)
curve = p6.plot(pen='y')
data = datastream.nextchunk()
# ptr = 0
def update():
    global curve, data, ptr, p6
    curve.setData(datastream.nextchunk())
    # if ptr == 0:
    #     p6.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
    # ptr += 1
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0.01)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


# class App(QtGui.QMainWindow):
#     def __init__(self, parent=None):
#         super(App, self).__init__(parent)

#         #### Create Gui Elements ###########
#         self.mainbox = QtGui.QWidget()
#         self.setCentralWidget(self.mainbox)
#         self.mainbox.setLayout(QtGui.QVBoxLayout())

#         self.canvas = pg.GraphicsLayoutWidget()
#         self.mainbox.layout().addWidget(self.canvas)

#         self.label = QtGui.QLabel()
#         self.mainbox.layout().addWidget(self.label)

#         self.view = self.canvas.addViewBox()
#         self.view.setAspectLocked(True)
#         self.view.setRange(QtCore.QRectF(0,0, 100, 100))

#         #  image plot
#         self.img = pg.ImageItem(border='w')
#         self.view.addItem(self.img)

#         self.canvas.nextRow()
#         #  line plot
#         self.otherplot = self.canvas.addPlot()
#         self.h2 = self.otherplot.plot(pen='y')


#         #### Set Data  #####################

#         self.x = np.linspace(0,50., num=100)
#         self.X,self.Y = np.meshgrid(self.x,self.x)

#         self.counter = 0
#         self.fps = 0.
#         self.lastupdate = time.time()

#         #### Start  #####################
#         self._update()

#     def _update(self):
#         self.ydata = datastream.nextchunk()
#         # self.ydata = np.sin(self.x/3.+ self.counter/9.)

#         self.h2.setData(self.ydata)

#         now = time.time()
#         dt = (now-self.lastupdate)
#         if dt <= 0:
#             dt = 0.000000000001
#         fps2 = 1.0 / dt
#         self.lastupdate = now
#         self.fps = self.fps * 0.9 + fps2 * 0.1
#         tx = 'Mean Frame Rate:  {fps:.3f} FPS'.format(fps=self.fps )
#         self.label.setText(tx)
#         QtCore.QTimer.singleShot(1, self._update)
#         self.counter += 1


# if __name__ == '__main__':

#     app = QtGui.QApplication(sys.argv)
#     thisapp = App()
#     thisapp.show()
#     sys.exit(app.exec_())




# ## Always start by initializing Qt (only once per application)
# app = QtGui.QApplication([])

# ## Define a top-level widget to hold everything
# w = QtGui.QWidget()

# ## Create some widgets to be placed inside
# btn = QtGui.QPushButton('press me')
# text = QtGui.QLineEdit('enter text')
# listw = QtGui.QListWidget()
# plot = pg.PlotWidget()

# ## Create a grid layout to manage the widgets size and position
# layout = QtGui.QGridLayout()
# w.setLayout(layout)

# ## Add widgets to the layout in their proper positions
# layout.addWidget(btn, 0, 0)   # button goes in upper-left
# layout.addWidget(text, 1, 0)   # text edit goes in middle-left
# layout.addWidget(listw, 2, 0)  # list widget goes in bottom-left
# layout.addWidget(plot, 0, 1, 3, 1)  # plot goes on right side, spanning 3 rows

# ## Display the widget as a new window
# w.show()

# ## Start the Qt event loop
# app.exec_()