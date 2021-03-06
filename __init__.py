"""
Package to provide support for various objects and modules

This module contains functions that don't have an obvious home in a
submodule.
"""
import datetime
import logging
import os
import sys

from numpy import array
from os import environ, makedirs
from os.path import exists
from time import sleep, time

from numpy import array

logger = logging.getLogger(__name__)

__version__ = "1.2.0"

def python_version():
    return sys.version.split()[0]

######################### Classes with extra features #####################

class NamedClass(object):
    """
    A base class enhanced with methods for reporting self.
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.base() + ' "' + str(self.name) + '"'

    def __repr__(self):
        return self.base() + ' "' + str(self.name) + '"'

    def base(self):
        """
        String representing the class instance type
        """
        return str(type(self)).split()[-1].strip('>').strip("'").split('.')[-1]


class PropertiedClass(NamedClass):
    """
    A subclass of MCobject enhanced with properties.
    """

    def __init__(self):
        self.data = {}

    def __setitem__(self, key, item):
        self.data[key] = item

    def __getitem__(self, key):
        return self.data[key]

    def keys(self):
        return self.data.keys()

    def has_key(self, key):
        if self.data.has_key(key):
            return True
        else:
            return False

########################## functions for numpy arrays ########################

def nearest_index(np_array, value):
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
        index = abs(data_array - ref_value).argmin()
    else:
        index = abs(np_array - value).argmin()
    # value is beyond the ends of the array
    # this test assumes the data are monotonic, then result is unknown
    if (((np_array[0] < np_array[-1]) and
             (value < np_array[0] or value > np_array[-1])) or
            ((np_array[0] > np_array[-1]) and
                 (value > np_array[0] or value < np_array[-1]))):
        return -1
    else:
        return index
  
def trim_extremes(data):
  """
  Remove extreme values from a data array.

  Extreme values are those greater than 10x the standard deviation
  and are 'skinny'.: numpy array

  @param data : numpy array
  """
  data_array = array(data)
  amean   = mean(data_array)
  avar    = var(data_array)
  astdev  = sqrt(avar)
  amax = data_array.max()
  amin = data_array.min()
  # Check the maximum
  if abs(amax-amean) > 10*astdev:
    index = argmax(data_array)
    if is_skinny(data_array,index):
      data_array = clobber(data_array,index)
  # check the minimum
  if abs(amin-amean) > 10*astdev:
    index = argmin(data_array)
    if is_skinny(data_array,index):
      data_array = clobber(data_array,index)
  return data_array

def is_skinny(data_array,index):
  """
  Test whether a data value is an isolated outlier

  Returns True if the data values adjacent to the test value are
  less that 1/10 of the test value, i.e., the data point is a spike

  @param data_array : numpy array

  @param index : int

  @return: boolean
  """
  amean   = mean(data_array)
  test_value = abs(data_array[index]-amean)
  if index == 0:
    ref_value = abs(data_array[index+1] - amean)
  elif index == len(data_array)-1:
    ref_value = abs(data_array[index-1] - amean)
  else:
    ref_value = (data_array[index-1] + data_array[index+1])/2. - amean
  if test_value > 10 * ref_value:
    return True
  else:
    return False

def clobber(data_array,index):
  """
  Replace a data array value with the adjacent value(s)

  @param data_array : numpy array

  @param index : int
  """
  if index == 0:
    data_array[index] = data_array[index+1]
  elif index == len(data_array)-1:
    data_array[index] = data_array[index-1]
  else:
    data_array[index] = (data_array[index-1] + data_array[index+1])/2.
  return data_array

########################## Users and Permissions ############################

def get_user():
  """
  Returns the user running this session

  This will return the username of the logged-in user.  If the user is logged
  in as 'root' (or by doing 'su'), then there is no way to find out who the
  actual user is.
  """
  try:
    test = os.environ['USER']
    # there is a USER
    logger.debug("get_user: USER = %s", test)
  except KeyError:
    # probably was run by a cron job
    logger.debug("get_user: no USER; trying LOGNAME")
    try:
      test = os.environ['LOGNAME']
    except KeyError:
      logger.error("get_user: no USER or LOGNAME")
      logger.debug("get_user: environment is %s", os.environ)
      return None
  if test == "root":
    try:
      # maybe the user was using 'sudo'
      logger.debug("get_user: user is %s; trying SUDO_USER", test)
      user = os.environ['SUDO_USER']
    except KeyError:
      # no, this is really by 'root'
      logger.debug("get_user: SUDO_USER not set")
      user = "root"
  else:
    user = test
    logger.debug("get_user: settled on %s", user)
  return user

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
      logger.error("You must be in group '%s', root or 'sudo'er", group)
      return False
  logger.info(" User permissions verified")

def sync_second():
    """
    Wait until the second changes

    This returns roughly 6.2 ms after the second changes. I can't seem to get the
    delay below this.

    Using 'sleep' rather than 'pass' requires less CPU cycles.
    """
    now = int(time())
    while not bool(int(time()) - now):
        sleep(0.0001)

def cpu_arch():
    """
    """
    p = invoke('uname -a')
    text = p.stdout.readline()
    return text.split()[-2]

def mkdir_if_needed(path):
    """
    python3 only
    """
    if exists(path) == False:
        logger.warning(" Creating %s", path)
        makedirs(path, mode=0o775)
