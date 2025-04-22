# player.py
import pygame
import math
from constants import MOVE_SPEED
from render import message_system

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
        self.tile_size = 32
        # 背包初始化，容量为64
        self.backpack = {'batteries': 10}  # 初始10个电池
        self.backpack_capacity = 64  # 背包总容量
        self.backpack_used = 10  # 已使用空间（初始10个电池）

        # The properties of the player
        self.hp = 10  # HP
        self.max_hp = 10  # The maximum amount of health the player can hold
        self.armor = 5  # Armor
        self.max_armor = 5  # The maximum amount of armor the player can hold
        self.energy = 100  # Energy
        self.max_energy = 100  # The maximum amount of energy the player can hold
        self.collision_radius = 20  # 添加碰撞半径属性

        # 经验系统
        self.experience = 0  # 总经验值
        self.current_level_experience = 0  # 当前关卡获得的经验值

        # 技能系统
        self.skills = {
            "dash": {
                "name": "dash",
                "energy_cost": 20,
                "cooldown": 10000,  # 10秒冷却
                "last_used": 0,
                "active": False,
                "duration": 100,  # 冲刺持续时间（毫秒）
                "distance": 150,  # 冲刺距离（像素）
                "timer": 0
            },
            "double_damage": {
                "name": "double_damage",
                "energy_cost": 20,
                "cooldown": 20000,  # 20秒冷却
                "last_used": 0,
                "active": False,
                "duration": 5000,  # 5秒持续时间
                "damage_multiplier": 2.0,  # 伤害倍数
                "timer": 0
            }
        }
        self.active_skill = None
        self.selected_skill = "dash"  # 默认选择dash技能
        self.damage_multiplier = 1.0  # 伤害倍数，用于double_damage技能

        self.last_damage_time = 0  # 上次受伤时间
        self.armor_recovery_cooldown = 3000  # 护甲恢复冷却时间（毫秒）
        self.armor_recovery_rate = 1.0  # 护甲恢复速度（每秒）
        self.last_armor_recovery_time = 0  # 上次护甲恢复时间
        self.armor_recovery_interval = 1000  # 护甲恢复间隔（毫秒）

    # update player
    def update(self, keys, current_time, mouse_pos=None):
        move_x = 0.0
        move_y = 0.0
        dt = 0.016  # 假设60FPS，每帧约16ms

        # 处理技能
        if keys[pygame.K_f] and self.active_skill is None:
            self.activate_skill(self.selected_skill, current_time)

        # 更新当前技能
        if self.active_skill:
            skill = self.skills[self.active_skill]
            if skill["active"]:
                skill["timer"] -= 16  # 假设16ms一帧
                if skill["timer"] <= 0:
                    skill["active"] = False
                    self.active_skill = None
                    if skill["name"] == "double_damage":
                        self.damage_multiplier = 1.0  # 重置伤害倍数

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
            self.world_x = max(self.tile_size, min(new_x, self.screen_width - self.tile_size))
            self.world_y = max(self.tile_size, min(new_y, self.screen_height - self.tile_size))

        # 使用鼠标位置计算射击方向
        if mouse_pos:
            dx = mouse_pos[0] - self.screen_width // 2
            dy = mouse_pos[1] - self.screen_height // 2
            self.angle = math.degrees(math.atan2(-dy, dx))
            length = math.sqrt(dx ** 2 + dy ** 2)
            if length > 0:
                self.last_direction = [dx / length, dy / length]
        elif move_x != 0 or move_y != 0:
            self.angle = math.degrees(math.atan2(-self.direction[1], self.direction[0]))

        # 更新图像旋转
        self.image = pygame.transform.rotate(self.image_original, self.angle)
        self.rect = self.image.get_rect(center=(self.screen_width // 2, self.screen_height // 2))

        # rect keep center
        self.rect.center = (self.screen_width // 2, self.screen_height // 2)

        # 护甲恢复逻辑
        if current_time - self.last_damage_time >= self.armor_recovery_cooldown and self.armor < self.max_armor:
            if current_time - self.last_armor_recovery_time >= self.armor_recovery_interval:
                self.armor = min(self.max_armor, self.armor + 1)  # 每秒恢复1点护甲
                self.last_armor_recovery_time = current_time
                print(f"Armor recovered to {int(self.armor)}")
        
        return True

    def activate_skill(self, skill_name, current_time):
        if skill_name not in self.skills:
            return False
        
        skill = self.skills[skill_name]
        if current_time - skill["last_used"] < skill["cooldown"]:
            message_system.add_message("Skill is cooling down!")
            return False
        
        if not self.use_energy(skill["energy_cost"]):
            return False
        
        skill["last_used"] = current_time
        skill["active"] = True
        skill["timer"] = skill["duration"]
        self.active_skill = skill_name
        
        # 执行技能效果
        if skill_name == "dash":
            # 使用最后的方向进行冲刺
            self.world_x += self.last_direction[0] * skill["distance"]
            self.world_y += self.last_direction[1] * skill["distance"]
            message_system.add_message("Dash!")
        elif skill_name == "double_damage":
            self.damage_multiplier = skill["damage_multiplier"]
            message_system.add_message("Double Damage activated!")
        
        return True

    # draw player
    def draw(self, win):
        win.blit(self.image, self.rect)
    # add batteries
    def add_batteries(self, amount):
        space_left = self.backpack_capacity - self.backpack_used
        added = min(amount, space_left)
        self.backpack['batteries'] = self.backpack.get('batteries', 0) + added
        self.backpack_used += added
        return added  # Returns the actual amount of batteries added
    # remove batteries
    def remove_batteries(self, amount):
        current_batteries = self.backpack.get('batteries', 0)
        removed = min(amount, current_batteries)
        self.backpack['batteries'] -= removed
        self.backpack_used -= removed
        return removed  # Returns the actual amount of batteries removed
    
    # take damage
    def take_damage(self, amount):
        """处理玩家受伤"""
        print(f"Player taking damage: {amount}, current HP: {self.hp}, current Armor: {self.armor}")
        self.last_damage_time = pygame.time.get_ticks()  # 更新最后受伤时间
        
        # 先减少护甲
        if self.armor > 0:
            armor_damage = min(amount, self.armor)
            self.armor -= armor_damage
            amount -= armor_damage
            print(f"Armor reduced by {armor_damage}, remaining: {self.armor}")

        # 如果还有剩余伤害，减少HP
        if amount > 0:
            self.hp = max(0, self.hp - amount)
            print(f"HP reduced by {amount}, remaining: {self.hp}")
            
        # 返回玩家是否存活
        is_alive = self.hp > 0
        print(f"Player alive status: {is_alive}")
        return is_alive
    
    # use energy
    def use_energy(self, amount):
        # check if enough energy
        if self.energy >= amount:
            self.energy -= amount
            return True
        message_system.add_message("Not enough energy!")
        return False

    # recover energy
    def recover_energy(self, amount):
        self.energy = min(self.max_energy, self.energy + amount)

    # add experience
    def add_experience(self, amount):
        """添加经验值"""
        self.current_level_experience += amount
        print(f"获得 {amount} 点经验值，当前关卡经验：{self.current_level_experience}")

    def save_experience(self):
        """保存当前关卡获得的经验值"""
        self.experience += self.current_level_experience
        print(f"保存 {self.current_level_experience} 点经验值，总经验：{self.experience}")
        self.current_level_experience = 0

    def lose_experience(self):
        """失去当前关卡获得的经验值"""
        print(f"失去 {self.current_level_experience} 点经验值")
        self.current_level_experience = 0
