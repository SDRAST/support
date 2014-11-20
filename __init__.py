"""
Package to provide support for various objects and modules
"""
from numpy import array
from os import environ

import logging
module_logger = logging.getLogger(__name__)

from lists import *
from support.process import invoke

    
################################ IP support ###################################

def decode_IP(IP_address):
  """
  Returns a long int for an IPv4 or IPv6 address.

  @param IP_address :  like "192.168.1.101"
  @type  IP_address : str of decimal separated ints

  @return: int
  """
  parts = IP_address.split('.')
  if len(parts) == 4 or len(parts) == 6:
    ipvalue = 0
    for i in range(len(parts)):
      shift = 8*(len(parts)-1-i)
      ipvalue += int(parts[i]) << shift
    return ipvalue
  else:
    raise RuntimeError("Invalid IP address: %s" % IP_address)

def decode_MAC(MAC_address):
  """
  Returns a long int for a MAC address

  @param MAC_address : like "00:12:34:56:78:9a"
  @type  MAC_address : str of colon separated hexadecimal ints

  @return: long int
  """
  parts = MAC_address.split(':')
  if len(parts) == 6:
    value = 0
    for i in range(6):
      shift = 8*(5-i)
      value += int(parts[i],16) << shift
    return value
  else:
    raise RuntimeError("Invalid MAC address: %s" % MAC_address)

################################## Miscellaneous ################################3

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
