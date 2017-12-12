import unittest
import logging
import inspect

from support.logs import logging_config

module_logger = logging.getLogger()


class AutomaticTest(object):
    """
    Class for creating automated tests.
    For methods to automatable, they have to have the @AutoTestAnnotation decorator
    """

    def __init__(self, cls, server_cls):
        """
        Args:
            cls (class): The class whose methods we are trying to automate.
            server_cls (class): The class of the server whose methods we are testing.
        """
        self.cls = cls
        self.server_cls = server_cls
        self.logger = logging_config(module_logger.name + ".AutomaticTest", loglevel=logging.DEBUG)

    def _make_test_fn(self, func_name):

        cls_func = getattr(self.server_cls, func_name)

        test_fn_name = "test_{}".format(func_name)

        # self.logger.debug(cls_func)

        def test_function(unittest_obj):
            return cls_func(unittest_obj.server, *cls_func._sample_args)

        try:
            exposed = cls_func._pyroExposed
            args = cls_func._sample_args
            self.logger.info("Making automatic test for method: {}".format(func_name))
            return test_function, test_fn_name
        except AttributeError:
            # self.logger.debug("{} doesn't have IOAnnotation decorator".format(func_name))
            return None, test_fn_name

    def create_test_suite(self):
        suite = unittest.TestSuite()
        for func_name in dir(self.server_cls):
            if (callable(getattr(self.server_cls, func_name)) and not
                                    func_name.startswith("__") and not
                                    func_name.startswith("_")):

                test_fn, test_fn_name = self._make_test_fn(func_name)
                if test_fn:
                    setattr(self.cls, test_fn_name, test_fn)
                    suite.addTest(self.cls(test_fn_name))

        return suite
