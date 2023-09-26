import argparse
import math
import serial
from datetime import datetime
import time
import pygame
import os
from moviepy.editor import *
import pyproj

#TODO : FIX DEVICE POSITION
#TODO : TRY ADDING AuthaGraph PROJECTION
#TODO : DISTANCE MEASUREMENTS
#TODO : ADD SERIAL SUPPORT
#TODO : GIF OPACITY
#TODO : LETTERS

MILLISECONDS_PER_SECOND = 1000 

class HeadCanvas:

    def __init__(self, file_path, fps, position, size):
        self.video = VideoFileClip(file_path)
        self.frames = self.video.iter_frames()
        self.update_period = MILLISECONDS_PER_SECOND/(fps)
        self.time_since_last_update = self.update_period # Always update at first call 
        self.position = position
        self.size = size

    def update(self, dt, screen):
        self.time_since_last_update += dt
        if self.time_since_last_update < self.update_period:
            return
        self.time_since_last_update = 0
        try:
            frame = next(self.frames)
            gif_surface = pygame.surfarray.make_surface(frame)
            gif_surface = pygame.transform.scale(gif_surface, self.size)
            screen.blit(gif_surface, self.position)
        except StopIteration:
            self.frames = self.video.iter_frames()
            frame = next(self.frames)
            gif_surface = pygame.surfarray.make_surface(frame)
            gif_surface = pygame.transform.scale(gif_surface, self.size)
            screen.blit(gif_surface, self.position)

class TextField:

    def __init__(self, position, device_location, font_size=32):
        self.position = position
        self.device_location = device_location
        self.font = pygame.font.Font('freesansbold.ttf', font_size)

    def update(self, dt, screen):
        text = self.font.render(f'{self.device_location[0]} {self.device_location[1]}', True, (0,255,0), (0,0,0))
        textRect = text.get_rect()
        textRect.center = self.position 
        screen.blit(text, textRect)



class Position:

    def __init__(self, timestamp, lat, lon):
        self.lat = lat
        self.lon = lon
        self.timestamp = timestamp



class Satellites:

    def __init__(self, folder, sampling_rate):
        self.sats = {}
        for entry in os.scandir(folder):
            if entry.is_file():
                sat_name = entry.name.split('.')[0].replace('_',' ')
                sat_path = os.path.join(folder, entry.name)
                print(f'Satellite {sat_name} at path {sat_path}')
                sat_file = open(sat_path, "r")
                self.sats[sat_name] = sat_file 
        self.update_period = MILLISECONDS_PER_SECOND/sampling_rate
        self.time_since_last_update = 0
        self.positions = {}

    def update_positions(self):
        for sat_name, sat_file in self.sats.items():
            line = sat_file.readline()
            try:
                timestamp, lat, lon = line.split(';')
                timestamp = int(timestamp)
                lat = float(lat)
                lon = float(lon)
                position = Position(timestamp, lat, lon)
                self.positions[sat_name] = position
            except Exception as e:
                pass

    def set_initial_readout(self, initial_timestamp=None, update_timestamps=True):
        if initial_timestamp is None:
            initial_timestamp = datetime.now()
            initial_timestamp = time.mktime(initial_timestamp.timetuple())
        self.update_positions()
        if not update_timestamps:
            return
        skipped_positions = 0
        while list(self.positions.values())[0].timestamp < initial_timestamp:
            self.update_positions()
            skipped_positions += 1
        print(f'Skipped {skipped_positions} positions.')


    def update(self, dt):
        self.time_since_last_update += dt
        if self.time_since_last_update < self.update_period:
            return
        self.update_positions()
        self.time_since_last_update = 0

    def cleanup(self):
        for _, file in self.sats.items():
            file.close()

    def is_satellite_in_range(self, device_position, distance):
        for position in self.positions:
           a = position[0]-device_position[0] 
           b = position[1]-device_position[1]
           if math.sqrt(a*a+b*b)<distance:
               return True
        return False

