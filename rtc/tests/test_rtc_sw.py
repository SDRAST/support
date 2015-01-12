"""
Test of RTC.time()

Must be root to run this.
"""

from support.process import invoke
from support.rtc import RTC

p = invoke('hwclock --show --debug')
lines = p.stdout.readlines()
for line in lines:
  print line.strip()

# if the RTC is invokes first then close it before doing the above
rtc = RTC()
print "RTC.time() returns", rtc.time()
rtc.close()