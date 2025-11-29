import pygame
import random

# Game settings
FPS = 20
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
COLOR_CYAN = (0, 255, 255)      # I piece
COLOR_YELLOW = (255, 255, 0)    # O piece
COLOR_PURPLE = (128, 0, 128)    # T piece
COLOR_GREEN = (0, 255, 0)       # S piece
COLOR_RED = (255, 0, 0)         # Z piece
COLOR_BLUE = (0, 0, 255)        # J piece
COLOR_ORANGE = (255, 165, 0)    # L piece

# Game constants
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 30
BOARD_X_OFFSET = 50
BOARD_Y_OFFSET = 80
FALL_SPEED_INITIAL = 30  # frames per cell drop
SCORE_PER_LINE = 100
SCORE_PER_TETRIS = 400  # 4 lines at once

# Tetromino shapes (4x4 grid representation)
TETROMINOES = {
    'I': [
        ['....', '####', '....', '....'],
        ['...#', '...#', '...#', '...#']
    ],
    'O': [
        ['##', '##']
    ],
    'T': [
        ['.#.', '###', '...'],
        ['.#.', '.##', '.#.'],
        ['...', '###', '.#.'],
        ['.#.', '##.', '.#.']
    ],
    'S': [
        ['.##', '##.', '...'],
        ['.#.', '.##', '..#']
    ],
    'Z': [
        ['##.', '.##', '...'],
        ['..#', '.##', '.#.']
    ],
    'J': [
        ['#..', '###', '...'],
        ['.##', '.#.', '.#.'],
        ['...', '###', '..#'],
        ['.#.', '.#.', '##.']
    ],
    'L': [
        ['..#', '###', '...'],
        ['.#.', '.#.', '.##'],
        ['...', '###', '#..'],
        ['##.', '.#.', '.#.']
    ]
}

# Color mapping
TETROMINO_COLORS = {
    'I': COLOR_CYAN,
    'O': COLOR_YELLOW,
    'T': COLOR_PURPLE,
    'S': COLOR_GREEN,
    'Z': COLOR_RED,
    'J': COLOR_BLUE,
    'L': COLOR_ORANGE
}


class Tetromino:
    def __init__(self, shape_type):
        self.shape_type = shape_type
        self.rotations = TETROMINOES[shape_type]
        self.rotation_index = 0
        self.x = BOARD_WIDTH // 2 - 1
        self.y = 0
        self.color = TETROMINO_COLORS[shape_type]

    def get_shape(self):
        """Get current rotation of the tetromino"""
        return self.rotations[self.rotation_index]

    def rotate(self):
        """Rotate to next rotation"""
        self.rotation_index = (self.rotation_index + 1) % len(self.rotations)

    def get_rotated_shape(self):
        """Get next rotation (for collision checking)"""
        next_index = (self.rotation_index + 1) % len(self.rotations)
        return self.rotations[next_index]

    def get_cells(self):
        """Get list of (x, y) cell positions occupied by this tetromino"""
        shape = self.get_shape()
        cells = []
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell == '#':
                    cells.append((self.x + col_idx, self.y + row_idx))
        return cells


