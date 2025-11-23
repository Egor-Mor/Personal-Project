import pygame
import random

# Game settings
FPS = 10
clock = pygame.time.Clock()

# Game states
STATE_PLAYING = "playing"
STATE_GAME_OVER = "game_over"
STATE_WAITING = "waiting"

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_PURPLE = (128, 0, 128)
COLOR_WHITE = (255, 255, 255)

# Direction constants
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)


class Tile:
    def __init__(self, value=None, x=0, y=0):
        self.value = value  # None=empty, "W"=wall, "S"=snake, "A"=apple
        self.x = x
        self.y = y
        self.size = 32

    def render(self, window):
        rect = pygame.Rect(self.x * self.size, self.y * self.size, self.size, self.size)
        
        if self.value == "W":  # Wall
            pygame.draw.rect(window, COLOR_PURPLE, rect)
        elif self.value == "S":  # Snake
            pygame.draw.rect(window, COLOR_GREEN, rect)
        elif self.value == "A":  # Apple
            pygame.draw.rect(window, COLOR_RED, rect)
        else:  # Empty
            pygame.draw.rect(window, COLOR_BLACK, rect)
        
        # Draw grid lines
        pygame.draw.rect(window, (50, 50, 50), rect, 1)

    def change(self, value):
        self.value = value


