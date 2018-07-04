import sys
import logging

import h5py

module_logger = logging.getLogger(__name__)

__all__ = ["inspect_file_attrs", "inspect_file_structure"]

def _get_file_obj(f_path_or_f_obj):
    """
    Get an instance of h5py.File from either an existing instance
    or a path to a HDF5 file.

    Args:
        f_path_or_f_obj (str/h5py.File): Path to HDF5 or h5py.File object
    Returns:
        h5py.File
    """
    if not isinstance(f_path_or_f_obj, h5py.File):
        f_obj = h5py.File(f_path_or_f_obj, "r")
    else:
        f_obj = f_path_or_f_obj
    return f_obj


def inspect_file_attrs(f_path_or_f_obj):
    """
    List out the attributes of some HDF5 file object.
    If a path is provided, then it will open the file in
    read mode.

    Examples:

    .. code-block:: python

        import h5py

        from support.hdf5_util import inspect_file_attrs

        file_path = "example.hdf5"
        with h5py.File(file_path, "w") as f:
            f.attrs["first_name"] = "dill"
            f.attrs["last_name"] = "pickle"
            f.attrs["age"] = 0.1

        inspect_file_attrs(file_path).close()

    This will output the following:

    .. code-block:: none

        first_name: "dill"
        last_name: "pickle"
        age: 0.1

    """
    f_obj = _get_file_obj(f_path_or_f_obj)
    for attr_name in f_obj.attrs:
        print("{}: {}".format(attr_name, f_obj.attrs[attr_name]))

    return f_obj

def inspect_file_structure(f_path_or_f_obj):
    """
    Get a dictionary that reports the structure of some HDF5 file.

    Examples:

    .. code-block:: python

        import numpy as np
        import h5py

        from support.hdf5_util import inspect_file_structure

        file_path = "example.hdf5"
        with h5py.File(file_path, "w") as f:
            g = f.create_group("group0")
            g.create_dataset("dataset0",data=np.zeros(10))

        report, f_obj = inspect_file_structure(file_path)
        f_obj.close
        print(report)

    This outputs the following dictionary:

    .. code-block:: none

        {u'group0': {u'dataset0': (10,)}}

    """
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
    _inspect_file_structure(f_obj,report)
    return report, f_obj

if __name__ == "__main__":
    inspect_file_attrs(sys.argv[1]).close()
