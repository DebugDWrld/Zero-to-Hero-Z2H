# main.py
import pygame
import constants
from initial import initialize_game
from bullet import shoot_bullet, update_bullets
from constants import BULLETS, SHOOT_COOLDOWN, F_KEY_COOLDOWN, ENERGY_RECOVERY_RATE, LAST_SHOT_TIME, LAST_F_KEY_TIME, GAME_OVER_DELAY
from render import draw_start_hall, draw_main_level, draw_game_over
from menu import BatteryMenu

# initialize game
try:
    win, red, font, screen_width, screen_height, images, player, start_hall = initialize_game()
    constants.HALL_WIDTH = screen_width
    constants.HALL_HEIGHT = screen_height
except Exception as e:
    print(f"Initialization failed: {e}")
    pygame.quit()
    exit(1)

# game variables
in_start_hall = True
WORLD_WIDTH = screen_width * 3
WORLD_HEIGHT = screen_height * 3
battery_menu = BatteryMenu(screen_width, screen_height)
clock = pygame.time.Clock()
last_update_time = pygame.time.get_ticks()
game_over = False
game_over_time = 0

# main game loop
running = True
while running:
    current_time = pygame.time.get_ticks()
    dt = (current_time - last_update_time) / 1000.0
    last_update_time = current_time
    player.recover_energy(ENERGY_RECOVERY_RATE * dt)

    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        if battery_menu.handle_event(event, player, start_hall):
            continue

        # handle battery menu interaction
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if start_hall.check_battery_interaction(player, pygame.key.get_pressed()):
                battery_menu.active = True
                print(f"Battery menu activated: {battery_menu.active}")

        # handle key press
        if not battery_menu.active:
            # handle mouse click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if current_time - LAST_SHOT_TIME >= SHOOT_COOLDOWN and player.use_energy(4):
                    shoot_bullet(player, current_time, 1)
                    constants.LAST_SHOT_TIME = current_time
                    print(f"Shot fired, Energy: {player.energy}")

            # handle F key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                print(f"F key pressed, Cooldown: {current_time - LAST_F_KEY_TIME}/{F_KEY_COOLDOWN}, Energy: {player.energy}")
                if current_time - LAST_F_KEY_TIME >= F_KEY_COOLDOWN and player.use_energy(16):
                    constants.LAST_F_KEY_TIME = current_time
                    print(f"F key used, consumed 16 energy. Current energy: {player.energy}")

    if not game_over:
        # handle player movement and shooting
        keys = pygame.key.get_pressed()

        if not battery_menu.active:
            # update player
            player.update(keys)

        # calculate camera offset
        camera_offset = (screen_width // 2 - player.world_x, screen_height // 2 - player.world_y)

        # update bullets
        update_bullets(BULLETS, constants.HALL_WIDTH if in_start_hall else WORLD_WIDTH, 
                       constants.HALL_HEIGHT if in_start_hall else WORLD_HEIGHT, 
                       current_time, player, images["player_original"], images["bullet_original"])

        # draw start hall or main level
        if in_start_hall:
            if start_hall.check_gate_interaction(player, keys):
                in_start_hall = False
                print("Entering main level...")
            draw_start_hall(win, red, font, screen_width, screen_height, images, start_hall, player, BULLETS, camera_offset)
        else:
            draw_main_level(win, images, player, BULLETS, camera_offset, font, screen_width)

        # draw battery menu
        battery_menu.draw(win)
        
        # check game over
        if game_over:
            draw_game_over(win, font, red, screen_width, screen_height)
            if current_time - game_over_time >= GAME_OVER_DELAY:
                running = False
        pygame.display.flip()

    # limit frame rate to 120 FPS
    clock.tick(120)

# quit pygame
pygame.quit()
