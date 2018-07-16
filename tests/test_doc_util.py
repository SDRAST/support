from __future__ import print_function
import unittest

from support.doc_util import get_help, _get_method_doc


class TestClass(object):

    @property
    def prop1(self):
        """
        prop1 documentation
        """
        return self._prop1

    def method1(self):
        """
        method1 documentation
        """
        pass

    def method2(self, arg1, kwarg0=None):
        """
        method2 documentation
        """
        pass

    def method3(self, *args, **kwargs):
        """
        method3 documentation
        """
        pass

    def method_no_doc(self):
        pass

    @staticmethod
    def static_method1(arg1):
        """
        static_method1 documentation
        """
        pass

    @classmethod
    def class_method1(cls, arg1):
        """
        class_method1 documentation
        """
        pass



class TestDocUtil(unittest.TestCase):

    def test__get_method_doc(self):
        self.assertTrue(isinstance(_get_method_doc(TestClass.method1), str))

    # @unittest.skip("")
    def test_get_help(self):
        help = get_help(TestClass)
        self.assertTrue(isinstance(help, str))
        print(help)


if __name__ == "__main__":
    unittest.main()
