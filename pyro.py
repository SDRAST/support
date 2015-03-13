# -*- coding: utf-8 -*-
"""
Functions to set up Pyro using tunnels if necessary.

The module keeps track of the tunnels it creates.  A call to
'cleanup_tunnels()' should be made before ending the program.
"""
import Pyro.core
import Pyro.naming
import Pyro.errors
import tunneling as T
import time
import logging
import os, os.path
import atexit

# Set up Pyro system logging
NONE = 0
ERRORS = 1
WARNINGS = 2
ALL = 3
Pyro.config.PYRO_TRACELEVEL = WARNINGS
Pyro.config.PYRO_STDLOGGING = True
SLog = Pyro.util.SystemLogger()
if not os.path.exists("/usr/local/logs/PYRO/"):
  os.mkdir("/usr/local/logs/PYRO/")

module_logger = logging.getLogger(__name__)

class PyroTaskServer():
  """
  Class to create Pyro daemons which can be linked to Pyro servers
  
  Pyro servers are sub-classes of Pyro.core.ObjBase.  They are linked to
  Pyro daemons and then published by a Pyro namserver.
  """
  def __init__(self, pyroHostName, taskName):
    """
    Create a PyroTaskServer() object.

    @param pyroHostName : host where the Pyro nameserver resides
    @type  pyroHostName : str

    @param taskName : name to be used for logging
    @type  taskName : str
    """
    self.taskName = taskName
    self.logger = logging.getLogger(module_logger.name+".PyroTaskServer")
    self.logger.debug(" Initiating PyroTaskServer()")
    Pyro.config.PYRO_LOGFILE = '/usr/local/logs/PYRO/'+taskName+'.log'
    SLog.msg(self.taskName,"pyro_support module imported")
    SLog.msg(self.taskName,"server started")
    self.logger.debug(" %s creating daemon", self.taskName)
    self._create_daemon(pyroHostName)
    self.logger.debug(" %s initialized", self.taskName)

  def _create_daemon(self, hostName):
    """
    Create the server daemon

    @param hostName : the host wehere the nameserver resides
    @type  hostName : str
    """
    self._connect_to_pyro_nameserver(hostName)
    self.logger.debug('_create_daemon: %s using host %s and port %d',
                  self.taskName, self.pyro_host, self.pyro_port)
    # Find a nameserver:
    #   1. get the name server locator
    locator = Pyro.naming.NameServerLocator()
    #   2. locate the name server
    self.ns = locator.getNS(host=self.pyro_host,port=self.pyro_port)
    # Create a daemon
    self.daemon = Pyro.core.Daemon(port=T.free_socket())
    # Get the daemon socket; is this necessary?
    host, port = self.daemon.sock.getsockname()
    self.logger.debug('_create_daemon: The pyro deamon is running on port %d',port)
    self.daemon.useNameServer(self.ns)

  def start(self, server, pyroServerName):
    """
    @param server : the Pyro task server object
    @type  server : instance of subclass of Pyro.core.ObjBase

    @param pyroServerName : the name by which the server object is known
    @type  pyroServerName : str
    """
    self.server = server
    try:
      uri=self.daemon.connect(server,pyroServerName)
    except Pyro.errors.NamingError, details:
      self.logger.error(
        "start: could not connect server object to Pyro daemon. %s already exists",
        str(details[1]), exc_info=True)
      raise Exception("Cannot connect server to daemon.")
    else:
      # Servers advertised
      self.logger.debug("start: nameserver database: %s",self.ns.flatlist())
      try:
        self.daemon.requestLoop(condition=server.running)
      except KeyboardInterrupt:
        self.logger.warning("start: keyboard interrupt")
        #self.ULog.warn(self.taskName,"Keyboard interrupt")
      finally:
        self.logger.info("start: request loop exited")
        self.daemon.shutdown(True)
      module_logger.info("start: daemon done")
      #self.ULog.warn(self.taskName,'session ended')

  def halt(self):
    """
    """
    self.daemon.shutdown(True)
    SLog.msg(self.taskName,"server started")

  def _connect_to_pyro_nameserver(self,server):
    """
    This either accesses the Pyro nameserver directly or tunnels to it.

    If a tunnel is necessary, the tunnel endpoint is also assumed to be
    the nameserver.

    @param server : nameserver short name
    @type  server : str

    @return: pyro_host (str), pyro_port (int)
    """
    if T.at_jpl():
      self.logger.debug("_connect_to_pyro_nameserver: localhost is at JPL")
      # no tunnel is needed
      self.pyro_host = server
      self.pyro_port = 9090
    else:
      self.logger.debug("_connect_to_pyro_nameserver: need a tunnel to JPL")
      # create a tunnel to the nameserver
      troach = T.Tunnel(server)
      self.logger.info("_connect_to_pyro_nameserver: we have a tunnel")
      self.pyro_port = T.free_socket() %d
      self.logger.info("_connect_to_pyro_nameserver: we have proxy port at",
                       pyro_port)
      p = T.makePortProxy(server,pyro_port,server,9090)
      self.pyro_host = 'localhost'
    return self.pyro_host, self.pyro_port

