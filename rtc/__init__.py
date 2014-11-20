"""
Module for using the computer's Real Time Clock device

Provides class RTC

The rtc time structure is::
  struct rtc_time {
    int tm_sec;
    int tm_min;
    int tm_hour;
    int tm_mday;
    int tm_mon;
    int tm_year;
    int tm_wday;     /* unused */
    int tm_yday;     /* unused */
    int tm_isdst;    /* unused */};

Compiled C program 'rtc_constants' returns the addresses of the RTC registers
for the RTC.

See 'man rtc' for documentation

From http://www.larsen-b.com/Article/221.html
"""
import struct
import logging
import threading
import os

from  fcntl import ioctl
from ctypes import create_string_buffer
from time import sleep

module_logger = logging.getLogger(__name__)

# RTC requests are sent with:
#     ioctl(fd, request_code, parameter)

# These codes are common to all Linux hosts.
RTC_AIE_ON   =     0x7001 # enable  alarm interrupt
RTC_AIE_OFF  =     0x7002 # disable alarm interrupt
RTC_UIE_ON   =     0x7003 # enable  1/sec interrupts
RTC_UIE_OFF  =     0x7004 # disable 1/sec interrupts
RTC_PIE_ON   =     0x7005 # enable  periodic interrupt
RTC_PIE_OFF  =     0x7006 # disable periodic interrupt

# These codes vary from OS to OS
RTC_IRQP_SET = 0x4008700c # set the interrupt period to long in third arg (1)
RTC_ALM_SET  = 0x40247007 # set the alarm to the time struct in the third arg
RTC_IRQP_READ= 0x8008700b # Read the interrupt period as long in third arg
RTC_ALM_READ = 0x80247008 # read the alarm time as time struct in third arg
RTC_RD_TIME  = 0x80247009 # returns an RTC time structure with current time

# (1)  Interrupts per sec.  The set of allowable frequencies is the multiples
#      of two in the range 2 to 8192.

class RTC(object):
  """
  Class for the Real Time Clock device

  This creates a persistent RTC object, i.e., it can be created and kept for
  the duration of the program.
  """
  def __init__(self):
    """
    Initialize the RTC object.

    This should be done at the start of a program using the RTC.
    """
    self.logger = logging.getLogger(module_logger.name+".RTC")
    self.open()
    self.one_pps = self.One_pps(self)
    self.N_pps = self.many_pps(self)
    self.logger.debug(" initialized")

  def open(self):
    """
    open the realtime clock
    """
    self.f = open ("/dev/rtc", "r")
    self.fd = self.f.fileno()
    self.logger.debug(" opened %s", self.fd)

  def close(self):
    """
    close the RTC device
    """
    self.f.close()

  def time(self):
    """
    """
    s = struct.Struct('9i')
    buf = create_string_buffer(s.size)
    ioctl(self.fd, RTC_RD_TIME, buf)
    (sc, mn, hr, md, mo, yr, d0, d1,d2) = s.unpack(buf)
    return (1900+yr, mo, md, hr, mn, sc)

  class One_pps(object):
    """
    Pseudo-device which interrupts on the second
    """
    def __init__(self, parent):
      """
      """
      self.parent = parent

    def start(self):
      """
      """
      ioctl(self.parent.fd, RTC_UIE_ON, 0)

    def stop(self):
      """
      """
      ioctl(self.parent.fd, RTC_UIE_OFF, 0)

  class many_pps(object):
    """
    Pseudo-device to produce 2**N interrupts per second
    """
    def __init__(self, parent):
      """
      """
      self.parent = parent
      self.logger = logging.getLogger(self.parent.logger.name+".many_pps")

    def start(self, N):
      """
      """
      try:
        assert 0<N<14, "only 2-8192 interrupts/sec (0<N<14)"
      except AssertionError:
        return False
      else:
        self.logger.debug(" turned on")
        ioctl(self.parent.fd, RTC_IRQP_SET, 2**N)
        ioctl(self.parent.fd, RTC_PIE_ON, 0)
        return True

    def stop(self):
      """
      stop
      """
      ioctl(self.parent.fd, RTC_PIE_OFF, 0)

class Signaller(threading.Thread):
  """
  """
  signal = threading.Event()
  def __init__(self, rtc):
    mylogger = logging.getLogger(module_logger.name+".Signaller")
    threading.Thread.__init__(self)
    self.logger = mylogger
    self.rtc = rtc
    self.end_flag = False
    self.logger.debug(" initialized with %s", self.rtc)
   
  def run(self):
    """
    """
    self.logger.debug(" running")
    while not self.end_flag:
      Signaller.signal.clear()
      # the read will block until the next interrupt.
      self.logger.debug(" reading %d", self.rtc.fd)
      os.read(self.rtc.fd, 4)  # 4 = size of double
      Signaller.signal.set()
    self.logger.debug(" finished")

  def terminate(self):
    """
    Thread termination routine
    """
    self.logger.info(" %s ends", self.name)
    self.end_flag = True

    