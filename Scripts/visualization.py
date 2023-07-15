import argparse
from datetime import datetime
import time
import pygame
import os
from moviepy.editor import *

MILLISECONDS_PER_SECOND = 1000 

class HeadCanvas:

    def __init__(self, file_path, fps, position):
        self.video = VideoFileClip(file_path)
        self.frames = self.video.iter_frames()
        self.update_period = MILLISECONDS_PER_SECOND/(fps)
        self.time_since_last_update = self.update_period # Always update at first call 
        self.position = position

    def update(self, dt, screen):
        self.time_since_last_update += dt
        if self.time_since_last_update < self.update_period:
            return
        self.time_since_last_update = 0
        try:
            frame = next(self.frames)
            gif_surface = pygame.surfarray.make_surface(frame)
            screen.blit(gif_surface, self.position)
        except StopIteration:
            self.frames = self.video.iter_frames()
            frame = next(self.frames)
            gif_surface = pygame.surfarray.make_surface(frame)
            screen.blit(gif_surface, self.position)


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
            timestamp, lat, lon = line.split(';')
            timestamp = int(timestamp)
            lat = float(lat)
            lon = float(lon)
            position = Position(timestamp, lat, lon)
            self.positions[sat_name] = position

    def set_initial_readout(self, initial_timestamp=None):
        if initial_timestamp is None:
            initial_timestamp = datetime.now()
            initial_timestamp = time.mktime(initial_timestamp.timetuple())
        self.update_positions()
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

class EarthCanvas:

    def __init__(self, image_path, satellites, position, size):
        self.backdrop = pygame.image.load(image_path)#.convert()
        self.position = position
        self.size = size
        self.satellites = satellites

    def update(self, dt, screen):
        self.satellites.update(dt)
        screen.blit(self.backdrop, self.position)

    def cleanup(self):
        self.satellites.cleanup()

class ManWhoLaughsDisplay:

    def __init__(self, head, earth, screen_size):
        self.head = head
        self.earth = earth
        self.screen = pygame.display.set_mode(screen_size)
        self.clock = pygame.time.Clock()

    def update(self):
        self.handle_events()
        dt = self.clock.tick()
        self.head.update(dt, self.screen)
        self.earth.update(dt, self.screen)
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

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gif_file', type=str, required=True,
                        help='Path to GIF file')
    parser.add_argument('--gif_fps', type=int, default=60,
                        help='Frames per second of gif animation')
    parser.add_argument('--gif_position', type=integer_pair, default=(0,0),
                        help='Position of top left corner of gif.')
    parser.add_argument('--window_size', type=integer_pair, default=(800,600),
                        help='Size of the window in pixels.')
    parser.add_argument('-s', '--satellite_directory', type=str, required=True,
                        help='Folder with satellite files')
    parser.add_argument('-e', '--earth_file', type=str, required=True,
                        help='Path to earth backdrop image')
    parser.add_argument('--initial_timestamp', type=int, default=None,
                        help='Initial timestampt in unix format, set only during tests.')
    parser.add_argument('--sampling_rate', type=int, default=1,
                        help='Sampling rate of satellite positions in seconds')
    return parser.parse_args()


def main():
    pygame.init()
    args = parse_arguments()
    satellites = Satellites(args.satellite_directory, args.sampling_rate)
    satellites.set_initial_readout(args.initial_timestamp)
    earth = EarthCanvas(args.earth_file, satellites, (0,0), (800, 600))
    head = HeadCanvas(args.gif_file, args.gif_fps, args.gif_position)
    mwl_display = ManWhoLaughsDisplay(head, earth, args.window_size)
    try:
        while True:
            mwl_display.update()
    except StopIteration:
        print('Stopped')
        mwl_display.cleanup()

if __name__ == '__main__':
    main()


