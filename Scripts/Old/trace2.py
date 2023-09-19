import pygame
import datetime
from skyfield.api import Topos, load

# Function to parse TLE entry and return satellite object
def parse_tle(tle_data):
    lines = tle_data.strip().split('\n')
    satellites = load.tle(lines)
    satellite = satellites[0]
    return satellite

# Function to calculate satellite position for a given time
def calculate_position(satellite, time):
    ts = load.timescale()
    t = ts.utc(time.year, time.month, time.day, time.hour, time.minute, time.second)
    geocentric = satellite.at(t)
    subpoint = geocentric.subpoint()
    latitude = subpoint.latitude.degrees
    longitude = subpoint.longitude.degrees
    return latitude, longitude

# Function to display satellite trace on Pygame window
def display_trace(tle_data, start_time, end_time):
    satellite = parse_tle(tle_data)
    start_datetime = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_datetime = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    size = width, height = 800, 600
    black = 0, 0, 0

    pygame.init()
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    running = True
    current_time = start_datetime

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(black)

        latitude, longitude = calculate_position(satellite, current_time)
        x = int((longitude + 180) * (width / 360))
        y = int((90 - latitude) * (height / 180))
        pygame.draw.circle(screen, (255, 255, 255), (x, y), 2)

        pygame.display.flip()
        clock.tick(60)

        current_time += datetime.timedelta(seconds=1)
        if current_time > end_datetime:
            running = False

    pygame.quit()

# Example usage
tle_entry = """
ISS (ZARYA)             
1 25544U 98067A   21290.47597024  .00000765  00000-0  16968-4 0  9995
2 25544  51.6456  10.3567 0009774 337.5833  22.4636 15.48919442442026
"""
start_time = "2023-07-09 00:00:00"
end_time = "2023-07-09 01:00:00"

display_trace(tle_entry, start_time, end_time)