class Board:
    def __init__(self):
        self.width = BOARD_WIDTH
        self.height = BOARD_HEIGHT
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]

    def is_valid_position(self, tetromino):
        """Check if tetromino is in a valid position"""
        cells = tetromino.get_cells()
        for x, y in cells:
            # Check boundaries
            if x < 0 or x >= self.width or y >= self.height:
                return False
            # Check collision with placed pieces
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def place_tetromino(self, tetromino):
        """Place tetromino on the board"""
        cells = tetromino.get_cells()
        for x, y in cells:
            if y >= 0:  # Only place if on board
                self.grid[y][x] = tetromino.color

    def clear_lines(self):
        """Clear full lines and return number of lines cleared"""
        lines_cleared = 0
        y = self.height - 1
        while y >= 0:
            if all(cell is not None for cell in self.grid[y]):
                # Line is full, remove it
                del self.grid[y]
                # Add empty line at top
                self.grid.insert(0, [None for _ in range(self.width)])
                lines_cleared += 1
            else:
                y -= 1
        return lines_cleared

    def is_game_over(self):
        """Check if game is over (top row has blocks)"""
        return any(cell is not None for cell in self.grid[0])

    def render(self, window, x_offset, y_offset):
        """Render the board"""
        # Draw grid
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(
                    x_offset + x * CELL_SIZE,
                    y_offset + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                # Draw cell
                if self.grid[y][x] is not None:
                    pygame.draw.rect(window, self.grid[y][x], rect)
                else:
                    pygame.draw.rect(window, COLOR_BLACK, rect)
                # Draw border
                pygame.draw.rect(window, COLOR_GRAY, rect, 1)

        # Draw board border
        board_rect = pygame.Rect(
            x_offset,
            y_offset,
            self.width * CELL_SIZE,
            self.height * CELL_SIZE
        )
        pygame.draw.rect(window, COLOR_WHITE, board_rect, 3)


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
        self.screen_width = BOARD_WIDTH * CELL_SIZE + 300
        self.screen_height = BOARD_HEIGHT * CELL_SIZE + 100
        self.ui_height = 60
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), 0, 32)
        pygame.display.set_caption("Tetris")
        
        self.state = STATE_WAITING
        self.board = Board()
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_timer = 0
        self.fall_speed = FALL_SPEED_INITIAL
        
        self.reset_game()

    def reset_game(self):
        self.board = Board()
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_timer = 0
        self.fall_speed = FALL_SPEED_INITIAL
        self.current_piece = None
        self.next_piece = None
        self.state = STATE_WAITING

    def spawn_piece(self):
        """Spawn a new tetromino"""
        if self.next_piece is None:
            shape_type = random.choice(list(TETROMINOES.keys()))
            self.current_piece = Tetromino(shape_type)
            shape_type = random.choice(list(TETROMINOES.keys()))
            self.next_piece = Tetromino(shape_type)
        else:
            self.current_piece = self.next_piece
            self.current_piece.x = BOARD_WIDTH // 2 - 1
            self.current_piece.y = 0
            self.current_piece.rotation_index = 0
            shape_type = random.choice(list(TETROMINOES.keys()))
            self.next_piece = Tetromino(shape_type)

    def start_game(self):
        self.reset_game()
        self.spawn_piece()
        self.state = STATE_PLAYING

    def move_piece(self, dx, dy):
        """Try to move current piece"""
        if self.current_piece is None:
            return False
        
        self.current_piece.x += dx
        self.current_piece.y += dy
        
        if not self.board.is_valid_position(self.current_piece):
            # Undo move
            self.current_piece.x -= dx
            self.current_piece.y -= dy
            return False
        return True

    def rotate_piece(self):
        """Try to rotate current piece"""
        if self.current_piece is None:
            return False
        
        self.current_piece.rotate()
        if not self.board.is_valid_position(self.current_piece):
            # Undo rotation
            self.current_piece.rotation_index = (self.current_piece.rotation_index - 1) % len(self.current_piece.rotations)
            return False
        return True

    def drop_piece(self):
        """Drop piece one cell down, return True if it landed"""
        if not self.move_piece(0, 1):
            # Piece landed
            self.board.place_tetromino(self.current_piece)
            lines = self.board.clear_lines()
            if lines > 0:
                self.lines_cleared += lines
                # Score calculation
                if lines == 4:
                    self.score += SCORE_PER_TETRIS * self.level
                else:
                    self.score += SCORE_PER_LINE * lines * self.level
                # Level up every 10 lines
                self.level = (self.lines_cleared // 10) + 1
                self.fall_speed = max(5, FALL_SPEED_INITIAL - (self.level - 1) * 2)
            
            # Check game over
            if self.board.is_game_over():
                self.state = STATE_GAME_OVER
            else:
                self.spawn_piece()
            return True
        return False

    def hard_drop(self):
        """Drop piece all the way down"""
        if self.current_piece is None:
            return
        while self.move_piece(0, 1):
            self.score += 2  # Bonus for hard drop
        self.drop_piece()  # Final placement

    def render_ui(self):
        """Render UI panel"""
        ui_panel = pygame.Rect(0, 0, self.screen_width, self.ui_height)
        pygame.draw.rect(self.screen, COLOR_BLACK, ui_panel)
        pygame.draw.line(self.screen, COLOR_WHITE, (0, self.ui_height),
                        (self.screen_width, self.ui_height), 2)

        font = pygame.font.Font(None, 36)
        
        # Score
        score_text = font.render(f"Score: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (10, 15))
        
        # Lines
        lines_text = font.render(f"Lines: {self.lines_cleared}", True, COLOR_WHITE)
        self.screen.blit(lines_text, (200, 15))
        
        # Level
        level_text = font.render(f"Level: {self.level}", True, COLOR_WHITE)
        self.screen.blit(level_text, (350, 15))
        
        # Start button (only show when waiting)
        if self.state == STATE_WAITING:
            start_btn = Button(self.screen_width - 120, 10, 100, 40, "START")
            start_btn.check_hover(pygame.mouse.get_pos())
            start_btn.render(self.screen)
            return start_btn
        
        return None

    def render_next_piece(self):
        """Render next piece preview"""
        if self.next_piece is None:
            return
        
        preview_x = BOARD_X_OFFSET + BOARD_WIDTH * CELL_SIZE + 20
        preview_y = BOARD_Y_OFFSET
        
        font = pygame.font.Font(None, 24)
        next_text = font.render("Next:", True, COLOR_WHITE)
        self.screen.blit(next_text, (preview_x, preview_y - 25))
        
        shape = self.next_piece.get_shape()
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell == '#':
                    rect = pygame.Rect(
                        preview_x + col_idx * (CELL_SIZE - 5),
                        preview_y + row_idx * (CELL_SIZE - 5),
                        CELL_SIZE - 8,
                        CELL_SIZE - 8
                    )
                    pygame.draw.rect(self.screen, self.next_piece.color, rect)
                    pygame.draw.rect(self.screen, COLOR_WHITE, rect, 1)

    def render_current_piece(self):
        """Render current falling piece"""
        if self.current_piece is None:
            return
        
        shape = self.current_piece.get_shape()
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell == '#':
                    x = BOARD_X_OFFSET + (self.current_piece.x + col_idx) * CELL_SIZE
                    y = BOARD_Y_OFFSET + (self.current_piece.y + row_idx) * CELL_SIZE
                    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, self.current_piece.color, rect)
                    pygame.draw.rect(self.screen, COLOR_WHITE, rect, 2)

    def render_playing(self):
        """Render game during play"""
        self.screen.fill(COLOR_BLACK)
        
        # Render board
        self.board.render(self.screen, BOARD_X_OFFSET, BOARD_Y_OFFSET)
        
        # Render current piece
        self.render_current_piece()
        
        # Render next piece
        self.render_next_piece()
        
        # Render controls hint
        hint_font = pygame.font.Font(None, 20)
        controls = [
            "A/D or Left/Right: Move",
            "W or Up: Rotate",
            "S or Down: Soft Drop",
            "Space: Hard Drop",
            "P: Pause"
        ]
        hint_y = BOARD_Y_OFFSET + BOARD_HEIGHT * CELL_SIZE + 20
        for i, control in enumerate(controls):
            hint_text = hint_font.render(control, True, COLOR_GRAY)
            self.screen.blit(hint_text, (BOARD_X_OFFSET, hint_y + i * 20))
        
        # Render UI
        self.render_ui()

    def render_waiting(self):
        """Render waiting screen"""
        self.render_playing()
        self.render_ui()

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
        title = font_title.render("GAME OVER", True, COLOR_RED)
        title_rect = title.get_rect(center=(screen_w // 2, screen_h // 2 - 50))
        self.screen.blit(title, title_rect)

        font_score = pygame.font.Font(None, 48)
        score_text = font_score.render(f"Final Score: {self.score}", True, COLOR_WHITE)
        score_rect = score_text.get_rect(center=(screen_w // 2, screen_h // 2))
        self.screen.blit(score_text, score_rect)

        lines_text = font_score.render(f"Lines: {self.lines_cleared}", True, COLOR_WHITE)
        lines_rect = lines_text.get_rect(center=(screen_w // 2, screen_h // 2 + 40))
        self.screen.blit(lines_text, lines_rect)

        # Restart button
        btn_width = 200
        btn_height = 50
        btn_x = screen_w // 2 - btn_width // 2

        restart_btn = Button(btn_x, screen_h // 2 + 100, btn_width, btn_height, "RESTART")
        restart_btn.check_hover(pygame.mouse.get_pos())
        restart_btn.render(self.screen)

        return restart_btn

    def handle_input(self, keys):
        """Handle continuous key presses"""
        if self.state != STATE_PLAYING:
            return
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.move_piece(-1, 0)
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.move_piece(1, 0)
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            if self.move_piece(0, 1):
                self.score += 1  # Bonus for soft drop

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
                    elif self.state == STATE_PLAYING:
                        if event.key == pygame.K_w or event.key == pygame.K_UP:
                            self.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()
                        elif event.key == pygame.K_p:
                            self.state = STATE_PAUSED if self.state == STATE_PLAYING else STATE_PLAYING
                    elif self.state == STATE_PAUSED:
                        if event.key == pygame.K_p:
                            self.state = STATE_PLAYING
                    elif self.state == STATE_GAME_OVER:
                        if event.key == pygame.K_SPACE:
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
                # Handle continuous input
                self.handle_input(keys)
                
                # Auto drop
                self.fall_timer += 1
                if self.fall_timer >= self.fall_speed:
                    self.fall_timer = 0
                    self.drop_piece()

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

