"""
support.git - creates superdep.txt and subdep.txt files

subdep.txt lists repositories below the current repository in the filesystem.

superdep.txt lists repositories above the current one to the top of tree.

TO DO::
* Handle the case of multiple remotes.  Use only 'jpl' and 'origin'.
* Take care of the intermediate repositories
* Look at the imports in __init__.py to see what other repos are needed
"""
examples = """  """

import sys
import os
import logging
import git

from support.logs import init_logging, get_loglevel

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
    mylogger.debug("\nfind_sub_repos: path=%s, file=%s", path, fileobj.name)
  else:
    mylogger.debug("\nfind_sub_repos: path=%s", path)
  is_repo = check_repo(os.path.abspath(path))
  subdirs = os.walk(path).next()[1]
  if is_repo:
    mylogger.info("find_sub_repos: %s is a repo", path)
    if fileobj == None:
      file_creator = True
    fileobj = make_subdep_entry(os.path.abspath(path), subdirs, fileobj=fileobj)
  for subdir in subdirs:
    fullpath = path+'/'+subdir
    if subdir[0] != ".":
      fileobj = find_sub_repos(fullpath, fileobj)
  if is_repo:
    mylogger.debug("find_sub_repos: %s completed", path)
    try:
      mylogger.debug("find_sub_repos: file creator is %s", file_creator)
      if file_creator:
        mylogger.info("find_sub_repos: finished with %s", fileobj.name)
        fileobj.close()
        fileobj = None
    except:
      mylogger.debug("find_sub_repos: %s has no file creator defined.",path)
  os.chdir(thisdir)
  return fileobj

def check_repo(path):
  """
  Convenience so this test hast to be done only once
  """
  mylogger.debug("check_repo: path = %s", path)
  if os.path.exists(path+"/.git"):
    return True
  else:
    return False

def make_subdep_entry(path, subdirs, fileobj=None):
  """
  """
  global top_repos
  if fileobj:
    mylogger.debug("make_subdep_entry: path=%s, subdirs=%s, file=%s",
                   path, subdirs, fileobj.name)
  else:
    mylogger.debug("make_subdep_entry: path=%s, subdirs=%s",
                   path, subdirs)
  if fileobj == None:
    fileobj = open(path+"/subdep.txt","w")
    top_repos.append(path)
    mylogger.info("make_subdep_entry: created %s", fileobj.name)
  else:
    #make text entry in subdep.txt
    remotes = git.Repo(path).remotes
    name = remotes[0].name
    url = remotes[0].url
    fileobj.write(os.path.realpath(path)+" "+name+" "+url+'\n')
    mylogger.info("make_subdep_entry: wrote remote %s", name)
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
      mylogger.info("Wrote %s/superdep.txt", subdir)

def install_dependencies():
  """
  """
  for direction in ["sub","super"]:
    filename = direction+"dep.txt"
  try:
    fd = open(filename,"r")
  except IOError, details:
    mylogger.warning(" IOError, "+str(details))
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
    print "git clone --origin=jpl", url, subdir
  