class PyroTaskClient(Pyro.core.DynamicProxy):
  """
  Superclass for clients of Pyro tasks

  This creates a DynamicProxy.  It also creates a temporary nameserver
  client which goes away after the initialization.
  
  Pulic attributes::
   ns -          Pyro nameserver object used by client
   server -      Pyro remote task server object
   server_host - host which has the remote task server
   server_port - port on remote host used by server
  """
  def __init__(self, servername, pyro_ns = "dto", pyro_port = 9090):
    """
    Create an instance of a Pyro task client

    @param servername : Pyro name of the remote task server
    @type  servername : str

    @param pyro_ns : name of the Pyro nameserver host
    @type  pyro_ns : str

    @param pyro_port : port used by the Pyro nameserver
    @type  pyro_port : int
    """
    self.logger = logging.getLogger(module_logger.name+".PyroTaskClient")
    with NameserverResource() as nsr:
      self.logger.debug(" nameserver object is %s",str(nsr.ns))
      server = nsr.ns.resolve(servername)
      server_host, server_port = pyro_server_details(
        pyro_server[server.address], server.port)
      device_request = \
        "PYROLOC://" + server_host + ":" + str(server_port) + \
        "/" + servername
      self.logger.debug(" proxy request: %s",device_request)
      try:
        Pyro.core.DynamicProxy.__init__(self, device_request)
      except Pyro.errors.NamingError:
        self.logger.error(" pyro name error", exc_info=True)
        raise Exception("Connecting to Pyro nameserver failed")
      except Exception:
        self.logger.error(" request for server connection failed",
                            exc_info=True)
        raise Exception("Connecting to Pyro nameserver failed")
      else:
        # Give connection time to be established
        time.sleep(2)
      self.logger.debug(" dynamicProxy instantiated.")
    
class NameserverResource:
  """
  """
  def __enter__(self, pyro_ns = "dto", pyro_port = 9090):
    """
    """
    self.logger = logging.getLogger(module_logger.name+".NameserverResource")
    
    class PyroNameserver:
      """
      """
      def __init__(self,pyro_ns="dto", pyro_port = 9090):
        self.logger = logging.getLogger(
                            module_logger+".NameserverResource.PyroNameserver")
        self.tunnels = []
        # Find a nameserver:
        self.logger.debug(
          " Requested PyroNameserver host is %s using port %d",
          pyro_ns,pyro_port)
        # This will create a tunnel to the nameserver if needed
        pyro_ns_host, ns_proxy_port = self._pyro_server_details(pyro_ns,
                                                                pyro_port)
        self.logger.debug(" Real nameserver is %s using port %d",
                            pyro_ns_host, ns_proxy_port)
        # 1. get a non-persistent name server locator
        locator = Pyro.naming.NameServerLocator()
        # 2. locate the name server
        self.ns  = pyro_server_request(locator.getNS,
                                       host=pyro_ns_host,
                                       port=ns_proxy_port)
        if self.ns == None:
          self.logger.error("No nameserver connection")
          raise RuntimeError("No nameserver connection")

      def _pyro_server_details(self, ns_shortname, pyro_ns_port):
        """
        Provides the hostname and port where the Pyro server appears.

        The hostname and port will be the obvious ones if the client is in the
        same domain.  Otherwise, the server will appear at a tunnel port on the
        localhost.

        @param ns_shortname : Pyro nameserver short host name (without domain)
        @type  ns_shortname : str

        @param pyro_ns_port : Pyro nameserver port, typically 9090
        @type  pyro_ns_port : int

        @return: (apparent_host [str], apparent port [int])
        """
        if T.at_jpl() or ns_shortname == "localhost":
          ns_proxy_port = pyro_ns_port
          if ns_shortname == "localhost":
            pyro_ns_host = ns_shortname
          else:
            pyro_ns_host = ns_shortname+".jpl.nasa.gov"
        else:
          # we need a tunnel to the Pyro nameserver
          nameserver_tunnel = T.Tunnel(ns_shortname)
          self_logger.debug(
                       "_pyro_server_details: NameserverResource has a tunnel")
          ns_proxy_port = T.free_socket()
          self.logger.debug(
                "_pyro_server_details: Pyro nameserver has a proxy port at %d",
                              ns_proxy_port)
          ns_tunnel_process = T.makePortProxy(ns_shortname,
                                              ns_proxy_port,
                                              IP[ns_shortname],
                                              pyro_ns_port)
          self.tunnels.append(ns_tunnel_process)
          self.logger.debug("_pyro_server_details: Tunnels for %s: %s",
                                                        str(self),self.tunnels)
          pyro_ns_host = 'localhost'
          self.logger.debug("_pyto_server_details: process ID is %d",
                            ns_tunnel_process.pid)
        return pyro_ns_host, ns_proxy_port

      def __enter__(self):
        return self

      def _cleanup(self):
        """
        """
        self.logger.debug("_cleanup: called for %s",self.tunnels)
        for task in self.tunnels:
          self.logger.info("_cleanup: %d killed",task.pid)
          task.terminate()
          self.tunnels.remove(task)
          self.logger.debug(
                    "_cleanup: %s removed from NameserverResource tunnel list",
                    str(task))
        
    self.nameserver_obj = PyroNameserver(pyro_ns = pyro_ns,
                                         pyro_port = pyro_port)
    return self.nameserver_obj

  def __exit__(self, type, value, traceback):
    """
    """
    self.logger.debug("__exit__() called")
    self.nameserver_obj._cleanup()

