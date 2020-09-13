"""
Decorator async_method adds a callback attribute to a function or method

A client invokes a server method with a callback as an additional parameter.
The callback is an object, method, or function which is used by the server to
return data to the client

Examples
========
  class Server(object):
    ...
    @async_method
    def long_running_method(self, *args, **kwargs):
      ...
      self.long_running_method.cb(update_info)
      ...
      self.long_running_method.cb(final_info)

"""
import logging
import functools

import six

__all__ = ["async_method"]

module_logger = logging.getLogger(__name__)

class _CallbackProxy(object):
    """
    A container for callbacks.
    
    This is only used by the ``async_method()`` decorator.

    Attributes:
        cb (callable): a callable that represents a client-side callback
        cb_handler (): the proxy which has _RemoteMethods that is the 
                       ``cb()`` attributes.
    """
    def __init__(self, cb_info=None, socket_info=None):
        """
        Args:
            cb_info     (dict, optional): Callback info (None)
            socket_info (dict, optional): Information about the flask_socketio 
                                          socket (None)
        """
        if not cb_info:
            # set the dict values to ``None``
            self.cb = lambda *args, **kwargs: None
            self.cb_handler = None
        else:
            dummy = lambda *args, **kwargs: None
            self.cb_handler = cb_info.get('cb_handler', None)
            cb = cb_info.get(key, None)
            if not cb:
                setattr(self, key, dummy)
            if callable(cb):
                setattr(self, key, cb)
            elif isinstance(cb, six.string_types):
                if socket_info is not None:
                    module_logger.debug(
                             "_CallbackProxy.__init__: socket_info is not None")
                    app = socket_info['app']
                    socketio = socket_info['socketio']

                    def f(cb_name):
                        def emit_f(*args, **kwargs):
                            with app.app_context():
                                # module_logger.debug("_CallbackProxy.__init__:f.emit_f: calling socket.emit")
                                socketio.emit(cb_name, {"args": args, "kwargs": kwargs})
                                # module_logger.debug("_CallbackProxy.__init__:f.emit_f: socket.emit called")
                        return emit_f
                    setattr(self, key, f(cb))
                else:
                    module_logger.debug("_CallbackProxy.__init__: socket_info is None")
                    if self.cb_handler is not None:
                        try:
                            setattr(self, key, getattr(self.cb_handler, cb))
                            setattr(self, key+"_name", cb)
                        except AttributeError as err:
                            setattr(self, key, dummy)
                    else:
                        raise RuntimeError("__init__: Need to provide a callback handler")


def async_method(func):
    """
    Decorator that declares that a method is to be called asynchronously.
    Methods that are decorated with this class use a common callback interface.

    Examples:

    .. code-block:: python

        class Server(Pyro4Server):

            ...
            @async_method
            def long_running_method(self, *args, **kwargs):
                ...
                self.long_running_method.cb(update_info)
                ...
                self.long_running_method.cb(final_info)



    Any method that is decorated with this decorator will have three new attributes:
    "cb",  and "cb_handler". This assumes no a priori information about
    the client to which we are connected.

    Now client side, we would call ``long_running_method`` as follows:

    .. code-block:: python

        # Here handler is some Pyro4.Daemon that has some methods/objects registered to it.
        client.long_running_method(*args,cb_info={'cb_handler':handler,
                                            "cb":"long_running_method_cb"})


    We have to make sure that our client has registered the `long_running_method_cb`
    method:

    .. code-block:: python

        import threading

        import Pyro4

        class Handler(object):

            def __init__(self):
                self.daemon = Pyro4.Daemon()
                self.uri = self.daemon.register(self)
                self.daemon_thread = threading.Thread(target=self.daemon.requestLoop)

            def long_running_method_cb(self, res)
                print(res)


        uri = "" # some valid Pyro4 URI refering to a server with long_running_method registered.

        handler = Handler()
        proxy = Pyro4.Proxy(uri)

        proxy.long_running_method(cb_info={"cb_handler":handler.uri,
                                            "cb":"long_running_method_cb"})

        # Alternatively, we can pass a Proxy object refering to the handler to
        # long_running_method:

        proxy.long_running_method(cb_info={"cb_handler":Pyro4.Proxy(handler.uri),
                                            "cb":"long_running_method_cb"})


    Note that you can also decorate "__init__" functions, but the behavior is different.
    Instead of setting *function* attributes, we set *instance attributes*. This is mostly
    useful for worker threads:

    .. code-block:: python

        class Worker(threading.Thread):

            @async_method
            def __init__(self,*args, **kwargs):
                threading.Thread.__init__(self)

            def run(self):
                ...
                self.cb(update_info)
                ...
                self.cb(cb_info)

    Args:
        func (callable): Function or method we'd like to decorate
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        """
        Process cb_info dictionary, setting function attributes accordingly.
        The decorator assumes a cb_info dictionary with the following keys:

        cb_info:
            cb_handler (Pyro4.Daemon): The handler object
            cb (str): The name of the final callback

        Args:
            args (list/tuple): passed to func
            kwargs (dict): kwargs dictionary containing "cb_info"

        Returns:
            result of decorated function.
        """
        name = func.__name__

        if name == "__init__":  # We're decorating a class, namely a worker class
            this = self
        else:
            this = wrapper
        module_logger.debug(
            "async.wrapper.{}: kwargs: {}".format(name, kwargs))
        cb_info = kwargs.pop("cb_info", None)
        socket_info = kwargs.pop('socket_info', None)

        this.cb_info = cb_info
        this.socket_info = socket_info
        module_logger.debug("async.wrapper.{}: cb_info: {}".format(
            name, this.cb_info))
        module_logger.debug("async.wrapper.{}: socket_info: {}".format(
            name, this.socket_info))
        cur_handler = getattr(self, "cb_handler", None)
        if this.cb_info:
            if "cb_handler" not in this.cb_info:
                this.cb_info["cb_handler"] = cur_handler
        async_cb = _CallbackProxy(
            cb_info=this.cb_info,
            socket_info=this.socket_info,
        )
        this.cb = async_cb.cb
        this.cb_handler = async_cb.cb_handler
        try:
            this.cb_name = async_cb.cb_name
        except AttributeError:
            pass

        return func(self, *args, **kwargs)

    wrapper._pyroAsync = True
    return wrapper
    