import sys
import pygame
import pylab
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from pathlib import Path
from beyond.io.tle import Tle
from beyond.dates import Date, timedelta

matplotlib.use("Agg")
matplotlib.rcParams['savefig.pad_inches'] = 0
import matplotlib.backends.backend_agg as agg

ISS_TLE = Tle("""ISS (ZARYA)
1 25544U 98067A   19004.59354167  .00000715  00000-0  18267-4 0  9995
2 25544  51.6416  95.0104 0002419 236.2184 323.8248 15.53730729149833""")

def tle_to_coordinate_list(tle_str):

    # Conversion into `Orbit` object
    orb = tle_str.orbit()

    # Tables containing the positions of the ground track
    latitudes, longitudes = [], []
    lons, lats = [], []
    prev_lon, prev_lat = None, None


    period = orb.infos.period
    start = orb.date - period
    stop = 2 * period
    step = period / 100

    for point in orb.ephemeris(start=start, stop=stop, step=step):

        # Conversion to earth rotating frame
        point.frame = 'ITRF'

        # Conversion from cartesian to spherical coordinates (range, latitude, longitude)
        point.form = 'spherical'

        # Conversion from radians to degrees
        lon, lat = np.degrees(point[1:3])

        # Creation of multiple segments in order to not have a ground track
        # doing impossible paths
        if prev_lon is None:
            lons = []
            lats = []
            longitudes.append(lons)
            latitudes.append(lats)
        elif orb.i < np.pi /2 and (np.sign(prev_lon) == 1 and np.sign(lon) == -1):
            lons.append(lon + 360)
            lats.append(lat)
            lons = [prev_lon - 360]
            lats = [prev_lat]
            longitudes.append(lons)
            latitudes.append(lats)
        elif orb.i > np.pi/2 and (np.sign(prev_lon) == -1 and np.sign(lon) == 1):
            lons.append(lon - 360)
            lats.append(lat)
            lons = [prev_lon + 360]
            lats = [prev_lat]
            longitudes.append(lons)
            latitudes.append(lats)

        lons.append(lon)
        lats.append(lat)
        prev_lon = lon
        prev_lat = lat
    latitudes = np.hstack(latitudes)
    longitudes = np.hstack(longitudes)
    return orb, zip(latitudes, longitudes)

# Set up pygame
pygame.init()
width, height = 800, 400
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

orb, coords = tle_to_coordinate_list(ISS_TLE)

running = True
im = plt.imread('Data/earth.jpg')

# Animation loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill((255, 255, 255))


    
    try:
        lons, lats = next(coords)
        fig = pylab.figure(figsize=[8, 4], # Inches
                   dpi=100,
                   )
        fig.tight_layout(pad=0)
        ax = fig.gca()
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        #ax.set_axis_off()
        #ax.margins(x=0, y=0)
        plt.autoscale(tight=True)
        #ax.imshow(im, extent=[-180, 180, -90, 90])
        ax.set_xlim([-180, 180])
        ax.set_ylim([-90, 90])
        ax.plot([lons], [lats], 'ro', linestyle='none')

        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()
        plt_surface = pygame.image.fromstring(raw_data, size, "RGB")
        plt.close(fig)
    except StopIteration:
        pass # In this demo just stop updating and ignore event
    # Display the plot on the screen
    screen.blit(plt_surface, (0, 0))
    pygame.display.flip()


    # Control the animation speed
    clock.tick(240)

# Quit the program
pygame.quit()
plt.close()

