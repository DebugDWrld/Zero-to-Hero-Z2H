# render.py
import pygame
from bullet import draw_bullets
from world_beta import WorldBeta

class MessageSystem:
    def __init__(self):
        self.messages = []
        self.message_timers = {}
        self.message_duration = 3000  # 消息显示时间（毫秒）
        self.last_message_time = 0
        self.message_cooldown = 1000  # 相同消息的冷却时间（毫秒）
        self.energy_warning_active = False
        self.energy_warning_timer = 0
        self.energy_warning_duration = 2000

    def add_message(self, message):
        current_time = pygame.time.get_ticks()
        if message not in self.message_timers or current_time - self.message_timers[message] > self.message_cooldown:
            self.messages.append(message)
            self.message_timers[message] = current_time
            if len(self.messages) > 3:  # 最多显示3条消息
                self.messages.pop(0)

    def add_energy_warning(self):
        self.energy_warning_active = True
        self.energy_warning_timer = self.energy_warning_duration

    def update(self):
        current_time = pygame.time.get_ticks()
        self.messages = [msg for msg in self.messages 
                        if current_time - self.message_timers[msg] < self.message_duration]
        
        if self.energy_warning_active:
            self.energy_warning_timer -= 16
            if self.energy_warning_timer <= 0:
                self.energy_warning_active = False

    def draw(self, win, font):
        y_offset = 100
        for message in self.messages:
            text_surface = font.render(message, True, (255, 255, 255))
            win.blit(text_surface, (10, y_offset))
            y_offset += 30

        if self.energy_warning_active:
            warning_text = "ENERGY DEPLETED!"
            text_surface = font.render(warning_text, True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(win.get_width() // 2, 50))
            win.blit(text_surface, text_rect)

# 创建全局消息系统实例
message_system = MessageSystem()

# 绘制技能冷却UI
def draw_skill_cooldown(win, font, player, current_time, screen_width):
    # Dash技能UI位置 - 统一x轴位置
    dash_x = screen_width - 400
    dash_y = 130  # 调整为与能量显示保持40像素间距
    rect_width = 15
    rect_height = 15
    rect_spacing = 5
    
    # 绘制技能名称
    skill_text = font.render("Dash:", True, (255, 255, 255))
    text_width = skill_text.get_width()
    win.blit(skill_text, (dash_x, dash_y))
    
    # 获取dash技能信息
    dash_skill = player.skills["dash"]
    cooldown_remaining = max(0, (dash_skill["cooldown"] - (current_time - dash_skill["last_used"])) / 1000)
    filled_rects = min(10, int((10 - cooldown_remaining)))
    
    # 计算矩形起始位置，确保与文本对齐
    rect_start_x = dash_x + text_width + 15
    
    # 绘制冷却矩形
    total_rect_width = (rect_width + rect_spacing) * 10 - rect_spacing
    for i in range(10):
        rect = pygame.Rect(rect_start_x + i * (rect_width + rect_spacing), 
                         dash_y + 2, rect_width, rect_height)
        if i < filled_rects:
            pygame.draw.rect(win, (0, 255, 0), rect)
        else:
            pygame.draw.rect(win, (100, 100, 100), rect, 2)
    
    # 如果技能可用，显示Complete提示（居中对齐）
    if cooldown_remaining <= 0:
        complete_text = font.render("Complete", True, (0, 255, 0))
        complete_width = complete_text.get_width()
        complete_x = rect_start_x + (total_rect_width - complete_width) // 2
        win.blit(complete_text, (complete_x, dash_y + rect_height + 8))

def draw_hud(win, font, player, screen_width):
    # 绘制背包信息
    backpack_text = font.render(f"Batteries in Backpack: {player.backpack.get('batteries', 0)}/{player.backpack_capacity}", True, (255, 255, 255))
    win.blit(backpack_text, (10, 10))
    
    # 绘制经验值信息
    experience_text = font.render(f"Experience gained: {player.current_level_experience}", True, (255, 215, 0))  # 金色
    win.blit(experience_text, (10, 50))  # 在背包信息下方40像素处
    
    # 绘制状态信息（右上角）- 统一x轴位置
    status_x = screen_width - 400
    
    # 绘制生命值
    hp_text = font.render(f"HP: {int(player.hp)}/{player.max_hp}", True, (255, 0, 0))
    win.blit(hp_text, (status_x, 10))
    
    # 绘制护甲值 - 40像素间距
    armor_text = font.render(f"Armor: {int(player.armor)}/{player.max_armor}", True, (128, 128, 128))
    win.blit(armor_text, (status_x, 50))
    
    # 绘制能量值 - 40像素间距
    energy_text = font.render(f"Energy: {int(player.energy)}/{player.max_energy}", True, (0, 255, 255))
    win.blit(energy_text, (status_x, 90))
    
    # 更新并绘制消息
    message_system.update()
    message_system.draw(win, font)
    
    # 绘制技能冷却UI
    current_time = pygame.time.get_ticks()
    draw_skill_cooldown(win, font, player, current_time, screen_width)

# 绘制开始大厅
def draw_start_hall(win, red, font, screen_width, screen_height, images, start_hall, player, bullets, camera_offset, enemies, enemy_bullets):
    win.fill((0, 0, 0))
    start_hall.draw(win, images, camera_offset)
    for enemy in enemies:
        enemy.draw(win, camera_offset)
    player.draw(win)
    draw_bullets(bullets, images.get("bullet_original"), win, camera_offset, images.get("enemy_bullet"))
    draw_bullets(enemy_bullets, images.get("bullet_original"), win, camera_offset, images.get("enemy_bullet"))
    draw_hud(win, font, player, screen_width)
    
    # Gate interaction text
    gate_x = start_hall.gate_pos[0] * start_hall.tile_size + start_hall.tile_size // 2
    gate_y = start_hall.gate_pos[1] * start_hall.tile_size + start_hall.tile_size // 2
    if (abs(player.world_x - gate_x) < start_hall.tile_size * 1.5 and 
        abs(player.world_y - gate_y) < start_hall.tile_size * 1.5):
        text_surface = font.render("Press E to start...", True, red)
        text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height - 100))
        win.blit(text_surface, text_rect)
    
    # Battery interaction text
    battery_x = start_hall.battery_pos[0] * start_hall.tile_size + start_hall.tile_size // 2
    battery_y = start_hall.battery_pos[1] * start_hall.tile_size + start_hall.tile_size // 2
    if (abs(player.world_x - battery_x) < start_hall.tile_size * 1.5 and 
        abs(player.world_y - battery_y) < start_hall.tile_size * 1.5):
        text_surface = font.render("Press E to interact", True, red)
        text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height - 130))
        win.blit(text_surface, text_rect)

    # Property tree interaction text
    tree_x = start_hall.property_tree_pos[0] * start_hall.tile_size + start_hall.tile_size // 2
    tree_y = start_hall.property_tree_pos[1] * start_hall.tile_size + start_hall.tile_size // 2
    if (abs(player.world_x - tree_x) < start_hall.tile_size * 1.5 and 
        abs(player.world_y - tree_y) < start_hall.tile_size * 1.5):
        text_surface = font.render("Press E to interact", True, red)
        text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height - 160))
        win.blit(text_surface, text_rect)

