from .pausable_thread import PausableThread

class PublisherThread(PausableThread):
    """
    A barebones publisher thread.

    Meant to be subclassed.

    The run method needs to be reimplemented in the subclass.

    """
    def __init__(self, server, thread_name=None, bus=None):
                 # callback_fn=None,
                 # callback_args=(),
                 # callback_kwargs={}):

        PausableThread.__init__(self, name=thread_name)
        self.server = server
        self.bus = bus
        # self.callback_fn = callback_fn
        # self.callback_args = callback_args
        # self.callback_kwargs = callback_kwargs

    def run(self):

        # if self.callback_fn:
        #     res = self.callback_fn(*self.callback_args, **self.callback_kwargs)
        # else:
        raise NotImplementedError("Need to subclass PublisherThread if not using ")