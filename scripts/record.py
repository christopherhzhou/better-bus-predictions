import threading

from scripts.trackers.buses_tracker import BusesTracker


def record_data(origin_terminus_id, route_id, direction_id):
    buses_tracker = BusesTracker(origin_terminus_id, route_id, direction_id)
    buses_tracker.run()


if __name__ == '__main__':
    t1 = threading.Thread(target=record_data, args=('23391', '39', '0'))
    t2 = threading.Thread(target=record_data, args=('10833', '34', '1'))

    t1.start()
    t2.start()

    t1.join()
    t2.join()
