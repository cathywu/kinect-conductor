#!/usr/bin/env python
# 
"""
These functions, when given a magnitude mag between cmin and cmax, return
a colour tuple (red, green, blue). Light blue is cold (low magnitude)
and yellow is hot (high magnitude).

"""
import math
import numpy as np

def floatRgb(mag, cmin, cmax):
       """
       Return a tuple of floats between 0 and 1 for the red, green and
       blue amplitudes.
       """
       zeros = np.zeros(mag.shape)
       ones = np.ones(mag.shape)

       try:
              # normalize to [0,1]
              x = (mag-cmin).astype(float)/float(cmax-cmin)
       except:
              # cmax = cmin
              x[:,:] = 0.5
       blue = np.minimum(np.maximum(4*(0.75-x), zeros), ones)
       red  = np.minimum(np.maximum(4*(x-0.25), zeros), ones)
       green= np.minimum(np.maximum(4*np.abs(x-0.5)-1., zeros), ones)
       return (red, green, blue)

def strRgb(mag, cmin, cmax):
       """
       Return a tuple of strings to be used in Tk plots.
       """

       red, green, blue = floatRgb(mag, cmin, cmax)       
       return "#%02x%02x%02x" % (red*255, green*255, blue*255)

def rgb(mag, cmin, cmax):
       """
       Return a tuple of integers to be used in AWT/Java plots.
       """

       red, green, blue = floatRgb(mag, cmin, cmax)
       return ((red*255).astype(int), (green*255).astype(int), 
                    (blue*255).astype(int))

def htmlRgb(mag, cmin, cmax):
       """
       Return a tuple of strings to be used in HTML documents.
       """
       return "#%02x%02x%02x"%rgb(mag, cmin, cmax)

