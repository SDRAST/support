"""
paths to local packages and data
"""
import os
from socket import gethostname

# local package software
local_packages = "/usr/local/RATools/"

# data locations
data_dir = "/usr/local/RA_data/"
fits_dir = data_dir+"FITS/"
hdf5_dir = data_dir+"HDF5/"
project_data_dir = "/usr/local/project_data/"

# project working directories
projects_dir = "/usr/local/projects/"
# project observing configurations
proj_conf_path = local_packages+"MonitorControl/Configurations/projects/"

# logs for software running on this host
log_dir = os.path.join("/usr/local/Logs/", gethostname(),'')

