"""
module with enhancements to the Python logging
"""
import logging
import optparse

loglevel = {'debug':    logging.DEBUG,
            'info':     logging.INFO,
            'warning':  logging.WARNING,
            'error':    logging.ERROR,
            'critical': logging.CRITICAL}

module_logger = logging.getLogger(__name__)

def init_logging(logger,
                 loglevel = logging.INFO,
                 consolevel = logging.WARNING,
                 logname = "/tmp/logging.log"):
  """
  Create a logger that displays to the console and writes a log file.

  @param loglevel : logging level for the file log
  @type  loglevel : logging module parameter

  @param consolevel : logging level for messages sent to the console
  @type  loglevel : logging module parameter

  @param logname : path and name of the logging file
  @type  logname : str

  @return: logging.Logger instance
  """
  # default handler is the logger to sys.stderr
  logger.debug("init_logging: handlers: %s", logger.handlers)
  dh = logger.handlers[0]
  logger.debug("init_logging: default handler is %s", dh)
  dh.setLevel(consolevel)

  # create formatter and add it to the handler
  formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s:  %(message)s')
  dh.setFormatter(formatter)

  # create file handler which logs even debug messages
  fh = logging.FileHandler(logname)
  # add the handler to the logger
  logger.addHandler(fh)
  fh.setLevel(loglevel)
  fh.setFormatter(formatter)
  logger.setLevel(min(dh.level, fh.level))
  return logger

def get_loglevel(level):
  """
  Get the level value from text

  @param level : dump, debug, info, warning, error, critical
  @type  level : str

  @return: int
  """
  if level == "dump":
    Level = 5
  elif level == "debug":
    Level = logging.DEBUG
  elif level == "info":
    Level = logging.INFO
  elif level == "warning":
    Level = logging.WARNING
  elif level == "error":
    Level = logging.ERROR
  elif level == "critical":
    Level = logging.CRITICAL
  else:
    module_logger.warning("Invalid logging level %s.  Set to 'warning' (%d)",
                     level, Level)
  return Level

def set_loglevel(logger, level):
  """
  Set the level of a logger

  @type  logger : logging.Logger instance
  @type  level : int

  @return: None
  """
  logger.setLevel(level)
  logger.warning("Logger level is %d", level)

def set_module_loggers(logger_dict):
  """
  Set logging level of imported modules

  @param logger_dict : like {"support": "warning", ... }
  @type  logger_dict : dict of str

  @return: dict of loggers
  """
  loggers = {}
  for module in logger_dict.keys():
    command = "from "+module+" import module_logger as temp"
    exec(command)
    loggers[module] = temp
    level = logger_dict[module]
    command = "loggers['"+module+"'].setLevel(logging."+level.upper()+")"
    module_logger.debug("%s", command)
    exec(command)
  return loggers

def initiate_option_parser(description):
  """
  Initiate an option parser with default logging options
  
  This creates a command line option parser with predefined options for using
  the Python logging module.  The defaults are::
    stderr handler logging level (WARNING)
    file handler logging level (WARNING)
    path to the log file (/usr/local/logs/)
    modified module logger levels ({}), that is, None
  """
  p = optparse.OptionParser()
  p.set_usage(__name__+' [options]')
  p.set_description(description)
  p.add_option('--stderr_loglevel',
               dest = 'stderr_loglevel',
               type = 'str',
               default = 'warning',
               help = 'console Logging level')
  p.add_option('--file_loglevel',
               dest = 'file_loglevel',
               type = 'str',
               default = 'warning',
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
    
