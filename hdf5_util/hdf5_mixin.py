import os
import datetime
import logging

import h5py

current_dir = os.path.dirname(os.path.abspath(__file__))

module_logger = logging.getLogger(__name__)


class HDF5Mixin(object):
    """
    Mixin class with methods for creating and writing to HDF5 files.
    This mixin assumes that the derived class implements the following
    attributes:

        * name
        * base_data_dir
        * data_dir
        * data_file_obj
        * date_file_name
        * data_file_path
        * file_attr_keys
        * header

    Moreover, the ``create_scangroup`` and ``write_to_data_file`` methods
    are to be reimplemented.
    """

    def create_data_directory(self):
        """
        Create year and day of year (doy) subdirectories under the ``data_dir``
        attribute
        """
        now = datetime.datetime.utcnow()
        year, doy = now.strftime("%Y,%j").split(",")
        data_dir = self.data_dir
        if data_dir is None:
            data_dir = self.base_data_dir
        today_data_dir = os.path.join(data_dir, year, doy)
        if not os.path.exists(today_data_dir):
            os.makedirs(today_data_dir, 0775)
        return today_data_dir

    def open_data_file(self):
        """
        create, if necessary, subdirectories for today's data directory, and
        then open up a ``h5py.File`` object.

        Returns:
            h5py.File
        """
        # get the base location for the data directory
        if self.data_dir is None:
            self.data_dir = self.base_data_dir
        if self.data_file_obj is not None:
            # close the open datafile
            self.data_file_obj.close()
        # use current date in file name and path
        now = datetime.datetime.utcnow()
        self.data_file_name = self.name + now.strftime("-%Y-%j-%H%M%S.hdf5")
        module_logger.debug("open_data_file {}".format(
            self.data_file_name
        ))
        data_dir = self.create_data_directory() # if needed
        self.data_file_path = os.path.join(data_dir, self.data_file_name)
        module_logger.debug("open_data_file: path is {}".format(
            self.data_file_path
        ))
        self.data_file_obj = h5py.File(self.data_file_path, "w")
        self.initialize_data_file()

        return self.data_file_obj

    def initialize_data_file(self):
        """
        Put the highest level metadata in the datafile.

        The registers that never change in a ROACH are put in top-level attributes
        """
        module_logger.debug("initialize_data_file: file is {}".format(
            self.data_file_obj))
        self.data_file_obj.attrs["name"] = self.name
        for key in self.file_attr_keys:
            self.data_file_obj.attrs[key] = self.header[key]
        module_logger.debug("initialize_data_file: attributes: {}".format(
                     self.data_file_obj.attrs.keys()))

    def create_scangroup(self):
        """
        create a HDF5 group for a scan

        Creates empty datasets for the data and metadata associated with each
        record of a scan.
        """
        raise NotImplementedError

    def write_to_data_file(self):
        """
        Write the data and metadata from the latest accumulation in the file

        After writing a new empty record is created if more records are expected for
        this scan.
        """
        raise NotImplementedError
