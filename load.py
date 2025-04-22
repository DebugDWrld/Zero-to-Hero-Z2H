# load.py
import pygame
import os

def load_images(current_path, screen_width, screen_height):
    images = {}
    
    # 加载玩家和敌人图片
    try:
        player_original = pygame.image.load(os.path.join(current_path, "images", "player.png")).convert_alpha()
        player_original = pygame.transform.scale(player_original, (64, 64))
        images["player_original"] = player_original
        
        melee_enemy = pygame.image.load(os.path.join(current_path, "images", "melee_enemy.png")).convert_alpha()
        melee_enemy = pygame.transform.scale(melee_enemy, (64, 64))
        images["melee_enemy"] = melee_enemy
        
        ranged_enemy = pygame.image.load(os.path.join(current_path, "images", "ranged_enemy.png")).convert_alpha()
        ranged_enemy = pygame.transform.scale(ranged_enemy, (64, 64))
        images["ranged_enemy"] = ranged_enemy
        
        boss_original = pygame.image.load(os.path.join(current_path, "images", "boss.png")).convert_alpha()
        boss_original = pygame.transform.scale(boss_original, (128, 128))
        images["boss_original"] = boss_original
        
        bullet_original = pygame.image.load(os.path.join(current_path, "images", "bullet.png")).convert_alpha()
        bullet_original = pygame.transform.scale(bullet_original, (32, 32))
        images["bullet"] = bullet_original
    except Exception as e:
        print(f"Warning: Failed to load some images: {e}")
    
    # 加载开始大厅图片
    try:
        wall = pygame.image.load(os.path.join(current_path, "images", "wall.png")).convert_alpha()
        wall = pygame.transform.scale(wall, (32, 32))
        images["wall"] = wall
        
        floor = pygame.image.load(os.path.join(current_path, "images", "floor.png")).convert_alpha()
        floor = pygame.transform.scale(floor, (32, 32))
        images["floor"] = floor
        
        gate_open = pygame.image.load(os.path.join(current_path, "images", "gate_open.png")).convert_alpha()
        gate_open = pygame.transform.scale(gate_open, (32, 32))
        images["gate_open"] = gate_open
        
        battery_inventory = pygame.image.load(os.path.join(current_path, "images", "battery_inventory.png")).convert_alpha()
        battery_inventory = pygame.transform.scale(battery_inventory, (32, 32))
        images["battery_inventory"] = battery_inventory
        
        property_tree = pygame.image.load(os.path.join(current_path, "images", "property_tree.png")).convert_alpha()
        property_tree = pygame.transform.scale(property_tree, (32, 32))
        images["property_tree"] = property_tree
    except Exception as e:
        print(f"Warning: Failed to load start hall images: {e}")
    
    # 加载关卡背景图片
    try:
        # 加载四个关卡的背景
        for i in range(1, 5):
            bg_key = f"background_{i}"
            bg_path = os.path.join(current_path, "images", f"background_{i}.png")
            if os.path.exists(bg_path):
                bg = pygame.image.load(bg_path).convert()
                bg = pygame.transform.scale(bg, (screen_width * 3, screen_height * 3))
                images[bg_key] = bg
            else:
                print(f"Warning: Background image {bg_key} not found")
        
        # 加载走廊背景
        corridor_path = os.path.join(current_path, "images", "corridor.png")
        if os.path.exists(corridor_path):
            corridor = pygame.image.load(corridor_path).convert()
            corridor = pygame.transform.scale(corridor, (200, screen_height * 3))  # 走廊宽度固定为200
            images["corridor"] = corridor
        else:
            print("Warning: Corridor background image not found")
    except Exception as e:
        print(f"Warning: Failed to load background images: {e}")
    
    return images

if __name__ == "__main__":
    pygame.init()
    current_path = os.path.dirname(os.path.abspath(__file__))
    screen_info = pygame.display.Info()
    screen_width = screen_info.current_w
    screen_height = screen_info.current_h
    images = load_images(current_path, screen_width, screen_height)
    print("Images loaded successfully:", list(images.keys()))
    pygame.quit()