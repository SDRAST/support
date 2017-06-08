# -*- coding: utf-8 -*-
"""
Module Ephem - extends module pyephem for radio astronomy

Module Ephem extends module ephem (package pyephem).  Everything from
module 'ephem' is inherited.  In addition, it provides the classes
Quasar(), Pulsar() and DSS().  It also provides pulsar physical
data and quasar fluxes.  Use like this:
>>> from Astronomy import Ephem
>>> x = Ephem.Pulsar('J1809-0743')

Notes
=====
module ephem
------------
http://rhodesmill.org/brandon/projects/pyephem-manual.html

About Celestial Coordinates
---------------------------
a_ra, a_dec — Astrometric geocentric position for epoch (e.g. J2000)
g_ra, g_dec — Apparent geocentric position for date specified in
              the compute(), after correcting for precession, relativistic
              deflection, nutation and aberration
ra, dec     - apparent topocentric position, after correction for parallax
              and refraction. Set the Observer() attribute pressure to zero if
              you want PyEphem to ignore the effects of atmospheric refraction

Diagnostics
-----------
To see what this module does internally:
>>> from Astronomy import Ephem
>>> Ephem.diag = True
>>> x = Ephem.Pulsar('J1809-0743')
"""
import datetime
from ephem import Date, FixedBody, Observer
from math import pi
from matplotlib.dates import date2num
import logging

import Astronomy
from Astrophysics.Pulsars import pulsar_data as PD
from Radio_Astronomy import michigan
from Radio_Astronomy import vla_cal

module_logger = logging.getLogger(__name__)

J2000 = Date("2000/1/1 00:00:00")

diag = False

# planets recognized by module ephem
Planets = ['Jupiter', 'Mars', 'Mercury', 'Moon', 'Neptune', 'Pluto',
           'Saturn', 'Sun', 'Uranus', 'Venus']

Jnames = PD.data.keys() # pulsar Julian epoch names
Jnames.sort()

cal_dict = vla_cal.get_cal_dict() # VLA calibrators
Bname_dict, cat_3C_dict = vla_cal.VLA_name_xref(cal_dict) # name dictionaries
Bnames = vla_cal.Jnames_to_B(Bname_dict) # B names keyed on J names

dsn = Astronomy.get_geodetic_coords()
xyz = Astronomy.get_cartesian_coordinates()

def remove_item(thislist, item):
  """
  Remove item from list without complaining if absent

  @param thislist : list of items
  @param item : item which may or may not be in the list

  @return: reduced list
  """
  try:
    thislist.remove(item)
  except ValueError:
    pass
  return thislist
  
class EphemException(Exception):
  """
  Exception class for Ephem module
  """
  def __init__(self, value=None, details=None):
    """
    Creates an instance of EphemException()
    """
    if value:
      self.value = value
    if details:
      self.details = details
  def __str__(self):
    """
    EphemException() instance message
    """
    msg = "error"
    if self.value:
      msg += ": " + repr(self.value)
    if self.details:
      msg += ", " + self.details
    return repr(msg)

class Pulsar(FixedBody):
  """
  FixedBody() with pulsar properties.

  The pulsar astrophysical properties can be accessed with:
  >>> x.properties
  {'CLK': 'UTC(NIST)',
   'DIST_DM': '+17.82',
   'DIST_DM1': '6.33',
   'DM': '240.70',
   'EPHEM': 'DE200',
   'FINISH': '51889.103',
   'P0': '0.313885674748',
   'P1': '1.521E-16',
   'PEPOCH': '51650.000',
   'S1400': '0.29',
   'START': '51396.419',
   'SURVEY': 'swmb,pksmb',
   'W50': '12'}
  To find out what a property is:
  >>> print Ephem.PD.help['S1400']
  (PD stands for 'pulsar data'.)
  """
  def __init__(self, name):
    """
    Create a Pulsar() instance from its name.

    The preferred name form is like 'J2305+4707'.  However, 'B2303+46'
    is also exceptable, as is '2305+4707'.  In the latter case, it must
    be a Julian epoch name.

    Notes
    =====
    Instance attributes
    -------------------
    properties - a dictionary of pulsar physical properties

    Inherited methods and attributes
    --------------------------------
    All methods and attributes of FixedBody()
    """
    super(Pulsar,self).__init__()
    if name[0] == "J":
      self.name = name
    elif name[0] == "B":
      self.name = PD.names[name]
    else:
      self.name = "J"+name
    try:
      Jnames.index(self.name)
    except:
      raise(self.name,"unknown pulsar")
    if diag:
      print self.name
    pulsar_data = PD.data[self.name]
    [ra,dec]    = PD.equatorial(pulsar_data)
    if diag:
      print "From catalogue:", ra, dec
      print "In ephem format:",hours(str(ra)),degrees(str(dec))
    self._ra    = hours(str(ra))     # pulsar_data['RAJ']  or derived
    self._dec   = degrees(str(dec)) # pulsar_data['DECJ'] or derived
    self._pmra  = float(pulsar_data['PMRA'])
    self._pmdec = float(pulsar_data['PMDEC'])
    self.period = PD.period(pulsar_data)
    self.dpdt   = PD.period_change_rate(pulsar_data)
    if diag:
      print "As attributes:",self._ra, self._dec
    self._epoch = J2000
    self._class = "L"
    # to initialize ra, dec to something
    self.compute("2000/1/1 00:00:00")
    keys = pulsar_data.keys()
    keys = remove_item(keys,'RAJ')
    keys = remove_item(keys,'DECJ')
    keys = remove_item(keys,'ELONG')
    keys = remove_item(keys,'ELAT')
    keys = remove_item(keys,'PMRA')
    keys = remove_item(keys,'PMDEC')
    keys = remove_item(keys,'PSRB')
    keys = remove_item(keys,'P0')
    keys = remove_item(keys,'P1')
    if diag:
      print "Properties:",keys
    self.properties = {}
    for prop in keys:
      self.properties[prop] = pulsar_data[prop]
    self.pressure = 0

