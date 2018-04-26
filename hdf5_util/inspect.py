import sys
import logging

import h5py

module_logger = logging.getLogger(__name__)

def _get_file_obj(f_path_or_f_obj):
    if not isinstance(f_path_or_f_obj, h5py.File):
        f_obj = h5py.File(f_path, "r")
    else:
        f_obj = f_path_or_f_obj
    return f_obj


def inspect_file_attrs(f_path_or_f_obj):
    """
    List out the attributes of some HDF5 file object.
    If a path is provided, then it will open the file in
    read mode.
    """
    f_obj = _get_file_obj(f_path_or_f_obj)
    for attr_name in f_obj.attrs:
        print("{}: {}".format(attr_name, f_obj.attrs[attr_name]))

    return f_obj

def inspect_file_structure(f_path_or_f_obj):
    report = {}
    def _inspect_file_structure(grp, report):
        if hasattr(grp, "keys"):
            for key in grp:
                if isinstance(grp[key], h5py.Group):
                    report[key] = {}
                    _inspect_file_structure(grp[key], report[key])
                else:
                    report[key] = grp[key].shape

    f_obj = _get_file_obj(f_path_or_f_obj)
    _inspect_file_structure(f_path_or_f_obj,report)
    return report, f_obj

if __name__ == "__main__":
    inspect_file_attrs(sys.argv[1]).close()
