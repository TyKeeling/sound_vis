# -*- coding: utf-8 -*-
"""
This example demonstrates the use of GLSurfacePlotItem.
"""

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

import pyqtgraph_visualizer as pqvis

class Solid:
    def __init__(self, timeres=100, cols=90, rows=100):
        self.timeRes = timeres
        ## Animated example
        ## compute surface vertex data
        self.cols = cols
        self.rows = rows
        self.x = np.linspace(-8, 8, self.cols+1)
        self.y = np.linspace(-8, 8, self.rows+1)

        xx, yy = np.meshgrid(self.y, self.x)
        self.z = np.sin(xx**2 + yy**2) *20 / (xx**2 + yy**2 + 0.1)# - abs(xx) -abs(yy)
        # self.z = 8-abs(xx+yy)-abs(yy-xx)

        self.pTime = []
        for i in range(self.timeRes):
            self.pTime.append(self.z * i/self.timeRes)

        ## create a surface plot, tell it to use the 'heightColor' shader
        ## since this does not require normal vectors to render (thus we 
        ## can set computeNormals=False to save time when the mesh updates)
        self.p = gl.GLSurfacePlotItem(x=self.x, y = self.y, shader='heightColor', computeNormals=False, smooth=False)
        self.p.shader()['colorMap'] = np.array([0.2, 3, 0.5, 0.2, 1, 1, 0.2, 0, 2])
    
class Grapher:
    def __init__(self, **kwargs):

        if "datastream" in kwargs.keys():
            self.datastream = kwargs.get("datastream")
        elif "file" in kwargs.keys():
            self.datastream = pqvis.Datastream(kwargs.get("file"), sections=4)
        else:
            raise InvalidKWargs('kwargs must contain "datastream" object or "file" string')

        self.app = QtGui.QApplication([])

        self.w = gl.GLViewWidget()
        self.w.resize(2000,2000)
        self.w.show()
        self.w.setWindowTitle('GLSurfacePlot')
        self.w.setCameraPosition()

        # Add a grid to the view
        self.g = gl.GLGridItem()
        self.g.scale(2,2,1)
        self.g.setDepthValue(10)  # draw grid after surfaces since they may be translucent
        self.w.addItem(self.g)

        self.solid = Solid()
        self.p = self.solid.p
        self.p.translate(0, -20, 0)
        self.w.addItem(self.p)

        self.solid2 = Solid()
        self.p2 = self.solid2.p
        self.p2.translate(0,20,0)
        self.w.addItem(self.p2)

        self.solid3 = Solid()
        self.p3 = self.solid3.p
        self.p3.translate(20, 0, 0)
        self.w.addItem(self.p3)

        self.solid4 = Solid()
        self.p4 = self.solid4.p
        self.p4.translate(-20,0,0)
        self.w.addItem(self.p4)

        # n = 51
        # y = np.linspace(-10,10,n)
        # x = np.linspace(-10,10,100)
        # for i in range(n):
        #     yi = np.array([y[i]]*100)
        #     d = (x**2 + yi**2)**0.5
        #     z = 10 * np.cos(d) / (d+1)
        #     pts = np.vstack([x,yi,z]).transpose()
        #     plt = gl.GLLinePlotItem(pos=pts, color=pg.glColor((i,n*1.3)), width=(i+1)/10., antialias=True)
        
        #     self.w.addItem(plt)
            

        # self.index = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0.00001)


    def update(self):
        try:
            # Must call nextChunk/multiChunk to update chunks
            self.datastream.nextChunk()
            self.datastream.multiChunk()

            areas = self.datastream.getAreas()

            # Max(bass) range is ~2.5e6? so now we map the range 
            index = [int(min(a * self.solid.timeRes / 5000000, self.solid.timeRes-1)) for a in areas]

            self.p.setData(z=self.solid.pTime[index[0]])
            self.p.rotate(1/4, 0, 10, 0, local=True)
            self.p.rotate(3/4, 0, 0, 10, local=False)

            self.p2.setData(z=self.solid2.pTime[index[1]])
            self.p2.rotate(1/4, 0, 10, 0, local=True)
            self.p2.rotate(3/4, 0, 0, 10, local=False)

            self.p3.setData(z=self.solid2.pTime[index[2]])
            self.p3.rotate(1/4, 0, 10, 0, local=True)
            self.p3.rotate(3/4, 0, 0, 10, local=False)

            self.p4.setData(z=self.solid2.pTime[index[3]])
            self.p4.rotate(1/4, 0, 10, 0, local=True)
            self.p4.rotate(3/4, 0, 0, 10, local=False)

        except BufferError:
            self.datastream.close()
            sys.exit("end of WAV")


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    grapher = Grapher(file="03 Apocalypse Dreams.wav")
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        grapher.app.instance().exec_()
