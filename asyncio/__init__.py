"""
asyncio - package for asynchronous computing

Notes
=====
Asynchronous computing allows for delayed responses to function or method calls.
Decorator `async_method` adds an argument `callback` for the function which
handles the eventual result.

Example
-------

  import datetime
  import time
  import urllib

  from support.asyncio import async_method
  @async_method
  def query_SIMBAD(url):
    return urllib.request.urlopen(url)

  def SIMBAD_handler(result):
    global response
    print("\nhandler got", result, "at", datetime.datetime.now())
    response = result

  request = "http://simbad.u-strasbg.fr/simbad/sim-basic" +\
            "?Ident=3C273&submit=SIMBAD+search"
  print(datetime.datetime.now())
  query_SIMBAD(request, callback=SIMBAD_handler)
  for count in list(range(30)):
    time.sleep(0.1)
    print(".", end="")
  print(response.readlines()[200:220], "at", datetime.datetime.now())

Doing this with a remote process depends on the way interprocess communications
are done. This package has two modules, for `pyro` and `flaskio`.
"""
import functools
import threading

def async_method(func):
    @functools.wraps(func) # copy all the private attributes of 'func' to 'wrapper'
    def wrapper(*args, **kwargs):
        print("async_method:", func.__name__, "args:", args)
        print("async_method:", func.__name__, "keyword args:",kwargs)
        if 'callback' in kwargs:
            callback = kwargs['callback']
            kwargs.pop('callback')
            # original unwrapped function
            def orig_func(*args, **kwargs):
                res = func(*args, **kwargs)
                callback(res) # invoke callback when done
            # have a thread execute the original function
            mythread = threading.Thread(target=orig_func, args=args, kwargs=kwargs)
            mythread.start()
        else:
            return func(*args, **kwargs)
    return wrapper

