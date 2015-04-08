# -*- coding: utf-8 -*-
"""
process - support for executing shell commands
"""
import re
import shlex
from subprocess import PIPE, Popen
import logging

module_logger = logging.getLogger(__name__)

def invoke(command):
  """
  Convenient alternate for a command without stdin.

  For a shell command line input that requires no additional data.
  Returns an open process whose stdout and stderr can be read::
    In [6]: import process_tools
    In [7]: p = support.process.invoke("ls")
    In [8]: p.stdout.readlines()
    Out[8]: ['client.log\n', 'manager.log\n', 'manager.py\n',
             'manager.py~\n', 'MMS.log\n']

  @param command : command to be executed by the OS
  @type  command : list or str

  @return: Popen() instance
  """
  module_logger.debug("invoke: argument %s is %s",command,type(command))
  if type(command) == str:
    args = shlex.split(command)
  else:
    args = command
  module_logger.debug("invoke: argument list is %s",str(args))
  try:
    p = Popen(args, shell=False, stdout=PIPE, stderr=PIPE)
  except OSError, details:
    raise
  except ValueError, details:
    raise
  except Exception, details:
    raise
  else:
    return p

def search_response(command_list1,command_list2):
  """
  Search a local command response.

  command_list2 is usually some form of 'grep'

  Example::
    In [14]: process_tools.search_response(["ps", "-ef"],["grep", "python"])
    Out[14]:
      ['kuiper    3696  3669  0 09:57 pts/1    00:00:00 /usr/bin/python \
                                                        /usr/bin/ipython\n',
       'kuiper    3785  3696  0 10:17 pts/1    00:00:00 grep python\n']

  @param command_list1 : the command which generates the initial output
  @type  command_list1 : list of str

  @param command_list2 : the command which searches the output
  @type  command_list2 : list of str

  @return: line(s) with the match
  """
  p1 = Popen(command_list1, stdout=PIPE)
  p2 = Popen(command_list2, stdin=p1.stdout, stdout=PIPE)
  waiting = True
  while waiting:
    try:
      output = p2.stdout.readlines()
      waiting = False
    except IOError:
      # probably an interrupted system call.  Try again
      continue
  return output

def is_running(task):
  """
  """
  lines = search_response(["ps", "-ef"],["grep", task])
  found = False
  for line in lines:
    if re.search("grep",line):
      pass
    elif re.search(task,line):
      found = True
      break
    else:
      continue
  return found
