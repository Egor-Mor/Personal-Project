import pygame
import random
import math

# Game settings
FPS = 60
clock = pygame.time.Clock()

# Game states
STATE_WAITING = "waiting"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"

# Colors (black and white)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (128, 128, 128)

# Game constants
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 80
PADDLE_SPEED = 8
BALL_SIZE = 10
BALL_SPEED = 5
WIN_SCORE = 5


class Paddle:
    def __init__(self, x, y, width=PADDLE_WIDTH, height=PADDLE_HEIGHT):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel_y = 0
        self.score = 0

    def update(self, game_height, ui_height):
        self.y += self.vel_y
        # Keep paddle on screen (accounting for UI offset)
        min_y = ui_height
        max_y = ui_height + game_height - self.height
        if self.y < min_y:
            self.y = min_y
        elif self.y > max_y:
            self.y = max_y

    def render(self, window):
        paddle_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(window, COLOR_WHITE, paddle_rect)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Ball:
    def __init__(self, x, y, size=BALL_SIZE):
        self.x = x
        self.y = y
        self.size = size
        self.vel_x = BALL_SPEED
        self.vel_y = BALL_SPEED
        self.horizontal_speed = BALL_SPEED  # Track horizontal speed separately
        self.reset_velocity()

    def reset_velocity(self, reset_speed=True):
        if reset_speed:
            self.horizontal_speed = BALL_SPEED
        # Randomize initial direction
        direction = random.choice([-1, 1])
        angle = random.uniform(-math.pi / 4, math.pi / 4)
        self.vel_x = direction * self.horizontal_speed * math.cos(angle)
        self.vel_y = self.horizontal_speed * math.sin(angle)

    def increase_horizontal_speed(self, factor=1.1):
        """Increase horizontal speed by a factor - this accumulates with each hit"""
        self.horizontal_speed *= factor

    def update(self, screen_width, game_height, ui_height, paddle_left, paddle_right):
        self.x += self.vel_x
        self.y += self.vel_y

        # Bounce off top and bottom walls (accounting for UI offset)
        if self.y <= ui_height or self.y + self.size >= ui_height + game_height:
            self.vel_y = -self.vel_y
            # Ensure ball doesn't go outside bounds
            if self.y < ui_height:
                self.y = ui_height
            elif self.y + self.size > ui_height + game_height:
                self.y = ui_height + game_height - self.size

        # Check collision with paddles
        ball_rect = self.get_rect()
        left_paddle_rect = paddle_left.get_rect()
        right_paddle_rect = paddle_right.get_rect()

        if ball_rect.colliderect(left_paddle_rect):
            if self.vel_x < 0:  # Moving left
                # Increase horizontal speed on paddle hit - this accumulates with each hit
                self.increase_horizontal_speed(1.1)  # Increase by 10%
                # Calculate bounce angle based on where ball hits paddle
                hit_pos = (self.y + self.size / 2) - (paddle_left.y + paddle_left.height / 2)
                normalized_hit = hit_pos / (paddle_left.height / 2)
                # Clamp normalized_hit to avoid extreme angles
                normalized_hit = max(-1, min(1, normalized_hit))
                angle = normalized_hit * math.pi / 3  # Max 60 degrees
                # Apply bounce with increased horizontal speed (use the accumulated horizontal speed)
                self.vel_x = self.horizontal_speed * math.cos(angle)
                self.vel_y = self.horizontal_speed * math.sin(angle)

        if ball_rect.colliderect(right_paddle_rect):
            if self.vel_x > 0:  # Moving right
                # Increase horizontal speed on paddle hit - this accumulates with each hit
                self.increase_horizontal_speed(1.1)  # Increase by 10%
                # Calculate bounce angle based on where ball hits paddle
                hit_pos = (self.y + self.size / 2) - (paddle_right.y + paddle_right.height / 2)
                normalized_hit = hit_pos / (paddle_right.height / 2)
                # Clamp normalized_hit to avoid extreme angles
                normalized_hit = max(-1, min(1, normalized_hit))
                angle = normalized_hit * math.pi / 3  # Max 60 degrees
                # Apply bounce with increased horizontal speed (use the accumulated horizontal speed)
                self.vel_x = -self.horizontal_speed * math.cos(angle)
                self.vel_y = self.horizontal_speed * math.sin(angle)

        # Check if ball goes out of bounds (score point)
        if self.x < 0:
            return "right_score"  # Right player scores
        elif self.x > screen_width:
            return "left_score"  # Left player scores
        
        return None

    def reset(self, screen_width, game_height, ui_height, reset_speed=True):
        self.x = screen_width // 2 - self.size // 2
        self.y = ui_height + game_height // 2 - self.size // 2
        self.reset_velocity(reset_speed=reset_speed)

    def render(self, window):
        ball_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        pygame.draw.rect(window, COLOR_WHITE, ball_rect)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def render(self, window):
        color = COLOR_WHITE if self.is_hovered else COLOR_GRAY
        pygame.draw.rect(window, color, self.rect)
        pygame.draw.rect(window, COLOR_WHITE, self.rect, 2)

        font = pygame.font.Font(None, 36)
        text_surf = font.render(self.text, True, COLOR_BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        window.blit(text_surf, text_rect)


class Game:
    def __init__(self):
        self.screen_width = 800
        self.screen_height = 600
        self.ui_height = 60
        self.game_height = self.screen_height - self.ui_height
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), 0, 32)
        pygame.display.set_caption("Pong - 2 Player")
        
        self.state = STATE_WAITING
        
        # Create paddles (accounting for UI offset)
        paddle_margin = 20
        self.paddle_left = Paddle(paddle_margin, self.ui_height + self.game_height // 2 - PADDLE_HEIGHT // 2)
        self.paddle_right = Paddle(self.screen_width - paddle_margin - PADDLE_WIDTH, 
                                   self.ui_height + self.game_height // 2 - PADDLE_HEIGHT // 2)
        
        # Create ball (accounting for UI offset)
        self.ball = Ball(self.screen_width // 2 - BALL_SIZE // 2, 
                        self.ui_height + self.game_height // 2 - BALL_SIZE // 2)
        
        # Reset everything
        self.reset_game()

    def reset_game(self):
        self.paddle_left.score = 0
        self.paddle_right.score = 0
        self.paddle_left.y = self.ui_height + self.game_height // 2 - PADDLE_HEIGHT // 2
        self.paddle_right.y = self.ui_height + self.game_height // 2 - PADDLE_HEIGHT // 2
        self.ball.reset(self.screen_width, self.game_height, self.ui_height, reset_speed=True)
        self.state = STATE_WAITING

    def start_game(self):
        self.ball.reset(self.screen_width, self.game_height, self.ui_height, reset_speed=True)
        self.state = STATE_PLAYING

    def render_ui(self):
        # UI Panel at top
        ui_panel = pygame.Rect(0, 0, self.screen_width, self.ui_height)
        pygame.draw.rect(self.screen, COLOR_BLACK, ui_panel)
        pygame.draw.line(self.screen, COLOR_WHITE, (0, self.ui_height), 
                        (self.screen_width, self.ui_height), 2)

        font = pygame.font.Font(None, 36)
        
        # Left player score
        left_score_text = font.render(f"Player 1: {self.paddle_left.score}", True, COLOR_WHITE)
        self.screen.blit(left_score_text, (20, 15))
        
        # Right player score
        right_score_text = font.render(f"Player 2: {self.paddle_right.score}", True, COLOR_WHITE)
        right_score_x = self.screen_width - right_score_text.get_width() - 20
        self.screen.blit(right_score_text, (right_score_x, 15))
        
        # Controls info
        controls_font = pygame.font.Font(None, 24)
        controls_text = controls_font.render("P1: W/S  P2: Arrow Keys", True, COLOR_GRAY)
        controls_x = self.screen_width // 2 - controls_text.get_width() // 2
        self.screen.blit(controls_text, (controls_x, 20))
        
        # Start button (only show when waiting)
        if self.state == STATE_WAITING:
            start_btn = Button(self.screen_width // 2 - 50, 10, 100, 40, "START")
            start_btn.check_hover(pygame.mouse.get_pos())
            start_btn.render(self.screen)
            return start_btn
        
        return None

    def render_playing(self):
        # Black background
        self.screen.fill(COLOR_BLACK)
        
        # Draw center line (dashed)
        dash_length = 20
        gap_length = 10
        y = self.ui_height
        while y < self.screen_height:
            pygame.draw.line(self.screen, COLOR_GRAY, 
                           (self.screen_width // 2, y), 
                           (self.screen_width // 2, min(y + dash_length, self.screen_height)), 1)
            y += dash_length + gap_length
        
        # Render paddles
        self.paddle_left.render(self.screen)
        self.paddle_right.render(self.screen)
        
        # Render ball
        self.ball.render(self.screen)
        
        # Render UI
        self.render_ui()

    def render_waiting(self):
        self.render_playing()  # Show game field
        self.render_ui()  # UI with start button

    def render_game_over(self):
        # Draw game in background
        self.render_playing()
        
        # Game Over overlay
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(200)
        overlay.fill(COLOR_BLACK)
        self.screen.blit(overlay, (0, 0))

        # Determine winner
        if self.paddle_left.score >= WIN_SCORE:
            winner = "Player 1 Wins!"
        else:
            winner = "Player 2 Wins!"

        font_title = pygame.font.Font(None, 72)
        title = font_title.render(winner, True, COLOR_WHITE)
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(title, title_rect)

        font_score = pygame.font.Font(None, 48)
        score_text = font_score.render(
            f"{self.paddle_left.score} - {self.paddle_right.score}", 
            True, COLOR_WHITE)
        score_rect = score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(score_text, score_rect)

        # Restart button
        btn_width = 200
        btn_height = 50
        btn_x = self.screen_width // 2 - btn_width // 2

        restart_btn = Button(btn_x, self.screen_height // 2 + 60, btn_width, btn_height, "RESTART")
        restart_btn.check_hover(pygame.mouse.get_pos())
        restart_btn.render(self.screen)

        return restart_btn

    def handle_input(self, keys):
        if self.state == STATE_PLAYING:
            # Player 1 controls (W/S or Up/Down arrow)
            if keys[pygame.K_w]:
                self.paddle_left.vel_y = -PADDLE_SPEED
            elif keys[pygame.K_s]:
                self.paddle_left.vel_y = PADDLE_SPEED
            else:
                self.paddle_left.vel_y = 0

            # Player 2 controls (Arrow keys)
            if keys[pygame.K_UP]:
                self.paddle_right.vel_y = -PADDLE_SPEED
            elif keys[pygame.K_DOWN]:
                self.paddle_right.vel_y = PADDLE_SPEED
            else:
                self.paddle_right.vel_y = 0

    async def run(self):
        import asyncio
        running = True

        while running:
            clock.tick(FPS)
            await asyncio.sleep(0)  # Yield control to event loop for pygbag

            keys = pygame.key.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    if self.state == STATE_WAITING and event.key == pygame.K_SPACE:
                        self.start_game()
                    elif self.state == STATE_PLAYING and event.key == pygame.K_SPACE:
                        # Pause/Unpause
                        self.state = STATE_PAUSED if self.state == STATE_PLAYING else STATE_PLAYING
                    elif self.state == STATE_PAUSED and event.key == pygame.K_SPACE:
                        self.state = STATE_PLAYING
                    elif self.state == STATE_GAME_OVER and event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.start_game()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if self.state == STATE_WAITING:
                        start_btn = self.render_ui()
                        if start_btn and start_btn.check_click(mouse_pos):
                            self.start_game()

                    elif self.state == STATE_GAME_OVER:
                        restart_btn = self.render_game_over()
                        if restart_btn and restart_btn.check_click(mouse_pos):
                            self.reset_game()
                            self.start_game()

            # Game logic
            if self.state == STATE_PLAYING:
                # Handle input
                self.handle_input(keys)
                
                # Update paddles
                self.paddle_left.update(self.game_height, self.ui_height)
                self.paddle_right.update(self.game_height, self.ui_height)
                
                # Update ball and check for scoring (speed increase happens in ball.update() on paddle hits)
                score_result = self.ball.update(self.screen_width, self.game_height, self.ui_height,
                                              self.paddle_left, self.paddle_right)
                
                if score_result == "left_score":
                    self.paddle_left.score += 1
                    if self.paddle_left.score >= WIN_SCORE:
                        self.state = STATE_GAME_OVER
                    else:
                        self.ball.reset(self.screen_width, self.game_height, self.ui_height, reset_speed=True)
                
                elif score_result == "right_score":
                    self.paddle_right.score += 1
                    if self.paddle_right.score >= WIN_SCORE:
                        self.state = STATE_GAME_OVER
                    else:
                        self.ball.reset(self.screen_width, self.game_height, self.ui_height, reset_speed=True)

            # Rendering
            if self.state == STATE_WAITING:
                self.render_waiting()
            elif self.state == STATE_PLAYING or self.state == STATE_PAUSED:
                self.render_playing()
                if self.state == STATE_PAUSED:
                    # Draw pause overlay
                    font = pygame.font.Font(None, 72)
                    pause_text = font.render("PAUSED", True, COLOR_WHITE)
                    pause_rect = pause_text.get_rect(center=(self.screen_width // 2, 
                                                            self.screen_height // 2))
                    self.screen.blit(pause_text, pause_rect)
            elif self.state == STATE_GAME_OVER:
                self.render_game_over()

            pygame.display.update()

