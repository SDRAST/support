"""
Decorator ``async_method`` adds a callback attribute to a function or method

A client invokes a server method with a callback as an additional parameter.
The callback is an object, method, or function which is used by the server to
return data to the client.

The callback mechanism works in its own thread.  In the case of Flask-IO the
socket connection serves as this thread. This is what is implemented here.

The client invokes a function or class on the server. The client's call includes
an argument which provides a client function or class forhandling the response. 
The server function or class does not itself deal with this argument. A 
decorator ``async_method`` provides a wrapper for the functionto handle the 
callback.

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

Notes
=====
This provides a method with extra attributes, one of which is ``_pyroAsync``.
In a version of this which works with Pyro, it tells the ``Pyro5Server`` method
``flaskify_io`` that a server method is wrap the server's method appropriately.
Here, the attribute name is unfortunate sinceit has nothing to do with Pyro. It
just means that the function has been `asynchronized`.
"""
import logging
import eventlet
import functools

import six

__all__ = ["async_method"]

module_logger = logging.getLogger(__name__)
module_logger.debug("async_method module imported")

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
      cb_info     (dict, optional): Callback info provided by the client (None)
      socket_info (dict, optional): Information about the flask_socketio 
                                    socket (None)
    
    Notes
    =====
    Original argument ``func_name`` was removed as it is not used.
    
    ``socket_info`` must be provided if ``cb`` is a string.
    """
    self.logger = logging.getLogger(module_logger.name+"._CallbackProxy")
    self.logger.debug("__init__: called with cb_info=%s, socket_info=%s",
                      cb_info, socket_info)
    if not cb_info:
      # no callback info provided; set the callback attributes to ``None``
      # this is like a simple method call
      self.cb = lambda *args, **kwargs: None
      self.cb_handler = None
    else:
      # callback info provided
      #    make an anonymous dummy function with defaults
      dummy = lambda *args, **kwargs: None
      # now get callback arguments provided
      self.cb_handler = cb_info.get('cb_handler', None)
      cb = cb_info.get('cb', None)
      if not cb:
        # set attribute ``cb`` to the default
        setattr(self, 'cb', dummy)
      if callable(cb):
        # if ``cb`` is a function or method, assign it to the ``cb`` attribute
        setattr(self, 'cb', cb)
      elif isinstance(cb, str):
        # if its is a string then we expect that it came from a socket.
        # get socket info; create a callback function
        if socket_info is not None:
          # get the details of the socket
          self.logger.debug("_CallbackProxy.__init__: socket_info is not None")
          app = socket_info['app']
          socketio = socket_info['socketio']

          def f(cb_name):
            # create a callback function with the provided name string; this
            # function emits a signal to the socket with results of the function
            # call
            def emit_f(*args, **kwargs):
              with app.app_context():
                self.logger.debug(
                "__init__:f.emit_f: calling socket.emit with args=%s, kwargs=%s",
                                    args, kwargs)
                socketio.emit(cb_name, {"args": args, "kwargs": kwargs})
                self.logger.debug("__init__:f.emit_f: socket.emit called")
            return emit_f

          setattr(self, "cb", f(cb))
        else:
          # socket_info not provided; was a handler provided instead? A handler
          # is a class
          self.logger.debug("__init__: socket_info is None")
          if self.cb_handler is not None:
            # a handler was provided
            try:
              # use handler callback method if provided
              setattr(self, 'cb', getattr(self.cb_handler, cb))
              setattr(self, 'cb_name', cb)
            except AttributeError as err:
              setattr(self, 'cb', dummy)
          else:
            self.logger.error("__init__: Need to provide a callback handler")
            raise RuntimeError("no callback handler provided or inferred")

def async_method(func):
  """
  Decorator that declares that a method is to be called asynchronously.
  Methods that are decorated with this class use a common callback interface.

  Examples
  ========
    class Server(Pyro4Server):
      ...
      @async_method
      def long_running_method(self, *args, **kwargs):
        ...
        self.long_running_method.cb(update_info)
        ...
        self.long_running_method.cb(final_info)

  Any method that is decorated with this decorator will have two new attributes::
    ``cb``,  and ``cb_handler``. This assumes no *a priori* information about
    the client to which we are connected.

  Now client side, we would call ``long_running_method`` as follows::

    # Here handler that has some methods/objects registered to it.
    client.long_running_method(*args,cb_info={'cb_handler': handler,
                                              'cb': "long_running_method_cb"})

  Since the callback function needs to wait for a response, it needs a separate
  thread::
  
    import threading
        
    class Handler(object):
      def __init__(self):
        self.daemon_thread = threading.Thread(target=self.daemon.requestLoop)

      def long_running_method_cb(self, res)
        print(res)  
              
  If the communication channel is Pyro, then we have to make sure that the 
  client has registered the ``long_running_method_cb`` method:

    import threading
    import Pyro4

    class PyroHandler(Handler):
      def __init__(self):
        self.daemon = Pyro4.Daemon()
        self.uri = self.daemon.register(self) 
        Handler.__init__(self)
        
    uri = "" # some Pyro URI for the server with long_running_method registered.

    handler = Handler()
    proxy = Pyro4.Proxy(uri)

  In either case, the client invokes the remote method the same way:
  
    proxy.long_running_method(cb_info={"cb_handler": handler.uri,
                                       "cb":         "long_running_method_cb"})

  For a Pyro channel, one can pass a Pyro Proxy object referring to the handler:
  
    # long_running_method:
    proxy.long_running_method(cb_info={"cb_handler": Pyro4.Proxy(handler.uri),
                                       "cb":         "long_running_method_cb"})

  Notes
  =====
  You can also decorate ``__init__`` functions, but the behavior is different.
  Instead of setting *function* attributes, we set *instance attributes*. This
  is mostly useful for worker threads:

    class Worker(threading.Thread):

      @async_method
      def __init__(self,*args, **kwargs):
        threading.Thread.__init__(self)

      def run(self):
        ...
        self.cb(update_info)
        ...
        self.cb(cb_info)

  Args
  ====
    func (callable): Function or method we'd like to decorate
  """
  @functools.wraps(func)
  def wrapper(self, *args, **kwargs):
    """
    Process cb_info dictionary, setting function attributes accordingly.
    The decorator assumes a cb_info dictionary with the following keys:

    cb_info:
      cb_handler (Thread): The handler object
      cb         (str):    The name of the final callback

      Args:
        args (list/tuple): passed to func
        kwargs (dict): kwargs dictionary containing "cb_info"

      Returns:
        result of decorated function.
    """
    name = func.__name__
    # the decorator can be applied to a function, method, or class.  In the
    # latter case the decorated method is ``__init__()``.
    if name == "__init__":  # We're decorating a class, namely a worker class
       this = self
    else:
       this = wrapper
    module_logger.debug("async.wrapper.{}: kwargs: {}".format(name, kwargs))
    # the optional keyword arguments ``cb_info`` and ``socket_info`` do not 
    # belong to the decorated function. Extract the information if it exists and
    # then remove those arguments
    cb_info = kwargs.pop("cb_info", None)
    socket_info = kwargs.pop('socket_info', None)

    # the callback and socket arguments are made attributes
    this.cb_info = cb_info
    this.socket_info = socket_info
    module_logger.debug("async.wrapper.{}: cb_info: {}".format(
                        name, this.cb_info))
    module_logger.debug("async.wrapper.{}: socket_info: {}".format(
                        name, this.socket_info))
    cur_handler = getattr(self, "cb_handler", None)
    
    if this.cb_info:
      # there is ``cb_info``
      if "cb_handler" not in this.cb_info:
        # but is does not have a handler class
        this.cb_info["cb_handler"] = cur_handler
    async_cb = _CallbackProxy(cb_info    =this.cb_info,
                              socket_info=this.socket_info)
    this.cb = async_cb.cb
    this.cb_handler = async_cb.cb_handler
    try:
      this.cb_name = async_cb.cb_name
    except AttributeError:
      pass
    return func(self, *args, **kwargs)

  wrapper._pyroAsync = True
  return wrapper
    
