# -*- coding: utf-8 -*-
"""
text - functions for handling text
"""
import logging
import os
import re
import smtplib
import socket

from email.mime.text import MIMEText
from os.path import basename, isdir, isfile, splitext
from glob import glob

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

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def distance(a,b):
    """
    Calculates the Levenshtein distance between a and b.
    
    References
    ==========
    http://en.wikisource.org/wiki/Levenshtein_distance#Python
    """
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    current = list(range(n+1))
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
  response = input(prompt+' ['+str(default)+']: ')
  if response == '':
    response = default
  return response

def select_files(pattern, text="Select file(s) by number"
                               " separated with spaces: ",
                 ftype=None, single=False):
  """
  Select files by glob pattern

  Present the user with a numbered list of files based on a glob
  pattern.  The user selects the files by number, separated by spaces
  if more than one, and returns a list with the selected files.
  If only one file is selected, then just that name is returned.
  """
  logger.debug("select_files: looking for %s (type %s)", pattern, ftype)
  files = glob(pattern)
  files.sort()
  num_files = len(files)
  if num_files == 1:
    if (ftype == "file" and isfile(files[0])) or \
       (ftype == "dir" and isdir(files[0])):
      return [files[0]]
    else:
      return []
  elif num_files > 1:
    index = 0
    for f in files:
      if (ftype == "file" and isfile(f)) or (ftype == "dir" and isdir(f)) or \
        (ftype == None):
        print(index,'>',basename(files[index]))
        index += 1
      else:
        files.remove(f)
        continue
    if files == []:
      return files
    selections = input(text)
    if not selections.isspace():
      indices = selections.split()
      selected = []
      for index in indices:
        try:
          selected.append(files[int(index)])
        except IndexError as details:
          logger.error("select_files: %s is not a valid index", index)
          raise IndexError
      logger.debug("select_files: %s has %d items(s)", selected,
                   len(selected))
      if len(selected) == 1:
        return selected[0]
      else:
        if single:
          raise AssertionError("You can select only one file.")
        else:
          return selected
    else:
      return []
  else:
    return []

def get_version(fileroot, filetype):
  """
  Append an updated version number to a file
  
  Gets the version number from a filename of the form FILEROOTVO1.EXT
  
  @param fileroot : glob-style first part of file name
  @param filetype : filename extent
  """
  files = glob(fileroot+"*"+filetype)
  logger.debug("get_version: files found: %s", files)
  if files:
    files.sort()
    version = int(splitext(files[-1])[0][-2:])
    version += 1
  else:
    version = 0
  return version

def remove_html_tags(data):
  """
  remove HTML tags from text

  References
  ==========
  http://love-python.blogspot.com/2008/07/strip-html-tags-using-python.html
  """
  p = re.compile(r'<.*?>')
  return p.sub('', data)

def remove_extra_spaces(data):
  """
  reduce multiple whitespaces to one

  References
  ==========
  http://love-python.blogspot.com/2008/07/strip-html-tags-using-python.html
  """
  p = re.compile(r'\s+')
  return p.sub(' ', data)

def make_title(text):
  """
  turn a text string of words into a title by capitalizing each word
  """
  words = text.split()
  new_words = []
  for word in words:
    new_words.append(word[0].upper()+word[1:])
  return ' '.join(new_words)
  
def longest_text(textlist):
  """
  Find the length of the longest string in a list
  """
  maxlen = 0
  for text in textlist:
    maxlen = max(maxlen,len(text))
  return maxlen

def clean_TeX(string):
  """
  Remove or replace math mode symbols like underscore
  """
  return string.replace("_"," ")

def send_email(msg_text, to, Subject="no subject",
               From="anonymous", Bc=[], Cc=[], mimetype='html'):
  """
  Send an e-mail message
  
  Because Microsoft does not handle MIME=text well (if at all), messages
  should generally be in HTML
  """
  if mimetype == 'text':
    msg = MIMEText(msg_text, 'text')
  else:
    msg = MIMEText(msg_text, 'html')
  msg['Subject'] = Subject
  msg['From'] = From
  # message header addresses must be comma separated text
  # but the second argument to 'sendmail' must be a list
  if type(to) == str:
    to = [to]
  msg['To'] = ",".join(to)
  if type(Cc) == str:
    cc = [Cc]
  else:
    cc = Cc
  msg['Cc'] = ",".join(cc)
  if type(Bc) == str:
    bc = [Bc]
  else:
    bc = Bc
  msg['Bc'] = ",".join(bc)
  if socket.gethostname() == "crab14":
    s = smtplib.SMTP('localhost')
  else:
    s = smtplib.SMTP('smtp.jpl.nasa.gov')
  addressees = to+bc+cc
  logger.debug("send_email: sending to %s", addressees)
  s.sendmail(From, addressees, msg.as_string())
  s.quit()
