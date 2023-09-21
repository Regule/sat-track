import argparse
import math
import serial
import time
import os
import pygame as pg
from datetime import datetime

#===================================================================================================
#                                             MODEL 
#===================================================================================================

MILLISECONDS_PER_SECOND = 1000 


def coordinates_to_authagraph(location):
    # Constants for AuthaGraph projection
    radius = 1.0  # Radius of the AuthaGraph sphere

    # Convert latitude and longitude to radians
    lat_rad = math.radians(location[0])
    lon_rad = math.radians(location[1])

    # Calculate AuthaGraph coordinates
    x = radius * (1 + 0.5 * math.cos(lat_rad) * math.cos(lon_rad))
    y = radius * (1 + 0.5 * math.cos(lat_rad) * math.sin(lon_rad))
    #z = radius * 0.5 * math.sin(lat_rad)

    return x, y#, z

class Location:

    def __init__(self, timestamp, lat, lon):
        self.lat = lat
        self.lon = lon
        self.timestamp = timestamp

    def get_coordinates(self):
        return [self.lat, self.lon]

    def __str__(self):
        return f'{self.timestamp} - [{self.lat} {self.lon}]'

class SatelliteFile:

    def __init__(self, path):
        self.sat_file = open(path, 'r')
        self.location = None

    def get_next_location(self):
        try:
            line = self.sat_file.readline()
            self.location = self.parse_location_entry(line)
        except Exception:
            pass # If we filed at reading new location we just ignore that :(

    def cleanup(self):
        self.sat_file.close()

    @staticmethod
    def parse_location_entry(line):
        timestamp, lat, lon = line.split(';')
        timestamp = int(timestamp)
        lat = float(lat)
        lon = float(lon)
        position = Location(timestamp, lat, lon)


class Satellites:

    def __init__(self, folder, sampling_rate):
        self.sats = {}
        for entry in os.scandir(folder):
            if entry.is_file():
                sat_name = entry.name.split('.')[0].replace('_',' ')
                sat_path = os.path.join(folder, entry.name)
                self.sats[sat_name] = SatelliteFile(sat_path) 
        self.update_period = MILLISECONDS_PER_SECOND/sampling_rate
        self.time_since_last_update = 0
        self.positions = {}

    def update_positions(self):
        for sat_name, sat_file in self.sats.items():
            self.positions[sat_name] = sat_file.get_next_location()

    def set_initial_readout(self, timestamp=None, skip_to_timestamp=True):
        self.update_positions()
        if skip_to_timestamp:
           self.skip_to_timestamp(timestamp) 

    def skip_to_timestamp(self, timestamp):
        skipped_positions = 0
        if timestamp is None:
            timestamp = datetime.now()
            timestamp = time.mktime(timestamp.timetuple())
        while list(self.positions.values())[0].timestamp < timestamp:
            self.update_positions()
            skipped_positions += 1
        print(f'Skipped {skipped_positions} positions.')

    def update(self, dt):
        self.time_since_last_update += dt
        if self.time_since_last_update < self.update_period:
            return
        self.time_since_last_update = 0
        self.update_positions()

    def cleanup(self):
        for _, file in self.sats.items():
            file.cleanup()

    def is_satellite_in_range(self, position, distance):
        for position in self.positions:
           a = position[0]-position[0] 
           b = position[1]-position[1]
           if math.sqrt(a*a+b*b)<distance:
               return True
        return False


#===================================================================================================
#                                            DISPLAY
#===================================================================================================
class DisplayBox:

    def __init__(self, position, size):
        self.position = position
        self.size = size

    def normalized_to_relative_position(self, normalized_position):
        relative_position = [0,0]
        for idx in range(len(relative_position)):
            relative_position[idx] = int(normalized_position[idx]*self.size[idx]+self.position[idx])
        return relative_position

    def update(self, screen, dt):
        pass


