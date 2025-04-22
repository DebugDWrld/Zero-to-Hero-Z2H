# menu.py
import pygame
import starthall
from render import message_system

# BatteryMenu class
class BatteryMenu:
    # Initialize the BatteryMenu
    def __init__(self, screen_width, screen_height):
        self.active = False
        self.menu_state = None
        self.slider_dragging = False
        self.slider_pos = 0
        self.max_amount = 0
        self.menu_rect = pygame.Rect(screen_width // 4, screen_height // 4, screen_width // 2, screen_height // 2)
        self.deposit_button = pygame.Rect(screen_width // 2 - 100, screen_height // 4 + 50, 200, 50)
        self.withdraw_button = pygame.Rect(screen_width // 2 - 100, screen_height // 4 + 110, 200, 50)
        self.exit_button = pygame.Rect(screen_width // 2 - 100, screen_height // 4 + 170, 200, 50)
        self.slider_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 20, 200, 20)
        self.knob_size = 20
        self.menu_font = pygame.font.Font(None, 48)
        self.hint_font = pygame.font.Font(None, 36)

    # Handle events
    def handle_event(self, event, player, start_hall):
        # Check if the menu is active
        if self.active:
            # Handle mouse button down
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                # Handle buttons
                if self.menu_state is None:
                    # Deposit
                    if self.deposit_button.collidepoint(mouse_pos) and player.backpack.get('batteries', 0) > 0:
                        self.menu_state = "deposit"
                        self.max_amount = player.backpack.get('batteries', 0)
                        self.slider_pos = 0
                        return True
                    # Withdraw
                    elif self.withdraw_button.collidepoint(mouse_pos) and start_hall.battery_storage > 0:
                        self.menu_state = "withdraw"
                        self.max_amount = min(start_hall.battery_storage, player.backpack_capacity - player.backpack_used)
                        self.slider_pos = 0
                        return True
                    # Exit
                    elif self.exit_button.collidepoint(mouse_pos):
                        self.active = False
                        return True
                # Handle slider dragging
                elif self.menu_state in ["deposit", "withdraw"]:
                    if self.slider_rect.collidepoint(mouse_pos):
                        self.slider_dragging = True
                        return True
                    
            # Handle mouse button up
            elif event.type == pygame.MOUSEBUTTONUP and self.slider_dragging:
                # Stop dragging
                self.slider_dragging = False
                # Calculate the amount
                amount = int((self.slider_pos / 200) * self.max_amount)
                # Deposit
                if self.menu_state == "deposit":
                    removed = player.remove_batteries(amount)
                    deposited = start_hall.deposit_battery(removed)
                    message_system.add_message(f"{deposited} batteries deposited")
                # Withdraw
                elif self.menu_state == "withdraw":
                    withdrawn = start_hall.withdraw_battery(amount)
                    added = player.add_batteries(withdrawn)
                    message_system.add_message(f"{added} batteries removed")
                self.menu_state = None
                return True
            
            # Handle mouse motion
            elif event.type == pygame.MOUSEMOTION and self.slider_dragging:
                mouse_x = event.pos[0]
                self.slider_pos = max(0, min(mouse_x - self.slider_rect.x, 200))
                return True
            
            # Handle keyboard E key's input
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                self.active = False
                self.menu_state = None
                self.slider_dragging = False
                return True
        return False

    # Draw the menu
    def draw(self, win, start_hall):
        # Check if the menu is active
        if not self.active:
            return
        # Draw the menu
        pygame.draw.rect(win, (50, 50, 50, 200), self.menu_rect)

        # 显示仓库内的电池数量
        storage_text = self.menu_font.render(f"Storage: {start_hall.battery_storage}/{start_hall.battery_limit}", True, (255, 255, 255))
        win.blit(storage_text, storage_text.get_rect(center=(self.menu_rect.centerx, self.menu_rect.y + 20)))

        # Add exit hint
        exit_hint = self.hint_font.render("Press E to exit", True, (200, 200, 200))
        win.blit(exit_hint, exit_hint.get_rect(center=(self.menu_rect.centerx, self.menu_rect.bottom - 30)))

        # Draw the buttons and slider
        if self.menu_state is None:
            pygame.draw.rect(win, (0, 200, 0), self.deposit_button)
            pygame.draw.rect(win, (200, 0, 0), self.withdraw_button)
            deposit_text = self.menu_font.render("Deposit", True, (255, 255, 255))
            withdraw_text = self.menu_font.render("Withdraw", True, (255, 255, 255))
            win.blit(deposit_text, deposit_text.get_rect(center=self.deposit_button.center))
            win.blit(withdraw_text, withdraw_text.get_rect(center=self.withdraw_button.center))
        # Draw the slider and amount
        elif self.menu_state in ["deposit", "withdraw"]:
            pygame.draw.rect(win, (100, 100, 100), self.slider_rect)
            knob_x = self.slider_rect.x + self.slider_pos
            knob_rect = pygame.Rect(knob_x - self.knob_size // 2, self.slider_rect.y - 5, self.knob_size, self.knob_size + 10)
            pygame.draw.rect(win, (255, 255, 0), knob_rect)
            amount = int((self.slider_pos / 200) * self.max_amount)
            amount_text = self.menu_font.render(f"Amount: {amount}", True, (255, 255, 255))
            win.blit(amount_text, amount_text.get_rect(center=(self.menu_rect.centerx, self.menu_rect.centery + 40)))

# PropertyTreeMenu class
class PropertyTreeMenu:
    # Initialize the PropertyTreeMenu
    def __init__(self, screen_width, screen_height):
        self.active = False
        self.menu_rect = pygame.Rect(screen_width // 4, screen_height // 4, screen_width // 2, screen_height // 2)
        self.exit_button = pygame.Rect(screen_width // 2 - 100, screen_height // 4 + 170, 200, 50)
        self.menu_font = pygame.font.Font(None, 48)
        self.hint_font = pygame.font.Font(None, 36)
        
        # 技能按钮
        button_width = 200
        button_height = 50
        button_spacing = 60
        start_y = screen_height // 4 + 50
        
        self.skill_buttons = {
            "dash": pygame.Rect(screen_width // 2 - button_width // 2, start_y, button_width, button_height),
            "double_damage": pygame.Rect(screen_width // 2 - button_width // 2, start_y + button_spacing, button_width, button_height),
            "skill3": pygame.Rect(screen_width // 2 - button_width // 2, start_y + button_spacing * 2, button_width, button_height),
            "skill4": pygame.Rect(screen_width // 2 - button_width // 2, start_y + button_spacing * 3, button_width, button_height)
        }
        
        self.selected_skill = None
        self.skill_locked = {
            "dash": False,
            "double_damage": True,
            "skill3": True,
            "skill4": True
        }

    # Handle events
    def handle_event(self, event, player):
        if self.active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                self.active = False
                return True
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for skill_name, button in self.skill_buttons.items():
                    if button.collidepoint(mouse_pos):
                        if not self.skill_locked[skill_name]:
                            self.selected_skill = skill_name
                            player.selected_skill = skill_name
                            message_system.add_message(f"Selected skill: {skill_name}")
                            return True
                        else:
                            message_system.add_message("This skill is locked!")
                            return True
        return False

    # Draw the menu
    def draw(self, win):
        if not self.active:
            return
        
        # Draw the menu background
        pygame.draw.rect(win, (50, 50, 50, 200), self.menu_rect)

        # Draw the title
        title_text = self.menu_font.render("Skill Selection", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.menu_rect.centerx, self.menu_rect.y + 30))
        win.blit(title_text, title_rect)

        # Draw skill buttons
        for skill_name, button in self.skill_buttons.items():
            # 根据技能是否锁定设置按钮颜色
            if self.skill_locked[skill_name]:
                button_color = (100, 100, 100)  # 灰色表示锁定
            else:
                button_color = (0, 200, 0) if self.selected_skill == skill_name else (200, 200, 200)
            
            pygame.draw.rect(win, button_color, button)
            
            # 显示技能名称
            skill_text = self.menu_font.render(skill_name.replace("_", " ").title(), True, (255, 255, 255))
            win.blit(skill_text, skill_text.get_rect(center=button.center))
            
            # 如果技能锁定，显示"Locked"
            if self.skill_locked[skill_name]:
                locked_text = self.hint_font.render("Locked", True, (255, 0, 0))
                win.blit(locked_text, (button.right + 10, button.centery - 10))

        # Add exit hint
        exit_hint = self.hint_font.render("Press E to exit", True, (200, 200, 200))
        win.blit(exit_hint, exit_hint.get_rect(center=(self.menu_rect.centerx, self.menu_rect.bottom - 30)))