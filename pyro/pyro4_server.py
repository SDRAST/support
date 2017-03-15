# pyro4_server.py
import logging
import os
import signal
import threading
import time

import Pyro4

from support.logs import logging_config
from support.tunneling import Tunnel, TunnelingException
from pyro3_util import full_name
from pyro4_util import arbitrary_tunnel, check_connection

def blocking(fn):
    """
    This decorator will make it such that the server can do
    nothing else while fn is being called.
    """

    def wrapper(*args, **kwargs):
        lock = args[0].lock
        with lock:
            res = fn(*args, **kwargs)
        return res

    return wrapper


def non_blocking(fn):
    """
    Proceed as normal unless a functuon with the blocking
    decorator has already been called
    """

    def wrapper(*args, **kwargs):
        lock = args[0].lock
        while lock.locked():
            time.sleep(0.01)
        time.sleep(0.01)
        res = fn(*args, **kwargs)
        return res

    return wrapper

class Pyro4ServerError(Pyro4.errors.CommunicationError):
    pass

class Pyro4Server(object):
    """
    A super class for servers.
    """

    def __init__(self, name, obj=None, **kwargs):
        """
        Setup logging for the server, in addition to creating a
        lock. Subclasses of this class can interact directly with the lock,
        or through the blocking and non-blocking decorators.
        args:
            - name (str): The name of the Pyro server.
        kwargs:
            - **kwargs: TAMS_BackEnd.util.logging_config kwargs
        """
        self.serverlog = logging_config(**kwargs)
        self._lock = threading.Lock()
        self._name = name
        self._running = False
        self._tunnel = None
        self._remote_ip = None
        self._remote_port = None
        self._proc = []

        self._exposed_obj = None
        if obj:
            self._exposed_obj = obj
        else:
            pass

        self.server_uri = None
        self.daemon_thread = None
        self.daemon = None

    @Pyro4.expose
    def running(self):
        with self._lock:
            return self._running

    @Pyro4.expose
    @property
    def name(self):
        return self._name

    @Pyro4.expose
    @property
    def locked(self):
        return self.lock.locked()

    def handler(self, signum, frame):
        """
        Define actions that should occur before the server
        is shut down.
        """
        try:
            self.serverlog.info("Closing down server.")
            self.close()
        except Exception as e:
            self.serverlog.error("Error shutting down daemon: {}".format(e), exc_info=True)
        finally:
            os.kill(os.getpid(), signal.SIGKILL)

    def launch_server(self, remote_server_name,
                            remote_port=22,
                            ns_host='localhost',
                            ns_port=9090,
                            local_forwarding_port=None,
                            remote_username=None,
                            tunnel_username=None,
                            threaded=False):
        """
        Launch server, remotely or locally. Assumes there is a nameserver registered on
        ns_host/ns_port.

        Args:
            remote_server_name (str): The name of the remote server.
                If we supply the name of a JPL domain, then uses support.tunneling.Tunnel
                to create a tunnel to the desired location
        Keyword Args:
            remote_port (int):
            ns_host:
            ns_port:
            threaded:

        Returns:

        """
        if remote_server_name == 'localhost':
            self._remote_ip = "localhost"
            return self._launch_server_local(ns_host, ns_port, threaded=threaded)
        elif remote_server_name in full_name:
            self._tunnel = Tunnel(remote_server_name, username=tunnel_username)
            self._remote_ip = "localhost"
            self._remote_port = self._tunnel.port
        else:
            self._remote_ip = remote_server_name # means we supplied an actual ip address.
            self._remote_port = remote_port

        # now with tunnel in place (or not depending on condition), we can create
        # further ssh tunnels to allow us to register object.
        # First estalbish what port to use for local forwarding
        if not local_forwarding_port:
            local_forwarding_port = ns_port

        # Create tunnel to nameserver
        proc_ns = arbitrary_tunnel(self._remote_ip, 'localhost', local_forwarding_port, ns_port,
                                port=self._remote_port, username=remote_username)
        self._proc.append(proc_ns)
        # now check the tunnel
        success = check_connection(Pyro4.locateNS, args=('localhost', local_forwarding_port))

        self.serverlog.debug("Lauching server.")
        # now launch the server "locally"
        if success:
            self._launch_server_local('localhost', local_forwarding_port, False)
        else:
            raise TunnelingException("Could not successfully tunnel to remote!")
            return


    def _launch_server_local(self, host, port, threaded=False):
        """
        Connect to a Pyro name server. This also sets up the program such that
        a kill command (ctrl+c) will attempt to call close on the server before exiting.
        This is useful in the case of an APC server, as it is necessary to issue
        the close command before exiting a program with a socket connection to the APC.
        args:
            - host (str): The name server host.
            - port (int): The name server port.
        kwargs:
            - threaded (bool): If we're running this on a thread, then we can't use signaling.
        """
        self.serverlog.info("Connecting to the Pyro nameserver.")

        self.daemon = Pyro4.Daemon()
        if self._exposed_obj: # means we're not inheriting
            self.server_uri = self.daemon.register(self._exposed_obj)
        else: # means we're using Pyro4Server as parent class.
            self.server_uri = self.daemon.register(self)
        self.serverlog.debug("Server uri is {}".format(self.server_uri))
        self.ns = Pyro4.locateNS(port=port, host=host)
        self.ns.register(self._name, self.server_uri)
        self.serverlog.info("{} available".format(self._name))

        if not threaded:
            signal.signal(signal.SIGINT, self.handler)
        else:
            pass
        with self._lock:
            self._running = True
        self.serverlog.debug("Starting request loop")
        self.daemon.requestLoop(self.running)

    def close(self):
        """
        Close down the server.
        If we're running this by itself, this gets called by the signal handler.

        If we're running the server's daemon's requestLoop in a thread, then we
        might proceed as follows:

        ```
        s = PyroServer("CoolPyroServer")
        # The true argument is necessary so we don't attempt to call signal handler
        t = threading.Thread(target=s.connect, args=('localhost', 9090, True))
        t.start()
        # Do some other fresh stuff.
        s.close()
        t.join()
        ```
        """
        with self._lock:
            self._running = False
            if self._exposed_obj:
                self.daemon.unregister(self._exposed_obj)
            else:
                self.daemon.unregister(self)
            # if we use daemon.close, this will hang forever in a thread.
            # This might appear to hang.
            self.daemon.shutdown()
            # remove the name/uri from the nameserver so we can't try to access
            # it later when there is no daemon running.
            self.ns.remove(self._name)
            for proc in self._proc:
                proc.kill()



if __name__ == '__main__':

    @Pyro4.expose
    class BasicServer(object):

        def __init__(self):
            pass

        def square(self, x):

            return x**2

    server = Pyro4Server("BasicServer", obj=BasicServer(),loglevel=logging.DEBUG)
    server.launch_server('192.168.0.143', remote_port=2222, remote_username='dean', ns_host='localhost', ns_port=2224)

