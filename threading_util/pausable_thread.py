import logging
import threading
import time

module_logger = logging.getLogger(__name__)

__all__ = ["iterativeRun", "Pause", "PausableThread", "PausableThreadCallback"]

def iterativeRun(run_fn):
    """
    A decorator for running functions repeatedly inside a PausableThread.
    Allows one to pause and stop the thread while its repeatedly calling
    the overriden run function.

    Args:
        run_fn (callable): the overridden run function from PausableThread
    Returns:
        callable: wrapped function
    """
    def wrapper(self):
        while True:
            if self.stopped():
                break
            if self.paused():
                time.sleep(0.001)
                continue
            else:
                self._running.set()
                run_fn(self)
                self._running.clear()
    return wrapper


class Pause(object):
    """
	A context manager for pausing threads.
	
    This starts by pausing an input thread or threads and unpausing them when
    code inside block has been called.

	This makes sure that when we unpause the thread when we're done
	doing whatever task we needed.

    Attributes:
        thread (dict): A collection of threads to pause and unpause.
        init_pause_status (dict): The initial state of the threads in
            the thread attribute.
	"""

    def __init__(self, pausable_thread):
        """		    
        Args:
            pausable_thread (list, PausableThread): An instance, or list of
                instances of PausableThread. If we pass ``None``, then this gets
                dealt with properly down stream.
        """
        self.thread = pausable_thread
        if not isinstance(self.thread, dict):
            # if the argument is not a dict, make it one
            self.thread = {'thread': self.thread}

        self.init_pause_status = {}
        for name in list(self.thread.keys()):
            if self.thread[name]:
                self.init_pause_status[name] = self.thread[name].paused()
            else:
                self.init_pause_status[name] = None
        # self.init_pause_status = {name: self.thread[name].paused() for name in self.thread.keys()}

    def __enter__(self):
        """
        Pause the thread in question, and make sure that whatever
        functionality is being performing is actually stopped.
        """
        for name in list(self.thread.keys()):
            t = self.thread[name]
            if t:
                # if there really is a thread
                if not self.init_pause_status[name]:
                    # and it is not already paused
                    t.pause()
            else:
                pass
        # now make sure that they're actually paused.
        for name in list(self.thread.keys()):
            t = self.thread[name]
            if t:
                # if there really is a thread
                while self.thread[name].running():
                    # wait until it is no longer running
                    time.sleep(0.001)
            else:
                pass

    def __exit__(self, *args):
        """
        Unpause the thread
        """
        for name in list(self.thread.keys()):
            t = self.thread[name]
            if t:
                # if there really is a thread
                if not self.init_pause_status[name]:
                    self.thread[name].unpause()
            else:
                pass

class PausableThread(threading.Thread):
    """
    A pausable stoppable thread.
    
	It also has a running flag that can be used to determine if the process is 
	still running.

    Attributes:
        _running ():
        name (str):                 name of thread, if any
        logger (logging.getLogger): logging instance.
        _lock (threading.Lock):     thread's internal lock
        _pause (threading.Event):   setting and clearing this indicates to
            pause or unpause thread.
        _stop (threading.Event):    setting this stops thread.
        _running (threading.Event): setting this indicates thread is
            currently executing "run" method.
	"""
    def __init__(self, name=None, **kwargs):
        """
        create a pausable thread
        
        Args:
            name (str): name of thread.
			**kwargs: To be passed to
		"""
        threading.Thread.__init__(self)

        self.name = name
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        # create events for the thread states
        self._pause = threading.Event()
        self._stop = threading.Event()
        self._running = threading.Event()

    def stop(self):
        """
		Stop the thread from running all together. Make
		sure to join this up with threading.Thread.join()
		"""
        self._stop.set()

    def pause(self):
        self._pause.set()

    def unpause(self):
        self._pause.clear()

    def stopped(self):
        return self._stop.isSet()

    def paused(self):
        return self._pause.isSet()

    def running(self):
        return self._running.isSet()


class PausableThreadCallback(threading.Thread):
    """
	A thread that runs the same callback over an over again, with some
	predetermined wait time.
	This thread can be paused, unpaused, and stopped in a thread-safe manner.
	"""

    def __init__(self, callback, name=None, *args):

        threading.Thread.__init__(self)

        self.name = name
        self.callback = callback
        self.args = args

        self._pause = threading.Event()
        self._stop = threading.Event()
        self._running = threading.Event()

    def run(self):

        while True:
            if self.stopped():
                break

            if self.paused():
                time.sleep(0.001)
                continue
            else:
                self._running.set()
                self.callback(*self.args)
                self._running.clear()

    def stop(self):

        self._stop.set()

    def pause(self):

        self._pause.set()

    def unpause(self):

        self._pause.clear()

    def stopped(self):

        return self._stop.isSet()

    def paused(self):

        return self._pause.isSet()

    def running(self):

        return self._running.isSet()
