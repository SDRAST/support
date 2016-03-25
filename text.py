# -*- coding: utf-8 -*-
"""
text - functions for text processing
"""

from glob import glob
from os.path import basename
import re

NUL = "\x00"
SOH = "\x01"
STX = "\x02"
ETX = "\x03"
EOT = "\x04"
ENQ = "\x05"
ACK = "\x06"
BEL = "\a"
BS  = "\b"
HT  = "\t"
LF  = "\n"
VT  = "\v"
FF  = "\f"
CR  = "\r"
SO  = "\0e"
SI  = "\0f"
DLE = "\10"
ESC = "\1b"


def distance(a,b):
    """
    Calculates the Levenshtein distance between a and b.
    
    Reference
    =========
    http://en.wikisource.org/wiki/Levenshtein_distance#Python
    """
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*m
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]

def nocase_distance(aa,bb):
   """
   same as distance() but ignores case
   """
   a = aa.upper()
   b = bb.upper()
   return distance(a,b)

def user_input(prompt,default):
  """
  Like 'raw_input' except that a default value can be specified.
  """
  response = raw_input(prompt+' ['+str(default)+']: ')
  if response == '':
    response = default
  return response

def select_files(pattern,text="Select file(s) by number"
                              " separated with spaces: ",
                         single=False):
  """
  Select files by glob pattern

  Present the user with a numbered list of files based on a glob
  pattern.  The user selects the files by number, separated by spaces
  if more than one, and returns a list with the selected files.
  If only one file is selected, then just that name is returned.
  """
  files = glob(pattern)
  files.sort()
  num_files = len(files)
  if num_files == 1:
    return files[0]
  elif num_files > 1:
    for index in range(num_files):
      print index,'>',basename(files[index])
    selections = raw_input(text)
    if not selections.isspace():
      indices = selections.split()
      selected = []
      for index in indices:
        selected.append(files[int(index)])
      if len(selected) == 1:
        return selected[0]
      else:
        if single:
          raise AssertionError,"You can select only one file."
        else:
          return selected
    else:
      return []
  else:
    return []


def remove_html_tags(data):
  """
  remove HTML tags from text

  Reference
  =========
  http://love-python.blogspot.com/2008/07/strip-html-tags-using-python.html
  """
  p = re.compile(r'<.*?>')
  return p.sub('', data)

def remove_extra_spaces(data):
  """
  reduce multiple whitespaces to one

  Reference
  =========
  http://love-python.blogspot.com/2008/07/strip-html-tags-using-python.html
  """
  p = re.compile(r'\s+')
  return p.sub(' ', data)


def longest_text(textlist):
  """
  Find the length of the longest string in a list
  """
  maxlen = 0
  for text in textlist:
    maxlen = max(maxlen,len(text))
  return maxlen
