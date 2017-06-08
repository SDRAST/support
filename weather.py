import requests

api_key = "4450b8a98a0c113ad12ac164d83dbe9c"

def get_current_weather(lat, lon, mode='json'):
    client = requests.session()
    template = "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&mode={}&units=metric&APPID={}"
    resp = client.request("GET", template.format(lat, lon, mode, api_key))
    return resp

if __name__ == '__main__':
    import time
    lat_ad, lon_ad = 24.523338, 54.433461
    lat_can, lon_can = -35.2835, 149.1281

    print(get_current_weather(lat_ad, lon_ad))
    time.sleep(2.0)
    print(get_current_weather(lat_can, lon_can))