from time import sleep

from scripts.api.mbta.busutil import BusDataUtil
from scripts.trackers.buses_tracker import BusesTracker
from scripts.trackers.constants.route_origin_stops import RouteOriginStops


# tracks ALL buses from ALL routes
class MasterBusesTracker:

    def __init__(self, routes):
        print('Starting the master buses tracker....\n')

        self.route_trackers = {}

        for route in routes:
            if RouteOriginStops.get(route):
                self.route_trackers[f'r{route}-d0'] = BusesTracker(RouteOriginStops[route]['0'], route, '0')
                self.route_trackers[f'r{route}-d1'] = BusesTracker(RouteOriginStops[route]['1'], route, '1')
            else:
                print('Could not find information on route', route)
        print()

        # first value is number of seconds between each route-direction's check for new buses
        # second value is the total number of these route-directions (each route has two directions, 0 and 1)
        # third value is how many seconds between each update
        self.__sleep_duration = 2
        self.__update_cycles = int(300 / len(self.route_trackers.keys()) / self.__sleep_duration)

    def run(self):
        while True:
            for route_tracker_key in self.route_trackers.keys():
                all_bus_ids = []

                for tracker_key in self.route_trackers.keys():
                    for bus_id in self.route_trackers[tracker_key].get_bus_ids():
                        all_bus_ids.append(bus_id)

                for _ in range(self.__update_cycles):
                    all_buses_data = BusDataUtil.get_buses_data(all_bus_ids)
                    for tracker_key in self.route_trackers.keys():
                        self.route_trackers[tracker_key].update(all_buses_data)
                    sleep(self.__sleep_duration)

                self.route_trackers[route_tracker_key].check_for_departing_buses()

