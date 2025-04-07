import pygame
import math
from constants import player_x, player_y, move_speed, player_direction, last_direction, player_angle

class Player:
    def __init__(self, image, screen_width, screen_height):
        self.image_original = image
        self.image = self.image_original
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height // 2))
        self.direction = [0.0, 0.0]
        self.last_direction = [1.0, 0.0]
        self.angle = 0.0
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, keys):
        global player_x, player_y, player_direction, last_direction, player_angle
        move_x = 0.0
        move_y = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x += 1.0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y -= 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y += 1.0

        if move_x != 0 or move_y != 0:
            length = math.sqrt(move_x ** 2 + move_y ** 2)
            self.direction = [move_x / length, move_y / length]
            self.last_direction = self.direction[:]
            player_x += self.direction[0] * move_speed
            player_y += self.direction[1] * move_speed
            self.angle = math.degrees(math.atan2(-self.direction[1], self.direction[0]))
            self.image = pygame.transform.rotate(self.image_original, self.angle)
        else:
            self.direction = [0.0, 0.0]
        
        self.rect.center = (player_x, player_y)
        if (player_x < 0 or player_x > self.screen_width - 64 or 
            player_y < 0 or player_y > self.screen_height - 64):
            print(f"Boundary hit at ({player_x}, {player_y})!")
            return False
        return True

    def draw(self, win):
        win.blit(self.image, self.rect)