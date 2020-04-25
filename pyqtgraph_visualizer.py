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
import scipy

class Datastream:
    def __init__(self, wavfile):
        self.CHUNK = 1024
        self.spect_len = 100
        self.wf = wave.open(wavfile, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
                format=self.p.get_format_from_width(self.wf.getsampwidth()),
                channels=self.wf.getnchannels(),
                rate=self.wf.getframerate(),
                output=True)
        print("Filename: ", wavfile)
        print("Channels: ", self.wf.getnchannels())
        print("Sample Width: ", self.wf.getsampwidth()) # 2 
        print("Format: : ", self.p.get_format_from_width(self.wf.getsampwidth())) 
        # Filename:  01.-My-Old-Man.wav (2*self.CHUNK)
        # Channels:  2
        # Sample Width:  2
        # Format: :  8 := pyaudio.paInt16 --> two byte amplitude (max signed val: 32768)
        ###
        # Filename:  sine.wav (self.CHUNK)
        # Channels:  1
        # Sample Width:  2
        # Format: :  8

        self.inc = 1

        self.numpy_chunk = None 


        self.chunks_to_display = 16
        self.combined_chunks = np.zeros((self.CHUNK), dtype=np.int8)

    
    def nextChunk(self):
        data = self.wf.readframes(self.CHUNK)
        if len(data) < 1:
            raise BufferError("end of WAV.")

        self.stream.write(data)
        self.numpy_chunk = np.frombuffer(data, dtype=np.int16)
        return self.numpy_chunk
        
    def nextChunkLong(self):
        # print(np.shape(self.combined_chunks[self.CHUNK:]), np.shape(self.nextchunk()))
        self.combined_chunks = np.concatenate(
            (self.combined_chunks[int(self.CHUNK/self.chunks_to_display):], 
            self.nextChunk()[::self.chunks_to_display]))
        return  

    def getSpectogram(self):
        # self.longerchunk()

        # 1-chunk FFT 
        new_fft = scipy.fft.fft(self.numpy_chunk)
        return np.abs(new_fft)
        
        
datastream = Datastream("sine.wav")


# QtGui.QApplication.setGraphicsSystem('raster')
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

app = QtGui.QApplication([])

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

p6 = win.addPlot(title="Audio Channel")
p6v = p6.getViewBox()
p6v.setRange(xRange=(0,1000), yRange=(-32768,32768))
p6v.setMouseEnabled(x=False, y=False)
curve6 = p6.plot(pen='y')

win.nextRow()

p7 = win.addPlot(title="FFT")
p7v = p7.getViewBox()
p7v.setRange(xRange=(0,1000), yRange=(0,8000))
# p6v.setMouseEnabled(x=False, y=False)
curve7 = p7.plot(pen='y')

curve6.setData(datastream.nextChunk())
datastream.getSpectogram()

def update():
    global curve6, curve7
    curve6.setData(datastream.nextChunk())
    curve7.setData(datastream.getSpectogram())
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0.000001)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()