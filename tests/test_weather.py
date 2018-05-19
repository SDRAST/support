from __future__ import print_function
import unittest

from support import weather

class TestWeather(unittest.TestCase):

    def test_get_current_weather(self):
        lat, lon = 24.523338, 54.433461
        resp = weather.get_current_weather(lat, lon)
        json = resp.json()
        self.assertTrue(json["coord"]["lat"] == float("{:.2f}".format(lat)))
        self.assertTrue(json["coord"]["lon"] == float("{:.2f}".format(lon)))

    def test_get_lat_lon(self):
        resp = weather.get_lat_lon("Abu Dhabi")
        self.assertTrue("lat" in resp)

    def test_integration(self):
        lat_lon = weather.get_lat_lon("Abu Dhabi")
        resp = weather.get_current_weather(lat_lon["lat"], lat_lon["lon"])


if __name__ == "__main__":
    unittest.main()
