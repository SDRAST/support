from __future__ import print_function
import unittest
import os
import datetime

from support.pyro import async as async_util
from support.configuration import tams_config


test_dir = os.path.dirname(os.path.abspath(__file__))


class TestConfiguration(unittest.TestCase):

    def test_on(self):

        class Handler(async_util.AsyncCallbackManager):

            @async_util.async_callback
            def handler(self, new_val):
                pass

        h = Handler()
        tams_config.on("data_dir", h.handler)
        with h.wait("handler", timeout=1):
            tams_config.data_dir = test_dir

    def test_make_today(self):
        tams_config.data_dir = test_dir
        today_dir = tams_config.make_today_dir(tams_config.data_dir)
        year, doy = datetime.datetime.utcnow().strftime("%Y,%j").split(",")
        self.assertTrue(today_dir.endswith(doy))
        self.assertTrue(today_dir.endswith(os.path.join(year, doy)))


if __name__ == "__main__":
    unittest.main()
