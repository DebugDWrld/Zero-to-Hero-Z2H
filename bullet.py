# bullet.py
import pygame
import math
from constants import BULLET_SPEED, BULLET_LIFETIME, SHOOT_COOLDOWN, LAST_SHOT_TIME, BULLETS

# shoot bullet
def shoot_bullet(player, current_time, speed_multiplier=1):
    global LAST_SHOT_TIME
    if current_time - LAST_SHOT_TIME >= SHOOT_COOLDOWN:
        shoot_direction = player.direction if player.direction != [0.0, 0.0] else player.last_direction
        bullet = {
            "x": player.world_x,
            "y": player.world_y,
            "velocity": [shoot_direction[0] * BULLET_SPEED * speed_multiplier, 
                         shoot_direction[1] * BULLET_SPEED * speed_multiplier],
            "angle": player.angle,
            "spawn_time": current_time,
            "visible": True
        }
        BULLETS.append(bullet)
        LAST_SHOT_TIME = current_time

# update bullets
def update_bullets(bullets, screen_width, screen_height, current_time, player, player_image, bullet_image):
    for bullet in bullets[:]:
        if bullet["visible"]:
            bullet["x"] += bullet["velocity"][0]
            bullet["y"] += bullet["velocity"][1]
            if (current_time - bullet["spawn_time"] >= BULLET_LIFETIME or
                bullet["x"] < 0 or bullet["x"] > screen_width or
                bullet["y"] < 0 or bullet["y"] > screen_height):
                bullet["visible"] = False
        if not bullet["visible"]:
            bullets.remove(bullet)

# draw bullets
def draw_bullets(bullets, bullet_image, win, camera_offset):
    offset_x, offset_y = camera_offset
    for bullet in bullets:
        if bullet["visible"]:
            rotated_bullet = pygame.transform.rotate(bullet_image, bullet["angle"])
            bullet_rect = rotated_bullet.get_rect(center=(bullet["x"] + offset_x, bullet["y"] + offset_y))
            win.blit(rotated_bullet, bullet_rect)