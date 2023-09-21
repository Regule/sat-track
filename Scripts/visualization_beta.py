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

class Position:

    def __init__(self, timestamp, lat, lon):
        self.lat = lat
        self.lon = lon
        self.timestamp = timestamp

    def get_coordinates(self):
        return [self.lat, self.lon]

    def __str__(self):
        return f'{self.timestamp} - [{self.lat} {self.lon}]'

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


