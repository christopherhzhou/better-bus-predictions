from .api.busutil import BusDataUtil
from .api.locutil import BusLocationUtil

from .api.constants.stop_distance_thresholds import StopDistanceThresholds


# assumes that a bus is either at or soon to arrive at origin terminus station
class BusTracker:
    
    def __init__(self, bus_id, trip_id, route_id, direction_id):
        self.bus_id = bus_id
        
        bus_data = BusDataUtil.get_bus_data(bus_id)
        
        self.stops = BusDataUtil.get_stops_list(trip_id)
        self.origin_terminus = self.stops[0]
        self.dest_terminus = self.stops[len(self.stops)-1]
        self.last_at_stop_idx = 0
        
        
        self.data = {
            'tripId': trip_id,
            'route': route_id,
            'direction': direction_id,
            'stops': {}
        }
        
        self.origin_stop_distance_threshold = StopDistanceThresholds.get(self.origin_terminus) if StopDistanceThresholds.get(self.origin_terminus) else 80
        self.dest_stop_distance_threshold = StopDistanceThresholds.get(self.dest_terminus) if StopDistanceThresholds.get(self.dest_terminus) else 80
        
        if BusLocationUtil.is_near_stop(bus_data['latitude'], bus_data['longitude'], self.origin_terminus, distance_threshold=self.origin_stop_distance_threshold):
            self.status = 'AT_ORIGIN_TERMINUS'
        else:
            self.status = 'SOON_ARRIVING_ORIGIN_TERMINUS'
            
        
        print('now tracking bus with id {} and tripid {}, status {}'.format(bus_id, trip_id, self.status))
            
        
    def update(self):
        bus_data = BusDataUtil.get_bus_data(self.bus_id)
        
        if bus_data['response_status_code'] == 200:
            if self.status == 'SOON_ARRIVING_ORIGIN_TERMINUS' and BusLocationUtil.is_near_stop(bus_data['latitude'], bus_data['longitude'], self.origin_terminus, distance_threshold=self.origin_stop_distance_threshold):
                self.status = 'AT_ORIGIN_TERMINUS'
                
                self.__print_info(bus_data['latitude'], bus_data['longitude'],bus_data['updated_at'])
               
            elif self.status == 'AT_ORIGIN_TERMINUS' and not BusLocationUtil.is_near_stop(bus_data['latitude'], bus_data['longitude'], self.origin_terminus, distance_threshold=self.origin_stop_distance_threshold):
                self.status = 'IN_TRANSIT'
                
                self.data['stops'][self.origin_terminus] = {
                    'departed': bus_data['updated_at']
                }
                
                self.__print_info(bus_data['latitude'], bus_data['longitude'],bus_data['updated_at'])
                
            elif self.status == 'IN_TRANSIT' and BusLocationUtil.is_near_stop(bus_data['latitude'], bus_data['longitude'], self.stops[self.last_at_stop_idx+1]):
                self.status = 'NEAR_STOP'
                self.data['stops'][self.stops[self.last_at_stop_idx+1]] = {
                    'arrived': bus_data['updated_at']
                }
                
                self.__print_info(bus_data['latitude'], bus_data['longitude'],bus_data['updated_at'])
                
            elif self.status == 'NEAR_STOP' and not BusLocationUtil.is_near_stop(bus_data['latitude'], bus_data['longitude'], self.stops[self.last_at_stop_idx+1]):
                self.last_at_stop_idx += 1
                self.data['stops'][self.stops[self.last_at_stop_idx]]['departed'] = bus_data['updated_at']
                if self.last_at_stop_idx == len(self.stops)-2:
                    self.status = 'IN_TRANSIT_TO_DEST'
                else:
                    self.status = 'IN_TRANSIT'
                    
                self.__print_info(bus_data['latitude'], bus_data['longitude'],bus_data['updated_at'])
                    
            elif self.status == 'IN_TRANSIT_TO_DEST' and BusLocationUtil.is_near_stop(bus_data['latitude'], bus_data['longitude'], self.dest_terminus, distance_threshold=self.dest_stop_distance_threshold):
                self.status = 'AT_DEST_TERMINUS'
                self.data['stops'][self.dest_terminus] = {
                    'arrived': bus_data['updated_at']
                }
                
                self.__print_info(bus_data['latitude'], bus_data['longitude'],bus_data['updated_at'])
                
                
    def get_recorded_data(self):
        return self.data
        
        
    def __print_info(self, bus_lat, bus_long, updated_at):
        print(self.status, self.bus_id)
        print('timestamp:', updated_at)
        print('location: https://www.google.com/maps/search/?api=1&query={lat},{lon})'.format(lat=bus_lat, lon=bus_long))