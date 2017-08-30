"""
module with enhancements to the Python logging
"""
import logging
import time
import sys

from support.options import initiate_option_parser

logger = logging.getLogger(__name__)

def logging_config(name="", logger=None, logfile=None, loglevel=logging.INFO, handlers=None, **kwargs):
    """
    Configure stream and file output logging.
    If we don't provide a logfile (discouraged) then we don't do
    file logging.
    args:
        - name (str): The name of the module from which we log.
    kwargs:
        - logfile (str): The name of the logfile to use for file logging.
        - logger (logging.getLogger): An existing logger instance to which we want to add handlers.
        - loglevel (logging level): The logging level to use.
        - handlers (list of logging handlers): Extra handlers, that already have formatters.
        - **kwargs: Other (unexpected) keyword arguments.
    """
    if not logger:
        logger = logging.getLogger(name)

    logger.propagate = False
    logger.setLevel(loglevel)

    if len(logger.handlers) != 0:
        pass
    else:
        logging.Formatter.converter = time.gmtime
        formatter_file = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

        # configure stream logging (the output to stdout)
        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(loglevel)
        sh.setFormatter(formatter)

        logger.addHandler(sh)

        # if we have a logfile, configure file logging.
        if logfile:
            fh = logging.FileHandler(logfile)
            fh.setLevel(loglevel)
            fh.setFormatter(formatter_file)
            logger.addHandler(fh)

    if handlers:
        if not isinstance(handlers, list):
            handlers = [handlers]
        for handler in handlers:
            logger.addHandler(handler)

    return logger


def init_logging(extlogger,
                 loglevel=logging.INFO,
                 consolevel=logging.INFO,
                 logname="/tmp/logging.log"):
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
    dh = extlogger.handlers[0]
    logger.debug("init_logging: default handler is %s", dh)
    logger.debug("init_logging: default handler level is %s", dh.level)
    logger.debug("init_logging: requested level is %s", consolevel)
    dh.setLevel(consolevel)
    logger.debug("init_logging: default handler level is %s", dh.level)

    # create formatter and add it to the handler
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s:  %(message)s')
    dh.setFormatter(formatter)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(logname)
    # add the handler to the logger
    extlogger.addHandler(fh)
    fh.setLevel(loglevel)
    logger.debug("init_logging: file handler level is %s", fh.level)
    fh.setFormatter(formatter)
    extlogger.setLevel(min(dh.level, fh.level))
    return extlogger

def get_loglevel(level):
    """
    Get the level value from text

    @param level : dump, debug, info, warning, error, critical
    @type  level : str

    @return: int
    """
    level = level.lower()
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
        logger.warning("Invalid logging level %s.  Set to 'warning' (%d)",
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
    try:
      command = "from "+module+" import module_logger as temp"
      exec(command)
    except ImportError:
      # for the newer modules
      command = "from "+module+" import logger as temp"
      exec(command)
    loggers[module] = temp
    level = logger_dict[module]
    command = "loggers['"+module+"'].setLevel(logging."+level.upper()+")"
    logger.debug("%s", command)
    exec(command)
  return loggers

