"""
Generates an interrupt every 2048 ticks and prints duration of 1000 interrupts

Must be superuser or use 'sudo' to get access to RTC.
"""
import os
import datetime
from time import time
from support import check_permission
from support.rtc import RTC
from support import sync_second
  
if __name__ == "__main__":

  check_permission('ops')
  rtc = RTC()
  
  # returns a tuple of ints (Y,M,D,h,m,s)
  print "RTC time = %4d-%02d-%02d %02d:%02d:%02d UT" % rtc.time()

  # returns five samples at 1-sec intervals
  secs = 0
  print "Sampling at 1 pps:"
  sync_second()
  rtc.one_pps.start()
  while secs<5:
    os.read(rtc.fd, 4)
    #print datetime.datetime.now()
    print "  %.6f" % time()
    secs += 1

  # returns eight samples at 0.25~sec intervals.
  sample_rate_bit = 6
  sample_rate = 2**sample_rate_bit
  print "Sampling at %d samples/sec" % sample_rate
  rtc.N_pps.set_rate(sample_rate_bit)
  interrupt = 0
  times = []
  rtc.one_pps.stop()
  sync_second()
  rtc.N_pps.start()
  # For example, 2**6 = 64 interrupts should take 1 sec
  while interrupt < sample_rate*2 :
    # the read will block until the next interrupt.
    os.read(rtc.fd, 4)  # 4 = size of double
    interrupt += 1
    # this is where you do whatever needs accurate timing.
    times.append(time())
  rtc.N_pps.stop()
  rtc.close()
  for tm in times:
    print "  %.6f" % tm
  delta = times[-1] - times[0]
  print "End - start = %f sec" % delta
  print "Ticks per interrupt = %f" % ((interrupt-1)/delta)

 