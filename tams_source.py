import ephem
import numpy as np

class TAMS_Source(object):

    def __init__(self,
                 name="",
                 ra=0.0, dec=0.0,
                 az=None, alt=None,
                 epoch=ephem.J2000,
                 flux=0.0, velo=0.0,
                 category=None,
                 plot_params=None):
        """
        """
        self.body = ephem.FixedBody()
        self._name = name
        self.body._ra = ra
        self.body._dec = dec
        self.body._epoch = epoch

        if az != None or alt != None:
            self._az = az
            self._alt = alt

        self._velo = velo
        self._flux = flux
        self.category = category
        self.plot_params = plot_params

    @property
    def _ra_deg(self):
        return np.rad2deg(float(self.body._ra))

    @property
    def ra_deg(self):
        return np.rad2deg(float(self.body.ra))

    @property
    def _dec_deg(self):
        return np.rad2deg(float(self.body._dec))

    @property
    def dec_deg(self):
        return np.rad2deg(float(self.body.dec))

    @property
    def az_deg(self):
        try:
            az = self._az
        except AttributeError:
            az = self.body.az
        return np.rad2deg(float(az))

    @property
    def az(self):
        try:
            return self._az
        except AttributeError:
            return self.body.az

    @property
    def alt_deg(self):
        try:
            alt = self._alt
        except AttributeError:
            alt = self.body.alt
        return np.rad2deg(float(alt))

    @property
    def alt(self):
        try:
            return self._alt
        except AttributeError:
            return self.body.alt

    @property
    def name(self):
        return self._name

    @property
    def velo(self):
        return self._velo

    @property
    def flux(self):
        return self._flux

    def get_long(self):
        """
        Get longitude coordinates
        returns:
            - str
        """
        return str(ephem.hours(self._ra))

    def get_lat(self):
        """
        Get latitude coordinates
        returns:
            - str
        """
        return str(ephem.degrees(self._dec))

    def __str__(self):

        return str(self.name)
        # return "name: {}, az: {}, el: {}".format(self.name, self.az, self.alt)

    def __getattr__(self, attr):
        """
        This allows us to interact with the source object as if it were a normal
        Python object.
        args:
            - attr (str): The attribute we're trying to access
        """
        return getattr(self.body, attr)

    def toDict(self):
        """
        We want to supply the _ra and _dec values to the dictionary, instead of the calculated values.
        This means that when we load the dictionary in using the TAMS_Source.from_dict static method,
        then we don't use the calculated values as the _ra and _dec attributes.
        Returns:
            dict: With main attributes of source.
        """
        ra = self.body._ra
        dec = self.body._dec

        return {'ra': ra,
                'dec': dec,
                'flux': self.flux,
                'velo': self.velo,
                'name': self.name,
                'category': self.category}

    @staticmethod
    def fromDict(src_dict):

        if isinstance(src_dict, dict):
            return TAMS_Source(**src_dict)
        elif isinstance(src_dict, TAMS_Source):
            return src_dict


def compute_az_el(source_entry, observer):
    """
    Given the antenna position on the globe, and the current date,
    compute the azimuthal and elevation of the source, given its RA and DEC.
    args:
        - source_entry (list): A list containing ra, dec, flux, and velocity
        - observer (ephem.Observer): An ephem observer representing position of antenna.

    returns:
        - ephem.FixedBody object. One can get ra, dec, az and el attributes as follows:
            source.ra, source.dec, source.az, source.alt
    """
    source = TAMS_Source(ra=source_entry[0],
                         dec=source_entry[1],
                         flux=source_entry[2],
                         velo=source_entry[3])
    source.compute(observer)

    return source


if __name__ == '__main__':
    ra = "7:09:07.54"
    dec = "-49:35:11.1"
    b = TAMS_Source("J07084", ra=ra, dec=dec, epoch=ephem.now())
    print(b.name, b._ra, b._dec, b._ra_deg, b._dec_deg)
