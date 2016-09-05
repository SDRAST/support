"""
Support for (deprecated) Python optparse module
"""
import optparse


class OptParser(optparse.OptionParser):
  """
  Subclass of OptionParser which does not mess up examples formatting
  """
  def format_epilog(self, formatter):
    """
    Don't use textwrap; just return the string.
    """
    return self.epilog
    
class PlainHelpFormatter(optparse.IndentedHelpFormatter): 
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
                formatter=PlainHelpFormatter(),
                description=description)
  p.set_usage(__name__+' [options]')
  p.add_option('--stderr_loglevel',
               dest = 'stderr_loglevel',
               type = 'str',
               default = 'warning',
               help = 'console Logging level')
  p.add_option('--file_loglevel',
               dest = 'file_loglevel',
               type = 'str',
               default = 'info',
               help = 'file Logging level')
  p.add_option('-l', '--logfilepath',
               dest = 'logpath',
               type = 'str',
               default = '/usr/local/logs/',
               help = 'directory path for log file')
  p.add_option('--module_loglevels',
               dest = 'modloglevels',
               type = 'str',
               default = '{}',
               help = 'dict of module loglevels')
  return p

