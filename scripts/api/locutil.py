from geopy.distance import distance
import requests

from .constants.apikey import key
from .busutil import BusDataUtil


class BusLocationUtil:
    
    # 'distance_threshold' is distance in meters a bus should be within a stop for it to be considered 'arriving'
    @staticmethod
    def is_near_stop(bus_latitude, bus_longitude, stop_id, distance_threshold=50):
        payload = {
            'api_key': key
        }
        
        response = requests.get('https://api-v3.mbta.com/stops/{}'.format(stop_id), params=payload)
        
        if response.status_code == 200:
            stop_attributes = response.json()['data']['attributes']
            
            bus_coords = (bus_latitude, bus_longitude)
            stop_coords = (stop_attributes['latitude'], stop_attributes['longitude'])
            
            return distance(bus_coords, stop_coords).m < distance_threshold
            