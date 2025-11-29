import pygame
import time

# Game settings
FPS = 60
clock = pygame.time.Clock()

# Game states
STATE_WAITING = "waiting"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (128, 128, 128)
COLOR_LIGHT_BLUE = (173, 216, 230)  # Light blue background
COLOR_TEXT_TYPED = (255, 255, 255)  # White for typed text

# Game constants
TEXT_MARGIN = 50
LINE_SPACING = 40
FONT_SIZE = 32

# Sample Lorem Ipsum text
LOREM_IPSUM = (
    "Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod "
)


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def render(self, window, font):
        color = COLOR_WHITE if self.is_hovered else COLOR_GRAY
        pygame.draw.rect(window, color, self.rect)
        pygame.draw.rect(window, COLOR_WHITE, self.rect, 2)

        text_surf = font.render(self.text, True, COLOR_BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        window.blit(text_surf, text_rect)


class Game:
    def __init__(self):
        self.screen_width = 1000
        self.screen_height = 700
        self.ui_height = 60
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), 0, 32)
        pygame.display.set_caption("Typing Speed Test")
        
        # Try to use a monospace font, fallback to default
        try:
            self.font = pygame.font.SysFont("courier", FONT_SIZE, bold=True)
        except:
            try:
                self.font = pygame.font.SysFont("monospace", FONT_SIZE, bold=True)
            except:
                self.font = pygame.font.Font(None, FONT_SIZE)
        
        # UI font (smaller)
        try:
            self.ui_font = pygame.font.SysFont("courier", 24, bold=True)
        except:
            try:
                self.ui_font = pygame.font.SysFont("monospace", 24, bold=True)
            except:
                self.ui_font = pygame.font.Font(None, 24)
        
        self.state = STATE_WAITING
        self.text = LOREM_IPSUM
        self.typed_chars = 0
        self.start_time = None
        self.elapsed_time = 0.0
        self.paused_time = 0.0
        self.pause_start = None
        self.current_speed = 0
        self.previous_speed = 0
        self.fastest_speed = 0
        
        self.reset_game()

    def reset_game(self):
        self.text = LOREM_IPSUM
        self.typed_chars = 0
        self.start_time = None
        self.elapsed_time = 0.0
        self.paused_time = 0.0
        self.pause_start = None
        self.current_speed = 0
        self.state = STATE_WAITING

    def start_game(self):
        self.reset_game()
        self.start_time = time.time()
        self.state = STATE_PLAYING

    def calculate_speed(self):
        """Calculate typing speed in words per minute"""
        if self.elapsed_time <= 0:
            return 0
        
        # Average word length is 5 characters, so words = chars / 5
        words = self.typed_chars / 5.0
        minutes = self.elapsed_time / 60.0
        if minutes > 0:
            return int(words / minutes)
        return 0

    def update_time(self):
        """Update elapsed time (only when playing)"""
        if self.state == STATE_PLAYING and self.start_time is not None:
            current_time = time.time()
            if self.pause_start is None:
                # Not paused, calculate normally
                self.elapsed_time = current_time - self.start_time - self.paused_time
            else:
                # Currently paused, don't update
                pass

    def pause_game(self):
        if self.state == STATE_PLAYING:
            self.pause_start = time.time()
            self.state = STATE_PAUSED
        elif self.state == STATE_PAUSED:
            # Resume
            if self.pause_start is not None:
                self.paused_time += time.time() - self.pause_start
                self.pause_start = None
            self.state = STATE_PLAYING

    def stop_game(self):
        """Stop the game and show results"""
        if self.state == STATE_PLAYING or self.state == STATE_PAUSED:
            # Calculate final speed
            self.current_speed = self.calculate_speed()
            if self.current_speed > self.fastest_speed:
                self.fastest_speed = self.current_speed
            self.state = STATE_GAME_OVER

    def handle_typing(self, char):
        """Handle character input"""
        if self.state != STATE_PLAYING:
            return
        
        if self.typed_chars < len(self.text):
            expected_char = self.text[self.typed_chars]
            if char == expected_char:
                self.typed_chars += 1
                
                # Check if completed
                if self.typed_chars >= len(self.text):
                    self.current_speed = self.calculate_speed()
                    if self.current_speed > self.fastest_speed:
                        self.fastest_speed = self.current_speed
                    self.state = STATE_GAME_OVER

    def render_ui(self):
        """Render UI panel"""
        ui_panel = pygame.Rect(0, 0, self.screen_width, self.ui_height)
        pygame.draw.rect(self.screen, COLOR_BLACK, ui_panel)
        pygame.draw.line(self.screen, COLOR_WHITE, (0, self.ui_height),
                        (self.screen_width, self.ui_height), 2)

        # Time display
        time_str = f"Time: {self.elapsed_time:.1f}s"
        time_text = self.ui_font.render(time_str, True, COLOR_WHITE)
        self.screen.blit(time_text, (10, 15))
        
        # Speed display (only when playing or game over)
        if self.state == STATE_PLAYING:
            speed = self.calculate_speed()
            speed_str = f"Speed: {speed} WPM"
            speed_text = self.ui_font.render(speed_str, True, COLOR_WHITE)
            self.screen.blit(speed_text, (200, 15))
        elif self.state == STATE_GAME_OVER:
            speed_str = f"Speed: {self.current_speed} WPM"
            speed_text = self.ui_font.render(speed_str, True, COLOR_WHITE)
            self.screen.blit(speed_text, (200, 15))
        
        # Fastest speed
        fastest_str = f"Fastest: {self.fastest_speed} WPM"
        fastest_text = self.ui_font.render(fastest_str, True, COLOR_WHITE)
        self.screen.blit(fastest_text, (400, 15))
        
        # Buttons
        buttons = []
        
        # Start button (only show when waiting)
        if self.state == STATE_WAITING:
            start_btn = Button(self.screen_width - 120, 10, 100, 40, "START")
            start_btn.check_hover(pygame.mouse.get_pos())
            start_btn.render(self.screen, self.ui_font)
            buttons.append(start_btn)
        
        # Pause/Resume and Stop buttons (show when playing or paused)
        elif self.state == STATE_PLAYING or self.state == STATE_PAUSED:
            btn_text = "PAUSE" if self.state == STATE_PLAYING else "RESUME"
            # Stop button (on the left)
            stop_btn = Button(self.screen_width - 240, 10, 100, 40, "STOP")
            stop_btn.check_hover(pygame.mouse.get_pos())
            stop_btn.render(self.screen, self.ui_font)
            buttons.append(stop_btn)
            
            # Pause/Resume button (on the right)
            pause_btn = Button(self.screen_width - 120, 10, 100, 40, btn_text)
            pause_btn.check_hover(pygame.mouse.get_pos())
            pause_btn.render(self.screen, self.ui_font)
            buttons.append(pause_btn)
        
        return buttons if buttons else None

    def render_text(self):
        """Render the text with typed parts in white and untyped parts semi-transparent"""
        y_offset = self.ui_height + TEXT_MARGIN
        x_offset = TEXT_MARGIN
        max_width = self.screen_width - 2 * TEXT_MARGIN
        
        # Build lines by wrapping text
        lines = []
        current_line = ""
        current_line_width = 0
        
        i = 0
        while i < len(self.text):
            char = self.text[i]
            char_width = self.font.size(char)[0]
            
            # Check if adding this char would exceed width
            if current_line_width + char_width > max_width and current_line:
                lines.append(current_line)
                current_line = ""
                current_line_width = 0
                # Don't increment i, try this char again on new line
                continue
            
            current_line += char
            current_line_width += char_width
            i += 1
        
        if current_line:
            lines.append(current_line)
        
        # Render each line character by character
        char_index = 0
        for line in lines:
            line_y = y_offset
            x_pos = x_offset
            
            for char in line:
                if char_index < self.typed_chars:
                    # Typed character - white
                    char_surf = self.font.render(char, True, COLOR_TEXT_TYPED)
                else:
                    # Untyped character - semi-transparent gray
                    char_surf = self.font.render(char, True, (100, 100, 100))
                    char_surf.set_alpha(180)
                
                self.screen.blit(char_surf, (x_pos, line_y))
                
                # Get character width for positioning
                char_width = self.font.size(char)[0]
                x_pos += char_width
                char_index += 1
            
            y_offset += LINE_SPACING

    def render_playing(self):
        """Render game during play"""
        self.screen.fill(COLOR_LIGHT_BLUE)
        
        # Render text
        self.render_text()
        
        # Render UI
        self.render_ui()

    def render_waiting(self):
        """Render waiting screen"""
        self.screen.fill(COLOR_LIGHT_BLUE)
        
        # Render text preview (all semi-transparent)
        self.render_text()
        
        # Render instructions
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Typing Speed Test", True, COLOR_BLACK)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, self.ui_height + 30))
        self.screen.blit(title_text, title_rect)
        
        hint_font = pygame.font.Font(None, 24)
        hint_text = hint_font.render("Type the text above. Press SPACE to start.", True, COLOR_BLACK)
        hint_rect = hint_text.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        self.screen.blit(hint_text, hint_rect)
        
        # Render UI
        self.render_ui()

    def render_paused(self):
        """Render paused screen"""
        self.render_playing()
        
        # Pause overlay
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(150)
        overlay.fill(COLOR_BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause_font = pygame.font.Font(None, 72)
        pause_text = pause_font.render("PAUSED", True, COLOR_WHITE)
        pause_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(pause_text, pause_rect)
        
        hint_font = pygame.font.Font(None, 24)
        hint_text = hint_font.render("Click RESUME button to continue", True, COLOR_WHITE)
        hint_rect = hint_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
        self.screen.blit(hint_text, hint_rect)

    def render_game_over(self):
        """Render game over screen"""
        # Draw game in background
        self.render_playing()
        
        # Game Over overlay
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(200)
        overlay.fill(COLOR_BLACK)
        self.screen.blit(overlay, (0, 0))

        screen_w = self.screen_width
        screen_h = self.screen_height

        font_title = pygame.font.Font(None, 72)
        title = font_title.render("COMPLETE!", True, COLOR_WHITE)
        title_rect = title.get_rect(center=(screen_w // 2, screen_h // 2 - 150))
        self.screen.blit(title, title_rect)

        # Speed information
        font_score = pygame.font.Font(None, 48)
        
        current_text = font_score.render(f"Current Speed: {self.current_speed} WPM", True, COLOR_WHITE)
        current_rect = current_text.get_rect(center=(screen_w // 2, screen_h // 2 - 80))
        self.screen.blit(current_text, current_rect)
        
        if self.previous_speed > 0:
            previous_text = font_score.render(f"Previous Speed: {self.previous_speed} WPM", True, COLOR_WHITE)
            previous_rect = previous_text.get_rect(center=(screen_w // 2, screen_h // 2 - 30))
            self.screen.blit(previous_text, previous_rect)
        
        fastest_text = font_score.render(f"Fastest Speed: {self.fastest_speed} WPM", True, COLOR_WHITE)
        fastest_rect = fastest_text.get_rect(center=(screen_w // 2, screen_h // 2 + 20))
        self.screen.blit(fastest_text, fastest_rect)
        
        time_text = font_score.render(f"Time: {self.elapsed_time:.1f}s", True, COLOR_WHITE)
        time_rect = time_text.get_rect(center=(screen_w // 2, screen_h // 2 + 70))
        self.screen.blit(time_text, time_rect)

        # Restart button
        btn_width = 200
        btn_height = 50
        btn_x = screen_w // 2 - btn_width // 2

        restart_btn = Button(btn_x, screen_h // 2 + 130, btn_width, btn_height, "RESTART")
        restart_btn.check_hover(pygame.mouse.get_pos())
        restart_btn.render(self.screen, self.ui_font)

        return restart_btn

    async def run(self):
        import asyncio
        running = True

        while running:
            clock.tick(FPS)
            await asyncio.sleep(0)  # Yield control to event loop for pygbag

            # Update time
            self.update_time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    if self.state == STATE_WAITING and event.key == pygame.K_SPACE:
                        self.start_game()
                    elif self.state == STATE_PLAYING:
                        if event.unicode:
                            # Handle character input
                            self.handle_typing(event.unicode)
                    elif self.state == STATE_GAME_OVER:
                        if event.key == pygame.K_SPACE:
                            self.previous_speed = self.current_speed
                            self.reset_game()
                            self.start_game()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if self.state == STATE_WAITING:
                        buttons = self.render_ui()
                        if buttons:
                            for btn in buttons:
                                if btn.check_click(mouse_pos):
                                    self.start_game()
                                    break

                    elif self.state == STATE_PLAYING or self.state == STATE_PAUSED:
                        buttons = self.render_ui()
                        if buttons:
                            for btn in buttons:
                                if btn.check_click(mouse_pos):
                                    if btn.text == "STOP":
                                        self.stop_game()
                                    elif btn.text == "PAUSE" or btn.text == "RESUME":
                                        self.pause_game()
                                    break

                    elif self.state == STATE_GAME_OVER:
                        restart_btn = self.render_game_over()
                        if restart_btn and restart_btn.check_click(mouse_pos):
                            self.previous_speed = self.current_speed
                            self.reset_game()
                            self.start_game()

            # Rendering
            if self.state == STATE_WAITING:
                self.render_waiting()
            elif self.state == STATE_PLAYING:
                self.render_playing()
            elif self.state == STATE_PAUSED:
                self.render_paused()
            elif self.state == STATE_GAME_OVER:
                self.render_game_over()

            pygame.display.update()

