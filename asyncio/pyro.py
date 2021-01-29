"""
pyro - provides a callback mechanism for a Pyro5 client/server channel.

This defines a class `CallbackReceiver` as a Pyro server on the client which
can be invoked by the server to return data to the client.

This also defines a decorator `@async_method` which enables server methods to
access and use the callback without being specifically coded to do so.

Notes
=====
Pyro allows Python objects on a remote host to be accessed as if they were
local. Pyro can handle functions and class instances.  It can access `exposed`
methods of a remote class instance. It can also handle basic Python objects such
as dicts and lists.  However, there are limitations and one is that it cannot
pass class attributes or methods.

Pyro creates a server daemon which operates on a specified socket.  The client
creates a Pyro proxy for the server. The client invokes methods of classes that
are known to the server. The callback mechanism is a Pyro server on the client. 
The client provides the server with this object, and the server can then invoke
it to return data.

Example
-------
In this example, `centralServer` has a method `start_spec_scans()` which is
decorated with `@async_method.

  import logging
  import Pyro5.api

  from support.asyncio.pyro import CallbackReceiver

  uri='PYRO:DSS-43@localhost:50015'
  centralServer = Pyro5.api.Proxy(uri)
  cb_receiver = CallbackReceiver()

  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)

  centralServer.start_spec_scans(n_scans=1, n_spectra=3, int_time=1,
                                 log_n_avg=16, callback=cb_receiver)
  cb_receiver.queue.get()
  cb_receiver.queue.get()
  cb_receiver.queue.get()
"""
import functools
import logging
import Pyro5.api
import queue
import sys
import threading

logger = logging.getLogger(__name__)

class CallbackReceiver(object):
  """
  Class passed to remote server to handle the data transfer
  
  The class can be initialized with a queue to get the data.  If not provided,
  it will create its own queue.
  """
  def __init__(self, parent=None):
    """
    Initialize the receiver with a queue on which the server puts the data
    
    Args
    ====
      parent - the object of which this is an attribute
    """
    self.parent = parent
    self.logger = logging.getLogger(logger.name+".CallbackReceiver")
    self.queue = queue.Queue()
    self.daemon = Pyro5.api.Daemon()
    self.uri = self.daemon.register(self)
    self.lock = threading.Lock()
    with self.lock:
            self._running = True
  
    # the argument passed to requestLoop() is a condition which must return
    # True for the loop to continue running.
    self.thread = threading.Thread(target=self.daemon.requestLoop, 
                                   args=(self.running,) )
    self.thread.daemon = True
    self.thread.start()    

  @Pyro5.api.expose
  def running(self):
    """
    Get running status of server
    """
    with self.lock:
      return self._running
  
  @Pyro5.api.expose
  @Pyro5.api.callback
  def finished(self, who, msg):
    """
    Method used by the remote server to return the data
    
    Parent must have a thread waiting to do queue.get()
    
    Because this runs in the server namespace, no logging is possible.
    """
    self.logger.debug('finished: got result from %s', who)
    self.queue.put((who,msg)) # server puts data on the queue
    

def dummy(*args, **kwargs):
    pass
    
def async_method(func):
    """
    This adds a keyword argument `callback` to `func`. `callback` is an 
    instance of the class `CallbackReceiver`.
    
    `callback.finished` becomes an attribute `cb` of the decorated function.
    It invokes the `finished()` of the `CallbackReceiver` instance, which
    is represented as attribute `caller`.
    """
    @functools.wraps(func) # copy all the private attributes of 'func' to 'wrapper'
    def wrapper(*args, **kwargs):
        logger.debug("%s args: %s",   func.__name__, args)
        logger.debug("%s kwargs: %s", func.__name__, kwargs)
        if 'callback' in kwargs:
            callback = kwargs['callback']
            wrapper.cb = functools.partial(callback.finished, wrapper.__name__)
            wrapper.caller = callback
            kwargs.pop('callback')
            # original unwrapped function
            logger.debug("%s args: %s",   func.__name__, args)
            def orig_func(*args, **kwargs):
                callback._pyroClaimOwnership()
                res = func(*args, **kwargs)
                return res
            # have a thread execute the original function
            mythread = threading.Thread(target=orig_func, args=args,
                                        kwargs=kwargs)
            mythread.start()
        else:
            wrapper.cb = dummy # handles undefined func.cb calls
            return func(*args, **kwargs)
    return wrapper


