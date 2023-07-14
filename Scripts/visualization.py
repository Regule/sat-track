import argparse
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


class ManWhoLaughsDisplay:

    def __init__(self, head, satellites, earth, screen_size):
        self.head = head
        self.satellistes = satellites
        self.earth = earth
        self.screen = pygame.display.set_mode(screen_size)
        self.clock = pygame.time.Clock()

    def update(self):
        self.handle_events()
        dt = self.clock.tick()
        self.head.update(dt, self.screen)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise StopIteration

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--gif_file', type=str, required=True,
                        help='Path to GIF file')
    parser.add_argument('--gif_fps', type=int, default=60,
                        help='Frames per second of gif animation')
    return parser.parse_args()


def main():
    args = parse_arguments()
    head = HeadCanvas(args.gif_file, args.gif_fps, (0,0))
    mwl_display = ManWhoLaughsDisplay(head, None, None, (800,600))
    try:
        while True:
            mwl_display.update()
    except StopIteration:
        print('Stopped')

if __name__ == '__main__':
    main()


