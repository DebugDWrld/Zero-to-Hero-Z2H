# menu.py
import pygame

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
                    if self.deposit_button.collidepoint(mouse_pos) and player.battery_inventory > 0:
                        self.menu_state = "deposit"
                        self.max_amount = player.battery_inventory
                        self.slider_pos = 0
                        return True
                    # Withdraw
                    elif self.withdraw_button.collidepoint(mouse_pos) and start_hall.battery_storage > 0:
                        self.menu_state = "withdraw"
                        self.max_amount = min(start_hall.battery_storage, player.battery_capacity - player.battery_inventory)
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
                    print(f"Deposited {deposited} batteries. Storage: {start_hall.battery_storage}, Inventory: {player.battery_inventory}")

                # Withdraw
                elif self.menu_state == "withdraw":
                    withdrawn = start_hall.withdraw_battery(amount)
                    added = player.add_batteries(withdrawn)
                    print(f"Withdrew {added} batteries. Storage: {start_hall.battery_storage}, Inventory: {player.battery_inventory}")
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
                print("Menu closed")
                return True
        return False

    # Draw the menu
    def draw(self, win):
        # Check if the menu is active
        if not self.active:
            return
        # Draw the menu
        pygame.draw.rect(win, (50, 50, 50, 200), self.menu_rect)
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