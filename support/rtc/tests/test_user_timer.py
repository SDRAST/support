"""
This test program sees external signals sent with 'kill' but does not
see the signals created by the timer.
"""

import signal
import time
from ctypes import CDLL, c_float, c_int

timer = CDLL('./user_timer.so')
timer.timer_create.argtypes = [c_float,c_int]

def handler(signum, frame):
    print time.time(),'Signal handler called with signal', signum

# Any other signal will terminate the program.
signal.signal(signal.SIGUSR1, handler)
signal.signal(signal.SIGUSR2, handler)
signal.signal(signal.SIGHUP, handler)

timer.timer_create(0.5, 1)

while(True):
  print "waiting..."
  time.sleep(0.5)
