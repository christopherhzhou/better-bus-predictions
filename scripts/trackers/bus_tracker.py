from scripts.api.mbta.busutil import BusDataUtil
from scripts.api.mbta.stoputil import BusStopUtil
from scripts.api.other.gmaputil import GMapsUtil
from scripts.api.mbta.constants.stop_distance_thresholds import StopDistanceThresholds


# TODO write docstring
# assumes that a bus is either at or soon to arrive at origin terminus station
class BusTracker:

    def __init__(self, bus_id, trip_id):
        self.bus_id = bus_id

        trip_info = BusDataUtil.get_trip_info(trip_id)

        self.route_id = trip_info.get('route_id')
        self.direction_id = trip_info.get('direction_id')

        self.__stops = trip_info['stops']
        self.__dest_terminus_idx = len(self.__stops) - 1
        self.origin_terminus = self.__stops[0]
        self.dest_terminus = self.__stops[self.__dest_terminus_idx]
        self.__last_at_stop_idx = 0

        self.__error_strikes = 0

        self.__origin_stop_distance_threshold = StopDistanceThresholds.get(self.origin_terminus) if StopDistanceThresholds.get(self.origin_terminus) else 80
        self.__dest_stop_distance_threshold = StopDistanceThresholds.get(self.dest_terminus) if StopDistanceThresholds.get(self.dest_terminus) else 80

        bus_data = BusDataUtil.get_bus_data(bus_id)
        if BusStopUtil.is_near_stop(bus_data.get('latitude'), bus_data.get('longitude'), self.origin_terminus, distance_threshold=self.__origin_stop_distance_threshold):
            self.status = 'AT_ORIGIN_TERMINUS'
        else:
            self.status = 'SOON_ARRIVING_ORIGIN_TERMINUS'

        self.data = {
            'tripId': int(trip_id),
            'stops': {}
        }

        print('rte{rte}: now tracking bus with ID {bid}, trip ID {tid}, status {sts}'.format(rte=self.route_id, bid=bus_id, tid=trip_id, sts=self.status))

    def update(self, bus_data):
        if bus_data:
            # if bus is known to be soon arriving at origin terminus and it is found to be near origin terminus
            if self.status == 'SOON_ARRIVING_ORIGIN_TERMINUS' and BusStopUtil.is_near_stop(bus_data.get('latitude'), bus_data.get('longitude'), self.origin_terminus, distance_threshold=self.__origin_stop_distance_threshold):
                # update status
                self.status = 'AT_ORIGIN_TERMINUS'

                # print info
                self.__print_info(bus_data.get('latitude'), bus_data.get('longitude'), bus_data['updated_at'])

            # if bus is known to be at origin terminus but is no longer near origin terminus...
            elif self.status == 'AT_ORIGIN_TERMINUS' and not BusStopUtil.is_near_stop(bus_data.get('latitude'), bus_data.get('longitude'), self.origin_terminus, distance_threshold=self.__origin_stop_distance_threshold):
                # update status
                self.status = 'IN_TRANSIT'

                # set info
                self.data['stops'][self.origin_terminus] = {
                    'departed': bus_data['updated_at']
                }
                self.data['departOrigin'] = bus_data['updated_at']
                self.data['gmapsEstimate'] = GMapsUtil.get_gmaps_estimate(self.route_id, self.direction_id)

                # print info
                self.__print_info(bus_data.get('latitude'), bus_data.get('longitude'), bus_data['updated_at'])

            # if bus is in transit...
            elif self.status == 'IN_TRANSIT':
                at_stop = bus_data.get('stop_id')

                # if bus is near the next expected stop... (standard behavior)
                if BusStopUtil.is_near_stop(bus_data.get('latitude'), bus_data.get('longitude'), self.__stops[self.__last_at_stop_idx + 1]):
                    # update status
                    self.status = 'NEAR_STOP'

                    # update date
                    self.data['stops'][self.__stops[self.__last_at_stop_idx+1]] = {
                        'arrived': bus_data['updated_at']
                    }

                # this elif checks if there is a discrepancy between the bus's previous stop and the stop it's supposed
                # to be at according to the API
                elif self.__stops[self.__last_at_stop_idx] != at_stop and self.__stops[self.__last_at_stop_idx + 1] != at_stop:

                    # if this code begins to execute, it already means a rare error has occurred and the bus was not
                    # detected to have been near a stop
                    print('---- STOP SKIPPED - INFO BELOW ----')
                    self.__print_info(bus_data.get('latitude'), bus_data.get('longitude'), bus_data['updated_at'])
                    print('API determined nearest stop:', BusStopUtil.get_stop_name(at_stop))
                    print('Known last-at stop:', BusStopUtil.get_stop_name(self.__stops[self.__last_at_stop_idx]))

                    # iterates through all the stops between the current possible stop the bus could be at all the way
                    # until the destination terminus
                    for stop_idx in range(self.__last_at_stop_idx + 2, self.__dest_terminus_idx + 1):
                        if stop_idx < self.__dest_terminus_idx and at_stop == self.__stops[stop_idx]:
                            # if this condition below is not true, is it possible another stop skip will be detected
                            # again - however, after the second iteration all skip errors should be resolved
                            if BusStopUtil.is_near_stop(bus_data.get('latitude'), bus_data.get('longitude'), at_stop):
                                self.status = 'NEAR_STOP'
                                self.data['stops'][at_stop] = {
                                    'arrived': bus_data['updated_at']
                                }
                                print('Last skipped stop is {}, skip error resolved'.format(BusStopUtil.get_stop_name(self.__stops[stop_idx - 1])))

                            self.__last_at_stop_idx = stop_idx - 1
                            print('Last-at stop is now registered as', BusStopUtil.get_stop_name(self.__stops[self.__last_at_stop_idx]))
                            print('-----------------------------------')
                            break

                        elif stop_idx == self.__dest_terminus_idx and at_stop == self.dest_terminus:
                            if BusStopUtil.is_near_stop(bus_data.get('latitude'), bus_data.get('longitude'), self.dest_terminus, distance_threshold=self.__dest_stop_distance_threshold):
                                self.status = 'AT_DEST_TERMINUS'
                                self.data['stops'][self.dest_terminus] = {
                                    'arrived': bus_data['updated_at']
                                }
                                print('Bus skipped to destination terminus {}, skip error resolved'.format(at_stop))
                                
                            else:
                                self.status = 'IN_TRANSIT_TO_DEST'
                                print('Bus skipped to be in transit to destination terminus {}, skip error resolved'.format(at_stop))

                            print('-----------------------------------')
                            break

            elif self.status == 'NEAR_STOP' and not BusStopUtil.is_near_stop(bus_data.get('latitude'), bus_data.get('longitude'), self.__stops[self.__last_at_stop_idx + 1]):
                self.__last_at_stop_idx += 1
                self.data['stops'][self.__stops[self.__last_at_stop_idx]]['departed'] = bus_data['updated_at']
                if self.__last_at_stop_idx == self.__dest_terminus_idx - 1:
                    self.status = 'IN_TRANSIT_TO_DEST'
                else:
                    self.status = 'IN_TRANSIT'
                    
            elif self.status == 'IN_TRANSIT_TO_DEST' and BusStopUtil.is_near_stop(bus_data.get('latitude'), bus_data.get('longitude'), self.dest_terminus, distance_threshold=self.__dest_stop_distance_threshold):
                self.status = 'AT_DEST_TERMINUS'
                self.data['stops'][self.dest_terminus] = {
                    'arrived': bus_data['updated_at']
                }
                self.data['arriveDest'] = bus_data['updated_at']
                
                self.__print_info(bus_data.get('latitude'), bus_data.get('longitude'), bus_data['updated_at'])

        else:
            print('Received None for bus data')
            self.__error_strikes += 1

            if self.__error_strikes == 3:
                self.status = 'ERROR'
                print(f'Bus {self.bus_id} status now set to ERROR')

    def get_recorded_data(self):
        return self.data

    def __print_info(self, bus_lat, bus_long, updated_at):
        print(f'rte{self.route_id}, bID: {self.bus_id}, status {self.status}')
        print('timestamp:', updated_at)
        print(f'location: https://www.google.com/maps/search/?api=1&query={bus_lat},{bus_long}')
