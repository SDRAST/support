import unittest

from support.Ephem.serializable_body import SerializableBody

class TestSerializableBody(unittest.TestCase):

    def setUp(self):
        b = SerializableBody()
        b._ra = 1.44399937429555
        b._dec = 0.23617770979137057
        b.info["name"] = "0528+134"
        b.info["flux"] = {
            "X": "2.48",
            "C": "3.41",
            "L": "1.67",
            "K": "3.20",
            "S": "2.97",
            "W": "3.00"
        }
        self.b = b

    def test_to_dict(self):
        d = self.b.to_dict()
        self.assertTrue("az" not in d)
        self.assertTrue("alt" not in d)
        self.assertTrue("ra" not in d)
        self.assertTrue("dec" not in d)

    def test_from_dict(self):
        d = self.b.to_dict()
        b1 = SerializableBody.from_dict(d)
        self.assertTrue(self.b._ra == b1._ra)
        self.assertTrue(self.b._dec == b1._dec)
        self.assertTrue(self.b.info == b1.info)

if __name__ == "__main__":
    unittest.main()
