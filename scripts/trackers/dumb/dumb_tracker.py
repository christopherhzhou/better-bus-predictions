from datetime import datetime

from geopy.distance import distance
from dateutil import parser

from scripts.api.mbta.busutil import BusDataUtil


class DumbTracker:
    """Tracks the unique locations of a list of given buses.

    Will know when a bus is stopped and when it is moving.

    """
    # distance in meters a bus should be within its previous location to be considered stopped
    STOP_THRESHOLD = 1

    def __init__(self, bus_id, independent=True):
        self.__coords = []
        self.bus_id = bus_id
        self.indep = independent

    def update(self, data=None):
        bus_data = None

        if self.indep:
            bus_data = BusDataUtil.get_bus_data(self.bus_id)
            if bus_data.get('response_status_code') != 200:
                print(f'No data for {self.bus_id}, status code {bus_data.get("response_status_code")}')
                bus_data = None
        else:
            bus_data = data.get(self.bus_id)

        if bus_data:
            coords = bus_data.get('latitude'), bus_data.get('longitude')
            timestamp = bus_data.get('updated_at')

            if len(self.__coords) == 0 or (self.__coords[-1].get('timestamp') != timestamp
                                           and distance(self.__coords[-1].get('coords'), coords).m > DumbTracker.STOP_THRESHOLD):
                self.__coords.append({'coords': coords, 'timestamp': timestamp})

                datetime_timestamp = parser.parse(timestamp).replace(tzinfo=None)
                time_now = datetime.now()

                print('NEW UPDATE:')
                print('update lag:', time_now - datetime_timestamp)
                print('timestamp:', datetime_timestamp)
                print('location:', coords)
                print()
