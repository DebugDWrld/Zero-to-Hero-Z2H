# bullet.py
import pygame
import math
from constants import BULLET_SPEED, SHOOT_COOLDOWN, LAST_SHOT_TIME, BULLETS
from enemy import MeleeEnemy, RangedEnemy, Boss

# 计算两点之间的距离
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# 检查子弹与实体的碰撞
def check_collision(bullet, entity, collision_radius):
    return distance(bullet["x"], bullet["y"], entity.world_x, entity.world_y) < collision_radius

# shoot bullet
def shoot_bullet(player, current_time, mouse_pos, speed_multiplier=1):
    global LAST_SHOT_TIME
    if current_time - LAST_SHOT_TIME >= SHOOT_COOLDOWN:
        # Calculate direction based on mouse position
        dx = mouse_pos[0] - player.screen_width // 2
        dy = mouse_pos[1] - player.screen_height // 2
        length = math.sqrt(dx ** 2 + dy ** 2)
        if length > 0:
            # 先尝试消耗能量
            if player.use_energy(4):
                direction = [dx / length, dy / length]
                bullet = {
                    "x": player.world_x,
                    "y": player.world_y,
                    "velocity": [direction[0] * BULLET_SPEED * speed_multiplier, 
                                direction[1] * BULLET_SPEED * speed_multiplier],
                    "angle": math.degrees(math.atan2(-dy, dx)),
                    "spawn_time": current_time,
                    "visible": True,
                    "damage": 1 * player.damage_multiplier,  # 使用玩家的伤害倍数
                    "collision_radius": 10  # 碰撞检测半径
                }
                BULLETS.append(bullet)
                LAST_SHOT_TIME = current_time
                return True
            else:
                from render import message_system
                message_system.add_message("Not enough energy!")
                return False
    return False

# update bullets
def update_bullets(bullets, world_width, world_height, current_time, player, player_image, bullet_image, start_hall=None, in_start_hall=False, enemies=None):
    # 更新所有子弹
    for bullet in bullets[:]:
        # 更新子弹位置
        bullet["x"] += bullet["velocity"][0]
        bullet["y"] += bullet["velocity"][1]
        
        # 检查子弹是否在走廊安全区域内
        in_corridor = False
        if not in_start_hall and "world" in bullet:  # 确保bullet有world属性
            current_area = bullet["world"].get_current_area(bullet["x"], bullet["y"])
            if isinstance(current_area, str) and "corridor" in current_area:
                # 如果子弹进入走廊，移除它
                bullets.remove(bullet)
                continue

        # 检查子弹是否超出边界
        if in_start_hall:
            if start_hall and not start_hall.is_valid_position(bullet["x"], bullet["y"]):
                bullets.remove(bullet)
                continue
        else:
            if (bullet["x"] < 0 or bullet["x"] > world_width or
                bullet["y"] < 0 or bullet["y"] > world_height):
                bullets.remove(bullet)
                continue
        
        # 检查子弹是否击中玩家（仅对敌人子弹）
        if enemies is None:  # 这是敌人子弹
            # 确保子弹有必要的属性
            if "collision_radius" not in bullet:
                bullet["collision_radius"] = 10  # 默认碰撞半径
            if "damage" not in bullet:
                bullet["damage"] = 2  # 默认伤害值
            
            # 计算玩家和子弹之间的距离
            dx = bullet["x"] - player.world_x
            dy = bullet["y"] - player.world_y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            # 检查碰撞
            if distance < bullet["collision_radius"] + player.collision_radius:
                if not player.take_damage(bullet["damage"]):
                    print("Player defeated by enemy bullet")
                    return True  # 返回True表示玩家死亡
                bullet["visible"] = False
                continue
        
        # 检查子弹是否击中敌人（仅对玩家子弹）
        if enemies:
            for enemy in enemies[:]:
                if check_collision(bullet, enemy, bullet["collision_radius"] + enemy.collision_radius):
                    enemy.take_damage(bullet["damage"])
                    if not enemy.alive:  # 如果敌人死亡
                        if isinstance(enemy, MeleeEnemy):
                            player.add_experience(1)  # 击杀近战敌人获得1点经验
                        elif isinstance(enemy, RangedEnemy):
                            player.add_experience(3)  # 击杀远程敌人获得3点经验
                        elif isinstance(enemy, Boss):
                            player.add_experience(10)  # 击杀Boss获得10点经验
                    bullet["visible"] = False
                    break
        
        # 检查子弹是否击中墙壁
        if in_start_hall and start_hall:
            tile_size = start_hall.tile_size
            grid_x = int(bullet["x"] // tile_size)
            grid_y = int(bullet["y"] // tile_size)
            
            if 0 <= grid_x < start_hall.width and 0 <= grid_y < start_hall.height:
                if start_hall.grid[grid_y][grid_x] == 1:  # 1代表墙壁
                    bullet["visible"] = False
        
        if not bullet["visible"]:
            bullets.remove(bullet)
    return False  # 玩家存活

# draw bullets
def draw_bullets(bullets, bullet_image, win, camera_offset, enemy_bullet_image=None):
    offset_x, offset_y = camera_offset
    for bullet in bullets:
        if bullet["visible"]:
            if enemy_bullet_image is None:  # 敌人子弹缺失时绘制红色圆点
                pygame.draw.circle(win, (255, 0, 0), 
                                  (int(bullet["x"] + offset_x), int(bullet["y"] + offset_y)), 5)
            else:
                rotated_bullet = pygame.transform.rotate(bullet_image if bullet_image else enemy_bullet_image, bullet["angle"])
                bullet_rect = rotated_bullet.get_rect(center=(bullet["x"] + offset_x, bullet["y"] + offset_y))
                win.blit(rotated_bullet, bullet_rect)