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