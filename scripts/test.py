from scripts.api.stoputil import BusStopUtil
from scripts.api.busutil import BusDataUtil


if __name__ == '__main__':
    print(BusDataUtil.get_trip_info(44813439))
