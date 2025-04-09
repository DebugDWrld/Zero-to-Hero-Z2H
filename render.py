# bullet.py
import pygame
from bullet import draw_bullets

# draw hud
def draw_hud(win, font, player, screen_width):
    # draw inventory infos
    inventory_text = font.render(f"Batteries: {player.battery_inventory}/{player.battery_capacity}", True, (255, 255, 255))
    win.blit(inventory_text, (10, 10))
    # draw hp, armor, energy
    hp_text = font.render(f"HP: {player.hp}/{player.max_hp}", True, (255, 0, 0))
    armor_text = font.render(f"Armor: {player.armor}/{player.max_armor}", True, (150, 150, 150))
    energy_text = font.render(f"Energy: {int(player.energy)}/{player.max_energy}", True, (0, 255, 255))
    win.blit(hp_text, (screen_width - hp_text.get_width() - 10, 10))
    win.blit(armor_text, (screen_width - armor_text.get_width() - 10, 40))
    win.blit(energy_text, (screen_width - energy_text.get_width() - 10, 70))

# draw start hall
def draw_start_hall(win, red, font, screen_width, screen_height, images, start_hall, player, bullets, camera_offset):
    win.fill((0, 0, 0))
    start_hall.draw(win, images, camera_offset)
    player.draw(win)
    draw_bullets(bullets, images["bullet_original"], win, camera_offset)
    draw_hud(win, font, player, screen_width)
    gate_x = start_hall.gate_pos[0] * start_hall.tile_size + start_hall.tile_size // 2
    gate_y = start_hall.gate_pos[1] * start_hall.tile_size + start_hall.tile_size // 2

    # draw gate interaction hint
    if (abs(player.world_x - gate_x) < start_hall.tile_size * 1.5 and 
        abs(player.world_y - gate_y) < start_hall.tile_size * 1.5):
        text_surface = font.render("Press E to enter", True, red)
        text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height - 100))
        win.blit(text_surface, text_rect)
    battery_x = start_hall.battery_pos[0] * start_hall.tile_size + start_hall.tile_size // 2
    battery_y = start_hall.battery_pos[1] * start_hall.tile_size + start_hall.tile_size // 2

    # draw battery interaction hint
    if (abs(player.world_x - battery_x) < start_hall.tile_size * 1.5 and 
        abs(player.world_y - battery_y) < start_hall.tile_size * 1.5):
        text_surface = font.render("Press E to interact", True, red)
        text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height - 130))
        win.blit(text_surface, text_rect)

# draw main level
def draw_main_level(win, images, player, bullets, camera_offset, font, screen_width):
    win.fill((0, 0, 0))
    win.blit(images["background"], camera_offset)
    player.draw(win)
    draw_bullets(bullets, images["bullet_original"], win, camera_offset)
    draw_hud(win, font, player, screen_width)

# draw game over screen
def draw_game_over(win, font, red, screen_width, screen_height):
    win.fill((255, 255, 255))
    text_surface = font.render("GAME OVER", True, red)
    text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
    win.blit(text_surface, text_rect)