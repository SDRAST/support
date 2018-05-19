from __future__ import print_function
import inspect

from automatic_test import AutomaticTest

class AutoTestAnnotation(object):

    """
    This decorator allows for automated testing and simulating of TAMS servers.
    With the sample args, we can build simple will-it-run tests, and with the
    expected output we can build a simple simulator that will return expected_outputs.
    **Thinking I might want to set it up to run with a configuration file,
    such that I can avoid putting long return values in decorotors.**
    """
    def __init__(self, args=None, returns=None):

        if not args: args = ()
        self.sample_args = args
        self.expected_output = returns

    def __call__(self, func):

        # def wrapper(obj, *args, **kwargs):
        #     try:
        #         if obj.simulated:
        #             return self.expected_output
        #         else:
        #             return func(obj, *args, **kwargs)
        #     except AttributeError:
        #         return func(obj, *args, **kwargs)
        #
        # wrapper._sample_args = self.sample_args
        # wrapper._expected_output = self.expected_output
        #
        # return wrapper

        func._sample_args = self.sample_args
        func._expected_output = self.expected_output
        return func
