from __future__ import print_function
import logging

import Pyro4

from support.logs import logging_config

class Pyro4Client(object):
    """
    A simple wrapper around Pyro4.Proxy.
    This is meant to be subclassed. Client side methods are meant to be put here.
    """

    def __init__(self, proxy, **kwargs):
        """
        Intialize a connection the Pyro server.

        For example, we might connect to the spectrometer server
        as follows:
        ```
        spec_client = PyroClient()
        ```
            - logfile (str): The name of the logfile.
            - logger (logging.getLogger): An existing logger instance

        """
        self.server = proxy
        self.logger = logging_config(**kwargs)

    def __getattr__(self, attr):
        """
        This allows us to interact with the server as if it were a normal
        Python object.
        args:
            - attr (str): The attribute we're trying to access
        """
        return getattr(self.server, attr)
