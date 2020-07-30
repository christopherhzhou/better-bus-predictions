import json
from pathlib import Path

from geopy.distance import distance
import requests

from scripts.api.mbta.constants.apikey import key


class BusStopUtil:
    """Contains static methods for retrieving bus stop data.

    No __init__ method since it is not necessary to create
    an instance of BusStopUtil to use bus stop utility methods.

    """

    @staticmethod
    def get_stop_name(stop_id):
        """Returns the name of a bus stop with given ID.

        Useful for debugging purposes, but as of now implementation
        is not very efficient (requesting from API per call).

        Args:
            stop_id (str): ID of desired stop.

        Returns:
            str: Full name of the stop.

        """
        payload = {'api_key': key}
        response = requests.get('https://api-v3.mbta.com/stops/{}'.format(stop_id), params=payload)

        if response.status_code == 200:
            return response.json()['data']['attributes']['name']
        elif response.status_code == 404:
            print('404: Invalid stop ID')
        else:
            print('There was an error retrieving stop info')

    @staticmethod
    def get_stop_coords(stop_id):
        """Returns the coordinates of a bus stop with given ID.

        Since stop coordinates are frequently used, this method
        opens the constants/stop_coords.json file to efficiently obtain
        stop coordinates without the need to make a request to the API
        each time.

        Args:
            stop_id (str): ID of desired stop.

        Returns:
            tuple: Coordinates of the stop

        """
        stop_id = str(stop_id)

        file_path = Path(__file__).parent.resolve() / 'constants' / 'stop_coords.json'
        with open(file_path, 'r') as f:
            contents = f.read()
        stops_dict = json.loads(contents)

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
                print('404: Invalid stop ID')
            else:
                print('There was an error retrieving stop info')

    @staticmethod
    def is_near_stop(bus_latitude, bus_longitude, stop_id, distance_threshold=50):
        """Determines if a bus is near a stop.

        Args:
            bus_latitude (str): Latitude of bus.
            bus_longitude (str): Longitude of bus.
            stop_id (str): ID of desired stop.
            distance_threshold (:obj:`int`, optional): The distance in meters
                a bus should be within the stop in order to be considered
                "near" the stop.

        Returns:
            bool: True if bus is near stop, False otherwise.

        """
        if stop_id:
            bus_coords = (float(bus_latitude), float(bus_longitude))
            stop_coords = BusStopUtil.get_stop_coords(stop_id)

            if stop_coords:
                return distance(bus_coords, stop_coords).m < distance_threshold

        return False
