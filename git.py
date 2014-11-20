"""
support.git - creates superdep.txt and subdep.txt files

subdep.txt lists repositories below the current repository in the filesystem.

superdep.txt lists repositories above the current one to the top of tree.

TO DO::
* Handle the case of multiple remotes.  Use only 'jpl' and 'jplra'.
* Take care of the intermediate repositories
* Look at the imports in __init__.py to see what other repos are needed
"""
examples = """  """

import sys
import os
import logging
import git
import re

from support.logs import init_logging, get_loglevel

module_logger = logging.getLogger(__name__)

def find_sub_repos(path = os.getcwd(), fileobj = None):
  """
  Find the repo trunk(s) in the specified directory

  @param path : optional path to start point, default "."
  @type  path : str

  @param fileobj : the "subdep.txt" file, if it exists
  @type  fileobj : file object
  """
  thisdir = os.getcwd()
  if fileobj:
    file_creator = False
    module_logger.debug("\nfind_sub_repos: path=%s, file=%s", path, fileobj.name)
  else:
    module_logger.debug("\nfind_sub_repos: path=%s", path)
  is_repo = check_repo(os.path.abspath(path))
  subdirs = os.walk(path).next()[1]
  if is_repo:
    module_logger.info("find_sub_repos: %s is a repo", path)
    if fileobj == None:
      file_creator = True
    fileobj = make_subdep_entry(os.path.abspath(path), subdirs, fileobj=fileobj)
  for subdir in subdirs:
    fullpath = path+'/'+subdir
    if subdir[0] != ".":
      fileobj = find_sub_repos(fullpath, fileobj)
  if is_repo:
    module_logger.debug("find_sub_repos: %s completed", path)
    try:
      module_logger.debug("find_sub_repos: file creator is %s", file_creator)
      if file_creator:
        module_logger.info("find_sub_repos: finished with %s", fileobj.name)
        fileobj.close()
        fileobj = None
    except:
      module_logger.debug("find_sub_repos: %s has no file creator defined.",path)
  os.chdir(thisdir)
  return fileobj

def check_repo(path):
  """
  Convenience so this test hast to be done only once
  """
  module_logger.debug("check_repo: path = %s", path)
  if os.path.exists(path+"/.git"):
    return True
  else:
    return False

def make_subdep_entry(path, subdirs, fileobj=None):
  """
  """
  global top_repos
  if fileobj:
    module_logger.debug("make_subdep_entry: path=%s, subdirs=%s, file=%s",
                   path, subdirs, fileobj.name)
  else:
    module_logger.debug("make_subdep_entry: path=%s, subdirs=%s",
                   path, subdirs)
  if fileobj == None:
    fileobj = open(path+"/subdep.txt","w")
    top_repos.append(path)
    module_logger.info("make_subdep_entry: created %s", fileobj.name)
  else:
    #make text entry in subdep.txt
    remotes = git.Repo(path).remotes
    name = remotes[0].name
    url = remotes[0].url
    fileobj.write(os.path.realpath(path)+" "+name+" "+url+'\n')
    module_logger.info("make_subdep_entry: wrote remote %s", name)
  return fileobj

def make_superdeps(top_repos):
  for repo in top_repos:
    fd = open(repo+"/subdep.txt","r")
    deps = fd.readlines()
    fd.close()
    remotes = git.Repo(repo).remotes
    name = remotes[0].name
    url = remotes[0].url
    for line in deps:
      subdir = line.strip().split()[0]
      fd = open(subdir+"/superdep.txt","w")
      fd.write(repo+" "+name+" "+url+'\n')
      fd.close()
      module_logger.info("Wrote %s/superdep.txt", subdir)

def install_dependencies():
  """
  """
  for direction in ["sub","super"]:
    filename = direction+"dep.txt"
  try:
    fd = open(filename,"r")
  except IOError, details:
    module_logger.warning(" IOError, "+str(details))
  deps = fd.readlines()
  fd.close()
  for line in deps:
    fullpath, remote, url = line.strip().split()
    path = os.path.dirname(fullpath)
    subdir = os.path.basename(fullpath)
    # make sure the destination exists
    if os.path.exists(subdir) == False:      
      print "sudo mkdir -p",subdir
    print "cd",path
    print "git clone --jplra=jpl", url, subdir

def get_git_dirs():
  """
  Finds all the sub-directories on the system which are git sandboxes.

  This has a problem finding sub-repos.

  @return: list of str
  """
  response = os.popen('locate \.git | grep -v Trash | grep -v \.svn','r').readlines()
  prev_dir = ''
  first_pass = True
  git_dirs = []
  for line in response:
    filename = line.strip()
    file_parts = filename.split('/')
    # Look for .git in positions 3-10 of the path
    for git_dir in range(3,11):
      if git_dir < len(file_parts):
        if file_parts[git_dir] == '.git':
          this_dir = make_filename(file_parts[1:git_dir])
          if re.match(prev_dir,this_dir):
            # prev_dir is contained in this_dir
            if (len(this_dir) > len(prev_dir)):
              # but there are extra cahracters
              if (this_dir[len(prev_dir)] == '/'):
                # this_dir is a directory
                if first_pass:
                  # remember this_dir as the next prev_dir
                  prev_dir = this_dir
                  # and add to the list of git dirs
                  git_dirs.append( this_dir )
                  first_pass = False
              else:
                git_dirs.append( this_dir)
                prev_dir = this_dir
          else:
            git_dirs.append( this_dir)
            prev_dir = this_dir
  return git_dirs
  
#------------------------ under development ------------------------------------

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

def add_new_files():
  """
  Finds new files in the current directory as does 'git add' for them.

  This prints (to stdout) the status returned from each 'git add'.

  @return: True if new files found
  """
  response = os.popen('git status','r').readlines()
  found = False
  for line in response:
    stat,filename = line.strip().split()
    if stat == '?':
      exit_stat = os.system("git add "+filename)
      print "Adding",filename,"exit status =",exit_stat
      found = True
  return found

def report_status():
  """
  Does 'git status' for all the sandboxes.

  Prints the status report, if there is any, for each sandbox,

  @return: None
  """
  git_dirs = get_git_dirs()
  for git_dir in git_dirs:
    module_logger.debug("Processing %s", git_dir)
    fd_out = os.popen('git status '+git_dir,'r')
    status = fd_out.readlines()
    fd_out.close()
    if len(status) != 0:
      print git_dir
      for f in status:
        print f.strip()

