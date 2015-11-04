# -*- coding: utf-8 -*-
"""
module svn_support

Some utility functions to help when there are many sandboxes scattered
all over the disk.
"""

import os
import re

def make_filename(parts_list):
  """
  Assemble items in a list into a full path
  
  Creates a full path file name from a list of parts such as might
  have been created by full_path.split('/')

  @param parts_list : list of str

  @return: str
  """
  name = ''
  for part in parts_list:
    name += '/'+part
  return name

def get_svn_dirs():
  """
  Finds all the sub-directories on the system which are svn sandboxes.

  @return: list of str
  """
  response = os.popen('locate \.svn/entries | grep -v Trash','r').readlines()
  prev_dir = ''
  first_pass = True
  svn_dirs = []
  for line in response:
    filename = line.strip()
    file_parts = filename.split('/')
    for svn_dir in range(3,7):
      if svn_dir < len(file_parts):
        if file_parts[svn_dir] == '.svn':
          this_dir = make_filename(file_parts[1:svn_dir])
          if re.match(prev_dir,this_dir):
            if (len(this_dir) > len(prev_dir)):
              if (this_dir[len(prev_dir)] == '/'):
                if first_pass:
                  prev_dir = this_dir
                  svn_dirs.append( this_dir )
                  first_pass = False
              else:
                svn_dirs.append( this_dir)
                prev_dir = this_dir
          else:
            svn_dirs.append( this_dir)
            prev_dir = this_dir
  return svn_dirs

def add_new_files():
  """
  Finds new files in the current directory as does 'svn add' for them.

  This prints (to stdout) the status returned from each 'svn add'.

  @return: True if new files found
  """
  response = os.popen('svn status','r').readlines()
  found = False
  for line in response:
    stat,filename = line.strip().split()
    if stat == '?':
      exit_stat = os.system("svn add "+filename)
      print "Adding",filename,"exit status =",exit_stat
      found = True
  return found
  
def report_status():
  """
  Does 'svn status' for all the sandboxes.

  Prints the status report, if there is any, for each sandbox,

  @return: None
  """
  svn_dirs = get_svn_dirs()
  for subdir in svn_dirs:
    fd_out = os.popen('svn status '+subdir,'r')
    status = fd_out.readlines()
    fd_out.close()
    if len(status) != 0:
      print subdir
      for f in status:
        print f.strip()

