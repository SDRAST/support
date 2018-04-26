import unittest
import logging

class TestImports(unittest.TestCase):

    def test_import_pyro(self):

        from support.pyro import get_device_server
        from support.pyro import Pyro4Server

    def test_import_pyro_async(self):
        from support.pyro import async

    def test_import_pyro_zmq(self):
        from support.pyro import zmq

    def test_import_test(self):

        from support.test import auto_test, AutoTestSuite, Pyro4AutoTestSuite

    def test_import_trifeni(self):
        from support.trifeni import SSHTunnel

if __name__ == '__main__':
    unittest.main()
