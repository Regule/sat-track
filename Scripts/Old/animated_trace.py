import pygame
import datetime
from skyfield.api import Topos, load, EarthSatellite

# Function to parse TLE entry and return satellite object
def parse_tle(tle_data):
    lines = tle_data.strip().split('\n')
    #print(lines)
    ts = load.timescale()
    satellite = EarthSatellite(lines[1], lines[2], 'ISS (ZARYA)', ts)
    return satellite

# Function to calculate satellite position for a given time
def calculate_position(satellite, time):
    ts = load.timescale()
    t = ts.utc(time.year, time.month, time.day, time.hour, time.minute, time.second)
    geocentric = satellite.at(t)
    subpoint = geocentric.subpoint()
    #print(subpoint)
    latitude = subpoint.latitude.degrees
    #print(f'LATITUDE = {latitude}')
    longitude = subpoint.longitude.degrees
    return latitude, longitude

# Function to display satellite position and continents contour on Pygame window
def display_animation(tle_data):
    satellite = parse_tle(tle_data)

    size = width, height = 800, 600
    black = 0, 0, 0

    pygame.init()
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    #continents_image = pygame.image.load("Data/continents.jpg")  # Load continents contour image
    #continents_rect = continents_image.get_rect()

    running = True
    current_time = datetime.datetime.utcnow()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(black)
        #screen.blit(continents_image, continents_rect)

        latitude, longitude = calculate_position(satellite, current_time)
        x = int((longitude + 180) * (width / 360))
        y = int((90 - latitude) * (height / 180))
        pygame.draw.circle(screen, (255, 255, 255), (x, y), 2)

        pygame.display.flip()
        clock.tick(60)

        current_time += datetime.timedelta(seconds=1)

    pygame.quit()

# Example usage
tle_entry = """
ISS (ZARYA)             
1 25544U 98067A   21290.47597024  .00000765  00000-0  16968-4 0  9995
2 25544  51.6456  10.3567 0009774 337.5833  22.4636 15.48919442442026
"""

display_animation(tle_entry)

