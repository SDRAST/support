"""
module with enhancements to the Python logging
"""
import os
import datetime
import logging, logging.handlers
import time
import sys

from support.options import initiate_option_parser

logger = logging.getLogger(__name__)

__all__ = [
    "setup_logging",
    "set_loglevel",
    "get_loglevel",
    "init_logging",
    "setup_email_handler",
    "remove_handlers",
    "TLSSMTPHandler"
]

class TLSSMTPHandler(logging.handlers.SMTPHandler):
    """
    Custom handler for email logging using TLS encryption.

    Examples:

    Set up an instance to do gmail email logging.

    .. code-block:: python

        from cred import my_address, my_username, my_password

        to_address = ["someemail@somedomain"]

        eh = TLSSMTPHandler(mailhost=("smtp.gmail.com",587),
                                fromaddr=my_address,
                                toaddrs=to_address,
                                subject="subject",Overriden method.
                                credentials=(my_username, my_password),
                                secure=None)

    """
    def emit(self, record):
        """
        Format a logging record and send it to the specified addresses.
        This method is never called directly.
        """
        try:
            import smtplib
            try:
                from email.utils import formatdate
            except ImportError:
                formatdate = self.date_time
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)
            msg = self.format(record)
            msg = "From: {}\r\nTo: {}\r\nSubject: {}\r\nDate: {}\r\n\r\n{}".format(
                            self.fromaddr,
                            ",".join(self.toaddrs),
                            self.getSubject(record),
                            formatdate(), msg)
            if self.username:
                smtp.ehlo() # for tls add this line
                smtp.starttls() # for tls add this line
                smtp.ehlo() # for tls add this line
                smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

def setup_email_handler(toaddr, logLevel=logging.ERROR):
    """
    Setup an instance of TLSSMTPHandler
    """
    from support.cred import username, password
    if not isinstance(toaddr, list):
        toaddr = [toaddr]
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    eh = TLSSMTPHandler(mailhost=("smtp.gmail.com",587),
                            fromaddr="tams.dsn@gmail.com",
                            toaddrs=toaddr,
                            subject="MonitorControl logging",
                            credentials=(username, password),
                            secure=None)

    eh.setLevel(logLevel)
    eh.setFormatter(formatter)
    return eh

def remove_handlers(logger):
    """
    remove any handlers associated with a logger.
    """
    map(logger.removeHandler, logger.handlers[:])
    map(logger.removeFilter, logger.filters[:])
    return logger

def setup_logging(logger=None, logfile=None, logLevel=logging.DEBUG, handlers=None, **kwargs):
    """
    setup up some logging.getLogger instance with console logging and file logging
    handlers (StreamHandler and FileHandler handlers, respectively.)

    Examples:

    Super basic setup, with no file logging.

    .. code-block:: python

        import logging

        from support.logs import setup_logging

        logger = logging.getLogger("")
        setup_logging(logger=logger)

    Add a file handler:

    .. code-block:: python

        import logging

        from support.logs import setup_logging

        logger = logging.getLogger("")
        setup_logging(logger=logger, logfile="/path/to/logfile.log", logLevel=logging.INFO)

    Setup a custom email handler that uses TLS encryption:

    .. code-block:: python

        import logging

        from support.logs import setup_logging, setup_email_handler

        handler = setup_email_handler(["me@domain.com"])
        logger = logging.getLogger("")
        setup_logging(logger=logger, logfile="/path/to/logfile.log",
            logLevel=logging.INFO, handlers=handler)

    Args:
        logger (logging.getLogger, optional): logging instance to which to
            add handlers
        logfile (str, optional): logfile to log to. If this isn't provided,
            no FileHandler will be set up.
        logLevel (int, optional): logLevel for StreamHandler.
        handlers (list/logging.Handler, optional): Additional handlers to
            add to logging instance.
        **kwargs: Extra keyword arguments
    Returns:
        logging.getLogger: logging instance with new handlers added
    """
    if logger is None:
        logger = logging.getLogger()
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    file_formatter = logging.Formatter('%(asctime)s::%(levelname)s:%(name)s:%(message)s')

    map(logger.removeHandler, logger.handlers[:])
    map(logger.removeFilter, logger.filters[:])
    # logger.handlers = []
    logger.setLevel(logLevel)

    if logfile is not None:
        fh = logging.FileHandler(logfile)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(logLevel)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    if handlers is not None:
        if not isinstance(handlers, list):
            handlers = [handlers]
        for handler in handlers:
            logger.addHandler(handler)
    return logger

def logging_config(**kwargs):
    """alias for old logging_config function"""
    kwargs.pop("name")
    kwargs["logLevel"] = kwargs.pop("level", None)
    return setup_logging(**kwargs)

# def logging_config(name="", logger=None, logfile=None, level=logging.INFO,
#                    handlers=None, **kwargs):
#     """
#     Configure stream and file output logging.
#     If we don't provide a logfile (discouraged) then we don't do
#     file logging.
#
#     @param name : The name of the module from which we log.
#     @type  name : str
#
#     @param logger : An existing logger instance to which we want to add handlers.
#     @type  logger : logging.Logger
#
#     @param logfile : The name of the logfile to use for file logging.
#     @type  logfile : str
#
#     @param loglevel : The logging level to use.
#     @type  loglevel : logging.Level
#
#     @param handlers : Extra handlers, that already have formatters.
#     @type  handlers : list of logging handlers
#
#     @param **kwargs : Other (unexpected) keyword arguments.
#     """
#     if not logger:
#         logger = logging.getLogger(name)
#
#     logger.propagate = False
#     logger.setLevel(level)
#
#     if len(logger.handlers) != 0:
#         pass
#     else:
#         logging.Formatter.converter = time.gmtime
#         formatter_file = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')
#         formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
#
#         # configure stream logging (the output to stdout)
#         sh = logging.StreamHandler(sys.stdout)
#         sh.setLevel(level)
#         sh.setFormatter(formatter)
#
#         logger.addHandler(sh)
#
#         # if we have a logfile, configure file logging.
#         if logfile:
#             fh = logging.FileHandler(logfile)
#             fh.setLevel(level)
#             fh.setFormatter(formatter_file)
#             logger.addHandler(fh)
#
#     if handlers:
#         if not isinstance(handlers, list):
#             handlers = [handlers]
#         for handler in handlers:
#             logger.addHandler(handler)
#
#     return logger


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
        Level = logging.WARNING
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

def create_year_doy_dir(base_dir):
    """
    Given some base directory, create ``<base_dir>/<year>/<doy>``
    directory structure, if not already existing.
    """
    year, doy = datetime.datetime.utcnow().strftime("%Y %j").split(" ")
    year_doy_dir = os.path.join(base_dir, "{}/{}".format(year, doy))
    if not os.path.exists(year_doy_dir):
        os.makedirs(year_doy_dir)
    return year_doy_dir
