"""
Methods to support lists
"""

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


def list_dictionary(dictionary):
   """
   List a dictionary, one line for each item, with the keys sorted
   """
   report = ""
   dck = dictionary.keys()
   dck.sort()
   report += str(len(dictionary))+' items\n'
   for key in dck:
      report += str(key)+"\t"+str(dictionary[key])+'\n'
   return report