# --------------------------- module methods -------------------------------

def pyro_server_request(task,*args,**kwargs):
  """
  Make a request of a Pyro server

  Since it can take a while to set up a tunnel to a Pyro server, the
  first request of the server should be repeated until successful or until
  it times out.

  Note
  ====
  Timing out still to be implemented

  @param task : the function requested
  @type  task : a method instance

  @param args : positional arguments expected by task

  @param kwargs : keyword arguments expected by task

  @return: result of the requested task
  """
  if kwargs.has_key('timeout') == False:
    timeout=10.
  result = None
  while timeout > 0:
    try:
      result = task(*args,**kwargs)
    except Pyro.errors.ProtocolError, details:
      module_logger.warning("pyro_server_request: %s (%f sec left)",
                       details,timeout)
      if str(details) == "connection failed":
        timeout -= 0.5
        time.sleep(0.5)
    else:
      timeout = 0.
  return result

def pyro_server_details(ns_shortname,pyro_ns_port):
  """
  Provides the hostname and port where the Pyro server appears.

  The hostname and port will be the obvious ones if the client is in the
  same domain.  Otherwise, the server will appear at a tunnel port on the
  localhost.

  @param ns_shortname : Pyro nameserver short host name (without domain)
  @type  ns_shortname : str

  @param pyro_ns_port : Pyro nameserver port, typically 9090
  @type  pyro_ns_port : int

  @return: (apparent_host [str], apparent port [int])
  """
  global tunnels
  module_logger.debug("pyro_server_details: trying %s:%s",
                      ns_shortname, pyro_ns_port)
  if T.at_jpl() or ns_shortname == "localhost":
    # no proxy port
    ns_proxy_port = pyro_ns_port
    if ns_shortname == "localhost":
      module_logger.debug("pyro_server_details: ns is at localhost port")
      pyro_ns_host = ns_shortname
    else:
      module_logger.debug("pyro_server_details: ns is at JPL")
      pyro_ns_host = ns_shortname+".jpl.nasa.gov"
  else:
    module_logger.debug("pyro_server_details: ns is not at JPL")
    # we need a tunnel to the Pyro nameserver
    module_logger.debug("pyro_server_details: requesting a tunnel")
    nameserver_tunnel = T.Tunnel(ns_shortname)
    module_logger.debug("pyro_server_details: module has a tunnel")
    ns_proxy_port = T.free_socket()
    module_logger.debug("pyro_server details: Pyro server proxy port is at %d",
                  ns_proxy_port)
    ns_tunnel_process = T.makePortProxy(ns_shortname,
                                        ns_proxy_port,
                                        IP[ns_shortname],
                                        pyro_ns_port)
    tunnels.append(ns_tunnel_process)
    pyro_ns_host = 'localhost'
    module_logger.debug("pyro_server_details: Tunnel process ID is %d",
                        ns_tunnel_process.pid)
  module_logger.debug("pyro_server_details: server is %s:%s",
    pyro_ns_host, ns_proxy_port)
  return pyro_ns_host, ns_proxy_port

def cleanup_tunnels():
  """
  Remove tunnels that were created for this session
  """
  global tunnels
  module_logger.debug("Open tunnel tasks: %s",str(tunnels))
  for task in tunnels:
    module_logger.info("%d killed",task.pid)
    task.kill()

