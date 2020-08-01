import requests

from scripts.api.other.constants.owmappid import appid
from scripts.api.mbta.stoputil import BusStopUtil


class WeatherUtil:
    @staticmethod
    def get_weather_at_stop(stop_id):
        stop_lat, stop_long = BusStopUtil.get_stop_coords(stop_id)

        if stop_lat and stop_long:
            payload = {
                'lat': stop_lat,
                'lon': stop_long,
                'appid': appid
            }
            response = requests.get('https://api.openweathermap.org/data/2.5/weather', params=payload)

            if response.status_code == 200:
                return response.json()['weather'][0].get('main')
            else:
                print('Non-200 status code in OpenWeather API response:', response.status_code)
                print('Response json:')
                print(response.json())