class Field:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.field = []
        self.snake = []  # List of (x, y) positions
        self.direction = DIR_RIGHT
        self.next_direction = DIR_RIGHT
        self.apple_pos = None
        self.alive = True
        self.score = 0
        self.grow_next_move = False
        self.initialize_field()

    def initialize_field(self):
        # Create field with walls on borders
        self.field = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    tile = Tile("W", x, y)
                else:
                    tile = Tile(None, x, y)
                row.append(tile)
            self.field.append(row)

    def reset(self):
        self.initialize_field()
        # Initialize snake in the center
        center_x = self.width // 2
        center_y = self.height // 2
        self.snake = [(center_x, center_y), (center_x - 1, center_y), (center_x - 2, center_y)]
        self.direction = DIR_RIGHT
        self.next_direction = DIR_RIGHT
        self.alive = True
        self.score = 0
        self.grow_next_move = False
        
        # Update field with snake
        for x, y in self.snake:
            if 0 < x < self.width - 1 and 0 < y < self.height - 1:
                self.field[y][x].change("S")
        
        # Spawn apple
        self.spawn_apple()

    def spawn_apple(self):
        """Spawn apple at a random empty position"""
        empty_positions = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.field[y][x].value is None:
                    empty_positions.append((x, y))
        
        if empty_positions:
            self.apple_pos = random.choice(empty_positions)
            self.field[self.apple_pos[1]][self.apple_pos[0]].change("A")
            return True
        return False

    def change_direction(self, new_direction):
        """Change direction if valid (can't reverse into itself)"""
        # Prevent reversing direction
        if (new_direction[0] * -1, new_direction[1] * -1) == self.direction:
            return
        
        self.next_direction = new_direction

    def move(self):
        """Move the snake one step"""
        if not self.alive:
            return

        # Update direction
        self.direction = self.next_direction

        # Calculate new head position
        head_x, head_y = self.snake[0]
        new_head_x = head_x + self.direction[0]
        new_head_y = head_y + self.direction[1]

        # Check collision with walls
        if (new_head_x <= 0 or new_head_x >= self.width - 1 or
            new_head_y <= 0 or new_head_y >= self.height - 1):
            self.alive = False
            return

        # Check collision with self
        if (new_head_x, new_head_y) in self.snake:
            self.alive = False
            return

        # Add new head
        self.snake.insert(0, (new_head_x, new_head_y))
        self.field[new_head_y][new_head_x].change("S")

        # Check if apple is eaten
        if self.apple_pos and (new_head_x, new_head_y) == self.apple_pos:
            # Apple eaten - snake grows (don't remove tail)
            self.score += 10
            self.apple_pos = None
            self.field[new_head_y][new_head_x].change("S")
            self.spawn_apple()
        else:
            # No apple eaten - remove tail to maintain length
            tail_x, tail_y = self.snake.pop()
            if 0 < tail_x < self.width - 1 and 0 < tail_y < self.height - 1:
                self.field[tail_y][tail_x].change(None)

    def render(self, window, y_offset=0):
        for row in self.field:
            for tile in row:
                # Adjust y position for offset
                tile_copy = Tile(tile.value, tile.x, tile.y)
                tile_copy.y = tile.y + (y_offset // 32)
                tile_copy.render(window)


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        self.is_hovered = False

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def render(self, window):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(window, color, self.rect)
        pygame.draw.rect(window, COLOR_WHITE, self.rect, 3)

        font = pygame.font.Font(None, 36)
        text_surf = font.render(self.text, True, COLOR_WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        window.blit(text_surf, text_rect)


class Game:
    def __init__(self):
        self.state = STATE_WAITING
        self.field = Field(20, 20)
        self.screen = None
        self.high_score = 0
        self.ui_height = 60
        self.start_game_screen()

    def start_game_screen(self):
        # Create game screen with UI area at top
        screen_width = self.field.width * 32
        screen_height = self.field.height * 32 + self.ui_height
        self.screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)
        pygame.display.set_caption("Snake Game")
        self.field.reset()
        self.state = STATE_WAITING

    def start_game(self):
        self.field.reset()
        self.state = STATE_PLAYING

    def render_waiting(self):
        # Draw game field in background
        self.screen.fill(COLOR_BLACK)
        
        # Create a surface for the game area
        game_surface = pygame.Surface((self.field.width * 32, self.field.height * 32))
        game_surface.fill(COLOR_BLACK)
        
        # Render field to surface
        for row in self.field.field:
            for tile in row:
                rect = pygame.Rect(tile.x * 32, tile.y * 32, 32, 32)
                if tile.value == "W":
                    pygame.draw.rect(game_surface, COLOR_PURPLE, rect)
                elif tile.value == "S":
                    pygame.draw.rect(game_surface, COLOR_GREEN, rect)
                elif tile.value == "A":
                    pygame.draw.rect(game_surface, COLOR_RED, rect)
                else:
                    pygame.draw.rect(game_surface, COLOR_BLACK, rect)
                pygame.draw.rect(game_surface, (50, 50, 50), rect, 1)
        
        # Blit game surface with offset
        self.screen.blit(game_surface, (0, self.ui_height))
        
        # Render UI at top
        self.render_ui()

    def render_playing(self):
        self.screen.fill(COLOR_BLACK)
        
        # Create a surface for the game area
        game_surface = pygame.Surface((self.field.width * 32, self.field.height * 32))
        game_surface.fill(COLOR_BLACK)
        
        # Render field to surface
        for row in self.field.field:
            for tile in row:
                rect = pygame.Rect(tile.x * 32, tile.y * 32, 32, 32)
                if tile.value == "W":
                    pygame.draw.rect(game_surface, COLOR_PURPLE, rect)
                elif tile.value == "S":
                    pygame.draw.rect(game_surface, COLOR_GREEN, rect)
                elif tile.value == "A":
                    pygame.draw.rect(game_surface, COLOR_RED, rect)
                else:
                    pygame.draw.rect(game_surface, COLOR_BLACK, rect)
                pygame.draw.rect(game_surface, (50, 50, 50), rect, 1)
        
        # Blit game surface with offset
        self.screen.blit(game_surface, (0, self.ui_height))
        
        # Render UI at top
        self.render_ui()

    def render_ui(self):
        # UI Panel at top
        ui_panel = pygame.Rect(0, 0, self.screen.get_width(), self.ui_height)
        pygame.draw.rect(self.screen, (30, 30, 30), ui_panel)
        pygame.draw.line(self.screen, COLOR_PURPLE, (0, self.ui_height), (self.screen.get_width(), self.ui_height), 2)

        font = pygame.font.Font(None, 36)
        
        # Score
        score_text = font.render(f"Score: {self.field.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (10, 15))
        
        # High Score
        high_score_text = font.render(f"High Score: {self.high_score}", True, COLOR_WHITE)
        high_score_x = self.screen.get_width() // 2 - high_score_text.get_width() // 2
        self.screen.blit(high_score_text, (high_score_x, 15))
        
        # Start button (only show when waiting)
        if self.state == STATE_WAITING:
            start_btn = Button(self.screen.get_width() - 120, 10, 100, 40, "START", (70, 180, 70))
            start_btn.check_hover(pygame.mouse.get_pos())
            start_btn.render(self.screen)
            return start_btn
        
        return None

    def render_game_over(self):
        # Draw game field in background
        self.screen.fill(COLOR_BLACK)
        
        # Create a surface for the game area
        game_surface = pygame.Surface((self.field.width * 32, self.field.height * 32))
        game_surface.fill(COLOR_BLACK)
        
        # Render field to surface
        for row in self.field.field:
            for tile in row:
                rect = pygame.Rect(tile.x * 32, tile.y * 32, 32, 32)
                if tile.value == "W":
                    pygame.draw.rect(game_surface, COLOR_PURPLE, rect)
                elif tile.value == "S":
                    pygame.draw.rect(game_surface, COLOR_GREEN, rect)
                elif tile.value == "A":
                    pygame.draw.rect(game_surface, COLOR_RED, rect)
                else:
                    pygame.draw.rect(game_surface, COLOR_BLACK, rect)
                pygame.draw.rect(game_surface, (50, 50, 50), rect, 1)
        
        # Blit game surface with offset
        self.screen.blit(game_surface, (0, self.ui_height))
        
        # Render UI at top
        self.render_ui()

        # Game Over overlay
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(180)
        overlay.fill(COLOR_BLACK)
        self.screen.blit(overlay, (0, 0))

        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()

        font_title = pygame.font.Font(None, 72)
        title = font_title.render("GAME OVER", True, COLOR_RED)
        title_rect = title.get_rect(center=(screen_w // 2, screen_h // 2 - 50))
        self.screen.blit(title, title_rect)

        font_score = pygame.font.Font(None, 48)
        score_text = font_score.render(f"Final Score: {self.field.score}", True, COLOR_WHITE)
        score_rect = score_text.get_rect(center=(screen_w // 2, screen_h // 2))
        self.screen.blit(score_text, score_rect)

        # Restart button
        btn_width = 200
        btn_height = 50
        btn_x = screen_w // 2 - btn_width // 2

        restart_btn = Button(btn_x, screen_h // 2 + 60, btn_width, btn_height, "RESTART", (70, 130, 180))
        restart_btn.check_hover(pygame.mouse.get_pos())
        restart_btn.render(self.screen)

        return restart_btn

    async def run(self):
        import asyncio
        running = True
        move_timer = 0
        move_interval = FPS  # Move every FPS frames (so 1 move per second at 10 FPS)

        while running:
            clock.tick(60)  # Run at 60 FPS for smooth input
            await asyncio.sleep(0)  # Yield control to event loop for pygbag
            move_timer += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    return

                if event.type == pygame.KEYDOWN:
                    if self.state == STATE_PLAYING:
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.field.change_direction(DIR_UP)
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.field.change_direction(DIR_DOWN)
                        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            self.field.change_direction(DIR_LEFT)
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            self.field.change_direction(DIR_RIGHT)
                        elif event.key == pygame.K_SPACE:
                            # Restart game
                            self.field.reset()
                            self.state = STATE_PLAYING
                    elif self.state == STATE_GAME_OVER:
                        if event.key == pygame.K_SPACE:
                            # Restart game
                            self.field.reset()
                            self.state = STATE_PLAYING

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if self.state == STATE_WAITING:
                        start_btn = self.render_ui()
                        if start_btn and start_btn.check_click(mouse_pos):
                            self.start_game()

                    elif self.state == STATE_GAME_OVER:
                        restart_btn = self.render_game_over()
                        if restart_btn and restart_btn.check_click(mouse_pos):
                            self.start_game()

            # Game logic
            if self.state == STATE_PLAYING:
                # Move snake at slower rate
                if move_timer >= move_interval:
                    move_timer = 0
                    self.field.move()
                    
                    if not self.field.alive:
                        # Update high score
                        if self.field.score > self.high_score:
                            self.high_score = self.field.score
                        self.state = STATE_GAME_OVER

            # Rendering
            if self.state == STATE_WAITING:
                self.render_waiting()
            elif self.state == STATE_PLAYING:
                self.render_playing()
            elif self.state == STATE_GAME_OVER:
                self.render_game_over()

            pygame.display.update()
