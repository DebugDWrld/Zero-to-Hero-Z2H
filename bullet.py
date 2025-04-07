import math
import pygame
from constants import BULLETS, BULLET_SPEED, SHOOT_COOLDOWN, LAST_SHOT_TIME, BULLET_LIFETIME

def shoot_bullet(player, current_time, speed_multiplier=1, player_image=None):
    global LAST_SHOT_TIME, BULLETS
    if current_time - LAST_SHOT_TIME >= SHOOT_COOLDOWN:
        if player_image is None:
            raise ValueError("Player_image must be provided.")
        player_radius = player_image.get_width() / 2

        angle_rad = math.radians(player.angle)
        spawn_offset_x = math.cos(angle_rad) * player_radius
        spawn_offset_y = -math.sin(angle_rad) * player_radius

        bullet = {
            "x": player.rect.centerx + spawn_offset_x,
            "y": player.rect.centery + spawn_offset_y,
            "velocity": [0.0, 0.0],
            "spawn_time": current_time,
            "visible": True,
            "angle": player.angle
        }

        if player.direction != [0.0, 0.0]:
            bullet["velocity"] = [player.direction[0] * BULLET_SPEED * speed_multiplier, 
                                 player.direction[1] * BULLET_SPEED * speed_multiplier]
            bullet["angle"] = math.degrees(math.atan2(-player.direction[1], player.direction[0]))
            print(f"Velocity set from player.direction: {bullet['velocity']}")
        elif player.last_direction != [0.0, 0.0]:
            bullet["velocity"] = [player.last_direction[0] * BULLET_SPEED * speed_multiplier, 
                                 player.last_direction[1] * BULLET_SPEED * speed_multiplier]
            bullet["angle"] = math.degrees(math.atan2(-player.last_direction[1], player.last_direction[0]))
            print(f"Velocity set from player.last_direction: {bullet['velocity']}")
        else:
            bullet["velocity"] = [math.cos(angle_rad) * BULLET_SPEED * speed_multiplier,
                                 -math.sin(angle_rad) * BULLET_SPEED * speed_multiplier]
            print(f"Velocity set from player angle: {bullet['velocity']}")

        BULLETS.append(bullet)
        LAST_SHOT_TIME = current_time
        print(f"Spawning bullet at: ({bullet['x']}, {bullet['y']})")
    else:
        print(f"Shoot cooldown active: {current_time - LAST_SHOT_TIME} < {SHOOT_COOLDOWN}")

def update_bullets(bullets, screen_width, screen_height, current_time, player, player_image, bullet_image):
    if player_image is None or bullet_image is None:
        raise ValueError("player_image and bullet_image must be provided.")
    
    player_radius = player_image.get_width() / 2
    bullet_radius = bullet_image.get_width() / 2
    separation_distance = player_radius + bullet_radius

    for bullet in bullets[:]:
        bullet["x"] += bullet["velocity"][0]
        bullet["y"] += bullet["velocity"][1]
        
        #distance = math.sqrt((bullet["x"] - player.rect.centerx)**2 + (bullet["y"] - player.rect.centery)**2)
        #if distance > separation_distance and not bullet["visible"]:
            #bullet["visible"] = True
            #print(f"Bullet visible at: ({bullet['x']}, {bullet['y']}), distance: {distance}")

        if (bullet["x"] < 0 or bullet["x"] > screen_width or 
            bullet["y"] < 0 or bullet["y"] > screen_height):
            bullet["visible"] = False

        if current_time - bullet["spawn_time"] > BULLET_LIFETIME:
            bullet["visible"] = False
        
        if not bullet["visible"] and bullet in bullets:
            bullets.remove(bullet)

def draw_bullets(bullets, bullet_image_original, win):
    for bullet in bullets:
        if bullet["visible"]:
            print(f"Drawing bullet at: ({bullet['x']}, {bullet['y']}), angle: {bullet['angle']}")
            rotated_bullet = pygame.transform.rotate(bullet_image_original, bullet["angle"])
            bullet_rect = rotated_bullet.get_rect(center=(bullet["x"], bullet["y"]))
            win.blit(rotated_bullet, bullet_rect)