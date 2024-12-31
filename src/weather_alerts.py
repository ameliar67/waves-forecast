from surfpy.location import Location
import requests

class WeatherAlerts():

    _API_ROOT_URL = 'https://api.weather.gov/'

    @staticmethod
    def fetch_active_weather_alerts(location: Location) -> dict:
        # https://api.weather.gov/alerts/active?point=46.221924,-123.816882

        url = f'{WeatherAlerts._API_ROOT_URL}alerts/active?point={location.latitude},{location.longitude}'
        resp = requests.get(url)
        resp_json = resp.json()
        return resp_json