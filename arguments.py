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

def simple_parse_args(init_description):
    """
    Grab arguments relevant to the Pyro nameserver that have APC and Spectrometer servers
    registered.
    """
    parser = argparse.ArgumentParser(description=init_description)

    parser.add_argument('--remote_server_name', '-rsn', dest='remote_server_name',
                        action='store', default='localhost', type=str, required=False,
                        help="""Specify the name of the remote host. If you're trying to access a Pyro nameserver that
                             is running locally, then use localhost. If you supply a value other than 'localhost'
                             then make sure to give other remote login information.""")

    parser.add_argument('--remote_port', '-rp', dest='remote_port',
                        action='store', type=int, required=False, default=None,
                        help="""Specify the remote port.""")

    parser.add_argument('--tunnel_username', '-tu', dest='tunnel_username',
                        action='store', type=str, required=False,
                        help="""Specify the username to use for creating the tunnel to the remote machine.
                                This is probably the same as your JPL username""")

    parser.add_argument('--remote_username', '-ru', dest='remote_username',
                        action='store', type=str, required=False, default='ops',
                        help="""Specify the remote username.""")

    parser.add_argument('--local_forwarding_port', '-lfp', dest='local_forwarding_port',
                        action='store', type=int, required=False,
                        help="""Specify the local forwarding port to use.
                                If you supply nothing then the Pyro Object Discoverer will forward on the same
                                port as the remote nameserver port.""")

    parser.add_argument("--ns_host", "-nsn", dest='ns_host', action='store',default='localhost',
                        help="Specify a host name for the Pyro name server. Default is localhost")

    parser.add_argument("--ns_port", "-nsp", dest='ns_port', action='store',default=50000,type=int,
                        help="Specify a port number for the Pyro name server. Default is 9090.")

    parser.add_argument("--msg_bus_host", "-msg_n", dest='msg_bus_host', action='store', default='localhost',
                        help="Specify a host name for the MessageBus server. Default is localhost.")

    parser.add_argument("--msg_bus_port", "-msg_p", dest='msg_bus_port', action='store', default=0, type=int,
                        help="Specify a port number for the MessageBus server. If nothing is provided, defaults to 0 (random).")

    parser.add_argument("--messagebusflag", "-mbflg", dest='messagebusflag', action='store_true', default=False,
                        help="Specify whether or not to start up a fresh messagebus server.")

    parser.add_argument("--simulated", "-s", dest='simulated', action='store_true', default=False,
                        help="Specify whether or not the server is running in simulator mode.")

    parser.add_argument("--local", "-l", dest='local', action='store_true', default=False,
                        help="Specify whether or not the server is running locally or on a remote server.")

    parser.add_argument("--verbose", "-v", dest="verbose", action='store_true', default=False,
                        help="Specify whether not the loglevel should be DEBUG")

    return parser
