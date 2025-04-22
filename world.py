# world.py
import random
import pygame

class World:
    def __init__(self, tile_size=32):
        self.tile_size = tile_size
        self.width = 180
        self.height = 101
        self.grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
        self.rooms = []
        self.squares = []
        self.event_points = []
        self.enemy_spawn_points = []
        self.item_spawn_points = []
        self.battery_spawn_points = []
        self.teleport_points = []
        
        self.generate_rooms()
        self.generate_squares()
        self.generate_corridors()
        self.generate_event_points()
        self.generate_spawn_points()

        print(f"Number of rooms generated: {len(self.rooms)}")
        print(f"Rooms' details: {self.rooms}")
        print(f"Number of squares generated: {len(self.squares)}")
        print(f"Squares' details: {self.squares}")
        print(f"Number of event points generated: {len(self.event_points)}")

    def generate_rooms(self):
        num_rooms = random.randint(15, 20)
        room_types = ["small"] * (int(num_rooms * 0.4)) + \
                     ["medium"] * (int(num_rooms * 0.4)) + \
                     ["large"] * (num_rooms - int(num_rooms * 0.8))
        random.shuffle(room_types)

        for room_type in room_types:
            if room_type == "small":
                w, h = 5, 5
            elif room_type == "medium":
                w, h = 10, 10
            else:
                w, h = 15, 15

            for _ in range(200):
                x = random.randint(1, self.width - w - 1)
                y = random.randint(1, self.height - h - 1)
                overlap = False
                for rx, ry, rw, rh, _ in self.rooms + self.squares:
                    if (x < rx + rw and x + w > rx and
                        y < ry + rh and y + h > ry):
                        overlap = True
                        print(f"Room {room_type} overlaps at ({x}, {y}), trying new position")
                        break
                if not overlap:
                    self.rooms.append((x, y, w, h, room_type))
                    for ry in range(y, y + h):
                        for rx in range(x, x + w):
                            self.grid[ry][rx] = 0
                    print(f"Successfully placed {room_type} room at ({x}, {y})")
                    break
                if _ == 199:
                    print(f"Warning: Failed to place {room_type} room after 200 attempts")

    def generate_squares(self):
        square_types = ["safe", "resource", "battle"]
        for square_type in square_types:
            w, h = 20, 20
            for _ in range(200):
                x = random.randint(1, self.width - w - 1)
                y = random.randint(1, self.height - h - 1)
                overlap = False
                for rx, ry, rw, rh, _ in self.rooms + self.squares:
                    if (x < rx + rw and x + w > rx and
                        y < ry + rh and y + h > ry):
                        overlap = True
                        break
                if not overlap:
                    self.squares.append((x, y, w, h, square_type))
                    for ry in range(y, y + h):
                        for rx in range(x, x + w):
                            self.grid[ry][rx] = 0
                    print(f"Successfully placed {square_type} square at ({x}, {y})")
                    break
                if _ == 199:
                    print(f"Warning: Failed to place {square_type} square after 200 attempts")

    def generate_corridors(self):
        centers = [(x + w // 2, y + h // 2) for x, y, w, h, _ in self.rooms + self.squares]
        random.shuffle(centers)

        def carve_corridor(x1, y1, x2, y2):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                for dy in range(-1, 1):
                    ny = y1 + dy
                    if 0 <= ny < self.height and 0 <= x < self.width:
                        self.grid[ny][x] = 0
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for dx in range(-1, 1):
                    nx = x2 + dx
                    if 0 <= nx < self.width and 0 <= y < self.height:
                        self.grid[y][nx] = 0

        for i in range(len(centers) - 1):
            x1, y1 = centers[i]
            x2, y2 = centers[i + 1]
            carve_corridor(x1, y1, x2, y2)

        # 添加分支走廊
        for x, y, w, h, _ in self.rooms + self.squares:
            if random.random() < 0.25:
                branch_x = x + random.randint(0, w - 1)
                branch_y = y + random.randint(0, h - 1)
                length = random.randint(4, 8)
                direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                for i in range(length):
                    nx = branch_x + direction[0] * i
                    ny = branch_y + direction[1] * i
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        for dy in range(-1, 1):
                            for dx in range(-1, 1):
                                if 0 <= nx + dx < self.width and 0 <= ny + dy < self.height:
                                    self.grid[ny + dy][nx + dx] = 0

    def generate_event_points(self):
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                if self.grid[y][x] == 0:
                    wall_count = sum(self.grid[y + dy][x + dx] for dy in [-1, 0, 1] for dx in [-1, 0, 1])
                    if wall_count >= 4 and random.random() < 0.1:
                        self.grid[y][x] = 2
                        self.event_points.append((x, y))

    def generate_spawn_points(self):
        # 生成敌人出生点
        for x, y, w, h, room_type in self.rooms:
            if room_type in ["medium", "large"]:
                num_spawns = 2 if room_type == "medium" else 4
                for _ in range(num_spawns):
                    spawn_x = x + random.randint(1, w - 2)
                    spawn_y = y + random.randint(1, h - 2)
                    self.enemy_spawn_points.append((spawn_x, spawn_y))

        # 生成物品出生点
        for x, y, w, h, square_type in self.squares:
            if square_type == "resource":
                num_items = random.randint(3, 5)
                for _ in range(num_items):
                    item_x = x + random.randint(1, w - 2)
                    item_y = y + random.randint(1, h - 2)
                    self.item_spawn_points.append((item_x, item_y))

        # 生成电池出生点
        for x, y, w, h, room_type in self.rooms:
            if room_type == "large":
                num_batteries = random.randint(2, 3)
                for _ in range(num_batteries):
                    battery_x = x + random.randint(1, w - 2)
                    battery_y = y + random.randint(1, h - 2)
                    self.battery_spawn_points.append((battery_x, battery_y))

        # 生成传送点
        for x, y, w, h, square_type in self.squares:
            if square_type == "safe":
                teleport_x = x + w // 2
                teleport_y = y + h // 2
                self.teleport_points.append((teleport_x, teleport_y))

    def is_wall(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x] == 1
        return True
    
    def get_start_position(self):
        small_rooms = [(x, y, w, h) for x, y, w, h, t in self.rooms if t == "small"]
        if not small_rooms:
            print("Warning: No small rooms found, using default position")
            return self.width * self.tile_size // 2, self.height * self.tile_size // 2

        left_top_rooms = [(x, y, w, h) for x, y, w, h in small_rooms if x < 90 and y < 50]
        right_bottom_rooms = [(x, y, w, h) for x, y, w, h in small_rooms if x >= 90 and y >= 50]

        if left_top_rooms:
            x, y, w, h = random.choice(left_top_rooms)
            print(f"Player start position: Top-left small room ({x}, {y})")
        elif right_bottom_rooms:
            x, y, w, h = random.choice(right_bottom_rooms)
            print(f"Player start position: Bottom-right small room ({x}, {y})")
        else:
            x, y, w, h = random.choice(small_rooms)
            print(f"Warning: No top-left or bottom-right small rooms found, using random small room ({x}, {y})")

        center_x = x + w // 2
        center_y = y + h // 2
        attempts = 0
        while self.grid[center_y][center_x] != 0 and attempts < 10:
            print(f"Center position ({center_x}, {center_y}) is a wall, trying to adjust")
            new_x = random.randint(x, x + w - 1)
            new_y = random.randint(y, y + h - 1)
            center_x, center_y = new_x, new_y
            attempts += 1

        if self.grid[center_y][center_x] != 0:
            print("Warning: Could not find non-wall start position, using room center")
        
        return center_x * self.tile_size, center_y * self.tile_size

    def draw(self, win, camera_offset, scale=1.0):
        offset_x, offset_y = camera_offset
        for y in range(self.height):
            for x in range(self.width):
                pos = (int(x * self.tile_size * scale + offset_x),
                       int(y * self.tile_size * scale + offset_y))
                size = int(self.tile_size * scale)
                if self.grid[y][x] == 1:
                    pygame.draw.rect(win, (64, 64, 64), (*pos, size, size))
                elif self.grid[y][x] == 0:
                    color = (0, 128, 128)
                    for rx, ry, rw, rh, rtype in self.rooms:
                        if rx <= x < rx + rw and ry <= y < ry + rh:
                            color = (0, 255, 0)
                            break
                    for sx, sy, sw, sh, stype in self.squares:
                        if sx <= x < sx + sw and sy <= y < sy + sh:
                            color = (0, 255, 255) if stype == "safe" else (0, 128, 128)
                            break
                    pygame.draw.rect(win, color, (*pos, size, size))
                elif self.grid[y][x] == 2:
                    pygame.draw.rect(win, (255, 255, 0), (*pos, size, size))
                pygame.draw.rect(win, (50, 50, 50), (*pos, size, size), 1)

        # 绘制出生点
        for x, y in self.enemy_spawn_points:
            pos = (int(x * self.tile_size * scale + offset_x),
                   int(y * self.tile_size * scale + offset_y))
            pygame.draw.circle(win, (255, 0, 0), pos, int(4 * scale))

        for x, y in self.item_spawn_points:
            pos = (int(x * self.tile_size * scale + offset_x),
                   int(y * self.tile_size * scale + offset_y))
            pygame.draw.circle(win, (0, 255, 0), pos, int(4 * scale))

        for x, y in self.battery_spawn_points:
            pos = (int(x * self.tile_size * scale + offset_x),
                   int(y * self.tile_size * scale + offset_y))
            pygame.draw.circle(win, (255, 255, 0), pos, int(4 * scale))

        for x, y in self.teleport_points:
            pos = (int(x * self.tile_size * scale + offset_x),
                   int(y * self.tile_size * scale + offset_y))
            pygame.draw.circle(win, (0, 0, 255), pos, int(6 * scale))

if __name__ == "__main__":
    pygame.init()
    screen_width, screen_height = 1280, 720
    win = pygame.display.set_mode((screen_width, screen_height))