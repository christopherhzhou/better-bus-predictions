import requests

from .constants.apikey import key


class BusDataUtil:
    """
    Class methods:
    - get_bus_data(bus_id)
    - get_departing_buses(stop_id, route_id, direction_id)
    - get_stops_list(trip_id)
    
    """
    @staticmethod
    def get_bus_data(bus_id):
        """Returns a dictionary with bus data.
        
        Args:
        - bus_id (str): ID of bus
        
        Returns:
        - dictionary: Contains data of bus with given ID.
        Looks something like this if data was successfully retrieved: 
        {
            'response_status_code': 200,
            'response_url': 'a.friendly.url',
            'trip_id': '123',
            'direction': '1',
            'stop_sequence': '6',
            'latitude': '43.331212827',
            'longitude': '-71.1982703',
            'stop_id': '23391',
            'updated_at': 'some-time'
        }
        - None: If bus data could not be retrieved.
        
        """
        payload = {
            'api_key': key
        }
    
        response = requests.get('https://api-v3.mbta.com/vehicles/{}'.format(bus_id), params=payload)
    
        bus_data = {
            'response_status_code': response.status_code,
            'response_url': response.url
        }
    
        if bus_data.get('response_status_code') == 200:
            response_data = response.json()['data']
            
            if response_data['relationships']['stop']['data']:
                bus_data['stop_id'] = response_data['relationships']['stop']['data']['id']
            
            if response_data['relationships']['trip']['data']:
                bus_data['trip_id'] = response_data['relationships']['trip']['data']['id']
                
            bus_data['direction'] = response_data['attributes']['direction_id']
            bus_data['stop_sequence'] = response_data['attributes']['current_stop_sequence']
            bus_data['latitude'] = response_data['attributes']['latitude']
            bus_data['longitude'] = response_data['attributes']['longitude']
            bus_data['updated_at'] = response_data['attributes']['updated_at']
    
        return bus_data

    @staticmethod 
    def get_departing_buses(stop_id, route_id, direction_id):
        """Returns a dictionary with departing buses.
        
        Args:
        - stop_id (str): ID of stop to get departing buses from.
        - route_id (str): ID of route bus should be on at departure.
        - direction_id (str): ID of direction that bus should be departing in.
        
        Returns:
        - dictionary: A dictionary with bus IDs as keys and their respective trip IDs
        and departure times as additional info per object.
        Ideal data returned example: 
        {
            'y1234': {
                'trip_id': '098',
                'departure_time': '12:34'
            },
            'y5678': {
                'trip_id': '765',
                'departure_time': '12:56'
            }
        
        }
        - None: If data could not be retrieved.
        
        """
        payload = {
            'filter[direction_id]': direction_id,
            'filter[route_type]': '3',
            'filter[stop]': stop_id,
            'filter[route]': route_id,
            'api_key': key
        }
    
        response = requests.get('https://api-v3.mbta.com/predictions', params=payload)
        
        if response.status_code == 200:
            departures = {}
            
            for data in response.json().get('data'):
                if data['attributes'].get('departure_time') and data['relationships']['trip'].get('data') and data['relationships']['vehicle'].get('data') and len(data['relationships']['vehicle']['data'].get('id')) < 6 and data['relationships']['vehicle']['data'].get('id') not in departures:
                    departures[data['relationships']['vehicle']['data'].get('id')] = {
                        'trip_id': data['relationships']['trip']['data'].get('id'),
                        'departure_time': data['attributes'].get('departure_time')
                    }
                    
            return departures

    @staticmethod
    def get_stops_list(trip_id):
        """Returns a list of stop IDs for a given trip ID.
        
        Args:
        - trip_id: ID for a trip with desired route stops.
        
        Returns:
        - list: A list containing the stop IDs for all stops in order of the trip.
        Ideal data returned example: [
            '1234',
            '5678',
            '9012'
        ]
        - None: If data could not be retrieved.
        
        """
        payload = {
            'include': 'stops',
            'api_key': key
        }
        
        response = requests.get('https://api-v3.mbta.com/trips/{}'.format(trip_id), params=payload)
        
        if response.status_code == 200 and response.json()['data']['relationships']['stops'].get('data'):
            stops = []
            
            stops_list = response.json()['data']['relationships']['stops'].get('data')
            
            for stop in stops_list:
                stops.append(stop['id'])
        
            return stops

    @staticmethod
    def get_trip_info(trip_id):
        """Returns info on a given trip ID.
        
        Args:
        - trip_id: ID for a trip with desired route stops.
        
        Returns:
        - dictionary: Contains:
            - 'stops': A list with the stop IDs for all stops in order of the trip.
            Ideal data returned example: [
                '1234',
                '5678',
                '9012'
            ]
            - 'route_id': ID of route trip is on.
            - 'direction_id': ID of direction trip is in.
        - None: If data could not be retrieved.
        
        """
        payload = {
            'include': 'stops',
            'api_key': key
        }
        
        response = requests.get('https://api-v3.mbta.com/trips/{}'.format(trip_id), params=payload)
        
        if response.status_code == 200 and response.json()['data']['relationships']['stops'].get('data'):
            data = {
                'route_id': response.json()['data']['relationships']['route']['data']['id'],
                'direction_id': response.json()['data']['attributes']['direction_id'],
                'stops': []
            }
            
            stops_list = response.json()['data']['relationships']['stops'].get('data')
            
            for stop in stops_list:
                data['stops'].append(stop['id'])
        
            return data
