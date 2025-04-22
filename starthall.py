# starthall.py
import pygame

# Define the StartHall class
class StartHall:
    # Initialize the hall
    def __init__(self, screen_width, screen_height, tile_size=32):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = tile_size
        self.width = screen_width // tile_size
        self.height = screen_height // tile_size
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]  # 1 = wall, 0 = floor, 2 = gate, 3 = battery storage, 4 = property tree
        self.gate_pos = (self.width // 2, self.height - 2)
        self.battery_pos = (self.width // 3, self.height // 2)  # location of the battery storage
        self.property_tree_pos = (self.width * 2 // 3, self.height // 2)  # location of the property tree
        self.battery_storage = 10  # current battery storage
        self.battery_limit = 128  # up to 128 batteries
        
        # create a hall
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                self.grid[y][x] = 0  # 0 = floor
        
        # set the gate position
        self.grid[self.gate_pos[1]][self.gate_pos[0]] = 2 # 2 = gate

        # set the battery storage position
        self.grid[self.battery_pos[1]][self.battery_pos[0]] = 3 # 3 = battery storage

        # set the property tree position
        self.grid[self.property_tree_pos[1]][self.property_tree_pos[0]] = 4 # 4 = property tree

    # Draw the hall
    def draw(self, win, images, camera_offset):
        offset_x, offset_y = camera_offset

        # draw the hall
        for y in range(self.height):

            # draw the walls and floors
            for x in range(self.width):
                pos = (x * self.tile_size + offset_x, y * self.tile_size + offset_y)

                # wall
                if self.grid[y][x] == 1:
                    if "wall" not in images:
                        print("Warning: 'wall' image not found!")
                    else:
                        win.blit(images["wall"], pos)
                # floor
                elif self.grid[y][x] == 0:
                    if "floor" not in images:
                        print("Warning: 'floor' image not found!")
                    else:
                        win.blit(images["floor"], pos)

                # gate
                elif self.grid[y][x] == 2:
                    if "gate_open" not in images:
                        print("Warning: 'gate_open' image not found!")
                    else:
                        win.blit(images["gate_open"], pos)

                # battery storage
                elif self.grid[y][x] == 3:
                    if "battery_inventory" not in images:
                        pygame.draw.rect(win, (128, 128, 128), (*pos, self.tile_size, self.tile_size))  # if the image is not found, draw a green rectangle instead
                    else:
                        win.blit(images["battery_inventory"], pos)

                # property tree
                elif self.grid[y][x] == 4:
                    if "property_tree" not in images:
                        pygame.draw.rect(win, (0, 255, 0), (*pos, self.tile_size, self.tile_size))
                    else:
                        win.blit(images["property_tree"], pos)

    # Check if the player is interacting with the gate
    def check_gate_interaction(self, player, keys):
        gate_x = self.gate_pos[0] * self.tile_size + self.tile_size // 2
        gate_y = self.gate_pos[1] * self.tile_size + self.tile_size // 2

        # Check if the player is within a certain distance of the gate
        if (abs(player.world_x - gate_x) < self.tile_size and 
            abs(player.world_y - gate_y) < self.tile_size and 
            keys[pygame.K_e]):
            return True
        return False
    # Check if the player is interacting with the battery storage
    def check_battery_interaction(self, player, keys):
        battery_x = self.battery_pos[0] * self.tile_size + self.tile_size // 2
        battery_y = self.battery_pos[1] * self.tile_size + self.tile_size // 2

        # Check if the player is within a certain distance of the battery storage
        if (abs(player.world_x - battery_x) < self.tile_size * 1.5 and 
            abs(player.world_y - battery_y) < self.tile_size * 1.5 and 
            keys[pygame.K_e]):
            return True
        return False

    # Check if the player is interacting with the property tree
    def check_property_tree_interaction(self, player, keys):
        tree_x = self.property_tree_pos[0] * self.tile_size + self.tile_size // 2
        tree_y = self.property_tree_pos[1] * self.tile_size + self.tile_size // 2

        # Check if the player is within a certain distance of the property tree
        if (abs(player.world_x - tree_x) < self.tile_size * 1.5 and 
            abs(player.world_y - tree_y) < self.tile_size * 1.5 and 
            keys[pygame.K_e]):
            return True
        return False

    # Deposit battery into the storage
    def deposit_battery(self, amount):
        space_left = self.battery_limit - self.battery_storage
        deposited = min(amount, space_left)
        self.battery_storage += deposited
        return deposited  # return the actual amount deposited

    # Withdraw battery from the storage
    def withdraw_battery(self, amount):
        withdrawn = min(amount, self.battery_storage)
        self.battery_storage -= withdrawn
        return withdrawn  # return the actual amount withdrawn

# Main script
if __name__ == "__main__":
    print("starthall.py is working standalone!")