class EarthCanvas:

    def __init__(self, image_path, satellites, position, size, device_location):
        self.image_path = image_path
        self.backdrop = None
        self.position = position
        self.size = size
        self.satellites = satellites
        self.device_location = device_location

    def reload_image(self):
        self.backdrop = pygame.transform.scale(pygame.image.load(self.image_path), self.size)

    def update(self, dt, screen):
        self.satellites.update(dt)
        screen.blit(self.backdrop, self.position)
        for _, position in self.satellites.positions.items():
            self.draw_position(position, screen, (255,255,255))
        if self.device_location is not None:
            self.draw_position(self.device_location, screen, (255,0,0))

    def lat_lon_to_xy(self, lat, lon):
        # Define the AuthaGraph projection using Pyproj
        authagraph_proj = pyproj.Proj("+proj=aea +lat_1=25 +lat_2=45 +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=GRS80")
        mercator = pyproj.Proj(proj='merc', lat_ts=0, lon_0=5, x_0=0, y_0=0, ellps='WGS84')
        
        # Transform the latitude and longitude to x, y
        x, y = mercator(lon, lat)

        # Normalize x and y to the range [0, 1]
        x = (x + 20037508.34) / (2 * 20037508.34)
        y = (y + 20037508.34) / (2 * 20037508.34)
        #y = 1 - (y + 10018754.17) / (2 * 10018754.17)

        return x, y

    def draw_position(self, position, screen, color):
        
        # Constants for AuthaGraph projection
        radius = 1.0  # Radius of the AuthaGraph sphere

        # Convert latitude and longitude to radians
        lat_rad = math.radians(position.lat)
        lon_rad = math.radians(position.lon)

        # Calculate AuthaGraph coordinates
        x = radius * (1 + 0.5 * math.cos(lat_rad) * math.cos(lon_rad))
        y = radius * (1 + 0.5 * math.cos(lat_rad) * math.sin(lon_rad))
        #z = radius * 0.5 * math.sin(lat_rad)
        
        x = x/3.5
        y = y/2.5

        x,y = self.lat_lon_to_xy(position.lat, position.lon)
        print(f'{x} -- {y}')
        x = int((x)*self.size[0]+self.position[0])
        y = int((y)*self.size[1]+self.position[1])

        #x = int((position.lon + 180) * (self.size[0] / 360))+self.position[0]
        #y = int((90 - position.lat) * (self.size[1] / 180))+self.position[1]
        print(f'{x} -- {y}')
        pygame.draw.circle(screen, color, (x, y), 2)

    def cleanup(self):
        self.satellites.cleanup()

class Helmet:
    ROZKAZ_POMPA_WLACZ = b'P'
    ROZKAZ_POMPA_WYLACZ = b'L'
    ROZKAZ_ODPOWIETRZANIE_WLACZ = b'O'
    ROZKAZ_SERWO_WLACZ = b'S'
    ROZKAZ_SERWO_WYLACZ = b'Z'
    ROZKAZ_DEMO = b'D'

    def __init__(self, serial_path):
        if serial_path is None:
            self.serial = None
        else:
            self.serial = serial.Serial(serial_path)

    
    def activate_pump(self):
        if self.serial is None:
            return
        self.serial.write(Helmet.ROZKAZ_POMPA_WLACZ)

    def stop_pump(self):
        if self.serial is None:
            return
        self.serial.write(Helmet.ROZKAZ_POMPA_WYLACZ)

    def release_pump(self):
        if self.serial is None:
            return
        self.serial.write(Helmet.ROZKAZ_ODPOWIETRZANIE_WLACZ)

    def activate_servo(self):
        if self.serial is None:
            return
        self.serial.write(Helmet.ROZKAZ_SERWO_WLACZ)

    def deactivate_servo(self):
        if self.serial is None:
            return
        self.serial.write(Helmet.ROZKAZ_SERWO_WYLACZ)

    def play_demo(self):
        if self.serial is None:
            return
        self.serial.write(Helmet.ROZKAZ_DEMO)
    


