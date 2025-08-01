import argparse
import math
import serial
from datetime import datetime
import time
import pygame
import os
from moviepy.editor import VideoFileClip

MILLISECONDS_PER_SECOND = 1000 
enable_debug = False

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

    def __init__(self, position, font_size=22, satellites=None, 
                 font_type='freesansbold.ttf'):
        self.position = position
        self.font = pygame.font.Font(font_type, font_size)
        self.satellites = satellites

    def update(self, dt, screen):
        if self.satellites is not None:
            row_offset = 60
            column_offset = 180
            row = 0
            column = 0
            for satellite in self.satellites.positions.values():
                if row > 5:
                    column += 1
                    row = 0
                text = self.font.render(f'{satellite.lat:2.2f} {satellite.lon:2.2f}', True, (255,255,255), (0,0,0))
                textRect = text.get_rect()
                center = list(self.position) 
                center[0] += column * column_offset
                center[1] += row * row_offset
                textRect.center = center
                screen.blit(text, textRect)
                row += 1

class TextField2:

    def __init__(self, position, device_location, font_size=32,
                 font_type='freesansbold.ttf'):
        self.position = position
        self.device_location = device_location
        self.font = pygame.font.Font(font_type, font_size)

    def update(self, dt, screen):
        text = self.font.render(f'{self.device_location[0]:2.2f} {self.device_location[1]:2.2f}', True, (255,255,255), (0,0,0))
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
            except Exception:
                pass # If updating fails just ignore it

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

    def __init__(self, image_path, satellites, position,
                 size, device_location, alert_distance=0.0,
                 helmet=None):
        self.image_path = image_path
        self.backdrop = None
        self.position = position
        self.size = size
        self.satellites = satellites
        self.device_location = device_location
        self.alert_distance = alert_distance
        self.helmet = helmet

    def reload_image(self):
        print(self.size)
        #sys.exit()
        self.backdrop = pygame.transform.scale(pygame.image.load(self.image_path), self.size)

    def update(self, dt, screen):
        self.satellites.update(dt)
        screen.blit(self.backdrop, self.position)
        dev_pos = None
        alert = False
        if self.device_location is not None:
            dev_pos = self.draw_position(self.device_location, screen, (255,0,0))
            if enable_debug:
                self.draw_range(self.device_location, screen, (255,0,0), self.alert_distance)
        for _, position in self.satellites.positions.items():
            sat_pos = self.draw_position(position, screen, (255,255,255))
            dist = (dev_pos[0] - sat_pos[0])**2 + (dev_pos[1] - sat_pos[1])**2
            dist = math.sqrt(dist)
            if dist < self.alert_distance:
                alert = True
                if enable_debug:
                    self.draw_position(position, screen, (0,255,0))
        if self.helmet is not None:
            if alert:
                self.helmet.activate_pump()
            else:
                self.helmet.release_pump()

    def mercator_projection(self, longitude, latitude):
        # Define the Mercator projection bounds
        max_longitude = 180.0
        min_longitude = -180.0
        max_latitude = 85.051129
        min_latitude = -85.051129

        # Clamp the longitude and latitude within the bounds
        longitude = max(min(longitude, max_longitude), min_longitude)
        latitude = max(min(latitude, max_latitude), min_latitude)

        # Convert latitude and longitude to radians
        lat_rad = math.radians(latitude)

        # Perform the Mercator projection
        x = (longitude + 180.0) / 360.0
        y = (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0

        return x, y

    def draw_position(self, position, screen, color):
        x,y = self.mercator_projection(position.lon, position.lat)
        x = int((x)*self.size[0]+self.position[0])
        y = int((y)*self.size[1]+self.position[1])
        pygame.draw.circle(screen, color, (x, y), 5)
        return x, y

    def draw_range(self, position, screen, color, radius):
        x,y = self.mercator_projection(position.lon, position.lat)
        x = int((x)*self.size[0]+self.position[0])
        y = int((y)*self.size[1]+self.position[1])
        pygame.draw.circle(screen, color, (x, y), radius, width=2)
        return x, y

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

    def __init__(self, head, earth, helmet, text_field, text_field2):
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
        self.text_field2 = text_field2
        text_position = (screen_size[0]*self.text_field2.position[0], screen_size[1]*self.text_field2.position[1])
        self.text_field2.position = text_position
        self.clock = pygame.time.Clock()

    def update(self):
        self.handle_events()
        dt = self.clock.tick()
        #self.screen.fill((0,0,0))
        self.head.update(dt, self.screen)
        self.earth.update(dt, self.screen)
        self.text_field.update(dt, self.screen)
        self.text_field2.update(dt, self.screen)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise StopIteration
            elif event.type == pygame.KEYDOWN:
                if event.key == ord('a'):
                    self.helmet.activate_pump()
                elif event.key == ord('s'):
                    self.helmet.stop_pump()
                elif event.key == ord('d'):
                    self.helmet.release_pump()
                elif event.key == ord('z'):
                    self.helmet.activate_servo()
                elif event.key == ord('x'):
                    self.helmet.deactivate_servo()

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
    parser.add_argument('--text2_location', type=float_pair, default=(0.5, 0.5),
                        help='Loacation at which text will be displayed')
    parser.add_argument('--sat_font_size', type=int, default=32,
                        help='Size of font for satellite locations')
    parser.add_argument('--dev_font_size', type=int, default=32,
                        help='Size of font for satellite locations')
    parser.add_argument('--font_type', type=str, default='freesansbold.ttf',
                        help='Type of font used in application')
    parser.add_argument('--alert_distance', type=float, default=10.0,
                        help='Distance')
    parser.add_argument('--enable_debug', action='store_true',
                        help='Enables debug information')
    return parser.parse_args()


def main():
    global enable_debug
    pygame.init()
    args = parse_arguments()
    enable_debug = args.enable_debug
    device_location = None
    if args.device_location is not None:
        device_location = Position(0, args.device_location[0], args.device_location[1])
    helmet = Helmet(args.helmet_port)
    satellites = Satellites(args.satellite_directory, args.sampling_rate)
    satellites.set_initial_readout(args.initial_timestamp, not args.disable_timestamp_adjustment)
    earth = EarthCanvas(args.earth_file, satellites, args.display_position,
                        args.display_size, device_location, helmet=helmet,
                        alert_distance=args.alert_distance)
    head = HeadCanvas(args.gif_file, args.gif_fps, args.gif_position, args.gif_size)
    text_field2 = TextField2(args.text2_location, args.device_location,
                             font_size=args.dev_font_size, font_type=args.font_type)
    text_field = TextField(args.text_location, satellites=satellites,
                           font_size=args.sat_font_size, font_type=args.font_type)
    mwl_display = ManWhoLaughsDisplay(head, earth, helmet, text_field, text_field2)
    try:
        while True:
            mwl_display.update()
    except StopIteration:
        print('Stopped')
        mwl_display.cleanup()
    except Exception as e:
        print(f'Unexpected exception -> {e}')
        mwl_display.cleanup()

if __name__ == '__main__':
    main()


