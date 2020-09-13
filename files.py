"""
file access support
"""

def backup_one_line(fd):
  """
  Moves the file pointer to right after the previous newline in an ASCII file

  @param fd :
  @type  fd : file descriptor
  
  Notes
  =====
  It ignores the current character in case it is a newline.
  """
  index = -2
  c = ""
  while c != "\n":
    fd.seek(index,2)
    c = fd.read(1)
    index -= 1

def get_last_line(fd):
  """
  Gets the last line in an ASCII file.
  
  This is useful for getting the last line in a very large ASCII file.
  It also reports of the last line was completed with a newline or interrupted.

  @param fd :
  @type  fd : file descriptor
  """
  fd.seek(-1,2)
  clast = fd.read(1)
  if clast == "\n":
    complete_line = True
  else:
    complete_line = False
  backup_one_line(fd)
  line = fd.readline()
  return (complete_line, line)

