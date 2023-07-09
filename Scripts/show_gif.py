import pygame
import os
from moviepy.editor import *

def main():
    # Initialize Pygame
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("GIF Viewer")
    
    # Load the GIF
    gif_path = os.path.join("Data/amogus.gif")  # Replace with the actual path to your GIF file
    video = VideoFileClip(gif_path)
    gif_frames = video.iter_frames()
    
    # Create a clock object to control the frame rate
    clock = pygame.time.Clock()
    
    # Main loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Clear the screen
        screen.fill((0, 0, 0))
        
        try:
            # Get the next frame of the GIF
            frame = next(gif_frames)
            
            # Convert the frame into a Pygame surface
            gif_surface = pygame.surfarray.make_surface(frame)
            
            # Display the frame on the screen
            screen.blit(gif_surface, (0, 0))
        except StopIteration:
            # If we've reached the end of the GIF, restart from the beginning
            gif_frames = video.iter_frames()
        
        # Update the display
        pygame.display.flip()
        
        # Control the frame rate
        clock.tick(30)  # Set the desired frame rate (e.g., 30 frames per second)
    
    # Quit Pygame
    pygame.quit()

if __name__ == "__main__":
    main()

