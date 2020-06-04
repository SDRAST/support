"""
Methods to support lists
"""
import logging

logger = logging.getLogger(__name__)

def unique(hasDupes):
    """
    Removes duplicate elements from a list

    @param hasDupes : a list with duplicate items

    @return: list with duplicates removed
    """
    ul = list(set(hasDupes))
    ul.sort()
    return ul

def contains(List, value):
  """
  Reports whether 'value' is in 'List'
  """
  try:
    List.index(value)
  except ValueError:
    return False
  else:
    return True

def flatten(List):
  """
  Make a list of nested lists a simple list
  
  Doesn't seem to work or else I don't recall what it should do.
  """
  if type(List[0]) == list:
    newlist = sum(List, [])
  else:
    newlist = List
  return newlist

def remove_item(thislist, item):
  """
  Remove item from list without complaining if absent

  @param thislist : list of items
  @param item : item which may or may not be in the list

  @return: reduced list
  """
  try:
    thislist.remove(item)
  except ValueError:
    pass
  return thislist

def rotate(List, first_value, direction="l", last_value=None, other_lists=[]):
  """
  Rotate one or more lists subject to constraints on the first list
  
  'last_value' is useful if there are multiple instances of 'first_value'. This
  is dangerous because a list might not have a last value equal to 'last_value'
  when the first value is 'first_value'.
  
  The lists in 'other_lists' must have the same length as List.
  
  Examples::
  
    In [2]: l = [1, 3, 2, 8, 6, 0, 7, 5, 4]
    In [3]: rotate(l,"l",8)
    Out[3]: [8, 6, 0, 7, 5, 4, 1, 3, 2]
    In [4]: rotate(l,"r",1)
    Out[4]: [1, 3, 2, 8, 6, 0, 7, 5, 4]

    In [5]: l = [1,1,0,0,0,2,2,2,1]
    In [6]: rotate(l,'l',0,1)
    Out[6]: [0, 0, 0, 2, 2, 2, 1, 1, 1]
    In [7]: rotate(l,'r',1,2)
    Out[7]: [1, 1, 1, 0, 0, 0, 2, 2, 2]

    In [8]: l = [1, 3, 2, 8, 6, 0, 7, 5, 4]
    In [9]: ll = ['a','b','c','d','e','f','g','h','i']
    In [10]: rotate(l, 8, 'l', other_lists=[ll])
    Out[10]: [[8, 6, 0, 7, 5, 4, 1, 3, 2],
              ['d', 'e', 'f', 'g', 'h', 'i', 'a', 'b', 'c']]
              
  @param List : list to rotate and test for constraint compliance
  @type  List : list of any type
  
  @param first_value : value which must be first in the new list
  @type  first_value : same type as entries of List
  
  @param direction : left or right
  @type  direction : str
  
  @param last_value : value which must be last if 'first_value' is satisfied
  @type  last_value : same type as entries of List
  
  @param other_lists :
  """
  def shift(List, direction):
    if direction.upper()[0] == 'L':
      newlist = List[1:]+[List[0]] # left shift
    else:
      newlist = [List[-1]]+List[:-1]
    return newlist
  
  nshifts = 0
  while List[0] != first_value or (last_value and List[-1] != last_value):
    List = shift(List, direction)
    if other_lists:
      newlists = []
      for L in other_lists:
        L = shift(L, direction)
        newlists.append(L)
      other_lists = newlists
    nshifts += 1
    if nshifts == len(List):
      logger.error("rotate: fully rotated; endless loop detected")
      break
  if other_lists:
    return [List]+other_lists
  else:
    return List
        
      
def list_dictionary(dictionary):
   """
   Print a dictionary, one line for each item, with the keys sorted
   
   Examples::
   
     In [2]: print list_dictionary({'a':1, 'b':2, 'cc':{'x':8, 'y':9}})
     3 items
     a	1
     b	2
     cc	{'y': 9, 'x': 8}
     In [3]: list_dictionary({'a':1, 'b':2, 'cc':{'x':8, 'y':9}})
     Out[3]: "3 items\\na\\t1\\nb\\t2\\ncc\\t{'y': 9, 'x': 8}\\n"


   """
   report = ""
   dck = dictionary.keys()
   dck.sort()
   report += str(len(dictionary))+' items\n'
   for key in dck:
      report += str(key)+"\t"+str(dictionary[key])+'\n'
   return report
