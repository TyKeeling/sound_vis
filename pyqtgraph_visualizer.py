# import pyqtgraph.examples
# pyqtgraph.examples.run()
# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import pyaudio
import wave
import sys
import time
import scipy
import random

class Datastream:
    def __init__(self, wavfile):
        self.CHUNK = 1024
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

        self.channels = self.wf.getnchannels()

        self.numpy_chunk = None
        self.chunks_to_display = 16
        self.combined_chunks = np.zeros((self.CHUNK), dtype=np.int8)

    def close(self):
        self.stream.close()
        self.p.terminate()
    
    def nextChunk(self):
        data = self.wf.readframes(self.CHUNK)
        if len(data) < 1:
            raise BufferError("end of WAV.")

        self.stream.write(data)
        
        # only supports stereo and mono
        # only one channel is displayed 
        if (self.channels == 2):
            self.numpy_chunk = np.frombuffer(data, dtype=np.int16)[::2] #deserializing stereo data 
        else:
            self.numpy_chunk = np.frombuffer(data, dtype=np.int16)
        return self.numpy_chunk
        
    def multiChunk(self):
        # print(np.shape(self.combined_chunks[self.CHUNK:]), np.shape(self.nextchunk()))
        self.combined_chunks = np.concatenate(
            (self.combined_chunks[int(self.CHUNK/self.chunks_to_display):], 
            self.numpy_chunk[::self.chunks_to_display]))
        return self.combined_chunks

    def getSpectrogram(self):
        return np.abs(scipy.fft.fft(self.numpy_chunk))
        
    def getLongSpectrogram(self):
        longfft = np.absolute(scipy.fft.fft(self.combined_chunks))
        return np.repeat(longfft,2)
        
        
datastream = Datastream("01.-My-Old-Man.wav")


# QtGui.QApplication.setGraphicsSystem('raster')
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

app = QtGui.QApplication([])

win = pg.GraphicsWindow(title="Music Visualizer")
win.resize(800,500)
win.setWindowTitle('Window for Visualizer')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# Future reference: another way to add plots to pyqtgraph
# p5 = pg.PlotItem()
# p5.plot(np.random.normal(size=(1000)))
# p5v = p5.getViewBox()
# win.addItem(p5)

# p6 = win.addPlot(title="Instant Chunk")
# p6v = p6.getViewBox()
# p6v.setRange(xRange=(0,1000), yRange=(-32768,32768))
# p6v.setMouseEnabled(x=False, y=False)
# curve6 = p6.plot(pen='y')

# win.nextRow()

# p7 = win.addPlot(title="FFT")
# p7v = p7.getViewBox()
# p7v.setRange(xRange=(0,1000), yRange=(0,800000))
# # p7.setLogMode(x=False, y=True)
# # p6v.setMouseEnabled(x=False, y=False)
# curve7 = p7.plot(pen='c')

p9 = win.addPlot(title="Long FFT")
# p9.setLogMode(x=False, y=True)
p9v = p9.getViewBox()
p9v.setRange(xRange=(0,1000), yRange=(10,1000000))
# p6v.setMouseEnabled(x=False, y=False)
curve9 = p9.plot(pen='c', width=20)
curve9b = p9.plot(pen='m', width=6)
curve9c = p9.plot(pen='y', width=4)
curve9d = p9.plot(pen='b', width=3)

# win.nextRow()

# p8 = win.addPlot(title="Long Channel")
# p8v = p8.getViewBox()
# p8v.setRange(xRange=(0,1000), yRange=(-32768,32768))
# p8v.setMouseEnabled(x=False, y=False)
# curve8 = p8.plot(pen='m')


i = 0 
def update():
    global curve9, curve9b, curve9c, curve9d, i
    # global curve6, curve7, curve8, curve9
    try:
        datastream.nextChunk()
        datastream.multiChunk()
        # curve6.setData(datastream.nextChunk())
        # curve7.setData(datastream.getSpectrogram())
        # curve8.setData(datastream.multiChunk())
        if i == 0:
            curve9.setData(datastream.getLongSpectrogram())
        elif i == 1:
            curve9b.setData(datastream.getLongSpectrogram())
        elif i == 2:
            curve9c.setData(datastream.getLongSpectrogram())
        elif i == 3:
            curve9d.setData(datastream.getLongSpectrogram())
        
        i = random.randint(0,3)
        i=0
        
    except BufferError:
        datastream.close()
        sys.exit("end of WAV")

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0.001)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()