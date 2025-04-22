# main.py
import pygame
import constants
import traceback
import sys
import random
from initial import initialize_game
from bullet import shoot_bullet, update_bullets
from constants import BULLETS, ENEMIES, ENEMY_BULLETS, SHOOT_COOLDOWN, F_KEY_COOLDOWN, ENERGY_RECOVERY_RATE, LAST_SHOT_TIME, LAST_F_KEY_TIME, GAME_OVER_DELAY, PLAYER_BULLET_DAMAGE
from render import draw_start_hall, draw_main_level, draw_game_over, message_system
from menu import BatteryMenu, PropertyTreeMenu
from enemy import RangedEnemy, MeleeEnemy, Boss

# 设置异常处理
def exception_handler(exctype, value, tb):
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    print("发生错误:")
    print(error_msg)
    with open("error_log.txt", "a") as f:
        f.write(f"\n\n{error_msg}")
    pygame.quit()
    sys.exit(1)

sys.excepthook = exception_handler

# Show input method reminder
def show_input_reminder(win, font, screen_width, screen_height):
    title_font = pygame.font.Font(None, 72)
    subtitle_font = pygame.font.Font(None, 36)
    
    title = title_font.render("Z2H", True, (255, 255, 255))
    subtitle = subtitle_font.render("Please switch to English input method for WASD movement", True, (200, 200, 200))
    press_key = subtitle_font.render("Press any key to continue...", True, (150, 150, 150))
    
    title_rect = title.get_rect(center=(screen_width // 2, screen_height // 3))
    subtitle_rect = subtitle.get_rect(center=(screen_width // 2, screen_height // 2))
    press_key_rect = press_key.get_rect(center=(screen_width // 2, screen_height * 2 // 3))
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
        
        win.fill((0, 0, 0))
        win.blit(title, title_rect)
        win.blit(subtitle, subtitle_rect)
        win.blit(press_key, press_key_rect)
        pygame.display.flip()

# initialize game
try:
    win, red, font, screen_width, screen_height, images, player, start_hall = initialize_game()
    constants.HALL_WIDTH = screen_width
    constants.HALL_HEIGHT = screen_height
except Exception as e:
    print(f"Initialization failed: {e}")
    pygame.quit()
    exit(1)

# Show input method reminder
show_input_reminder(win, font, screen_width, screen_height)

# game variables
in_start_hall = True
WORLD_WIDTH = screen_width * 3
WORLD_HEIGHT = screen_height * 3
battery_menu = BatteryMenu(screen_width, screen_height)
property_tree_menu = PropertyTreeMenu(screen_width, screen_height)
clock = pygame.time.Clock()
last_update_time = pygame.time.get_ticks()
game_over = False
game_over_time = 0

# 在初始化部分添加关卡状态
current_level = 1
level_cleared = {1: False, 2: False, 3: False, 4: False}
corridor_entered = False
corridor_exit = False

# 添加World类
class World:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = screen_width * 3
        self.world_height = screen_height * 3
        
        # 定义关卡中心位置
        self.level_centers = {
            1: (self.screen_width // 2, self.screen_height // 2),  # 第一关在屏幕中心
            2: (self.screen_width * 3 // 2, self.screen_height // 2),
            3: (self.screen_width * 5 // 2, self.screen_height // 2),
            4: (self.screen_width * 7 // 2, self.screen_height // 2)
        }
        
        # 定义走廊位置（在关卡之间）
        corridor_width = 200
        self.corridors = {
            "corridor_1_2": {
                "start": (self.screen_width - corridor_width//2, self.screen_height // 2),
                "end": (self.screen_width + corridor_width//2, self.screen_height // 2),
                "width": corridor_width,
                "is_safe": True  # 标记为安全区域
            },
            "corridor_2_3": {
                "start": (self.screen_width * 2 - corridor_width//2, self.screen_height // 2),
                "end": (self.screen_width * 2 + corridor_width//2, self.screen_height // 2),
                "width": corridor_width,
                "is_safe": True
            },
            "corridor_3_4": {
                "start": (self.screen_width * 3 - corridor_width//2, self.screen_height // 2),
                "end": (self.screen_width * 3 + corridor_width//2, self.screen_height // 2),
                "width": corridor_width,
                "is_safe": True
            }
        }
        
        self.levels = {
            1: {"background": "background_1", "is_boss": False, "cleared": False},
            2: {"background": "background_2", "is_boss": True, "cleared": False},
            3: {"background": "background_3", "is_boss": False, "cleared": False},
            4: {"background": "background_4", "is_boss": True, "cleared": False}
        }
    
    def get_current_area(self, x, y):
        print(f"Checking position ({x}, {y})")  # 调试信息
        
        # 检查是否在走廊中
        for corridor_id, corridor in self.corridors.items():
            corridor_x = corridor["start"][0]
            corridor_y = corridor["start"][1]
            if (abs(x - corridor_x) <= corridor["width"] and
                abs(y - corridor_y) <= corridor["width"] // 2):
                print(f"Found in corridor {corridor_id}")  # 调试信息
                return corridor_id
        
        # 检查是否在关卡中
        for level_id, center in self.level_centers.items():
            level_x = center[0]
            level_y = center[1]
            # 使用屏幕尺寸作为关卡范围
            if (abs(x - level_x) <= self.screen_width // 2 and
                abs(y - level_y) <= self.screen_height // 2):
                print(f"Found in level {level_id}")  # 调试信息
                return level_id
        
        print("Not found in any area")  # 调试信息
        return None

    def get_next_level(self, current_level):
        if current_level < 4:
            return current_level + 1
        return None

    def get_previous_level(self, current_level):
        if current_level > 1:
            return current_level - 1
        return None

    def get_camera_offset(self, player_x, player_y):
        return (self.screen_width // 2 - player_x, self.screen_height // 2 - player_y)

# 创建世界实例
world = World(screen_width, screen_height)

# 初始化敌人（在主关卡生成）
def spawn_enemies():
    try:
        print("开始生成敌人...")
        ENEMIES.clear()
        ENEMY_BULLETS.clear()  # 清空敌人子弹
        # 在主关卡中生成敌人
        print("生成远程敌人1...")
        ENEMIES.append(RangedEnemy(1000, 1000, images))
        print("生成远程敌人2...")
        ENEMIES.append(RangedEnemy(1200, 1200, images))
        print("生成近战敌人1...")
        ENEMIES.append(MeleeEnemy(1400, 1400, images))
        print("生成近战敌人2...")
        ENEMIES.append(MeleeEnemy(1600, 1600, images))
        print("生成Boss...")
        ENEMIES.append(Boss(2000, 2000, images))
        print("敌人生成完成")
        return True
    except Exception as e:
        print(f"敌人生成失败: {e}")
        traceback.print_exc()
        return False

# 重置游戏状态
def reset_game():
    global in_start_hall, game_over, game_over_time, current_level, level_cleared, corridor_entered, corridor_exit
    # 重置玩家状态
    player.hp = player.max_hp
    player.armor = player.max_armor
    player.energy = player.max_energy
    player.backpack = {'batteries': 10}  # 重置背包，初始10个电池
    player.backpack_used = 10  # 重置背包已用空间
    player.world_x = start_hall.width * start_hall.tile_size // 2  # 大厅中心
    player.world_y = start_hall.height * start_hall.tile_size // 2
    player.direction = [0.0, 0.0]  # 停止移动
    player.angle = 0.0  # 重置朝向
    player.image = player.image_original  # 重置图像旋转
    player.rect.center = (screen_width // 2, screen_height // 2)
    # 清空敌人和子弹
    ENEMIES.clear()
    BULLETS.clear()
    ENEMY_BULLETS.clear()
    # 重置场景和菜单
    in_start_hall = True
    battery_menu.active = False
    game_over = False
    game_over_time = 0
    current_level = 1
    level_cleared = {1: False, 2: False, 3: False, 4: False}
    corridor_entered = False
    corridor_exit = False
    print("Reset game state.")

# main game loop
running = True
while running:
    current_time = pygame.time.get_ticks()
    dt = (current_time - last_update_time) / 1000.0
    last_update_time = current_time
    
    # 获取按键状态
    keys = pygame.key.get_pressed()
    
    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        if not game_over and battery_menu.handle_event(event, player, start_hall):
            continue
        if not game_over and property_tree_menu.handle_event(event, player):
            continue

        # handle battery menu and property tree interaction
        if not game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if start_hall.check_battery_interaction(player, pygame.key.get_pressed()):
                battery_menu.active = True
                print(f"Battery menu activated: {battery_menu.active}")
            elif start_hall.check_property_tree_interaction(player, pygame.key.get_pressed()):
                property_tree_menu.active = True
                print(f"Property tree menu activated: {property_tree_menu.active}")

        # handle key press
        if not game_over and not battery_menu.active:
            # handle mouse click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if current_time - LAST_SHOT_TIME >= SHOOT_COOLDOWN:
                    shoot_bullet(player, current_time, pygame.mouse.get_pos(), 1)

            # handle F key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                if current_time - LAST_F_KEY_TIME >= F_KEY_COOLDOWN:
                    constants.LAST_F_KEY_TIME = current_time
                    # 切换技能
                    if player.selected_skill == "dash":
                        player.selected_skill = "double_damage"
                        message_system.add_message("Switched to Double Damage!")
                    else:
                        player.selected_skill = "dash"
                        message_system.add_message("Switched to Dash!")
                    # 激活当前选中的技能
                    player.activate_skill(player.selected_skill, current_time)

    # 如果游戏结束，显示结束画面
    if game_over:
        # 清空屏幕
        win.fill((0, 0, 0))
        
        # 绘制游戏结束画面
        game_over_text = font.render("GAME OVER", True, red)
        
        # 计算文本位置
        game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 2))
        
        # 绘制文本
        win.blit(game_over_text, game_over_rect)
        
        # 更新显示
        pygame.display.flip()
        
        # 检查是否重启游戏
        if current_time - game_over_time >= GAME_OVER_DELAY:
            player.lose_experience()  # 失去当前关卡获得的经验
            reset_game()
        continue

    if not game_over:
        player.recover_energy(ENERGY_RECOVERY_RATE * dt)

        if not battery_menu.active:
            # update player
            player.update(keys, current_time, pygame.mouse.get_pos())

        # calculate camera offset
        camera_offset = (screen_width // 2 - player.world_x, screen_height // 2 - player.world_y)

        # 更新敌人
        for enemy in ENEMIES[:]:
            enemy.update(dt, player, WORLD_WIDTH, WORLD_HEIGHT, ENEMY_BULLETS, current_time, start_hall if in_start_hall else None, in_start_hall)
            if not enemy.alive:
                ENEMIES.remove(enemy)

        # update bullets
        update_bullets(BULLETS, WORLD_WIDTH, WORLD_HEIGHT, current_time, player, images.get("player_original"), images.get("bullet_original"), start_hall if in_start_hall else None, in_start_hall, ENEMIES)
        
        # 更新敌人子弹，如果玩家死亡则结束游戏
        bullet_result = update_bullets(ENEMY_BULLETS, WORLD_WIDTH, WORLD_HEIGHT, current_time, player, images.get("player_original"), images.get("bullet_original"), start_hall if in_start_hall else None, in_start_hall)
        if bullet_result:
            print(f"Player HP after bullet damage: {player.hp}")
            game_over = True
            game_over_time = current_time
            print("Player defeated by enemy bullet")
            continue

        # 检查近战敌人的攻击
        for enemy in ENEMIES:
            if isinstance(enemy, MeleeEnemy) and enemy.alive and current_time - enemy.last_contact_time >= enemy.contact_cooldown:
                if enemy.rect.colliderect(player.rect):
                    if not player.take_damage(enemy.contact_damage):
                        print(f"Player HP after contact damage: {player.hp}")
                        game_over = True
                        game_over_time = current_time
                        print("Player defeated by melee enemy contact")
                    enemy.last_contact_time = current_time

        # draw start hall or main level
        if in_start_hall:
            # 检查是否按下E键进入第一关
            if keys[pygame.K_e]:
                # 检查玩家是否在传送门附近
                if abs(player.world_x - screen_width // 2) < 50 and abs(player.world_y - screen_height // 2) < 50:
                    in_start_hall = False
                    current_level = 1
                    # 将玩家传送到主关卡中心
                    player.world_x = WORLD_WIDTH // 2
                    player.world_y = WORLD_HEIGHT // 2
                    # 恢复玩家状态
                    player.energy = player.max_energy
                    player.hp = player.max_hp
                    player.armor = player.max_armor
                    # 生成第一关的敌人
                    enemies = []
                    for _ in range(3):
                        enemy = MeleeEnemy(random.randint(100, WORLD_WIDTH - 100),
                                         random.randint(100, WORLD_HEIGHT - 100),
                                         images["melee_enemy"])
                        enemies.append(enemy)
                    print("Entered level 1 from start hall")
            if start_hall.check_gate_interaction(player, keys):
                try:
                    # 先清空所有子弹
                    BULLETS.clear()
                    ENEMY_BULLETS.clear()
                    print("子弹已清空")
                    
                    # 设置玩家位置到主关卡
                    player.world_x = WORLD_WIDTH // 2
                    player.world_y = WORLD_HEIGHT // 2
                    print(f"玩家位置已设置: ({player.world_x}, {player.world_y})")
                    
                    # 生成敌人
                    print("开始生成敌人...")
                    if not spawn_enemies():
                        raise Exception("敌人生成失败")
                    print("敌人生成完成")
                    
                    # 最后切换关卡状态
                    in_start_hall = False
                    message_system.add_message("Energy fully restored!")
                    print("成功进入主关卡")
                    
                    # 强制更新显示
                    pygame.display.flip()
                except Exception as e:
                    print(f"进入主关卡失败: {e}")
                    traceback.print_exc()
                    message_system.add_message("Failed to enter main level!")
                    continue
            
            # 绘制开始大厅
            try:
                draw_start_hall(win, red, font, screen_width, screen_height, images, start_hall, player, BULLETS, camera_offset, ENEMIES, ENEMY_BULLETS)
            except Exception as e:
                print(f"绘制开始大厅失败: {e}")
                traceback.print_exc()
                continue
        else:
            # 绘制主关卡
            try:
                draw_main_level(win, images, player, BULLETS, camera_offset, font, screen_width, screen_height, ENEMIES, ENEMY_BULLETS, world)
            except Exception as e:
                print(f"绘制主关卡失败: {e}")
                traceback.print_exc()
                continue

        # draw battery menu and property tree menu
        try:
            battery_menu.draw(win, start_hall)
            property_tree_menu.draw(win)
        except Exception as e:
            print(f"绘制菜单失败: {e}")
            traceback.print_exc()
            continue

        # 在游戏主循环中添加走廊限制逻辑
        if corridor_entered:
            # 限制玩家在走廊内的移动
            if player.x < 0:
                player.x = 0
            elif player.x > screen_width - 200:  # 走廊宽度为200
                player.x = screen_width - 200
            
            # 在走廊中显示提示信息
            font = pygame.font.Font(None, 36)
            if not level_cleared[current_level]:
                text = font.render("Clear all enemies to proceed!", True, (255, 255, 255))
            else:
                text = font.render("Press SPACE to enter next level", True, (255, 255, 255))
            text_x = screen_width // 2 - text.get_width() // 2
            win.blit(text, (text_x, 50))
            
            # 检查是否按下空格键进入下一关
            if level_cleared[current_level] and keys[pygame.K_SPACE]:
                corridor_entered = False
                corridor_exit = False
                if current_level == 1:
                    current_level = 2
                    player.x = 100
                elif current_level == 2:
                    current_level = 3
                    player.x = screen_width - 100
                elif current_level == 3:
                    current_level = 4
                    player.x = 100
                # 生成新关卡的敌人
                enemies = []
                if current_level == 2 or current_level == 4:
                    boss = Boss(screen_width // 2, screen_height // 2, images["boss_original"])
                    enemies.append(boss)
                elif current_level == 3:
                    for _ in range(2):
                        enemy = RangedEnemy(random.randint(100, screen_width - 100),
                                          random.randint(100, screen_height - 100),
                                          images["ranged_enemy"])
                        enemies.append(enemy)

        # 在游戏主循环中添加门和走廊的交互逻辑
        if not in_start_hall:
            current_area = world.get_current_area(player.world_x, player.world_y)
            
            if isinstance(current_area, int):  # 在关卡中
                # 检查是否按E键且在门附近
                if keys[pygame.K_e]:
                    # 计算当前关卡右侧门的位置
                    gate_x = world.level_centers[current_level][0] + world.world_width//4
                    gate_y = world.level_centers[current_level][1]
                    
                    if (abs(player.world_x - gate_x) < 100 and 
                        abs(player.world_y - gate_y) < 100):
                        # 进入走廊
                        corridor_id = f"corridor_{current_level}_{current_level + 1}"
                        if corridor_id in world.corridors:
                            # 将玩家传送到走廊左侧
                            corridor = world.corridors[corridor_id]
                            player.world_x = corridor["start"][0] + 100
                            player.world_y = corridor["start"][1]
                            print(f"Entered corridor {corridor_id}")
            
            elif isinstance(current_area, str) and "corridor" in current_area:  # 在走廊中
                corridor = world.corridors[current_area]
                level_parts = current_area.split("_")
                if len(level_parts) == 3:
                    from_level = int(level_parts[1])
                    to_level = int(level_parts[2])
                    
                    # 检查是否按E键且在左门附近
                    if keys[pygame.K_e]:
                        if (abs(player.world_x - corridor["start"][0]) < 100 and 
                            abs(player.world_y - corridor["start"][1]) < 100):
                            # 返回左侧关卡的右门位置
                            gate_x = world.level_centers[from_level][0] + world.world_width//4
                            gate_y = world.level_centers[from_level][1]
                            player.world_x = gate_x
                            player.world_y = gate_y
                            current_level = from_level
                            print(f"Returned to level {from_level}")
                        # 检查是否在右门附近且关卡已清空
                        elif (abs(player.world_x - corridor["end"][0]) < 100 and 
                              abs(player.world_y - corridor["end"][1]) < 100 and 
                              world.levels[from_level]["cleared"]):
                            # 进入右侧关卡
                            player.world_x = world.level_centers[to_level][0] - world.world_width//4
                            player.world_y = world.level_centers[to_level][1]
                            current_level = to_level
                            print(f"Entered level {to_level}")

        # 更新显示
        pygame.display.flip()

    # limit frame rate to 120 FPS
    clock.tick(120)

# quit pygame
pygame.quit()
