from __future__ import print_function

import Pyro4

from support.logs import logging_config

class Pyro4Client(object):
    """
    """

    def __init__(self, proxy=None, host='localhost', port=9090, name="", logfile=None, logger=None):
        """Intialize a connection the Pyro server.

        For example, we might connect to the spectrometer server
        as follows:
        ```
        spec_client = PyroClient('localhost',9090,'specserver')
        ```

        args:
            - host (str): The host name for the nameserver.
            - port (int): The port for the nameserver.
            - name (str): The name of the server.
        kwargs:
            - logfile (str): The name of the logfile.
            - logger (logging.getLogger): An existing logger instance

        """
        if not proxy:
            uri = "PYRONAME:{}@{}:{}".format(name, host, port)
            self.server = Pyro4.Proxy(uri)
        else:
            self.server = proxy

        self.clientlog = logging_config("", logfile=logfile, logger=logger)

    def __getattr__(self, attr):
        """
        This allows us to interact with the server as if it were a normal
        Python object.
        args:
            - attr (str): The attribute we're trying to access
        """
        return getattr(self.server, attr)

        # def __getattr__(self, callback):
        #   """
        #   This makes is so we can call server methods directly from the client.
        #   It distinguishes between Pyro futures calls, and server properties.
        #   Additionally, by calling this method, we immediately call for the the value of
        #   the Pyro future object.
        #   args:
        #       - callback (str): The name of the server attribute we'd like to
        #           get.
        #   returns:
        #       - lambda: if callback is a Pyro async method instance, then return a lambda
        #           that simply grabs the value from the Pyro future result.
        #       - Otherwise, simply return the value of the server attribute.
        #   """
        #   attr = getattr(self.server, callback)
        #   if (isinstance(attr, Pyro4.core._AsyncRemoteMethod)):
        #       return lambda *args, **kwargs: getattr(self.server, callback)(*args, **kwargs).value
        #   else:
        #       return attr

        # Pyro4.config.SERVERTYPE = 'thread'

        # def test_method():
        #   time.sleep(1.0)

        # def method1_async(server):
        #   res = server.method1()
        #   return res.value

        # def main():

        #   # uri = "PYRONAME:specserver@{}:{}".format("localhost", 9090)
        #   # server = Pyro4.Proxy(uri)
        #   # async_server = Pyro4.async(server)
        #   client = Client("localhost", 9090)
        #   print(client.method1())
        #   print(client.status)
        #   # w1 = threading.Thread(target=client.method1)
        #   # w2 = threading.Thread(target=client.method2)
        #   # w3 = threading.Thread(target=client.method2)

        #   # w1.start()
        #   # time.sleep(0.001)
        #   # w2.start()
        #   # w3.start()

        #   # w1.join()
        #   # w2.join()
        #   # w3.join()


        # if __name__ == '__main__':
        #   main()
