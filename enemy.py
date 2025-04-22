# enemy.py
import pygame
import math
import random
from constants import ENEMY_BULLET_SPEED

class Enemy:
    def __init__(self, world_x, world_y, images, image_key, hp, speed, damage=10, placeholder_color=(255, 255, 255)):
        self.world_x = world_x
        self.world_y = world_y
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.damage = damage
        self.use_placeholder = image_key not in images  # 检查图像是否缺失
        self.placeholder_color = placeholder_color
        self.placeholder_size = (64, 64)  # 矩形大小
        self.collision_radius = 32  # 碰撞检测半径
        if not self.use_placeholder:
            self.image_original = images[image_key]
            self.image = self.image_original
            self.rect = self.image.get_rect(center=(world_x, world_y))
        else:
            self.image = None
            self.rect = pygame.Rect(0, 0, self.placeholder_size[0], self.placeholder_size[1])
            self.rect.center = (world_x, world_y)
        self.direction = [0.0, 0.0]
        self.angle = 0.0
        self.last_direction = [1.0, 0.0]
        self.alive = True
        self.state = "idle"
        self.hit_effect_time = 0
        self.hit_effect_duration = 100  # 受击变红 100ms

    def update(self, dt, player, world_width, world_height, start_hall=None, in_start_hall=False):
        """虚方法，子类实现具体更新逻辑"""
        if not self.alive:
            return
        # 受击效果
        if self.hit_effect_time > 0:
            self.hit_effect_time -= dt * 1000
            if not self.use_placeholder:
                self.image = self._apply_hit_effect()
        else:
            if not self.use_placeholder:
                self.image = pygame.transform.rotate(self.image_original, self.angle)
        # 更新位置并检查墙壁碰撞
        new_x = self.world_x + self.direction[0] * self.speed * dt
        new_y = self.world_y + self.direction[1] * self.speed * dt
        if in_start_hall and start_hall:
            tile_size = start_hall.tile_size
            grid_x = int(new_x // tile_size)
            grid_y = int(new_y // tile_size)
            if 0 <= grid_x < start_hall.width and 0 <= grid_y < start_hall.height:
                if start_hall.grid[grid_y][grid_x] == 1:  # 墙壁
                    new_x, new_y = self.world_x, self.world_y  # 取消移动
        self.world_x = max(0, min(new_x, world_width))
        self.world_y = max(0, min(new_y, world_height))
        self.rect.center = (self.world_x, self.world_y)

    def draw(self, win, camera_offset):
        """绘制敌人，考虑相机偏移"""
        if not self.alive:
            return
        screen_x = self.world_x + camera_offset[0]
        screen_y = self.world_y + camera_offset[1]
        self.rect.center = (screen_x, screen_y)
        if self.use_placeholder:
            pygame.draw.rect(win, self.placeholder_color, 
                             (screen_x - self.placeholder_size[0] // 2, 
                              screen_y - self.placeholder_size[1] // 2, 
                              self.placeholder_size[0], self.placeholder_size[1]))
        else:
            win.blit(self.image, self.rect)

    def take_damage(self, damage):
        """处理敌人受损"""
        if not self.alive:
            return
        self.hp -= damage
        self.hit_effect_time = self.hit_effect_duration
        if self.hp <= 0:
            self.alive = False

    def _apply_hit_effect(self):
        """应用受击效果（图像变红）"""
        red_tint = pygame.Surface(self.image_original.get_size(), pygame.SRCALPHA)
        red_tint.fill((255, 100, 100, 128))
        tinted_image = self.image_original.copy()
        tinted_image.blit(red_tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return pygame.transform.rotate(tinted_image, self.angle)

class RangedEnemy(Enemy):
    def __init__(self, world_x, world_y, images):
        super().__init__(world_x, world_y, images, "ranged_enemy", hp=6, speed=80, 
                         damage=5, placeholder_color=(0, 255, 0))  # 绿色矩形
        self.collision_radius = 24  # 远程敌人碰撞半径较小
        self.min_distance = 200
        self.shoot_cooldown = 2000
        self.last_shot_time = 0
        self.shoot_damage = 2
        self.patrol_timer = 0
        self.patrol_duration = random.uniform(2000, 5000)
        self.patrol_direction = [random.uniform(-1, 1), random.uniform(-1, 1)]

    def update(self, dt, player, world_width, world_height, enemy_bullets, current_time, start_hall=None, in_start_hall=False):
        """更新远程敌人：巡逻、追逐、射击"""
        if not self.alive:
            return
        dx = player.world_x - self.world_x
        dy = player.world_y - self.world_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 500:
            self.state = "patrol"
        elif distance < self.min_distance:
            self.state = "retreat"
        else:
            self.state = "attack"
        if self.state == "patrol":
            self.patrol_timer += dt * 1000
            if self.patrol_timer >= self.patrol_duration:
                self.patrol_direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
                self.patrol_timer = 0
                self.patrol_duration = random.uniform(2000, 5000)
            length = (self.patrol_direction[0] ** 2 + self.patrol_direction[1] ** 2) ** 0.5
            self.direction = [self.patrol_direction[0] / length, self.patrol_direction[1] / length] if length > 0 else [0, 0]
        elif self.state == "retreat":
            self.direction = [-dx / distance, -dy / distance] if distance > 0 else [random.uniform(-1, 1), random.uniform(-1, 1)]
        elif self.state == "attack":
            self.direction = [0, 0]
            if distance > 0 and current_time - self.last_shot_time >= self.shoot_cooldown:
                self._shoot_bullet(enemy_bullets, dx, dy, distance, current_time)
        self.angle = math.degrees(math.atan2(-dy, dx))
        super().update(dt, player, world_width, world_height, start_hall, in_start_hall)

    def _shoot_bullet(self, enemy_bullets, dx, dy, distance, current_time):
        """发射子弹"""
        if len(enemy_bullets) < 50:
            bullet = {
                "x": self.world_x,
                "y": self.world_y,
                "velocity": [dx / distance * ENEMY_BULLET_SPEED, dy / distance * ENEMY_BULLET_SPEED],
                "angle": self.angle,
                "spawn_time": current_time,
                "visible": True
            }
            enemy_bullets.append(bullet)
            self.last_shot_time = current_time

class MeleeEnemy(Enemy):
    def __init__(self, world_x, world_y, images):
        super().__init__(world_x, world_y, images, "melee_enemy", hp=4, speed=100, 
                         damage=5, placeholder_color=(0, 0, 255))  # 蓝色矩形
        self.collision_radius = 20  # 近战敌人碰撞半径调整为20，与玩家相同
        self.charge_cooldown = 5000
        self.last_charge_time = 0
        self.charge_duration = 500
        self.charge_timer = 0
        self.charge_speed = self.speed * 2
        self.contact_damage = 2  # 接触伤害
        self.last_contact_time = 0  # 上次接触伤害时间
        self.contact_cooldown = 1000  # 接触伤害冷却时间

    def update(self, dt, player, world_width, world_height, enemy_bullets=None, current_time=None, start_hall=None, in_start_hall=False):
        """更新近战敌人：追逐、冲刺"""
        if not self.alive:
            return
        dx = player.world_x - self.world_x
        dy = player.world_y - self.world_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        # 检查接触伤害 - 只有当敌人和玩家真正接触时才造成伤害
        if distance <= self.collision_radius + player.collision_radius and current_time - self.last_contact_time >= self.contact_cooldown:
            if not player.take_damage(self.contact_damage):
                print("Player defeated by melee enemy contact")
            self.last_contact_time = current_time
        
        if distance > 300:
            self.state = "chase"
        elif distance > self.collision_radius + player.collision_radius:
            self.state = "approach"
        else:
            self.state = "attack"
            
        if self.state == "attack" and current_time - self.last_charge_time >= self.charge_cooldown:
            self.charge_timer = self.charge_duration
            self.last_charge_time = current_time
            
        speed = self.charge_speed if self.charge_timer > 0 else self.speed
        if self.charge_timer > 0:
            self.charge_timer -= dt * 1000
            
        if distance > 0:
            self.direction = [dx / distance, dy / distance]
            self.last_direction = self.direction[:]
            
        self.angle = math.degrees(math.atan2(-dy, dx))
        super().update(dt, player, world_width, world_height, start_hall, in_start_hall)

class Boss(Enemy):
    def __init__(self, world_x, world_y, images):
        super().__init__(world_x, world_y, images, "boss", hp=10, speed=60, 
                         damage=5, placeholder_color=(128, 0, 128))  # 紫色矩形
        self.collision_radius = 48  # Boss碰撞半径最大
        self.shoot_cooldown = 1500
        self.last_shot_time = 0
        self.min_distance = 150
        self.phase = 1
        self.burst_cooldown = 5000
        self.last_burst_time = 0
        self.burst_warning_time = 0
        self.burst_warning_duration = 500

    def update(self, dt, player, world_width, world_height, enemy_bullets, current_time, start_hall=None, in_start_hall=False):
        """更新Boss：阶段性行为、爆发射击"""
        if not self.alive:
            return
        dx = player.world_x - self.world_x
        dy = player.world_y - self.world_y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if self.hp < self.max_hp * 0.5 and self.phase == 1:
            self.phase = 2
            self.shoot_cooldown = 1000
        if distance < self.min_distance:
            self.state = "retreat"
            self.direction = [-dx / distance, -dy / distance] if distance > 0 else [random.uniform(-1, 1), random.uniform(-1, 1)]
        else:
            self.state = "attack"
            self.direction = [dx / distance, dy / distance] if distance > 0 else [0, 0]
        self.angle = math.degrees(math.atan2(-dy, dx))
        if self.state == "attack" and distance > 0:
            if self.phase == 2 and current_time - self.last_burst_time >= self.burst_cooldown:
                self.burst_warning_time = self.burst_warning_duration
                self.last_burst_time = current_time
                self._shoot_burst(enemy_bullets, dx, dy, distance, current_time)
            elif current_time - self.last_shot_time >= self.shoot_cooldown:
                self._shoot_bullet(enemy_bullets, dx, dy, distance, current_time)
        if self.burst_warning_time > 0:
            self.burst_warning_time -= dt * 1000
            if not self.use_placeholder:
                self.image = self._apply_warning_effect()
        super().update(dt, player, world_width, world_height, start_hall, in_start_hall)

    def _shoot_bullet(self, enemy_bullets, dx, dy, distance, current_time):
        """发射单发子弹"""
        if len(enemy_bullets) < 50:
            bullet = {
                "x": self.world_x,
                "y": self.world_y,
                "velocity": [dx / distance * ENEMY_BULLET_SPEED, dy / distance * ENEMY_BULLET_SPEED],
                "angle": self.angle,
                "spawn_time": current_time,
                "visible": True
            }
            enemy_bullets.append(bullet)
            self.last_shot_time = current_time

    def _shoot_burst(self, enemy_bullets, dx, dy, distance, current_time):
        """发射扇形弹幕"""
        if len(enemy_bullets) >= 50:
            return
        angles = [-30, -15, 0, 15, 30]
        for offset in angles:
            rad = math.radians(self.angle + offset)
            bullet = {
                "x": self.world_x,
                "y": self.world_y,
                "velocity": [math.cos(rad) * ENEMY_BULLET_SPEED, -math.sin(rad) * ENEMY_BULLET_SPEED],
                "angle": self.angle + offset,
                "spawn_time": current_time,
                "visible": True
            }
            enemy_bullets.append(bullet)
        self.last_shot_time = current_time

    def _apply_warning_effect(self):
        """应用爆发预警效果（闪烁黄色）"""
        yellow_tint = pygame.Surface(self.image_original.get_size(), pygame.SRCALPHA)
        yellow_tint.fill((255, 255, 0, 128))
        tinted_image = self.image_original.copy()
        tinted_image.blit(yellow_tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return pygame.transform.rotate(tinted_image, self.angle)