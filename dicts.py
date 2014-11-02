"""
support for dict objects
"""

import logging

module_logger = logging.getLogger(__name__)

def flattenDict(dictionary, init = ()):
  """
  Converts nested dicts with numeric or str keys to flat dict with tuple keys.

  For example, x[1][0][2] becomes xx[(1, 0, 2)].

  Based on::
   http://stackoverflow.com/questions/6027558/\
   flatten-nested-python-dictionaries-compressing-keys
  """
  def _tuple(x):
    """
    Returns x as a tuple
    """
    return (x,)

  def flatten(d, _keyAccum = init):
    """
    """
    #module_logger.debug("flatten: entered with %s",d)
    if type(d) == dict:
      if d == {}:
        return {(0,): None}
      newdict = {}
      for key in d.keys():
        reduced = flatten(d[key], init+_tuple(key))
        if type(reduced) == dict:
          for k,v in reduced.items():
            newdict[_tuple(key)+k] = v
        else:
          newdict[_tuple(key)] = d[key]
      return newdict
    else:
      return d

  return flatten(dictionary)

def get_from_deep_dict(values,keys):
  """
  Extract values from a multi-depth dictionary

  Example::
    In [2]: get_from_deep_dict(mydict,(0,0,0))
    [(0, 0, 0)] yields a
    Out[2]: 'a'
    In [3]: get_from_deep_dict(mydict,(1,1,2))
    [(1, 1, 2)] yields k
    Out[3]: 'k'
    In [4]: get_from_deep_dict(mydict,(3,1,2))
    [(3, 1, 2)] yields z
    Out[4]: 'z'

  @param values : a dictionary of dictionaries of ...
  @type  values : dict of dict of ...

  @param keys: high to low ordered keys
  @type  keys: tuple
  """
  value = values
  for position in range(len(keys)):
    value = value[keys[position]]
  module_logger.debug("[%s] yields %s", keys,value)
  return value

def tuple_keys_to_str(dictionary):
  """
  Converts tuple keys to str keys
  """
  finaldict = {}
  for key in dictionary.keys():
    strkey = ()
    for item in key:
      if type(item) == int:
        strkey += (str(item),)
      else:
        strkey += (item,)
    newkey = '_'.join(strkey)
    finaldict[newkey]=dictionary[key]
  return finaldict

