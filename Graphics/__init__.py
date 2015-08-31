"""
Various routines to support matplotlib graphics
"""

import pylab as py
from numpy import empty, log10, conj
from numpy.fft import fft, fftshift
import math as m
import logging

module_logger = logging.getLogger(__name__)

def ticks(axis, axis_limits, new_limits, tick_range, label_format):
    """
    Label an axis with different units from the data
    
    This puts value labels on a linear axis in units which are
    different from the data units. Given an axis (X or Y) with data
    limits given by axis_limits (a min, max tuple), assign the axis
    a new range given by new_limits (a min, max tuple) and place
    ticks on the range tick_range (min, max, step tuple) with the
    specified format.

    @param axis : one of "xXyY"
    @type  axis : str

    @param axis_limits : data values at the ends of the axis
    @type  axis_limits : tuple (float, float)

    @param new_limits : values at axis ends for label values
    @type  new_limits : tuple (float, float)

    @param tick_range : min, max and step values for tick locations
    @type  tick_range : tuple (float, float, float)

    @param label_format : format string for a single value
    @type  label_format : str
    """
    axis_min,axis_max = float(axis_limits[0]),float(axis_limits[1])
    min_value,max_value = float(new_limits[0]),float(new_limits[1])
    min_tick,max_tick,step = float(tick_range[0]),float(tick_range[1]), \
                                float(tick_range[2])
    
    axis_range = axis_max - axis_min
    value_range = max_value - min_value
    tick_labels = []
    tick_locations = []
    for t in py.arange(min_tick,max_tick+step,step):
        label = label_format % t
        location = (t-min_value)*(axis_max - axis_min)/value_range + \
                   axis_min
        tick_labels.append(label)
        tick_locations.append(location)
    if axis.upper() == "X":
        py.xticks(tick_locations,tick_labels)
    elif axis.upper() == "Y":
        py.yticks(tick_locations,tick_labels)

def auto_ticks(vmin,vmax):
    """
    Optional over-ride for matplotlib tick placement.
    
    Given the values at the ends of a linear axis, this figures out good
    places to put the ticks as a (first, last, step) tuple. If vmin > vmax,
    the tuple will be (last, first, -step).
    """
    vrange = float(vmax)-float(vmin)
    appr_vstep = abs(vrange/4.)
    module_logger.debug("vrange = %e, approx_step = %e",vrange, appr_vstep)
    vstep_order_of_magnitude = int(m.log10(appr_vstep))
    vstep_mantissa = appr_vstep*m.pow(10,-vstep_order_of_magnitude)
    if vstep_order_of_magnitude < 0:
        vstep_order_of_magnitude -= 1
        vstep_mantissa *= 10
    module_logger.debug("mantissa = %e, exponent = %e",
        vstep_mantissa,vstep_order_of_magnitude)
    if vstep_mantissa < 1.5:
        vstep_mantissa = 1.0
    elif vstep_mantissa < 3.0:
        vstep_mantissa = 2.0
    elif vstep_mantissa < 8.0:
        vstep_mantissa = 5.0
    else:
        vstep_mantissa = 10.0
    vstep = vstep_mantissa*m.pow(10.,vstep_order_of_magnitude)
    module_logger.debug("vstep = %e",vstep)
    i_start = int(vmin/vstep)
    i_stop = int(vmax/vstep)
    if i_stop > i_start:
        if i_start*vstep < vmin:
            i_start = i_start+1
        if i_stop*vstep > vmax:
            i_stop = i_stop-1
        return i_start*vstep, i_stop*vstep, vstep
    else:
        if i_stop*vstep < vmax:
            i_stop = i_stop+1
        return i_start*vstep, i_stop*vstep, -vstep

def X_axis_label_format(format):
  """
  Define the X-axis label format
  """
  this_axes = py.gca()
  this_figure = py.gcf()
  this_image = py.gci()
  # Set a tick on every integer that is multiple of base in the view interval
  # which is 1 in this case
  majorLocator = py.MultipleLocator (1)
  majorFormatter = py.FormatStrFormatter(format)
  this_axes.xaxis.set_major_locator (majorLocator)
  this_axes.xaxis.set_major_formatter(majorFormatter)

def twiny(ax=None):
    """
    Make a second axes overlay ax (or the current axes if ax is None)
    sharing the xaxis.  The ticks for ax2 will be placed on the right,
    and the ax2 instance is returned.  See examples/two_scales.py
    """
    if ax is None:
        ax=py.gca()
    ax2 = py.gcf().add_axes(ax.get_position(), sharey=ax, frameon=False)
    ax2.xaxis.tick_top()
    ax2.xaxis.set_label_position('top')
    ax.xaxis.tick_bottom()
    py.draw_if_interactive()
    return ax2

def make_spectrogram(data, num_spec, num_bins, log=False,
                     normalizer=None):
  """
  Converts a sequence of complex samples into a spectrogram

  matplotlib specgram takes real data.  This takes complex data.

  @param data : complex time series data
  @type  data : numpy array of complex

  @param num_spec : number of spectra along the time axis
  @type  num_spec : int

  @param num_bins : number of spectral bins along the frequency axis
  @type  num_bins : int

  @param log : flag to plot logarithm of the power
  @type  log : bool

  @param normalizer : gain normalization reference for spectra
  @type  normalizer : numpy 1D array num_bins long

  @return: 2D numpay array
  """
  subsetlen = num_spec*num_bins
  image = empty((num_spec, num_bins))
  for index in range(0, subsetlen, num_bins):
    dataslice = data[index:index+num_bins]
    xform = fft(dataslice)
    spectrum = fftshift(xform)
    if normalizer == None:
      pass
    else:
      spectrum *= normalizer
    ptr = index/num_bins
    if log:
      image[ptr] = log10(abs(spectrum*conj(spectrum)))
    else:
      image[ptr] = abs(spectrum*conj(spectrum))
  return image