# This is only used by get_device_server
def get_nameserver(pyro_ns = "dto", pyro_port = 9090):
  """
  Get a Pyro non-persistent nameserver object.

  Note that the nameserver object loses its connection to the server if it
  is not used for a while.  If this might happen, test for a
  Pyro.errors.NamingError exception and, if necessary, call this method
  again.

  Examples of what you might do with it::
   In [5]: from Observatory.pyro_support import get_nameserver
   In [6]: ns = get_nameserver()
   In [7]: ns.flatlist()
   Out[7]:
   [(':Pyro.NameServer',
    <PyroURI 'PYRO://128.149.22.108:9090/8095166c0d501fbe708a6e1d7bb6cf39b8'>),
   (':Default.kurtspec_server',
    <PyroURI 'PYRO://128.149.22.108:29052/8095166c1e751fbff7c27dd4bb93c186f4'>)]
   In [8]: ns.fullName('kurtspec_server')
   Out[8]: ':Default.kurtspec_server'
   In [9]: ns.unregister('kurtspec_server')

  @param pyro_ns : the host where the Pyro nameserver resides
  @type  pyro_ns : str

  @param pyro_port : the port used by the Pyro name server
  @type  pyro_port : int

  @return: Pyro nameserver object
  """
  # if necessary, create a tunnel to the nameserver
  module_logger.debug("get_nameserver: try at %s:%d", pyro_ns, pyro_port)
  pyro_ns_host, ns_proxy_port = pyro_server_details(pyro_ns, pyro_port)
  module_logger.debug("get_nameserver: nameserver host is %s:%d", pyro_ns_host,
                         ns_proxy_port)
  # Find a nameserver:
  # 1. get a non-persistent name server locator
  locator = Pyro.naming.NameServerLocator()
  # 2. locate the name server
  module_logger.debug("get_nameserver: have locator; requesting a nameserver")
  ns  = pyro_server_request(locator.getNS,
                            host=pyro_ns_host,
                            port=ns_proxy_port)
  if ns == None:
    module_logger.error("get_nameserver: no nameserver connection")
    raise RuntimeError("No nameserver connection")
  else:
    return ns

def get_device_server(servername, pyro_ns = "dto", pyro_port = 9090):
  """
  Establishes a connection to a Pyro device server.

  This is for Python command-line use, as in this example::
    In [5]: from Observatory.pyro_support import get_device_server
    In [6]: mgr = get_device_server('MMS_manager')
  If the server is behind a firewall, a tunnel is created.

  @param servername : the name as it appears in a 'pyro-nsc list' response
  @type  servername : str

  @param pyro_ns : the host where the Pyro nameserver resides
  @type  pyro_ns : str

  @param pyro_port : the port used by the Pyro name server
  @type  pyro_port : int

  @return:
  """
  ns = get_nameserver(pyro_ns, pyro_port)
  module_logger.debug("get_device_server: nameserver is %s", ns)
  # Find the device server
  server = ns.resolve(servername)
  module_logger.debug("get_device_server: try for device server at %s:%d",
                      server.address, server.port)
  server_host, server_port = pyro_server_details(pyro_server[server.address],
                                                            server.port)
  try:
    device_request = "PYROLOC://" + server_host + ":" + str(server_port) + \
                     "/"+servername
    module_logger.debug("get_device_server: proxy request: %s",device_request)
    device = Pyro.core.DynamicProxy(device_request)
    module_logger.debug("get_device_server: returns %s", device)
  except Pyro.errors.NamingError, details:
    module_logger.error("get_device_server: Pyro name error: %s: %s",
                        details[0],details[1])
    return [None, "get_device_server: Pyro name error", str(details)]
  except Exception,details:
    module_logger.error("get_device_server: Request for server connection failed\n%s",
                        details)
    return [None,"Request for server connection failed",str(details)]
  else:
    return device

def launch_server(serverhost, taskname, task):
  """
  Combines a device controller class with a Pyro class
  """
  # create the server launcher
  module_logger.debug(" Launching Pyro task server %s on %s",
                      taskname, serverhost)
  server_launcher = PyroTaskServer(serverhost, taskname)

  # check to see if the server is running already.
  response = server_launcher.ns.flatlist()
  no_conflict = True
  for item in response:
    if item[0].split('.')[1] == taskname:
      no_conflict = False
      break
  if no_conflict:
    # launch and publish the task server.  This starts the event loop.
    module_logger.info(" Starting the server...")
    server_launcher.start(task,taskname)
  else:
    module_logger.error(
                   "%s is already published.  Is the server already running?",
                   taskname)
    module_logger.error("If not, do 'pyro-nsc remove %s'",taskname)


# Generally, JPL/DSN hosts cannot be resolved by DNS
GATEWAY, IP, PORT = T.make_port_dict()
pyro_server = {'127.0.0.1':      'localhost',
               '128.149.22.108': 'dto',
               '137.78.97.24':   'mmfranco-0571605',
               '128.149.22.95':  'roachnest'}

# Remember any tunnels that may be opened
tunnels = []

atexit.register(cleanup_tunnels)
