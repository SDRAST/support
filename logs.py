"""
module with enhancements to the Python logging
"""
import logging

def init_logging(loglevel=logging.WARNING,
                 consolevel=logging.WARNING,
                 logname=None):
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
  logging.basicConfig(level=logging.WARNING)

  logger = logging.getLogger()
  logger.setLevel(consolevel)
  # default handler
  dh = logger.handlers[0]
  dh.setLevel(consolevel)

  # create formatter and add it to the handler
  formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s:\n%(message)s')
  dh.setFormatter(formatter)

  # create file handler which logs even debug messages
  if logname:
    fh = logging.FileHandler(logname)
    fh.setLevel(loglevel)
    fh.setFormatter(formatter)
    # add the handler to the logger
    logger.addHandler(fh)
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
