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
        self.chunks_to_display = 16
        self.sections = 100 # Parts to evaluate integrals

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
        self.combined_chunks = np.concatenate(
            (self.combined_chunks[int(self.CHUNK/self.chunks_to_display):], 
            self.numpy_chunk[::self.chunks_to_display]))
        return self.combined_chunks

    def getSpectrogram(self):
        return np.abs(scipy.fft.fft(self.numpy_chunk))
        
    def getLongSpectrogram(self):
        longfft = np.absolute(scipy.fft.fft(self.combined_chunks))
        return np.repeat(longfft,2)

    def getAreas(self):
        theFunc = np.repeat(np.absolute(scipy.fft.fft(self.combined_chunks)),2)
        theFunc = theFunc[:int(np.size(theFunc)/2)] #scipy fft has symmetry effect 
        section_len = int(np.size(theFunc)/self.sections)
        areas = np.zeros((self.sections), dtype=np.int32)
        for i in range(self.sections):
            areas[i] = np.max(theFunc[i*section_len:(i+1)*section_len])
        return areas

        
        
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

p9 = win.addPlot(title="Long FFT")
# p9.setLogMode(x=False, y=True)
p9v = p9.getViewBox()
p9v.setRange(xRange=(0,1000), yRange=(10,1000000))
# p6v.setMouseEnabled(x=False, y=False)
curve9 = p9.plot(pen='c', width=20)

p5 = win.addPlot(title="Areas")
p5v = p5.getViewBox()
p5v.setRange(xRange=(0,datastream.sections-1))
# p6v.setMouseEnabled(x=False, y=False)
# curve5 = p5.plot(pen='y', fillLevel=0, brush=(0,0,255,150))
curve5 = p5.plot(pen='y')


def update():
    global curve9, curve5

    try:
        # Must call nextChunk/multiChunk to update chunks
        datastream.nextChunk()
        datastream.multiChunk()
        curve9.setData(datastream.getLongSpectrogram())
        curve5.setData(datastream.getAreas())

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