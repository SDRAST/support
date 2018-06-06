import unittest
import datetime
import time
import logging

from support.logs import setup_logging

from support.control_flow import ControlFlowMixin

class MixedIn(ControlFlowMixin):

    def generator(self):
        for i in xrange(10):
            time.sleep(0.1)
            yield i

    def generator_func(self):
        def generator():
            for i in xrange(3):
                time.sleep(0.1)
                yield i
        return generator

class TestControlFlowMixin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.logger = logging.getLogger("TestControlFlowMixin")
        cls.obj = MixedIn()

    def test_until_run(self):
        now = self.obj.now()
        later = now + datetime.timedelta(seconds=1)
        for e in self.obj.until(later).run(self.obj.generator()):
            self.logger.debug("test_until_run: {}".format(e))

    def test_until_loop(self):
        now = self.obj.now()
        later = now + datetime.timedelta(seconds=0.8)
        for e in self.obj.until(later).loop(self.obj.generator_func()):
            self.logger.debug("test_until_loop: {}".format(e))

    def test_at_run(self):
        now = self.obj.now()
        later = now + datetime.timedelta(seconds=1)
        for e in self.obj.at(later).run(self.obj.generator):
            self.logger.debug("test_at_run: {}".format(e))


if __name__ == "__main__":
    setup_logging(logging.getLogger(""),logLevel=logging.DEBUG)
    unittest.main()
