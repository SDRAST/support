"""
Package to provide support for various objects and modules

This module contains functions that don't have an obvious home in a
submodule.
"""
from numpy import array
from os import environ
from time import time

import logging
module_logger = logging.getLogger(__name__)

from lists import *
from support.process import invoke

def nearest_index(np_array,value):
  """
  Return the index of the element of the array with the nearest value

  Note
  ====
  This has a problem with arrays of datetime.datetime() objects.

  @param np_array : an array of value
  @type  np_array : numpy array

  @param value : a single value
  @type  value : the same type as values in np_array

  @return: index of item in np_array closest to value
  """
  # Convert to to numpy array if necessary
  if type(np_array) == list or type(np_array) == tuple:
    np_array = array(np_array)
  # find the index of the array value nearest the test value
  if type(value) == datetime.datetime:
    data_array = date2num(np_array)
    ref_value = date2num(value)
    index = abs(data_array-ref_value).argmin()
  else:
    index = abs(np_array-value).argmin()
  # discard points beyond the ends of the array
  if value < np_array[0] or value > np_array[-1]:
    return -1
  else:
    return index

def check_permission(group):
  """
  Verify that the user has the necessary permissions.

  Permissions can be gained by being superuser, using 'sudo' or by belonging to
  the right group.

  Example::
    check_permission('dialout')
  """
  p = invoke("groups") # What groups does the user belong to?
  groups = p.stdout.readline().split()
  try:
    groups.index(group)
    return True
  except ValueError:
    if environ['USER'] != 'root':
      module_logger.error("You must be in group '%s', root or 'sudo'er", group)
      return False
  module_logger.info(" User permissions verified")

def sync_second():
  """
  Wait until the second changes

  This returns roughly 6.2 ms after the second changes. I can't seem to get the
  delay below this.

  There are various ways to do this but this seems to give the least spread.
  """
  now = int(time())
  while not bool(int(time())-now):
    pass
