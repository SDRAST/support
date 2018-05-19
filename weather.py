import time

import requests

api_key = "4450b8a98a0c113ad12ac164d83dbe9c"

__all__ = ["get_lat_lon","get_current_weather"]

def _make_geocoding_api_request(address, mode="json"):
    """
    get latitude and longitude from some address.
    See this page for more info:
    https://developers.google.com/maps/documentation/geocoding/intro

    Examples:

    .. code-block:: python

        from support.weather import get_lat_lon

        res = _make_geocoding_api_request("Abu Dhabi").json()
        if res["status"] == "OK":
            print(res["results"][0]["geometry"]["location"]["lat"],
                  res["results"][0]["geometry"]["location"]["lng"])

    Args:
        address (str): Some address. Could be the name of a city,
            or a specific street address.
    Returns:
        requests.Response
    """
    template = "https://maps.googleapis.com/maps/api/geocode/{}?{}"
    params = []
    address_str = "address={}".format(address.replace(" ","+"))
    params.append(address_str)
    request_url = template.format(mode, ",".join(params))
    resp = requests.get(request_url)
    return resp

def get_lat_lon(address, **kwargs):
    """
    Format response object from _make_geocoding_api_request.

    Examples:

    .. code-block:: python

        >>> from support.weather import get_lat_lon
        >>> res = get_lat_lon("New York City")
        >>> print(res["lat"], res["lon"])
        40.7127753 -74.0059728

    Args:
        address (str): passed to _make_geocoding_api_request
        **kwargs: passed to _make_geocoding_api_request
    Returns:
        dict: Dictionary with the following keys/values:
        * lat: Latitude in degrees
        * lon: Longitude in degrees
    """
    timeout = kwargs.pop("timeout", 2.0)
    max_tries = kwargs.pop("max_tries", 1)

    res = None

    def _format_resp(resp):
        res = None
        json = resp.json()
        if json["status"] == "OK":
            lat = json["results"][0]["geometry"]["location"]["lat"]
            lon = json["results"][0]["geometry"]["location"]["lng"]
            res = {"lat": lat, "lon": lon}
        return res

    resp = _make_geocoding_api_request(address, **kwargs)
    res = _format_resp(resp)

    for attempt in xrange(1, max_tries):
        if res is not None:
            break
        resp = _make_geocoding_api_request(addres, **kwargs)
        res = _format_resp(resp)
        time.sleep(timeout)

    return res

def get_current_weather(lat, lon, mode='json'):
    """
    Get the weather at a certain latitude and longitude

    Examples:

    .. code-block:: python

        from support.weather import get_current_weather

        # longitude and latitude in Abu Dhabi, UAE
        lat_ad, lon_ad = 24.523338, 54.433461
        resp = get_current_weather(lat_ad, lon_ad)
        print(resp.json())

    Args:
        lat (str/float): latitude
        lon (str/float): longitude
        mode (str, optional): data type to request. Accepts "json" or "xml"
    Returns:
        requests.Response: call the ``json`` method to get a dictionary
            with weather data.

    """
    client = requests.session()
    template = "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&mode={}&units=metric&APPID={}"
    resp = client.request("GET", template.format(lat, lon, mode, api_key))
    return resp
