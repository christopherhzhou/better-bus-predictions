from .api.busutil import BusDataUtil
from .api.locutil import BusLocationUtil

from .api.constants.stop_distance_thresholds import StopDistanceThresholds


# assumes that a bus is either at or soon to arrive at origin terminus station
class BusTracker:
    
    def __init__(self, bus_id, trip_id, route_id):
        self.bus_id = bus_id
        self.route_id = route_id
        
        bus_data = BusDataUtil.get_bus_data(bus_id)
        
        self.__stops = BusDataUtil.get_stops_list(trip_id)
        self.__dest_terminus_idx = len(self.__stops) - 1
        self.origin_terminus = self.__stops[0]
        self.dest_terminus = self.__stops[self.__dest_terminus_idx]
        self.__last_at_stop_idx = 0

        self.__origin_stop_distance_threshold = StopDistanceThresholds.get(self.origin_terminus) if StopDistanceThresholds.get(self.origin_terminus) else 80
        self.__dest_stop_distance_threshold = StopDistanceThresholds.get(self.dest_terminus) if StopDistanceThresholds.get(self.dest_terminus) else 80

        if BusLocationUtil.is_near_stop(bus_data['latitude'], bus_data['longitude'], self.origin_terminus, distance_threshold=self.__origin_stop_distance_threshold):
            self.status = 'AT_ORIGIN_TERMINUS'
        else:
            self.status = 'SOON_ARRIVING_ORIGIN_TERMINUS'

        self.data = {
            'tripId': trip_id,
            'stops': {}
        }

        print('RTE{rte}: now tracking bus with id {bid} and tripid {tid}, status {sts}'.format(rte=route_id, bid=bus_id, tid=trip_id, sts=self.status))

    def update(self):
        bus_data = BusDataUtil.get_bus_data(self.bus_id)

        if bus_data['response_status_code'] == 200:

            # if bus is known to be soon arriving at origin terminus and it is found to be near origin terminus
            if self.status == 'SOON_ARRIVING_ORIGIN_TERMINUS' and BusLocationUtil.is_near_stop(bus_data['latitude'], bus_data['longitude'], self.origin_terminus, distance_threshold=self.__origin_stop_distance_threshold):
                # update status
                self.status = 'AT_ORIGIN_TERMINUS'

                # print info
                self.__print_info(bus_data['latitude'], bus_data['longitude'], bus_data['updated_at'])

            # if bus is known to be at origin terminus but is no longer near origin terminus...
            elif self.status == 'AT_ORIGIN_TERMINUS' and not BusLocationUtil.is_near_stop(bus_data['latitude'], bus_data['longitude'], self.origin_terminus, distance_threshold=self.__origin_stop_distance_threshold):
                # update status
                self.status = 'IN_TRANSIT'

                # set info
                self.data['stops'][self.origin_terminus] = {
                    'departed': bus_data['updated_at']
                }
                self.data['departOrigin'] = bus_data['updated_at']

                # print info
                self.__print_info(bus_data['latitude'], bus_data['longitude'], bus_data['updated_at'])

            # if bus is in transit...
            elif self.status == 'IN_TRANSIT':
                at_stop = bus_data['stop_id']

                # if bus is near the next expected stop... (standard behavior)
                if BusLocationUtil.is_near_stop(bus_data['latitude'], bus_data['longitude'], self.__stops[self.__last_at_stop_idx + 1]):
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
                    self.__print_info(bus_data['latitude'], bus_data['longitude'], bus_data['updated_at'])
                    print('API determined nearest stop:', at_stop)

                    # iterates through all the stops between the current possible stop the bus could be at all the way
                    # until the destination terminus
                    for stop_idx in range(self.__last_at_stop_idx + 1, self.__dest_terminus_idx + 1):
                        if stop_idx < self.__dest_terminus_idx and at_stop == self.__stops[stop_idx]:
                            # if this condition below is not true, is it possible another stop skip will be detected
                            # again - however, after the second iteration all skip errors should be resolved
                            if BusLocationUtil.is_near_stop(bus_data['latitude'], bus_data['longitude'], at_stop):
                                self.status = 'NEAR_STOP'
                                self.data['stops'][at_stop] = {
                                    'arrived': bus_data['updated_at']
                                }
                                print('Last skipped stop is {}, skip error resolved'.format(self.__stops[stop_idx - 1]))

                            self.__last_at_stop_idx = stop_idx - 1
                            print('Last-at stop is now registered as', self.__stops[self.__last_at_stop_idx])
                            break

                        elif stop_idx == self.__dest_terminus_idx and at_stop == self.dest_terminus:
                            if BusLocationUtil.is_near_stop(bus_data['latitude'], bus_data['longitude'], self.dest_terminus, distance_threshold=self.__dest_stop_distance_threshold):
                                self.status = 'AT_DEST_TERMINUS'
                                self.data['stops'][self.dest_terminus] = {
                                    'arrived': bus_data['updated_at']
                                }
                                print('Bus skipped to destination terminus {}, skip error resolved'.format(at_stop))
                                
                            else:
                                self.status = 'IN_TRANSIT_TO_DEST'
                                print('Bus skipped to be in transit to destination terminus {}, skip error resolved'.format(at_stop))

                            break

            elif self.status == 'NEAR_STOP' and not BusLocationUtil.is_near_stop(bus_data['latitude'], bus_data['longitude'], self.__stops[self.__last_at_stop_idx+1]):
                self.__last_at_stop_idx += 1
                self.data['stops'][self.__stops[self.__last_at_stop_idx]]['departed'] = bus_data['updated_at']
                if self.__last_at_stop_idx == self.__dest_terminus_idx - 1:
                    self.status = 'IN_TRANSIT_TO_DEST'
                else:
                    self.status = 'IN_TRANSIT'
                    
            elif self.status == 'IN_TRANSIT_TO_DEST' and BusLocationUtil.is_near_stop(bus_data['latitude'], bus_data['longitude'], self.dest_terminus, distance_threshold=self.__dest_stop_distance_threshold):
                self.status = 'AT_DEST_TERMINUS'
                self.data['stops'][self.dest_terminus] = {
                    'arrived': bus_data['updated_at']
                }
                
                self.__print_info(bus_data['latitude'], bus_data['longitude'], bus_data['updated_at'])

        else:
            #TODO implement strike system so if retrieving bus data returns multiple errors, set status to "ERROR"
            print('Status code:', bus_data['response_status_code'])

    def get_recorded_data(self):
        return self.data

    def __print_info(self, bus_lat, bus_long, updated_at):
        print('RTE' + self.route_id, self.bus_id, self.status)
        print('timestamp:', updated_at)
        print('location: https://www.google.com/maps/search/?api=1&query={lat},{lon}'.format(lat=bus_lat, lon=bus_long))