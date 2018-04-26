def dump_dict(f_obj_or_group, data_dict):
    """
    Dump the contents of a data dictionary into some file object or group.

    Args:
        f_obj_or_group (h5py.File/h5py.Group): h5py file or group object
        data_dict (dict): dictionary whose contents we want to dump
    Returns:
        None

    Example:

        ```python
        import h5py

        from support.hdf5_util import dump_dict

        data_dict = {
            "level0": {
                "level1":{
                    "level2": np.ones(100)
                }
            }
        }
        f_obj = h5py.File("example.hdf5","r+")
        dump_dict(f_obj, data_dict)
        print(f_obj["level0/level1/level2"][...])
        # >>> bunch of ones!
        f_obj.close()
        ```
    """

    def _dump_dict(grp, data):
        if hasattr(data, "items"):
            for key in data:
                sub_data = data[key]
                if hasattr(sub_data, "items"):
                    _dump_dict(grp.create_group(key), data[key])
                else:
                    grp.create_dataset(key, data=sub_data)

    _dump_dict(f_obj_or_group, data_dict)

if __name__ == '__main__':
    import h5py
    from .inspect import inspect_file_structure
    data_dict = {
        "level0": {
            "level1_0":{
                "level2_0": [i for i in xrange(100)],
                "level2_1": [i+2 for i in xrange(100)]
            },
            "level1_1":{
                "level2_0": [i+1 for i in xrange(100)],
                "level2_1": [i+2 for i in xrange(100)]
            }
        }
    }
    f_obj = h5py.File("example.hdf5", "w")
    dump_dict(f_obj, data_dict)
    report = inspect_file_structure(f_obj)
    print(report)
    f_obj.close()
