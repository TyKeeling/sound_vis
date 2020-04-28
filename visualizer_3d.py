# -*- coding: utf-8 -*-
"""
This example demonstrates the use of GLSurfacePlotItem.
"""

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import numpy as np

import pyqtgraph_visualizer as pqvis

class Grapher:
    def __init__(self, **kwargs):

        if "datastream" in kwargs.keys():
            self.datastream = kwargs.get("datastream")
        elif "file" in kwargs.keys():
            self.datastream = pqvis.Datastream(kwargs.get("file"), sections=5)
        else:
            raise InvalidKWargs('kwargs must contain "datastream" object or "file" string')

        self.app = QtGui.QApplication([])

        self.w = gl.GLViewWidget()
        self.w.show()
        self.w.setWindowTitle('GLSurfacePlot')
        self.w.setCameraPosition()

        ## Add a grid to the view
        # self.g = gl.GLGridItem()
        # self.g.scale(2,2,1)
        # self.g.setDepthValue(10)  # draw grid after surfaces since they may be translucent
        # self.w.addItem(self.g)

        ## Animated example
        ## compute surface vertex data
        self.cols = 90
        self.rows = 100
        self.x = np.linspace(-8, 8, self.cols+1).reshape(self.cols+1,1)
        self.y = np.linspace(-8, 8, self.rows+1).reshape(1,self.rows+1)
        self.d = (self.x**2 + self.y**2) * 0.1
        self.d2 = self.d ** 0.5 + 0.1

        ## precompute height values for all frames
        self.phi = np.arange(0, np.pi*2, np.pi/20.)
        self.z = np.sin(self.d[np.newaxis,...] + self.phi.reshape(self.phi.shape[0], 1, 1)) / self.d2[np.newaxis,...]

        ## create a surface plot, tell it to use the 'heightColor' shader
        ## since this does not require normal vectors to render (thus we 
        ## can set computeNormals=False to save time when the mesh updates)
        self.p4 = gl.GLSurfacePlotItem(x=self.x[:,0], y = self.y[0,:], shader='heightColor', computeNormals=False, smooth=False)
        self.p4.shader()['colorMap'] = np.array([0.2, 2, 0.5, 0.2, 1, 1, 0.2, 0, 2])
        # p4.translate(10, 10, 0)
        self.w.addItem(self.p4)

        self.index = 0
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0.00001)

        print(self.z.shape[0])

    #Say that this maps to bass. Max(bass) range is ~2.5e6? so now we map the range 
    def update(self):
        self.index -= 1
        # self.p4.setData(z=self.z[self.index%self.z.shape[0]])
        try:
            # Must call nextChunk/multiChunk to update chunks
            self.datastream.nextChunk()
            self.datastream.multiChunk()

            areas = self.datastream.getAreas()
            self.p4.setData(z=self.z[ self.index % self.z.shape[0] ] )
            self.p4.rotate(3/2, 0, 0, 10, local=False)
            self.p4.scale(0.999, 1.0002, 1.0002)
            # self.p4.translate(0.5/2, 0, 0)

        except BufferError:
            self.datastream.close()
            sys.exit("end of WAV")

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    grapher = Grapher(file="02-Nangs.wav")
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        grapher.app.instance().exec_()
