"""
Support for Python argparse (or optparse) module

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

In either case, the parser object will be a argparse.ArgumentParser object

Converting from optparse to argparse
====================================
The package 'optparse' has been made obsolescent. In converting from 'optparse'
to 'argparse', replace 'add_option' with 'add_argument' and change the 'type'
value from a string to a Python variable type, e.g. float
"""
import argparse
import logging
import sys

if sys.version_info >= (3,5):
    from .local_dirs import log_dir
else:
    from local_dirs import log_dir


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

class OptionParser(argparse.ArgumentParser):
  """
  front end for ArgumentParser for older programs from 'optparse' days
  """
  def __init__(self, description="", usage="", examples=""):
    """
    """
    super(OptionParser,self).__init__(
                            description=description,
                            usage=usage,
                            epilog=examples,
                            formatter_class=argparse.RawDescriptionHelpFormatter)
    self.add_argument('arguments', type=str, nargs='?', default=[])

  def parse_args(self, args=None):
    """
    parse the command line arguments

    If this is passed arguments it is assumed that 'opt_parse' behavior is
    wanted, return opts,args.  If not, we assume 'arg_parse' behavior
    returning only args.
    """
    if args:
      result = super(OptionParser,self).parse_args(args=args)
      if result.arguments:
        if type(result.arguments) != list:
          argument_list = [result.arguments]
        else:
          argument_list = result.arguments
        arguments = []
        for arg in argument_list:
          try:
            arguments.append(int(arg))
          except ValueError:
            try:
              arguments.append(float(arg))
            except ValueError:
              arguments.append(arg)
        return result, arguments
      else:
        return result, []
    else:
      result = super(OptionParser,self).parse_args()
      return result

################################### Methods ##################################

def initiate_option_parser(description, examples):
  """
  Initiate an option parser with default logging options

  This creates a command line option parser with predefined options for using
  the Python logging module::
    --console_loglevel: stdout/stderr handler logging level (default: WARNING)
    --file_loglevel:    file handler logging level (default: WARNING)
    --logfilepath:      path to the log file (default: /usr/local/Logs/`hostname`)
    --module_loglevels: modified module logger levels, a dict of logging levels
                        keyed on module, e.g.,
                        "support.arguments": logging.WARNING
                        (default: {}, i.e. None)
  """
  p = OptionParser(description=description,
                   usage=__name__+' [options]',
                   examples=examples)

  p.add_argument('--console_loglevel',
                 dest = 'console_loglevel',
                 type = str,
                 default = 'warning',
    help = 'console logging level')
  p.add_argument('--file_loglevel',
                 dest = 'file_loglevel',
                 type = str,
                 default = 'info',
    help = 'file Logging level')
  p.add_argument('-l', '--logfilepath',
                 dest = 'logpath',
                 type = str,
                 default = log_dir,
    help = 'directory path for log file (default "local_dirs.log_dir")')
  p.add_argument('--module_loglevels',
                 dest = 'modloglevels',
                 type = str,
                 default = '{}',
     help = 'dict of module loglevels')
  return p

def simple_parse_args(init_description):
    """
    Grab arguments relevant to the Pyro nameserver that have APC and
    Spectrometer servers registered.
    """
    parser = argparse.ArgumentParser(description=init_description)

    parser.add_argument('--remote_server_name', '-rsn',
                        dest='remote_server_name',
                        action='store',
                        default='localhost',
                        type=str,
                        required=False,
      help="""Specify the name of the remote host. If you're trying to access a Pyro nameserver that is running locally, then use localhost. If you supply a value other than 'localhost' then make sure to give other remote login information.""")

    parser.add_argument('--remote_port', '-rp',
                        dest='remote_port',
                        action='store',
                        type=int,
                        required=False,
                        default=None,
                        help="""Specify the remote port.""")

    parser.add_argument('--tunnel_username', '-tu',
                        dest='tunnel_username',
                        action='store',
                        type=str,
                        required=False,
      help="""Specify the username to use for creating the tunnel to the remote machine. This is probably the same as your JPL username""")

    parser.add_argument('--remote_username', '-ru',
                        dest='remote_username',
                        action='store',
                        type=str,
                        required=False,
                        default='ops',
                        help="""Specify the remote username.""")

    parser.add_argument('--local_forwarding_port', '-lfp',
                        dest='local_forwarding_port',
                        action='store',
                        type=int,
                        required=False,
      help="""Specify the local forwarding port to use. If you supply nothing then the Pyro Object Discoverer will forward on the same port as the remote nameserver port.""")

    parser.add_argument("--ns_host", "-nsn",
                        dest='ns_host',
                        action='store',
                        default='localhost',
      help="Specify a host name for the Pyro name server. Default is localhost")

    parser.add_argument("--ns_port", "-nsp",
                        dest='ns_port',
                        action='store',
                        default=50000,
                        type=int,
      help="Specify a port number for the Pyro name server. Default is 50000.")

    parser.add_argument("--msg_bus_host", "-msg_n",
                        dest='msg_bus_host',
                        action='store',
                        default='localhost',
       help="Specify a host name for the MessageBus server. Default is localhost.")

    parser.add_argument("--msg_bus_port", "-msg_p",
                        dest='msg_bus_port',
                        action='store',
                        default=0,
                        type=int,
      help="""Specify a port number for the MessageBus server. If nothing is provided, defaults to 0 (random).""")

    parser.add_argument("--messagebusflag", "-mbflg",
                        dest='messagebusflag',
                        action='store_true',
                        default=False,
      help="Specify whether or not to start up a fresh messagebus server.")
    # parser.add_argument("--msg_bus_host", "-msg_n", dest='msg_bus_host', action='store',
    #                     default='localhost',
    #                     help="Specify a host name for the MessageBus server. Default is localhost.")
    #
    # parser.add_argument("--msg_bus_port", "-msg_p", dest='msg_bus_port', action='store', default=0,
    #                     type=int,
    #                     help="Specify a port number for the MessageBus server. If nothing is provided, defaults to 0 (random).")
    #
    # parser.add_argument("--messagebusflag", "-mbflg", dest='messagebusflag', action='store_true', default=False,
    #                     help="Specify whether or not to start up a fresh messagebus server.")

    parser.add_argument("--simulated", "-s",
                        dest='simulated',
                        action='store_true',
                        default=False,
      help="Specify whether or not the server is running in simulator mode.")

    parser.add_argument("--local", "-l",
                        dest='local',
                        action='store_true',
                        default=False,
       help="Specify whether or not the server is running locally or on a remote server.")

    parser.add_argument("--verbose", "-v",
                        dest="verbose",
                        action='store_true',
                        default=False,
      help="Specify whether not the loglevel should be DEBUG")

    return parser
