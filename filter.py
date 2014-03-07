#!/usr/bin/env python
import numpy as np
from scipy import signal

def gauss_kern(size, sizey=None):
    size = int(size)
    if not sizey:
        sizey = size
    else:
        sizey = int(sizey)
    x,y = np.mgrid[-size:size+1, -sizey:sizey+1]
    g = np.exp(-(x**2/float(size)+y**2/float(sizey)))
    return g / g.sum()

def blur_image(im, n, ny=None):
    g = gauss_kern(n, sizey=ny)
    improc = signal.convolve(im, g, mode='same')
    return improc

