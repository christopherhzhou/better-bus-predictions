import ast
import json
from pathlib import Path

from geopy.distance import distance
import requests

from .constants.apikey import key


class BusLocationUtil:

    @staticmethod
    def get_stop_coords(stop_id):
        stop_id = str(stop_id)

        file_path = Path(__file__).parent.resolve() / 'constants' / 'stop_coords.txt'
        with open(file_path, 'r') as f:
            contents = f.read()
        stops_dict = ast.literal_eval(contents)

        if stop_id in stops_dict:
            return stops_dict.get(stop_id)[0], stops_dict.get(stop_id)[1]

        else:
            payload = {'api_key': key}
            response = requests.get('https://api-v3.mbta.com/stops/{}'.format(stop_id), params=payload)

            if response.status_code == 200:
                print('Saving stop {name} (id {id})...'.format(name=response.json()['data']['attributes']['name'], id=stop_id))

                stop_coords = (response.json()['data']['attributes']['latitude'], response.json()['data']['attributes']['longitude'])

                stops_dict[stop_id] = stop_coords
                with open(file_path, 'w') as f:
                    f.write(json.dumps(stops_dict, indent=4))

                return stop_coords
            elif response.status_code == 404:
                print('404: Stop code invalid')
            else:
                print('There was an error retrieving stop info')

    # 'distance_threshold' is distance in meters a bus should be within a stop for it to be considered 'arriving'
    @staticmethod
    def is_near_stop(bus_latitude, bus_longitude, stop_id, distance_threshold=50):
        if stop_id:
            bus_coords = (bus_latitude, bus_longitude)
            stop_coords = BusLocationUtil.get_stop_coords(stop_id)

            if stop_coords:
                return distance(bus_coords, stop_coords).m < distance_threshold

        return False
