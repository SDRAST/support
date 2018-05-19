import os

import numpy as np
import h5py

from support.hdf5_util import inspect_file_structure

current_dir = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(current_dir, "example.hdf5")
with h5py.File(file_path, "w") as f:
    g = f.create_group("group0")
    g.create_dataset("dataset0",data=np.zeros(10))

report, f_obj = inspect_file_structure(file_path)
f_obj.close()
print(report)
