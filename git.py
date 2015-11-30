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
import os.path
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
  
  The directory is a git repo if it has a .git sub-directory.
  
  @param path : the path to the directory to be checked
  @type  path : str
  
  @return: bool
  """
  module_logger.debug("check_repo: path = %s", path)
  if os.path.exists(path+"/.git"):
    return True
  else:
    return False

def make_subdep_entry(path, fileobj=None):
  """
  Add submodule (separate repo in this directory) to subdep.txt
  
  subdep.txt is a file listing all the sub-repos, that is, repos which are
  under this directory
  
  @param path : path to the directory to be processed
  @type  path : str
  
  @param fileobj : file object for file subdep.txt
  @type  fileobj : instance of a file class
  
  @return: file object
  """
  global top_repos
  if fileobj:
    module_logger.debug("make_subdep_entry: path=%s, file=%s",
                   path, fileobj.name)
  else:
    module_logger.debug("make_subdep_entry: path=%s",
                   path)
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
  """
  Create list of repos in the directory tree above this repo
  
  This is kept in the file superdep.txt
  
  @param top_repos : a list of top-level repos to be examined
  @type  top_repos : list of str
  """
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
  Clones the repos needed by this repo.

  Dry-run only, so far.
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

  @return: list of str
  """

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
  response = os.popen('locate \.git | grep -v Trash | grep -v \.svn','r').readlines()
  prev_dir = ''
  first_pass = True
  git_dirs = []
  for line in response:
    filename = line.strip()
    file_parts = filename.split('/')
    if file_parts[1] == 'opt':
      # Ignore third party repos
      continue
    # Look for .git in positions 3-10 of the path because we can ignore
    # '', 'usr', 'local'
    # '', 'var', 'www'
    for git_dir_index in range(3,11):
      if git_dir_index < len(file_parts):
        if file_parts[git_dir_index] == '.git':
          # recreate the full path
          this_dir = make_filename(file_parts[1:git_dir_index])
          if re.match(prev_dir,this_dir):
            # prev_dir is contained in this_dir
            if (len(this_dir) > len(prev_dir)):
              # but there are extra characters so it may be a sub-directory
              if (this_dir[len(prev_dir)] == '/'):
                # the last character is '/' so this_dir is a directory
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

def report_status(show_all=False):
  """
  Does 'git status' for all the sandboxes.

  Prints the status report, if there is any, for each sandbox.
  There is a priority to what is reported, according to the severity of the
  status::
    work      - changes need to be committed
    untracked - there are untracked files which might need to be added
    behind    - a pull is required to bring the repo up to date
    ahead     - a push is required to update the remote

  @return: None
  """
  git_dirs = get_git_dirs()
  state = {}
  state['clean'] = []
  state['work'] = []
  state['untracked'] = []
  state['unknown'] = []
  state['behind'] = []
  state['ahead'] = []
  for git_dir in git_dirs:
    module_logger.debug("Processing %s", git_dir)
    os.chdir(git_dir)
    fd_out = os.popen('git status','r')
    response = fd_out.readlines()
    fd_out.close()
    if len(response) != 0:
      repo = os.path.basename(git_dir)
      status = "unknown"
      for f in response:
        line = f.strip()
        if re.search('On branch',line):
          branch = line.split()[-1]
        elif re.search("Changes",line):
          status = "work"
          break
        elif re.search("Untracked", line):
          status = "untracked"
          break
        elif re.search("is behind", line):
          status = "behind"
          break
        elif re.search("is ahead", line):
          status = "ahead"
          break
        elif re.search("nothing to commit",line):
          status = "clean"
      state[status].append("%18s  (%8s)  %8s" % (repo, branch, status))
    if show_all and (status != "clean"):
      print repo
      for f in response:
        print f.strip()
  for status in state.keys():
    for report in state[status]:
      print ("%9s: %31s" % (status,report[:30]))
  
#------------------------ under development ------------------------------------

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

def compare_to_remote(remote):
  """
  Compares status of local and remote repo
  """
  fd = os.popen('git remote show '+remote,'r')
  response = fd.readlines()
  fd.close()
  working = None
  tracked = []
  branch_status = []
  for line in response:
    parts = line.strip().split()
    if parts[0] == 'Fetch':
      pullURL = parts[2]
    elif parts[0] == 'Push':
      pushURL = parts[2]
    elif parts[1] == 'tracked':
      tracked.append(parts[0])
    if tracked:
      for branch in tracked:
        if parts[0] == branch and parts[1] == 'pushes':
          parts[3] = remote+'/'+parts[3]
          parts[4] = ' '.join(parts[4:])[1:-1]
          branch_status.append(parts[:5])
  return branch_status

def compare_to_remotes(remote):
  """
  Compares status of all local and remote repos
  """
  git_dirs = get_git_dirs()
  for git_dir in git_dirs:
    module_logger.debug("Processing %s", git_dir)
    os.chdir(git_dir)
    dirname = os.path.basename(git_dir)
    fd = os.popen('git remote','r')
    response = fd.readlines()
    fd.close()
    status = None
    for line in response:
      if line.strip() == remote:
        status = compare_to_remote(remote)
        for report in status:
          if report[-1] == 'up to date':
            pass
          else:
            print os.path.basename(git_dir), report
    if status:
      pass
    else:
      print "Ignoring",git_dir
    
