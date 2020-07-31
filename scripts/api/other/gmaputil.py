# Maximum of 10 waypoints allowed (see https://developers.google.com/maps/documentation/directions/overview#Waypoints)
import json
from pathlib import Path

import requests

from scripts.api.other.constants.apikey import key
from scripts.api.mbta.stoputil import BusStopUtil


class GMapsUtil:
    @staticmethod
    def get_gmaps_estimate(route_id, direction_id):
        route_id = str(route_id)
        direction_id = int(direction_id)

        # the waypoints are, by default, in outbound order
        file_path = Path(__file__).parent.resolve() / 'constants' / 'waypoints.json'
        with open(file_path, 'r') as f:
            contents = f.read()
        waypoints_dict = json.loads(contents)

        if route_id in waypoints_dict:
            waypoints_coords = [BusStopUtil.get_stop_coords(waypoint)
                                if type(waypoint) == str else (waypoint[0], waypoint[1])
                                for waypoint in waypoints_dict.get(route_id)]

            if direction_id == 1:
                waypoints_coords = list(reversed(waypoints_coords))

            origin_lat, origin_long = waypoints_coords[0]
            dest_lat, dest_long = waypoints_coords[-1]

            waypoints_str = '|via:'.join([f'{waypoint_lat},{waypoint_long}' for waypoint_lat, waypoint_long in waypoints_coords[1:-1]])

            payload = {
                'origin': f'{origin_lat},{origin_long}',
                'destination': f'{dest_lat},{dest_long}',
                'waypoints': 'via:' + waypoints_str,
                'departure_time': 'now',
                'traffic_model': 'best_guess',
                'key': key
            }
            response = requests.get('https://maps.googleapis.com/maps/api/directions/json?', params=payload)

            if response.status_code == 200:
                return response.json()['routes'][0]['legs'][0]['duration_in_traffic'].get('value')
            else:
                print('Non-200 status code when requesting to the GMaps API:', response.status_code)

        else:
            print('No waypoints set for rte{} direction {}'.format(route_id, direction_id))
