"""
Support for Python argparse module
"""
import argparse


class OptParser(argparse.ArgumentParser):
  """
  Subclass of OptionParser which does not mess up examples formatting
  """
  pass
      
class PlainHelpFormatter(argparse.HelpFormatter): 
  """
  Formatter which does not remove newline codes
  """
  def format_description(self, description):
    """
    Don't remove \n
    """
    if description:
      return description + "\n"
    else:
      return ""

def initiate_option_parser(description, examples):
  """
  Initiate an option parser with default logging options
  
  This creates a command line option parser with predefined options for using
  the Python logging module.  The defaults are::
    stderr handler logging level (WARNING)
    file handler logging level (WARNING)
    path to the log file (/usr/local/logs/)
    modified module logger levels ({}), that is, None
  """
  p = OptParser(epilog=examples,
                formatter_class=PlainHelpFormatter,
                description=description,
                usage=__name__+' [options]')
  p.add_argument('--console_loglevel',
                 type = str,
                 default = 'warning',
                 help = 'console Logging level')
  p.add_argument('--file_loglevel',
                 dest = 'file_loglevel',
                 type = str,
                 default = 'info',
                 help = 'file Logging level')
  p.add_argument('-l', '--logfilepath',
                 dest = 'logpath',
                 type = str,
                 default = '/usr/local/logs/',
                 help = 'directory path for log file')
  p.add_argument('--module_loglevels',
                 dest = 'modloglevels',
                 type = str,
                 default = '{}',
                 help = 'dict of module loglevels')
  return p

