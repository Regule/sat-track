import argparse
from datetime import datetime
import time
import pygame
import os
from moviepy.editor import *

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

class EarthCanvas:

    def __init__(self, image_path, satellites, position, size):
        self.backdrop = pygame.transform.scale(pygame.image.load(image_path), size)
        self.position = position
        self.size = size
        self.satellites = satellites

    def update(self, dt, screen):
        self.satellites.update(dt)
        screen.blit(self.backdrop, self.position)
        for _, position in self.satellites.positions.items():
            self.draw_position(position, screen)

    def draw_position(self, position, screen):
        x = int((position.lon + 180) * (self.size[0] / 360))+self.position[0]
        y = int((90 - position.lat) * (self.size[1] / 180))+self.position[1]
        #print(f'{x} -- {y}')
        pygame.draw.circle(screen, (255, 255, 255), (x, y), 2)

    def cleanup(self):
        self.satellites.cleanup()

class ManWhoLaughsDisplay:

    def __init__(self, head, earth):
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        screen_size = self.screen.get_size()
        self.head = head
        head_size = (screen_size[0]*self.head.size[0], screen_size[1]*self.head.size[1])
        head_position = (screen_size[0]*self.head.position[0], screen_size[1]*self.head.position[1])
        self.head.size = head_size
        self.head.position = head_position
        self.earth = earth
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

def float_pair(txt):
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
    parser.add_argument('--display_position', type=integer_pair, default=(0,0),
                        help='Position of earth and satellites display')
    parser.add_argument('--display_size', type=integer_pair, default=(100,0),
                        help='Size of display that shows earth and satellites')
    return parser.parse_args()


def main():
    pygame.init()
    args = parse_arguments()
    satellites = Satellites(args.satellite_directory, args.sampling_rate)
    satellites.set_initial_readout(args.initial_timestamp, not args.disable_timestamp_adjustment)
    earth = EarthCanvas(args.earth_file, satellites, args.display_position, args.display_size)
    head = HeadCanvas(args.gif_file, args.gif_fps, args.gif_position, args.gif_size)
    mwl_display = ManWhoLaughsDisplay(head, earth)
    try:
        while True:
            mwl_display.update()
    except StopIteration:
        print('Stopped')
        mwl_display.cleanup()

if __name__ == '__main__':
    main()


