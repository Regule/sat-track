import argparse
import math
import serial
import time
import os
import pygame as pg
from datetime import datetime


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


