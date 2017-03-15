"""
Pyro4 compatibility layer for RA's support module.
"""

import logging
import time
import os
import signal
import re

import Pyro4

from support.tunneling import Tunnel
from support.process import invoke, search_response, BasicProcess
from support.logs import logging_config
from pyro3_util import full_name

module_logger = logging.getLogger(__name__)
logging_config(logger=module_logger, loglevel=logging.DEBUG)

class Pyro4ObjectDiscoverer(object):
    """
    An class used to represent a set of ssh tunnels to a Pyro4 object located remotely.
    This is meant to be a replacement for Tom's support.pyro.get_device_server function.
    This does not just work for JPL tunnels, however. We can tunnel to arbitrary IP addresses
    and gain access to Pyro objects as well.

    Example Usage:
    If we want to get the URI of the APC Pyro object on crux, we would do the following:

    ```
    crux_tunnel = Pyro4ObjectDiscoverer("crux", remote_ns_host='localhost', remote_ns_port=50000,
                                        tunnel_username='ops', username='ops')
    apc = crux_tunnel.get_pyro_object('APC')
    ```

    To create the APC client, we would have to send the URI to TAMS_BackEnd.clients.APCClient:

    ```
    apc_client = TAMS_BackEnd.clients.APCClient(proxy=apc)
    # now we can call APC methods.
    apc_client.get_azel()
    ```

    Let's say I wanted to find an object on a remote server, but that remote server wasn't on
    the JPL network. I might do the following:

    ```
    remote_discoverer = Pyro4ObjectDiscoverer('192.168.0.2', remote_ns_host='localhost', remote_ns_port=2224,
                                                username='user', port=2222)
    basic_server = remote_discoverer.get_pyro_object('BasicServer')
    print(basic_server.name)
    >> u'BasicServer'
    ```


    Public Attributes:
        remote_server_name (str): The name or ip address of the remote server
        remote_port (int): The remote port to be used for tunneling.
            This should be a listening port on the remote server.
        remote_ns_port (int): The remote nameserver port
        remote_ns_host (str): The remote nameserver host name
        local_forwarding_port (int): The local port on which to listen;
            the local port we used for port forwarding
        tunnel_username (str): The username for the creation of a support.tunneling.Tunnel.
            This could be, for example, a login to the JPL ops gateway.
        username (str): The username to use for port forwarding. On crux, this would be 'ops'
        logger (logging.getLogger): Return value of logging_util.logging_config
        processes (list): A list of the running processes. These processes might be
            subprocess.Popen instances, or BasicProcess instances.
        uris (dict): A dictionary of Pyro4 URI objects. The keys are the server names
            on the remote nameserver.
    Public Methods:
        get_pyro_object_uri: Creates a tunnel to the remote server (if not in place already)
            and then creates tunnels to the nameserver and the requested object.
        cleanup: Kill the processes that are associated with the nameserver and the requested
            object(s).

    Private Attributes:
        _local (bool): Is this a local connection (ie, on this same computer)?
    """

    def __init__(self,
                 remote_server_name,
                 remote_port=22,
                 remote_ns_port=9090,
                 remote_ns_host='localhost',
                 local_forwarding_port=None,
                 tunnel_username=None,
                 username=None,
                 **kwargs):
        """
        Create a Pyro4Tunnel object.
        Args:
            remote_server_name (str): Name or ip of remote server.
        Keyword Args:
            remote_port (int): The remote listening port.
            remote_ns_port (int): The remote nameserver port
            remote_ns_host (str): The remote nameserver host name
            local_forwarding_port (int): The local port on which to listen;
                the local port we used for port forwarding
            tunnel_username (str): The username for the creation of a support.tunneling.Tunnel.
                This could be, for example, a login to the JPL ops gateway.
            username (str): The username to use for port forwarding. On crux, this would be 'ops'
            **kwargs: For logging_util.logging_config
        """
        self.remote_server_name = remote_server_name
        self.remote_ns_host = remote_ns_host
        self.remote_ns_port = remote_ns_port
        self.local_forwarding_port = local_forwarding_port
        self.tunnel_username = tunnel_username
        self.username = username

        logger = logging.getLogger(module_logger.name + ".Pyro4Tunnel")
        self.logger = logging_config(logger=logger, **kwargs)
        self.processes = []
        self._local = False

        if remote_server_name in full_name.keys():
            self.tunnel = Tunnel(remote_server_name, username=tunnel_username)
            self.remote_port = self.tunnel.port
            self.remote_server_ip = 'localhost'
        elif remote_server_name == 'localhost':
            self._local = True
        else:
            self.tunnel = None
            self.remote_server_ip = remote_server_name
            self.remote_port = remote_port

        if not self.local_forwarding_port:
            self.local_forwarding_port = self.remote_ns_port

        if not self._local:
            self.ns = self.find_nameserver(self.remote_server_ip,
                                           self.remote_ns_host,
                                           self.remote_ns_port,
                                           self.local_forwarding_port,
                                           self.remote_port,
                                           self.username)
        elif self._local:
            self.ns = Pyro4.locateNS(host=self.remote_ns_host, port=self.remote_ns_port)

        self.uris = {}

    def find_nameserver(self,
                        remote_server_ip,
                        remote_ns_host,
                        remote_ns_port,
                        local_forwarding_port,
                        remote_port,
                        username):
        """
        Get the nameserver sitting on remote_ns_port on the remote server.
        We explicitly pass arguments instead of using attributes so we can
        use this method outside of __init__.
        Args:
            remote_server_ip (str): The IP address of remote server.
            remote_ns_host (str): The hostname of the remote nameserver
                (I don't imagine a situation in which this would change)
            remote_ns_port (int): The port of the remote nameserver
            local_forwarding_port (int): The local port to use for forwarding.
            remote_port (int): A listening port on remote
        Returns:
            Pyro4.naming.NameServer instance or
            None if can't be found.
        """

        self.logger.debug("Remote server IP: {}".format(remote_server_ip))
        proc_ns = arbitrary_tunnel(remote_server_ip, 'localhost', local_forwarding_port,
                                   remote_ns_port, username=username, port=remote_port)

        self.processes.append(proc_ns)
        if check_connection(Pyro4.locateNS, kwargs={'host': remote_ns_host, 'port': local_forwarding_port}):
            ns = Pyro4.locateNS(host=remote_ns_host, port=local_forwarding_port)
            return ns
        else:
            self.logger.error("Couldn't connect to the remote Nameserver", exc_info=True)
            return None

    def get_pyro_object(self, remote_obj_name):
        """
        Say we wanted to connect to the APC server on crux, and the APC server
        was sitting on nameserver port 50000 on crux. We could do this as follows:

        Args:
            remote_obj_name (str): The name of the Pyro object.
        Returns:
            Pyro4.URI corresponding to requested pyro object, or
            None if connections wasn't successful.
        """
        obj_uri = self.ns.lookup(remote_obj_name)
        obj_proxy = Pyro4.Proxy(obj_uri)
        if self._local:
            return obj_proxy
        elif not self._local:
            obj_host, obj_port = obj_uri.location.split(":")
            proc_obj = arbitrary_tunnel(self.remote_server_ip, 'localhost', obj_port,
                                        obj_port, username=self.username, port=self.remote_port)

            self.processes.append(proc_obj)
            if check_connection(getattr, args=(obj_proxy, 'name')):  # We are trying to get property, hence getattr
                self.uris[remote_obj_name] = obj_uri
                return Pyro4.Proxy(obj_uri)
            else:
                self.logger.error("Couldn't connect to the object", exc_info=True)
                return None

    def cleanup(self):
        """
        Kill all the existing tunnels that correspond to processes created
        Returns:
            None
        """
        for proc in self.processes:
            proc.kill()


