import os, pygame
def initialize_window():

    # Initializing Pygame
    try:
        pygame.init()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Pygame: {e}")

    # Get the path of the current script file
    current_path = os.path.dirname(os.path.abspath(__file__))
    print(f"Current path: {current_path}")

    # Get display information
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h

    # Create a game window
    win = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
    pygame.display.set_caption("Z2H: Zero to Hero")

    # Define text color and font
    red = (255, 0, 0)
    font = pygame.font.Font(None, 64)
    
    # Return the initialized variables
    return win, red, font, screen_width, screen_height

if __name__ == "__main__":
    win, red, font, screen_width, screen_height = initialize_window()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()