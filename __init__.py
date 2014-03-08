"""
Package to provide support for various objects and modules
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
