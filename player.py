# player.py
import pygame
import math
from constants import MOVE_SPEED

# Define the Player class
class Player:
    # Initialize the player
    def __init__(self, image, screen_width, screen_height):
        self.image_original = image
        self.image = self.image_original
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height // 2))  # fix center
        self.world_x = screen_width // 2  # initial position
        self.world_y = screen_height // 2
        self.direction = [0.0, 0.0]
        self.last_direction = [1.0, 0.0]
        self.angle = 0.0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title_size = 32
        self.battery_inventory = 10  # current amount of batteries the player has
        self.battery_capacity = 64  # The maximum amount of batteries the player can hold

        # The properties of the player
        self.hp = 10  # HP
        self.max_hp = 10  # The maximum amount of health the player can hold
        self.armor = 5  # Armor
        self.max_armor = 5  # The maximum amount of armor the player can hold
        self.energy = 100  # Energy
        self.max_energy = 100  # The maximum amount of energy the player can hold
    # update player
    def update(self, keys):
        move_x = 0.0
        move_y = 0.0

        # get direction
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x += 1.0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y -= 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y += 1.0
            
        # move player
        if move_x != 0 or move_y != 0:
            length = math.sqrt(move_x ** 2 + move_y ** 2)
            self.direction = [move_x / length, move_y / length]
            self.last_direction = self.direction[:]  # update last direction
            new_x = self.world_x + self.direction[0] * MOVE_SPEED
            new_y = self.world_y + self.direction[1] * MOVE_SPEED
            self.world_x = max(self.title_size, min(new_x, self.screen_width - self.title_size))
            self.world_y = max(self.title_size, min(new_y, self.screen_height - self.title_size))
            self.angle = math.degrees(math.atan2(-self.direction[1], self.direction[0]))
            self.image = pygame.transform.rotate(self.image_original, self.angle)
            self.rect = self.image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        else:
            self.direction = [0.0, 0.0]

        # rect keep center
        self.rect.center = (self.screen_width // 2, self.screen_height // 2)
        return True
    # draw player
    def draw(self, win):
        win.blit(self.image, self.rect)
    # add batteries
    def add_batteries(self, amount):
        space_left = self.battery_capacity - self.battery_inventory
        added = min(amount, space_left)
        self.battery_inventory += added
        return added  # Returns the actual amount of  batterires added
    # remove batteries
    def remove_batteries(self, amount):
        removed = min(amount, self.battery_inventory)
        self.battery_inventory -= removed
        return removed  # Returns the actual amount of  batterires removed
    
    # take damage
    def take_damage(self, amount):

        # reduce armor first
        if self.armor > 0:
            armor_damage = min(amount, self.armor)
            self.armor -= armor_damage
            amount -= armor_damage

        # take damage
        if amount > 0:
            self.hp -= amount

        # check if player is dead
        if self.hp <= 0:
            self.hp = 0
            return False  # means player is dead
        return True  # means player is alive
    
    # use energy
    def use_energy(self, amount):

        # check if enough energy
        if self.energy >= amount:
            self.energy -= amount
            print(f"Energy used: {amount}, Remaining: {self.energy}")
            return True
        print(f"Not enough energy: {self.energy}/{amount}")
        return False

    # recover energy
    def recover_energy(self, amount):
        self.energy = min(self.max_energy, self.energy + amount)
