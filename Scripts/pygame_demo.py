import numpy as np
import matplotlib.pyplot as plt
import pygame

# Set up pygame
pygame.init()
width, height = 800, 400
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Set up Matplotlib
fig, ax = plt.subplots(figsize=(8, 4))
x = np.linspace(0, 2 * np.pi, 100)
line, = ax.plot(x, np.sin(x), 'r-', linewidth=2)

# Animation variables
frequency = 1
amplitude = 1
time = 0
running = True

# Animation loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill((255, 255, 255))

    # Update the sinusoid
    y = amplitude * np.sin(2 * np.pi * frequency * time + np.pi / 2)
    line.set_ydata(y)

    # Draw the plot
    ax.set_ylim(-amplitude, amplitude)
    ax.set_xlim(0, 2 * np.pi)
    fig.canvas.draw()

    # Convert the Matplotlib figure to a Pygame surface
    buf = fig.canvas.buffer_rgba()
    plt_surface = pygame.image.fromstring(buf.tobytes(), fig.canvas.get_width_height(), 'RGBA')

    # Display the plot on the screen
    screen.blit(plt_surface, (0, 0))
    pygame.display.flip()

    # Update time
    time += 0.01

    # Control the animation speed
    clock.tick(60)

# Quit the program
pygame.quit()
plt.close()

