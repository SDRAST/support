import ephem

class SerializableBody(ephem.FixedBody):
    """
    Simple extension to ephem.FixedBody that allows for conversion to and
    from a Python dictionary
    """
    def __init__(self, info=None, name="",observer_info=None):
        super(SerializableBody, self).__init__()
        if info is None:
            self.info = {}
        self.name = name
        self.observer_info = observer_info

    def to_dict(self):
        return_dict = {
            "info": self.info,
            "observer_info":self.observer_info,
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
        obj.observer_info = src_dict["observer_info"]
        obj.name = src_dict["name"]
        return obj

    def get_observer(self):
        """
        Return an ephem.Observer object from the body's observer_info dictionary.
        """
        if self.observer_info is not None:
            observer = ephem.Observer()
            observer.lon = self.observer_info["lon"]
            observer.lat = self.observer_info["lat"]
            observer.elevation = self.observer_info["elevation"]
            observer.date = self.observer_info["date"]
            observer.epoch = self.observer_info["epoch"]
            return observer
