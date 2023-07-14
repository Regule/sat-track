import time
import argparse
import datetime
import os
from skyfield.api import Topos, load

TIME_FORMAT = '%Y-%m-%d-%H:%M:%S'

class DiscreteTimeDomain:

    def __init__(self, start, end=None, step=1):
        self.start = start
        if end is None:
            self.end = start + datetime.timedelta(days=1)
        else:
            self.end = end
        self.step = datetime.timedelta(seconds=step)
        self.current = start

    def reset(self):
        self.current = self.start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > self.end:
            raise StopIteration
        return_value = self.current
        self.current += self.step
        return return_value

def load_satellites(file_path):
    satellites = load.tle_file(file_path)
    print('Loaded', len(satellites), 'satellites')
    return satellites


def calculate_position(satellite, time):
    ts = load.timescale()
    t = ts.utc(time.year, time.month, time.day, time.hour, time.minute, time.second)
    geocentric = satellite.at(t)
    subpoint = geocentric.subpoint()
    latitude = subpoint.latitude.degrees
    longitude = subpoint.longitude.degrees
    return latitude, longitude


def create_trace_file(satellite, time_domain, output_folder):
    print(f'Processing {satellite.name}')
    file_path = os.path.join(output_folder, f'{satellite.name.replace(" ","_")}.txt')
    with open(file_path, 'w') as sat_file:
        time_domain.reset()
        for t in time_domain:
            latitute , longitude = calculate_position(satellite, t)
            timestamp = time.mktime(t.timetuple())
            sat_file.write(f'{timestamp};{latitute};{longitude}\n')

def datetime_str(text):
    return datetime.datetime.strptime(text, TIME_FORMAT)

def satellite_list(txt):
    return txt.replace('_',' ').split(',')

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--satellite_file', type=str, default='http://celestrak.org/NORAD/elements/stations.txt',
                        help='Path to TLE file, may be url.')
    parser.add_argument('-s', '--start_datetime', type=datetime_str, default=datetime.datetime.now(),
                        help='Datetime of first position in format Y-m-d-H:M:S')
    parser.add_argument('-e', '--end_datetime', type=datetime_str, default=None,
                        help='Datetime of last position in format Y-m-d-H:M:S')
    parser.add_argument('-t', '--timestep', type=int, default=1,
                        help='Time in seconds between two positions.')
    parser.add_argument('-v', '--satellites', type=satellite_list, required=True,
                        help='Names of satellites that will be processed, separated by comma')
    parser.add_argument('-o', '--output_folder', type=str, default='./local',
                        help='Folder to which output will be saved')
    return parser.parse_args()

def main():
    args = parse_arguments()
    satellites = load_satellites(args.satellite_file)
    satellites = {sat.name: sat for sat in satellites}
    time_domain = DiscreteTimeDomain(args.start_datetime, args.end_datetime, args.timestep)
    for satellite in args.satellites:
        create_trace_file(satellites[satellite], time_domain, args.output_folder)

if __name__ == '__main__':
    main()
