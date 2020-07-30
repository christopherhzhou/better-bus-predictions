from time import sleep

from .bus_tracker import BusTracker
from scripts.api.busutil import BusDataUtil
from scripts.dynamodb.post_data import post_data


# TODO write docstring
class BusesTracker:
    
    def __init__(self, origin_terminus_id, route_id, direction_id):
        self.origin_terminus = origin_terminus_id
        self.route = route_id
        self.direction = direction_id
        
        self.buses = BusDataUtil.get_departing_buses(origin_terminus_id, route_id, direction_id)
        
        self.__bus_trackers = []
        
        for bus_id in self.buses:
            if BusDataUtil.get_stops_list(self.buses[bus_id]['trip_id']):
                self.__bus_trackers.append(BusTracker(bus_id, self.buses[bus_id]['trip_id']))
        
    def run(self):
        while True:
            bus_ids = self.buses.keys()
            for _ in range(40):
                buses_data = BusDataUtil.get_buses_data(bus_ids)
                for bus in self.__bus_trackers:
                    bus.update(buses_data.get(bus.bus_id))
                    if bus.status == 'AT_DEST_TERMINUS':
                        post_data(bus.get_recorded_data(), self.route, self.direction)
                        self.buses.pop(bus.bus_id)
                        self.__bus_trackers.remove(bus)
                    elif bus.status == 'ERROR':
                        print(f'BusesTracker: Removing bus {bus.bus_id}...')
                        self.buses.pop(bus.bus_id)
                        self.__bus_trackers.remove(bus)
                        print('BusesTracker: Bus removed')
                sleep(2)
                
            new_buses = BusDataUtil.get_departing_buses(self.origin_terminus, self.route, self.direction)
            for bus_id in new_buses:
                if bus_id not in self.buses and BusDataUtil.get_stops_list(new_buses[bus_id]['trip_id']):
                    self.buses[bus_id] = {
                        'trip_id': new_buses[bus_id]['trip_id'],
                        'departure_time': new_buses[bus_id]['departure_time']
                    }
                    self.__bus_trackers.append(BusTracker(bus_id, self.buses[bus_id]['trip_id']))
