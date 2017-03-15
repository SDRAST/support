import threading 

import Pyro4

from TAMS_BackEnd.messagebus import PYRO_MSGBUS_NAME
from TAMS_BackEnd.messagebus.messagebus import make_messagebus, MessageBus
from TAMS_BackEnd.util.logging_util import logging_config


class MessageBusThread(threading.Thread):

    """
    Sets up the messagebus server that relays messages 
    between the publisher and subscriber. 
    """
    def __init__(self, ns_host='localhost',ns_port=9090,
    				msg_bus_host='localhost', msg_bus_port=0):
        """
        kwargs:
            - ns_host (str): Nameserver host (localhost)
            - ns_port (int): Nameserver port (9090)
            - msg_bus_host (str): Pyro4 host to bind messagebus to (localhost)
            - msg_bus_port (int): Pyro4 port to bind messagebus to (0, or random)

        """
        threading.Thread.__init__(self)
        self.ns_host = ns_host
        self.ns_port = ns_port
        self.msg_bus_host = msg_bus_host
        self.msg_bus_port = msg_bus_port


        self.logger = logging_config(name=__name__+".MessageBusThread")


    def run(self):

        make_messagebus.storagetype = 'memory'
        daemon = Pyro4.Daemon(host=self.msg_bus_host,
        						port=self.msg_bus_port,unixsocket=None)
        uri = daemon.register(MessageBus)
        self.logger.info("Creating Message Bus, uri = {}".format(uri))
        self.logger.info("Finding nameserver, at host {}, port {}".format(self.ns_host, self.ns_port))
        ns = Pyro4.locateNS(host=self.ns_host,port=self.ns_port)
        ns.register(PYRO_MSGBUS_NAME, uri)
        self.logger.info("Message bus registered on nameserver.")
        daemon.requestLoop()

