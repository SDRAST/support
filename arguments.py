"""
Support for Python argparse module

How to use this:

    p = initiate_option_parser(description,examples)
    p.usage = usage
    # Add other options here
  
    opts, args = p.parse_args(sys.argv[1:])
  
    # This cannot be delegated to another module or class
    mylogger = init_logging(logging.getLogger(),
                            loglevel   = get_loglevel(opts.file_loglevel),
                            consolevel = get_loglevel(opts.stderr_loglevel),
                            logname    = opts.logpath+__name__+".log")
    loggers = set_module_loggers(eval(opts.modloglevels))

"""
import argparse
import logging

logger = logging.getLogger(__name__)

################################## Classes ###################################

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
    
class ArgumentInterpreter(object):
  """
  Interprets the argument provided as the specied type of iterable
  
  If a list is expected, a single value is embedded in a list.  A tuple is
  converted to a list. An nparray is flattened and converted to a list::
    a = ArgumentInterpreter()
    l = a.as_list(thing)
  
  Note
  ----
  As needed, we will as 'as_nparray', 'as_tuple'
  """
  def __init__(self):
    """
    """
    self.logger = logging.getLogger(logger.name+".ArgumentInterpreter")
  
  def as_list(self, argument):
    """
    """
    if type(argument) == list:
      return argument
    elif type(argument) == tuple:
      return list(argument)
    elif type(argument) == numpy.ndarray:
      return list(argument.flatten())
    else:
      return [argument]

################################### Methods ##################################

def initiate_option_parser(description, examples):
  """
  Initiate an option parser with default logging options
  
  This creates a command line option parser with predefined options for using
  the Python logging module::
    --console_loglevel: stdout/stderr handler logging level (default: WARNING)
    --file_loglevel:    file handler logging level (default: WARNING)
    --logfilepath:      path to the log file (default: /usr/local/logs/)
    --module_loglevels: modified module logger levels, a dict of logging levels
                        keyed on module, e.g.,
                        "support.arguments": logging.WARNING
                        (default: {}, i.e. None)
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

