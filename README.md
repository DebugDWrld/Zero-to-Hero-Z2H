# Z2H: Zero to Hero

这是一个基于Pygame的2D游戏，玩家在游戏中控制一个角色，射击子弹，管理电池库存，并与环境中的物体进行交互。

## 功能特性

- **玩家移动和射击**：使用键盘（WASD或方向键）移动，鼠标左键射击。
- **能量管理**：射击和特殊动作消耗能量，能量随时间恢复。
- **电池管理**：收集电池并通过菜单与电池存储交互，进行存取操作。
- **游戏场景**：包含起始大厅和主关卡，玩家可通过与门交互进入主关卡。
- **HUD显示**：屏幕上显示玩家的电池库存、生命值、护甲和能量。

## 安装指南

1. 确保安装了Python 3.x（推荐版本）。
2. 安装Pygame：
   ```bash
   pip install pygame

## 使用说明
- **开始游戏**：
1. 运行main.py文件。
2. 确保输入法为US keyboard。

- **玩家操控**：
1. 点击鼠标左键进行攻击和破坏。
2. 使用W、A、S、D键操控角色移动。
3. 使用F键释放技能。
4. 使用E键进行交互。
5. 使用Escape（Esc）键退出游戏。

- **画面显示**：
1. 左上角显示玩家背包内的实时电池数量。
2. 右上角显示玩家实时的生命值、护甲值和能量属性。

- **游戏机制**：
1. 玩家受到伤害时，优先扣除护甲值；当护甲值为0时，扣除生命值。
2. 玩家的攻击、破坏和释放技能均会消耗能量：攻击、破坏每次4点；释放技能每次16点。
3. 能量会自动恢复，每秒恢复2点。
4. 玩家背包上限为64。
5. 电池机制：电池可以从关卡内的宝箱中获得，用于延缓大门关闭时间。
