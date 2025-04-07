import pygame
import os
from initial import initialize_window
from load import load_images
from player import Player
from bullet import shoot_bullet, update_bullets, draw_bullets
from constants import bullets as BULLETS

# Initializing Pygame
pygame.init()

# Initializing window
win, red, font, screen_width, screen_height = initialize_window()

# Get the current path
current_path = os.path.dirname(os.path.abspath(__file__))

# Loading Images
images = load_images(current_path, screen_width, screen_height)

# Creating a Player Object
player = Player(images["player_original"], screen_width, screen_height)

# Set clock control frame rate
clock = pygame.time.Clock()

# Main Game Loop
running = True
game_over = False
game_over_time = 0

while running:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    if not game_over:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            running = False

        if not player.update(keys):
            print("Game Over triggered!")
            game_over = True
            game_over_time = current_time

        if keys[pygame.K_k]:
            shoot_bullet(player, current_time, 1, player_image=images["player_original"])
        if keys[pygame.K_l]:
            shoot_bullet(player, current_time, 2, player_image=images["player_original"])

        update_bullets(BULLETS, screen_width, screen_height, current_time, player, 
                       images["player_original"], images["bullet_original"])
        
        win.blit(images["background"], (0, 0))
        player.draw(win)
        draw_bullets(BULLETS, images["bullet_original"], win)

        pygame.display.flip()

    if game_over:
        win.fill((255, 255, 255))
        text_surface = font.render("GAME OVER", True, red)
        text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
        win.blit(text_surface, text_rect)
        pygame.display.flip()
        if current_time - game_over_time >= 1500:
            running = False

    clock.tick(120)

pygame.display.quit()
pygame.quit()