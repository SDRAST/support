# -*- coding: utf-8 -*-
"""
module mixin - mixes classes to augment an existing class or creat a new one

http://c2.com/cgi/wiki?MixinsForPython
"""
def mixIn (base, addition):
  """
  Mixes in place, i.e. the base class is modified.
  Tags the class with a list of names of mixed members.

  @param base : the base class
  @param addition : additional classes
  """
  assert not hasattr(base, '_mixed_')
  mixed = []
  for item, val in addition.__dict__.items():
    if not hasattr(base, item):
      setattr(base, item, val)
      mixed.append (item)
  # the base class remembers what is mixed in
  base._mixed_ = mixed

def unMix (cla):
  """
  Undoes the effect of a mixin on a class. Removes all attributes that
  were mixed in -- so even if they have been redefined, they will be
  removed.

  _mixed_ must exist, or there was no mixin

  @param cla : class with mixed-in attributes
  """
  try:
    cla._mixed_
  except:
    return
  for m in cla._mixed_:
    delattr(cla, m)
  del cla._mixed_

def mixedIn (base, addition):
  """
  Same as mixIn, but returns a new class instead of modifying
  the base.

  @param base : the base class
  @param addition : additional classes
  @return: new class
  """
  class newClass:
    pass
  newClass.__dict__ = base.__dict__.copy()
  mixIn (newClass, addition)
  return newClass

if __name__ == "__main__":
  class addSubMixin:
    def add(self, value):
      self.number += value
      return self.number

    def subtract(self, value):
      self.number -= value
      return self.number

  class myClass:
    def __init__(self, number):
  	  self.number = number

  mixIn(myClass, addSubMixin)
  myInstance = myClass(4)
  print(myInstance.add(2))       # prints "6"
  print(myInstance.subtract(2))  # prints "2"