def check_connection(callback, timeout=1.0, attempts=10, args=(), kwargs={}):
    """
    Check to see if a connection is viable, by running a callback.
    Args:
        callback: The callback to test the connection
    Keyword Args:
        timeout (float): The amount of time to wait before trying again
        attempts (int): The number of times to try to connect.
        args: To be passed to callback
        kwargs: To be passed to callback

    Returns:
        bool: True if the connection was successful, False if not successful.
    """
    attempt_i = 0
    while attempt_i < attempts:
        try:
            callback(*args, **kwargs)
        except Exception as e:
            module_logger.debug("Connection failed: {}. Timing out".format(e))
            time.sleep(timeout)
            attempt_i += 1
        else:
            module_logger.info("Successfully connected.")
            return True
    module_logger.error("Connection failed completely.")
    return False


def arbitrary_tunnel(remote_ip, relay_ip,
                     local_port, remote_port,
                     port=22, username=''):
    """
    Create an arbitrary ssh tunnel, after checking to see if a tunnel already exists.
    This just spawns the process that creates the tunnel, it doesn't check to see if the tunnel
    has successfully connected.

    Executes the following command:
    ```
    ssh  -p {port} -l {username} -L {local_port}:{relay_ip}:{remote_port} {remote_ip}
    ```
    Args:
        remote_ip (str): The remote, or target ip address.
            For local port forwarding this can be localhost
        relay_ip (str): The relay ip address.
        local_port (int): The local port on which we listen
        remote_port (int): The remote port on which we listen
    Keyword Args:
        port (int): The -p argument for ssh
        username (str): The username to use for tunneling
    Returns:
        subprocess.Popen: if there isn't an existing process corresponding to tunnel:
            or else BasicProcess instance, the corresponds to already running tunnel command.

    """
    command = "ssh -l {0} -p {1} -L {2}:{3}:{4} {5}".format(username,
                                                            port, local_port,
                                                            relay_ip, remote_port, remote_ip)

    command_relay = "{0}:{1}:{2} {3}".format(local_port, relay_ip, remote_port, remote_ip)
    module_logger.debug(command_relay)
    ssh_proc = search_response(['ps', 'x'], ['grep', 'ssh'])
    # re_pid = re.compile("\d+")
    # re_name = re.compile("ssh.*")
    for proc in ssh_proc:
        if command_relay in proc:
            module_logger.debug("Found matching process: {}".format(proc))
            # proc_id = int(re_pid.findall(proc)[0])
            # proc_name = re_name.findall(proc)[0]
            return BasicProcess(ps_line=proc, command_name='ssh')
            # return BasicProcess(name=proc_name, pid=proc_id)

    module_logger.debug("Invoking command {}".format(command))
    p = invoke(command)
    return p


if __name__ == '__main__':
    pass