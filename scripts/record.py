import threading

from scripts.trackers.buses_tracker import BusesTracker
from scripts.trackers.master_buses_tracker import MasterBusesTracker


def record_data(origin_terminus_id, route_id, direction_id):
    buses_tracker = BusesTracker(origin_terminus_id, route_id, direction_id)
    buses_tracker.run()


if __name__ == '__main__':
    master_buses_tracker = MasterBusesTracker(['34','39'])
    master_buses_tracker.run()
