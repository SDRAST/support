import time 

import numpy as np 

class SAOfwif_Simulator(object):

    def __init__(self, parent=None, roach='sao64k-1',template='sao'):

        self.parent = parent 
        self.roach = roach
        self.template = template
        self.int_time = 1.0
       
        self.spectrum = np.zeros(32768)
        self.accum_count = 0.0
        self.gain = 10.0 

    def get_next_accum(self):

        time.sleep(self.int_time)
        self.spectrum = np.random.rand(32768)
        self.accum_count += 1
        return self.spectrum

    def get_accum_count(self):

        return self.accum_count

    def acc_time_set(self, acc_time=1.0):

        self.int_time = acc_time

    def get_gains(self):

        return {0: {0: {'enabled': True, 'gain':self.gain}}}

    def rf_gain_set(self, value):

        self.gain = value 

    def ADC_samples(self):

        return np.random.rand(8192)


def get_roaches(template='sao'):

    return {'sao64k-1':'IP-1',
            'sao64k-2':'IP-2',
            'sao64k-3':'IP-3',
            'sao64k-4':'IP-4'}