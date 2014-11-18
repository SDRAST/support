"""
Generates an interrupt every 2048 ticks and prints duration of 1000 interrupts

Must be superuser or use 'sudo' to get access to RTC.
"""
import os
import time
from support import check_permission
from support.rtc import RTC
    
if __name__ == "__main__":

  check_permission('ops')
  rtc = RTC()

  secs = 0
  rtc.one_pps.start()
  while secs<5:
    os.read(rtc.fd,4)
    print rtc.time()
    secs += 1
  rtc.one_pps.stop()
  
  t0 = time.time()
  interrupt = 0
  # 2**6 = 64 interrupts should take 1 sec
  rtc.N_pps.start(6)
  while interrupt < 64 :
    # the read will block until the next interrupt.
    os.read(rtc.fd, 4)  # 4 = size of double
    interrupt += 1
  delta = time.time() - t0
  print "Elapsed time = %f sec" % delta
  print "Ticks per interrupt = %f" % (interrupt/delta)
  rtc.N_pps.stop()

  print "UT = %4d/%02d/%02d %02d:%02d:%02d" % rtc.time()
  rtc.close()