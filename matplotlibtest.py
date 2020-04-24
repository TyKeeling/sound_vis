# https://bastibe.de/2013-05-30-speeding-up-matplotlib.html
# None of this work is mine, I have included for FPS testing only. 
# only about 40fps still, contrast to 500 advertised 

import numpy as np
import pyaudio
import wave
import struct
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.colors as colors
import random
import scipy.signal
import scipy.io.wavfile
from celluloid import Camera
import time 
import matplotlib

matplotlib.use('Qt4Agg')
# matplotlib.use ('tkagg')

fig, ax = plt.subplots()
line, = ax.plot(np.random.randn(100))
plt.show(block=False)
plt.pause(1)

sec = 4
tstart = time.time()
num_plots = 0
while time.time()-tstart < sec:
    line.set_ydata(np.random.randn(100))
    ax.draw_artist(ax.patch)
    ax.draw_artist(line)
    fig.canvas.update()
    # fig.canvas.draw()
    fig.canvas.flush_events()
    num_plots += 1
print(num_plots/sec)