class Quasar(FixedBody):
  """
  FixedBody() with "J" or "B" name
  """
  def __init__(self,name):
    """
    Create an instance of a Quasar()
    
    The preferred name form is like 'J2305+4707'.  However, 'B2303+46'
    is also exceptable, as is '2305+4707'.  In the latter case, it must
    be a Julian epoch name.

    The name may also be given as "3C84" or "3C 84"

    Notes
    =====
    Instance methods and attributes
    -------------------------------
    flux -     radio flux in janskys at a specified frequency
    flux_ref - source for radio flux data
    freq -     frequency for which flux was calculated
    date -     date for which flux was calculated, if based on Michigan data
    Jname -    Julian epoch name
    Bname -    Besselian epoch name

    Inherited methods and attributes
    --------------------------------
    All methods and attributes of FixedBody()
    name - Julian epoch name without leading "J"
    """
    super(Quasar,self).__init__()
    if name[0] == "J":
      self.Jname = self.name
      self.name = name[1:]
      try:
        self.Bname = "B"+Bnames[self.name]
      except KeyError:
        raise(EphemException(name,"unknown J-name"))
    elif name[0] == "B":
      self.Bname = name
      try:
        self.name = Bname_dict[name[1:]]
      except KeyError:
        raise(EphemException(name,"unknown B-name"))
      self.Jname = "J"+self.name
    elif name[:2] == "3C":
      name = name.replace(" ","")
      try:
        self.name = cat_3C_dict[name]
      except KeyError:
        raise(EphemException(name,"unknown 3C source"))
      self.Jname = "J"+self.name
      self.Bname = "B"+Bnames[self.name]
    else:
      try:
        Jnames.index("J"+name)
      except:
        raise(EphemException(name,"unknown quasar"))
      self.name = name
      self.Jname = "J"+self.name
      self.Bname = "B"+Bnames[self.name]
    quasar_data = cal_dict[self.name]
    self._ra = hours(str(quasar_data['ra']))
    self._dec = degrees(str(quasar_data['dec']))
    if diag:
      print self._ra, self._dec
    self._epoch = J2000
    self._class = "Q"
    # to initialize ra, dec to something
    self.compute("2000/1/1 00:00:00")
    self.freq = None
    self.flux = None
    self.flux_ref = None
    self.date = None
    self.pressure = 0
 
  def interpolate_flux(self,freq,date=None):
    """
    Flux of source at given frequency in GHz.

    The Michigan data are interpolated if possible, that is, the source is
    in the data base and the frequency requested is between 4 and 15 GHz.
    Otherwise the VLA data are used.
    If the date is not given, it is assumed to be now.
    """
    self.freq = freq
    if self.freq > 4 and self.freq < 15:
      if date == None:
        self.date = datetime.datetime.now()
      else:
        self.date = date
      try:
        # in Michigan data
        michigan.Bnames.index(self.Bname[1:])
        self.flux = michigan.polate_flux(self.Bname[1:],
                                         date2num(self.date),
                                         freq)
        if diag:
          print "Michigan flux is",self.flux
        self.flux_ref = "Michigan"
        return self.flux
      except ValueError:
        # Not in the Michigan catalog or no date given
        if diag:
          print self.name,"=",self.Bname,"is not in the Michigan catalog"
    else:
      print "Outside Michigan frequency range"
    # try VLA cals
    try:
      cal_data = vla_cal.get_cal_data(self.Jname[1:])
      freqs,fluxes = vla_cal.get_flux_data(cal_data)
      self.flux = vla_cal.interpolate_flux(freqs,fluxes,freq)
      self.flux_ref = "VLA"
      if diag:
        print ref,"flux is",self.flux
      return self.flux
    except ValueError:
      self.flux = None
      self.flux_ref = None
      return None

class DSS(Observer):
  """
  Observer class for DSN stations
  """
  def __init__(self, number):
    """
    Creates an instance of a DSN station Observer()

    Attributes
    ==========
    lon       - east longitude (degrees)
    lat       - north latitude (degrees)
    elevation - altitude (meters)
    timezone  - difference (hours) from UTC
    name      -
    diam      - diameter (m)

    @param number : station number
    """
    super(DSS,self).__init__()
    module_logger.debug("Initiating DSS(%d)", number)
    self.lon = -dsn[number][0]*pi/180.
    self.lat = dsn[number][1]*pi/180.
    self.elevation = dsn[number][2]
    self.timezone = dsn[number][3]
    self.name = dsn[number][4]
    self.diam = dsn[number][5]
    self.xyz = xyz["DSS %2d" % number]

def calibrator(name):
  """
  Creates an Ephem (pyephem) Body() instance for a flux calibrator
  """
  try:
    # planet?
    Planets.index(name)
    exec('calibrator = '+name+'()')
    return calibrator
  except Exception, details:
    if diag:
      print "Not a planet:",details
    # quasar?
    try:
      calibrator = Quasar(name)
      return calibrator
    except Exception, details:
      print "Not a quasar:",details
      return None
