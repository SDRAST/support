"""
make_git_deps - make super/sub dependency files; install dependency repos
"""

from support.git import *
from optparse import OptionParser

class MyParser(OptionParser):
  """
  Subclass of OptionParser which does not mess up examples formatting
  """
  def format_epilog(self, formatter):
    """
    Don't use textwrap; just return the string.
    """
    return self.epilog

p = MyParser(epilog=examples)
p.set_usage('extractor.py [options]')
p.set_description(__doc__)
p.add_option('-d', '--makedeps',
             dest = 'makedeps',
             default = False,
             action = 'store_true',
             help = "Make subdep.txt and superdep.txt files")
p.add_option('-i', '--install_dependencies',
             dest = 'install_deps',
             default = False,
             action = 'store_true',
             help = "Install the sub repos of the repo in this directory")
p.add_option('-l', '--loglevel',
             dest = 'loglevel',
             default = 'warning',
             help = "Set logging to debug, info, warning, error or critical")
opts, args = p.parse_args(sys.argv[1:])
loglevel = opts.loglevel
mylogger = init_logging(consolevel=get_loglevel(loglevel))
mylogger.debug("Options and arguments: %s, %s", opts, args)
if args:
  assert len(args) == 1
  os.chdir(args[0])

if opts.makedeps:
  mylogger.debug("main: current directory: %s",os.getcwd())
  top_repos = []
  find_sub_repos() # this also populates the top repos list
  make_superdeps(top_repos)

if opts.install_deps:
  install_dependencies()
