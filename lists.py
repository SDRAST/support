
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