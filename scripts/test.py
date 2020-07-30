from scripts.api.mbta.busutil import BusDataUtil
from scripts.api.mbta.stoputil import BusStopUtil
from scripts.api.other.gmaputil import GMapsUtil


if __name__ == '__main__':
    print(GMapsUtil.get_gmaps_estimate('39','0'))
