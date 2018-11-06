import os
import datetime

from support.pyro import async

__all__ = [
    "tams_config"
]


def _check_and_create(path):
    if not os.path.exists(path):
        os.makedirs(path)


def _make_properties(prop_names):

    def property_factory(prop_name):
        def prop_get(self):
            prop_val = getattr(self, "_{}".format(prop_name))
            return prop_val

        def prop_set(self, new_val):
            setattr(self, "_{}".format(prop_name), new_val)

        return prop_get, prop_set

    def wrapper(cls):
        for prop_name in prop_names:
            prop = property(*property_factory(prop_name))
            setattr(cls, prop_name, prop)

        return cls
    return wrapper


class Configuration(object):

    _protected = {"_emitter", "_config"}

    def __init__(self, cls, *args, **kwargs):
        self._emitter = async.EventEmitter(
            threaded=kwargs.pop("threaded", False)
        )
        self._config = cls(*args, **kwargs)

    def __getattr__(self, attr):
        if attr in Configuration._protected:
            return object.__getattr__(self, attr)
        elif attr in self._emitter.__class__.__dict__:
            return getattr(self._emitter, attr)
        else:
            # self._emitter.emit(attr)
            return getattr(self._config, attr)

    def __setattr__(self, attr, val):
        if attr in Configuration._protected:
            object.__setattr__(self, attr, val)
        else:
            setattr(self._config, attr, val)
            self._emitter.emit(attr, val)

    def make_today_dir(self, base_dir):
        """
        Make the following directory structure:

        base_dir/<year>/<doy>

        Args:
            base_dir (str):

        Returns:
            str: base_dir with year and doy subdirectories
        """
        year, doy = datetime.datetime.utcnow().strftime("%Y,%j").split(",")
        today_dir = os.path.join(base_dir, year, doy)
        _check_and_create(today_dir)
        return today_dir


@_make_properties([
    "hdf5_data_dir",
    "fits_data_dir",
    "boresight_data_dir",
    "flux_calibration_data_dir",
    "tipping_data_dir",
    "status_dir",
    "sources_dir",
    "models_dir",
    "log_dir",
    "product_dir",
    "dss",
    "rest_freq"
])
class TAMSConfiguration(object):

    def __init__(self,
                 data_dir="",
                 calibration_dir="",
                 project_dir="",
                 log_dir="",
                 product_dir="",
                 boresight_model_file="",
                 rest_freq=2.223508e10):

        self._data_dir = data_dir
        self._hdf5_data_dir = os.path.join(self._data_dir, "HDF5", "dss43")
        self._fits_data_dir = os.path.join(self._data_dir, "FITS", "dss43")

        self._calibration_dir = calibration_dir
        self._boresight_data_dir = os.path.join(
            self._calibration_dir,
            "boresight_data"
        )
        self._flux_calibration_data_dir = os.path.join(
            self._calibration_dir,
            "flux_calibration_data"
        )
        self._tipping_data_dir = os.path.join(
            self._calibration_dir,
            "tipping_data"
        )
        self._status_dir = os.path.join(
            self._calibration_dir,
            "status"
        )

        self._project_dir = project_dir
        self._sources_dir = os.path.join(self._project_dir, "Observations")
        self._models_dir = os.path.join(self._project_dir, "models")
        self._boresight_model_file = boresight_model_file

        self._log_dir = log_dir

        self._product_dir = product_dir
        self._rest_freq = rest_freq

    @property
    def data_dir(self):
        return self._data_dir

    @data_dir.setter
    def data_dir(self, path):
        self._data_dir = path
        self._hdf5_data_dir = os.path.join(self._data_dir, "HDF5", "dss43")
        self._fits_data_dir = os.path.join(self._data_dir, "FITS", "dss43")

    @property
    def calibration_dir(self):
        return self._calibration_dir

    @data_dir.setter
    def calibration_dir(self, path):
        self._calibration_dir = path
        self.boresight_data_dir = os.path.join(
            self._calibration_dir, "boresight_data")
        self.flux_calibration_data_dir = os.path.join(
            self._calibration_dir, "flux_calibration_data")
        self.tipping_data_dir = os.path.join(
            self._calibration_dir, "tipping_data")
        self.status_dir = os.path.join(
            self._calibration_dir, "status")

    @property
    def project_dir(self):
        return self._project_dir

    @project_dir.setter
    def project_dir(self, path):
        self._project_dir = path
        self._sources_dir = os.path.join(self._project_dir, "Observations")
        self._models_dir = os.path.join(self._project_dir, "models")

    @property
    def boresight_model_file_path(self):
        return os.path.join(self.models_dir, self._boresight_model_file)


tams_config = Configuration(
    TAMSConfiguration,
    data_dir="/home/ops/roach_data/sao_test_data/RA_data",
    calibration_dir="/home/ops/roach_data/sao_test_data/data_dir",
    project_dir="/home/ops/projects/TAMS",
    log_dir="/usr/local/logs/dss43",
    product_dir="/home/ops/roach_data/sao_test_data/data_dir/products",
    boresight_model_file="AdaBoostClassifier.2018-07-05T09:17:31.dat",
    rest_freq=2.223508e10
)
