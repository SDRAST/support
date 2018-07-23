"""
paths to local packages and data
"""
import os
from socket import gethostname

local_packages = "/usr/local/lib/python2.7/DSN-Sci-packages/"

auto_pkg_dir = local_packages+"Automation/"
auto_apps_path = auto_pkg_dir + "apps/"

data_dir = "/usr/local/RA_data/"
fits_dir = data_dir+"FITS/"
hdf5_dir = data_dir+"HDF5/"

projects_dir = "/usr/local/projects/"
auto_dir = projects_dir+"DSAO/"
sci_proj_path = auto_dir+"Science/"
act_proj_path = auto_dir+"Activities/"

project_data_dir = "/usr/local/project_data/"

log_dir = os.path.join("/usr/local/Logs/", gethostname(),'')
wvsr_dir = "/data/"   # was data2 on crab14
postproc_dir = wvsr_dir+"post_processing/"
wvsr_fft_dir = postproc_dir+"auto/" # was cjnaudet/auto on crab14
SAOspec_dir = postproc_dir+"SAOspec/"
