from pyro3_util import *
try:
    from Pyro4.util import SerializerBase
    from pyro4_util import Pyro4ObjectDiscoverer, arbitrary_tunnel, check_connection
    from pyro4_server import Pyro4Server, Pyro4PublisherServer, Pyro4ServerError, blocking, non_blocking
    from pyro4_client import Pyro4Client
    # SerializerBase.register_class_to_dict(Pyro4Message, Pyro4Message.to_dict)
    # SerializerBase.register_dict_to_class("support.pyro.pyro4_server.Pyro4Message", Pyro4Message.from_dict)
except ImportError as err:
    # There are some virtualenvs where Pyro4 isn't installed.
    if "Pyro4" in str(err):
        pass
    else:
        print(err)