# 绘制主关卡
def draw_main_level(win, images, player, bullets, camera_offset, font, screen_width, screen_height, enemies, enemy_bullets, world_beta):
    win.fill((0, 0, 0))
    
    # 获取玩家当前所在的区域
    current_area = world_beta.get_current_area(player.world_x, player.world_y)
    print(f"Current area: {current_area}, Player position: ({player.world_x}, {player.world_y})")
    
    # 根据当前区域选择背景
    if isinstance(current_area, int) and current_area in world_beta.levels:
        # 如果是关卡，使用对应的背景
        level = world_beta.levels[current_area]
        background_key = level["background"]
        if background_key in images:
            # 直接使用屏幕大小作为背景大小
            scaled_bg = pygame.transform.scale(images[background_key], (screen_width, screen_height))
            
            # 计算背景位置（相对于玩家位置）
            x = camera_offset[0]
            y = camera_offset[1]
            
            win.blit(scaled_bg, (x, y))
            print(f"Drawing background {background_key} at ({x}, {y})")

            # 在背景右侧绘制门
            if "gate_open" in images:
                gate_size = 200  # 门的大小
                gate = pygame.transform.scale(images["gate_open"], (gate_size, gate_size))
                gate_x = screen_width - gate_size + camera_offset[0]
                gate_y = screen_height // 2 - gate_size // 2 + camera_offset[1]
                win.blit(gate, (gate_x, gate_y))

                # 检查玩家是否靠近门
                player_screen_x = player.world_x + camera_offset[0]
                player_screen_y = player.world_y + camera_offset[1]
                if (abs(player_screen_x - (screen_width - gate_size)) < 100 and 
                    abs(player_screen_y - (screen_height // 2)) < 100):
                    # 显示交互提示
                    text = font.render("Press E to enter safe zone", True, (255, 255, 255))
                    text_rect = text.get_rect(center=(screen_width // 2, screen_height - 100))
                    win.blit(text, text_rect)

        else:
            print(f"Warning: Background image '{background_key}' not found!")
    elif isinstance(current_area, str) and "corridor" in current_area:
        # 如果是走廊，使用走廊背景
        corridor = world_beta.corridors[current_area]
        if "corridor" in images:
            # 计算走廊位置和大小
            corridor_x = corridor["start"][0] + camera_offset[0]
            corridor_y = corridor["start"][1] - corridor["width"] // 2 + camera_offset[1]
            corridor_width = corridor["width"]
            corridor_height = corridor["width"]
            
            # 缩放走廊背景
            scaled_corridor = pygame.transform.scale(images["corridor"], (corridor_width, corridor_height))
            win.blit(scaled_corridor, (corridor_x, corridor_y))
            
            # 在走廊两端绘制门
            if "gate_open" in images:
                gate_size = corridor_height
                gate_left = pygame.transform.scale(images["gate_open"], (gate_size, gate_size))
                gate_right = pygame.transform.scale(images["gate_open"], (gate_size, gate_size))
                
                # 绘制左门和右门
                win.blit(gate_left, (corridor_x, corridor_y))
                win.blit(gate_right, (corridor_x + corridor_width - gate_size, corridor_y))

                # 检查玩家是否靠近左门
                if (abs(player.world_x - corridor["start"][0]) < 100 and 
                    abs(player.world_y - corridor["start"][1]) < 100):
                    # 显示交互提示
                    text = font.render("Press E to return", True, (255, 255, 255))
                    text_rect = text.get_rect(center=(screen_width // 2, screen_height - 100))
                    win.blit(text, text_rect)
                # 检查玩家是否靠近右门
                elif (abs(player.world_x - corridor["end"][0]) < 100 and 
                      abs(player.world_y - corridor["end"][1]) < 100):
                    # 显示交互提示（根据关卡是否清空显示不同信息）
                    level_parts = current_area.split("_")
                    if len(level_parts) == 3:
                        from_level = int(level_parts[1])
                        if world_beta.levels[from_level]["cleared"]:
                            text = font.render("Press E to proceed", True, (255, 255, 255))
                        else:
                            text = font.render("Clear current level to proceed", True, (255, 0, 0))
                        text_rect = text.get_rect(center=(screen_width // 2, screen_height - 100))
                        win.blit(text, text_rect)
        else:
            print("Warning: Corridor background image not found!")
    
    # 绘制敌人
    for enemy in enemies:
        enemy.draw(win, camera_offset)
    
    # 绘制玩家
    player.draw(win)
    
    # 绘制子弹
    draw_bullets(bullets, images.get("bullet_original"), win, camera_offset, images.get("enemy_bullet"))
    draw_bullets(enemy_bullets, images.get("bullet_original"), win, camera_offset, images.get("enemy_bullet"))
    
    # 绘制HUD
    draw_hud(win, font, player, screen_width)
    
    # 如果当前在Boss关，显示Boss警告
    if current_area in world_beta.levels and world_beta.levels[current_area]["is_boss"]:
        boss_warning = font.render("BOSS LEVEL!", True, (255, 0, 0))
        warning_rect = boss_warning.get_rect(center=(screen_width // 2, 50))
        win.blit(boss_warning, warning_rect)

# 绘制游戏结束界面
def draw_game_over(win, font, red, screen_width, screen_height):
    win.fill((255, 255, 255))
    text_surface = font.render("Game over!", True, red)
    text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
    win.blit(text_surface, text_rect)
    # 示例：在 draw_game_over 后绘制淡出