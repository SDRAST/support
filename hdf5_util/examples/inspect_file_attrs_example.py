import os

import h5py

from support.hdf5_util import inspect_file_attrs

current_dir = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(current_dir, "example.hdf5")
with h5py.File(file_path, "w") as f:
    f.attrs["first_name"] = "dill"
    f.attrs["last_name"] = "pickle"
    f.attrs["age"] = 0.1

inspect_file_attrs(file_path).close()
