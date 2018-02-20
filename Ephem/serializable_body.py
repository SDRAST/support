import ephem

class SerializableBody(ephem.FixedBody):
    """
    Simple extension to ephem.FixedBody that allows for conversion to and
    from a Python dictionary
    """
    def __init__(self, info=None, name=""):
        super(SerializableBody, self).__init__()
        if info is None:
            self.info = {}
        self.name = name

    def to_dict(self):
        return_dict = {
            "info": self.info,
            "name":self.name,
            "_ra": float(self._ra),
            "_dec": float(self._dec),
            "__class__":self.__class__.__name__
        }
        if hasattr(self, "ra"):
            return_dict["ra"] = float(self.ra)
            return_dict["dec"] = float(self.dec)

        if hasattr(self, "az"):
            return_dict["az"] = float(self.az)
            return_dict["alt"] = float(self.alt)
            return_dict["el"] = float(self.alt)

        return return_dict

    @classmethod
    def from_dict(cls, src_dict):
        obj = cls()
        obj._ra = src_dict["_ra"]
        obj._dec = src_dict["_dec"]
        obj.info = src_dict["info"]
        obj.name = src_dict["name"]
        return obj