class ManWhoLaughsDisplay:

    def __init__(self, head, earth, helmet, text_field):
        self.helmet = helmet
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        screen_size = self.screen.get_size()
        self.head = head
        head_size = (screen_size[0]*self.head.size[0], screen_size[1]*self.head.size[1])
        head_position = (screen_size[0]*self.head.position[0], screen_size[1]*self.head.position[1])
        self.head.size = head_size
        self.head.position = head_position
        self.earth = earth
        earth_size = (screen_size[0]*self.earth.size[0], screen_size[1]*self.earth.size[1])
        earth_position = (screen_size[0]*self.earth.position[0], screen_size[1]*self.earth.position[1])
        print(f'Earth position = {earth_position} Earth size = {earth_size}')
        self.earth.position = earth_position
        self.earth.size = earth_size
        self.earth.reload_image()
        self.text_field = text_field
        text_position = (screen_size[0]*self.text_field.position[0], screen_size[1]*self.text_field.position[1])
        self.text_field.position = text_position

        self.clock = pygame.time.Clock()

    def update(self):
        self.handle_events()
        dt = self.clock.tick()
        self.head.update(dt, self.screen)
        self.earth.update(dt, self.screen)
        self.text_field.update(dt, self.screen)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise StopIteration

    def cleanup(self):
        self.earth.cleanup()


def integer_pair(txt):
    val1, val2 = txt.split('x')
    return (int(val1), int(val2))

def float_pair(txt):
    txt = txt.replace('n','-')
    val1, val2 = txt.split('x')
    return (float(val1), float(val2))

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gif_file', type=str, required=True,
                        help='Path to GIF file')
    parser.add_argument('--gif_fps', type=int, default=60,
                        help='Frames per second of gif animation')
    parser.add_argument('--gif_size', type=float_pair, default=(0.3,0.3),
                        help='Size of animated gif')
    parser.add_argument('--gif_position', type=float_pair, default=(0,0),
                        help='Position of top left corner of gif.')
    parser.add_argument('-s', '--satellite_directory', type=str, required=True,
                        help='Folder with satellite files')
    parser.add_argument('-e', '--earth_file', type=str, required=True,
                        help='Path to earth backdrop image')
    parser.add_argument('--initial_timestamp', type=int, default=None,
                        help='Initial timestampt in unix format, set only during tests.')
    parser.add_argument('--sampling_rate', type=int, default=1,
                        help='Sampling rate of satellite positions in seconds')
    parser.add_argument('--disable_timestamp_adjustment', action='store_true',
                        help='Disables adjustment of timestamps in satellite file (FOR TESTS ONLY).')
    parser.add_argument('--display_position', type=float_pair, default=(0.7,1.0),
                        help='Position of earth and satellites display')
    parser.add_argument('--display_size', type=float_pair, default=(0.3,0),
                        help='Size of display that shows earth and satellites')
    parser.add_argument('--helmet_port', type=str, default=None,
                        help='Serial port for communication with helmet.')
    parser.add_argument('--device_location', type=float_pair, default=None,
                        help='Lat lon')
    parser.add_argument('--text_location', type=float_pair, default=(0.5, 0.5),
                        help='Loacation at which text will be displayed')
    return parser.parse_args()


def main():
    pygame.init()
    args = parse_arguments()
    device_location = None
    if args.device_location is not None:
        device_location = Position(0, args.device_location[0], args.device_location[1])
    helmet = Helmet(args.helmet_port)
    satellites = Satellites(args.satellite_directory, args.sampling_rate)
    satellites.set_initial_readout(args.initial_timestamp, not args.disable_timestamp_adjustment)
    earth = EarthCanvas(args.earth_file, satellites, args.display_position, args.display_size, device_location)
    head = HeadCanvas(args.gif_file, args.gif_fps, args.gif_position, args.gif_size)
    text_field = TextField(args.text_location, args.device_location)
    mwl_display = ManWhoLaughsDisplay(head, earth, helmet, text_field)
    try:
        while True:
            mwl_display.update()
    except StopIteration:
        print('Stopped')
        mwl_display.cleanup()

if __name__ == '__main__':
    main()


