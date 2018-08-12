import unittest
import os

from support.hdf5_util import HDF5Mixin

class Writer(HDF5Mixin):
    def __init__(self):
        self.name = "Writer"
        self.base_data_dir = os.getcwd()
        self.data_dir = None
        self.data_file_obj = None
        self.date_file_name = None
        self.data_file_path = None
        self.file_attr_keys = ["test_key"]
        self.header = {"test_key":"test_value"}

class TestHDF5Mixin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        writer = Writer()
        cls.writer = writer

    def test_create_data_directory(self):
        today_data_dir = self.writer.create_data_directory()

    def test_open_data_file(self):
        obj = self.writer.open_data_file()
        self.assertTrue(obj is self.writer.data_file_obj)
        for key in self.writer.file_attr_keys:
            self.assertTrue(key in obj.attrs)
        obj.close()
        os.remove(self.writer.data_file_path)
        today_data_dir = self.writer.create_data_directory()
        os.removedirs(today_data_dir)

    def test_create_scangroup(self):
        with self.assertRaises(NotImplementedError):
            self.writer.create_scangroup()

    def test_write_to_data_file(self):
        with self.assertRaises(NotImplementedError):
            self.writer.write_to_data_file()

if __name__ == "__main__":
    unittest.main()
