# initial.py
import pygame
import os
from load import load_images
from player import Player
from starthall import StartHall

# Initialize window
def initialize_window():

    # Initialize Pygame
    try:
        pygame.init()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Pygame: {e}")
    
    # Get screen dimensions
    current_path = os.path.dirname(os.path.abspath(__file__))
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    win = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
    pygame.display.set_caption("Z2H: Zero to Hero")
    red = (255, 0, 0)
    font = pygame.font.Font(None, 64)
    return win, red, font, screen_width, screen_height

# Initialize game
def initialize_game():
    win, red, font, screen_width, screen_height = initialize_window()
    current_path = os.path.dirname(os.path.abspath(__file__))
    images = load_images(current_path, screen_width, screen_height)
    player = Player(images["player_original"], screen_width, screen_height)
    start_hall = StartHall(screen_width, screen_height)
    return win, red, font, screen_width, screen_height, images, player, start_hall

# Main program
if __name__ == "__main__":
    win, red, font, screen_width, screen_height, images, player, start_hall = initialize_game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()