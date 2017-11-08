"""These functions, when given a magnitude mag between cmin and cmax, return
a colour tuple (red, green, blue). Light blue is cold (low magnitude)
and yellow is hot (high magnitude).
From http://code.activestate.com/recipes/52273/"""

import logging
import math
import pylab as py

from pylab import matplotlib

logger = logging.getLogger(__name__)

def indexed_color(index):
  """
  """
  colors = {0: 'b',  # blue
            1: 'g',  # green
            2: 'r',  # red
            3: 'c',  # cyan
            4: 'm',  # magenta
            5: 'y',  # yellow
            6: 'k',  # black
            7: 'w'   # white
           }
  return colors[index]

def floatRgb(mag, cmin, cmax):
       """
       Return a tuple of floats between 0 and 1 for the red, green and
       blue amplitudes.
       """
       try:
              # normalize to [0,1]
              x = float(mag-cmin)/float(cmax-cmin)
       except:
              # cmax = cmin
              x = 0.5
       # This creates weighting points at 0.25, 0.5, and 0.75
       # For a multiplier of 4,
       # val  ->  R    G    B
       # 0.0 -> (0.0, 1.0, 1.0)
       # 0.1 -> (0.0, 0.6, 1.0)
       # 0.2 -> (0.0, 0.2, 1.0)
       # 0.3 -> (0.2, 0.0, 1.0)
       # 0.4 -> (0.6, 0.0, 1.0)
       # 0.5 -> (1.0, 0.0, 1.0)
       # 0.6 -> (1.0, 0.0, 0.6)
       # 0.7 -> (1.0, 0.0, 0.2)
       # 0.8 -> (1.0, 0.2, 0.0)
       # 0.9 -> (1.0, 0.6, 0.0)
       # 1.0 -> (1.0, 1.0, 0.0)

       red  = min((max((4*(x-0.25), 0.)), 1.))
       green= min((max((4*math.fabs(x-0.5)-1., 0.)), 1.))
       blue = min((max((4*(0.75-x), 0.)), 1.))
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
       return (int(red*255), int(green*255), int(blue*255))

def htmlRgb(mag, cmin, cmax):
       """
       Return a tuple of strings to be used in HTML documents.
       """
       return "#%02x%02x%02x"%rgb(mag, cmin, cmax)
 
def colorbar(cmin,cmax):
  """
  Create a color bar using the RGB mapping of this module
  """
  E_level_axes = py.gca()
  cbar_axes,cbar_kw = matplotlib.colorbar.make_axes(E_level_axes)
  cbar_axes.set_ylim(cmin,cmax)
  colorwedge = []
  crange = 50
  for j in range(crange):
    y = cmin + (j/float(crange))*(cmax-cmin)
    color = floatRgb(y,cmin,cmax)
    colorline = []
    for i in range(10):
      colorline.append(color)
    colorwedge.append(colorline)
  wedge_image = py.array(colorwedge,float)
  A = 30./(cmax-cmin)
  logger.debug("colorbar: aspect=%f", A)
  py.imshow(wedge_image, origin='lower', extent=(-1.,1.,cmin,cmax),aspect=A)
  cbar_axes.xaxis.set_major_locator(py.NullLocator())
  cbar_axes.yaxis.tick_right()
