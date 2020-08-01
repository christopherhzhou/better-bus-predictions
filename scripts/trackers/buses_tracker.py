import datetime
from time import sleep

from .bus_tracker import BusTracker
from scripts.api.mbta.busutil import BusDataUtil
from scripts.dynamodb.post_data import post_data


# TODO write docstring
class BusesTracker:
    
    def __init__(self, origin_terminus_id, route_id, direction_id):
        self.origin_terminus = origin_terminus_id
        self.route = route_id
        self.direction = direction_id
        
        self.buses = BusDataUtil.get_departing_buses(origin_terminus_id, route_id, direction_id)
        
        self.__bus_trackers = []

        # dict with a bus's ID as a key and a datetime.datetime object that represents when the item
        # should be removed from the error list
        self.__error_dict = {}
        
        for bus_id in self.buses:
            if BusDataUtil.get_stops_list(self.buses[bus_id]['trip_id']):
                self.__bus_trackers.append(BusTracker(bus_id, self.buses[bus_id]['trip_id']))

    def update(self, buses_data):
        for bus in self.__bus_trackers:
            bus.update(buses_data.get(bus.bus_id))
            if bus.status == 'AT_DEST_TERMINUS':
                post_data(bus.get_recorded_data(), self.route, self.direction)
                self.buses.pop(bus.bus_id)
                self.__bus_trackers.remove(bus)
            elif bus.status == 'ERROR':
                print(f'BusesTracker: Moving bus {bus.bus_id} to error list for at least 10 minutes...')

                time_later = datetime.datetime.now() + datetime.timedelta(minutes=10)
                self.__error_dict[bus.bus_id] = time_later

                self.buses.pop(bus.bus_id)
                self.__bus_trackers.remove(bus)

                print(f'BusesTracker: Bus {bus.bus_id} moved to error list')
                print('----- ERROR RESOLVED -----')

    def check_for_departing_buses(self):
        new_buses = BusDataUtil.get_departing_buses(self.origin_terminus, self.route, self.direction)
        for bus_id in new_buses:
            if bus_id not in self.buses and bus_id not in self.__error_dict and BusDataUtil.get_stops_list(
                    new_buses[bus_id]['trip_id']):
                self.buses[bus_id] = {
                    'trip_id': new_buses[bus_id]['trip_id'],
                    'departure_time': new_buses[bus_id]['departure_time']
                }
                self.__bus_trackers.append(BusTracker(bus_id, self.buses[bus_id]['trip_id']))

        time_now = datetime.datetime.now()
        for bus_id in list(self.__error_dict):
            if self.__error_dict.get(bus_id) < time_now:
                self.__error_dict.pop(bus_id)
                print('--------------------')
                print(f'Removing bus {bus_id} from error dict')
                print('--------------------')

    def get_bus_ids(self):
        return self.buses.keys()
