# world_beta.py
import pygame
import os

class WorldBeta:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = 32
        
        # 关卡尺寸（每个关卡都是屏幕的3倍）
        self.level_width = screen_width * 3
        self.level_height = screen_height * 3
        
        # 走廊尺寸
        self.corridor_width = 200  # 走廊宽度
        self.corridor_height = screen_height * 3  # 走廊高度
        
        # 关卡位置（沿X轴排列）
        self.levels = {
            "level1": {
                "x": 0,
                "y": 0,
                "width": self.level_width,
                "height": self.level_height,
                "background": "background_1",
                "is_boss": False
            },
            "level2": {
                "x": self.level_width + self.corridor_width,
                "y": 0,
                "width": self.level_width,
                "height": self.level_height,
                "background": "background_2",
                "is_boss": True
            },
            "level3": {
                "x": (self.level_width + self.corridor_width) * 2,
                "y": 0,
                "width": self.level_width,
                "height": self.level_height,
                "background": "background_3",
                "is_boss": False
            },
            "level4": {
                "x": (self.level_width + self.corridor_width) * 3,
                "y": 0,
                "width": self.level_width,
                "height": self.level_height,
                "background": "background_4",
                "is_boss": True
            }
        }
        
        # 走廊位置
        self.corridors = {
            "corridor1": {
                "x": self.level_width,
                "y": 0,
                "width": self.corridor_width,
                "height": self.corridor_height,
                "background": "corridor"
            },
            "corridor2": {
                "x": self.level_width * 2 + self.corridor_width,
                "y": 0,
                "width": self.corridor_width,
                "height": self.corridor_height,
                "background": "corridor"
            },
            "corridor3": {
                "x": self.level_width * 3 + self.corridor_width * 2,
                "y": 0,
                "width": self.corridor_width,
                "height": self.corridor_height,
                "background": "corridor"
            }
        }
        
        # 世界总尺寸
        self.total_width = self.level_width * 4 + self.corridor_width * 3
        self.total_height = self.level_height
        
        # 关卡之间的传送点
        self.teleport_points = {
            "level1_to_corridor1": {
                "x": self.level_width - 50,
                "y": self.level_height // 2,
                "target": "corridor1",
                "target_x": 50,
                "target_y": self.corridor_height // 2
            },
            "corridor1_to_level1": {
                "x": 50,
                "y": self.corridor_height // 2,
                "target": "level1",
                "target_x": self.level_width - 50,
                "target_y": self.level_height // 2
            },
            "corridor1_to_level2": {
                "x": self.corridor_width - 50,
                "y": self.corridor_height // 2,
                "target": "level2",
                "target_x": 50,
                "target_y": self.level_height // 2
            },
            "level2_to_corridor1": {
                "x": 50,
                "y": self.level_height // 2,
                "target": "corridor1",
                "target_x": self.corridor_width - 50,
                "target_y": self.corridor_height // 2
            },
            "level2_to_corridor2": {
                "x": self.level_width - 50,
                "y": self.level_height // 2,
                "target": "corridor2",
                "target_x": 50,
                "target_y": self.corridor_height // 2
            },
            "corridor2_to_level2": {
                "x": 50,
                "y": self.corridor_height // 2,
                "target": "level2",
                "target_x": self.level_width - 50,
                "target_y": self.level_height // 2
            },
            "corridor2_to_level3": {
                "x": self.corridor_width - 50,
                "y": self.corridor_height // 2,
                "target": "level3",
                "target_x": 50,
                "target_y": self.level_height // 2
            },
            "level3_to_corridor2": {
                "x": 50,
                "y": self.level_height // 2,
                "target": "corridor2",
                "target_x": self.corridor_width - 50,
                "target_y": self.corridor_height // 2
            },
            "level3_to_corridor3": {
                "x": self.level_width - 50,
                "y": self.level_height // 2,
                "target": "corridor3",
                "target_x": 50,
                "target_y": self.corridor_height // 2
            },
            "corridor3_to_level3": {
                "x": 50,
                "y": self.corridor_height // 2,
                "target": "level3",
                "target_x": self.level_width - 50,
                "target_y": self.level_height // 2
            },
            "corridor3_to_level4": {
                "x": self.corridor_width - 50,
                "y": self.corridor_height // 2,
                "target": "level4",
                "target_x": 50,
                "target_y": self.level_height // 2
            },
            "level4_to_corridor3": {
                "x": 50,
                "y": self.level_height // 2,
                "target": "corridor3",
                "target_x": self.corridor_width - 50,
                "target_y": self.corridor_height // 2
            }
        }
    
    def get_level(self, level_name):
        """获取指定关卡的信息"""
        return self.levels.get(level_name)
    
    def get_corridor(self, corridor_name):
        """获取指定走廊的信息"""
        return self.corridors.get(corridor_name)
    
    def get_teleport_point(self, point_name):
        """获取指定传送点的信息"""
        return self.teleport_points.get(point_name)
    
    def check_teleport(self, player_x, player_y):
        """检查玩家是否在传送点附近"""
        for point_name, point in self.teleport_points.items():
            distance = ((player_x - point["x"]) ** 2 + (player_y - point["y"]) ** 2) ** 0.5
            if distance < 50:  # 传送触发距离
                return point
        return None
    
    def get_current_area(self, player_x, player_y):
        """获取玩家当前所在的区域（关卡或走廊）"""
        for level_name, level in self.levels.items():
            if (level["x"] <= player_x <= level["x"] + level["width"] and
                level["y"] <= player_y <= level["y"] + level["height"]):
                return level_name
        for corridor_name, corridor in self.corridors.items():
            if (corridor["x"] <= player_x <= corridor["x"] + corridor["width"] and
                corridor["y"] <= player_y <= corridor["y"] + corridor["height"]):
                return corridor_name
        return None 