import os
import logging
from pylab import *
from time import time
from numpy import array, polyfit, poly1d

from support import check_permission
from support.rtc import RTC, Signaller
from support import sync_second

if __name__ == "__main__":
  mylogger = logging.getLogger()
  mylogger.setLevel(logging.DEBUG)
  arch = 'armv6l' # cpu_arch()
  if arch == 'x86_64':
    check_permission('ops')
    rtc = RTC()

    sample_rate_bit = 6
    sample_rate = 2**sample_rate_bit
    print "Sampling at %d samples/sec" % sample_rate
    rtc.N_pps.set_rate(sample_rate_bit)
    interrupt = 0
    times = []
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
  else:
    sample_rate = 100
    npps = Signaller(interval=1./sample_rate)
    max_samples = 400
    sample_count = 0
    times = []
    sync_second()
    npps.start()
    while sample_count < max_samples:
      npps.signal.wait()
      times.append(time())
      sample_count += 1
    mylogger.debug("%d samples completed", sample_count)
    npps.terminate()
    npps.join()

  times_array = array(times)
  indices = arange(len(times))
  coefs = polyfit(indices,times_array,1)
  fit = poly1d(coefs)
  dif = array(times-fit(indices))*1000
  stdev = dif.std()
  plot(dif,'.')
  title('%d samples/sec, $\pm$%.3f ms' % (sample_rate,stdev))
  xlabel('Sample')
  xlim(0,len(indices))
  ylabel('Error (ms)')
  grid()
  show()
