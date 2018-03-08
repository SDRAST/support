import sys
import logging

import h5py

module_logger = logging.getLogger(__name__)

def inspect_file_attrs(f_path):

    f_obj = h5py.File(f_path, "r")
    for attr_name in f_obj.attrs:
        print("{}: {}".format(attr_name, f_obj.attrs[attr_name]))
    f_obj.close()

if __name__ == "__main__":
    inspect_file_attrs(sys.argv[1])
