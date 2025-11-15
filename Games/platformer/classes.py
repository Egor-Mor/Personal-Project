import pygame, os, sys


class Sprite:
    def __init__(self, img_route, x=0, y=0):
        self.image = pygame.image.load(img_route)
        self.x = x
        self.y = y
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def display(self, window, camera_x=0, camera_y=0):
        window.blit(self.image, (self.x - camera_x, self.y - camera_y))

    def update_position(self, x, y):
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class Player:
    def __init__(self, x, y):
        self.sprite = Sprite("img/player.png", x, y)
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.width = 32
        self.height = 32
        self.speed = 5
        self.jump_power = 12
        self.gravity = 0.8
        self.max_fall_speed = 15
        self.alive = True
        self.stars_collected = 0

    def move(self, keys, tiles):
        if not self.alive:
            return

        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed

        # Apply horizontal movement
        self.x += self.vel_x
        self.sprite.update_position(self.x, self.y)
        self.check_collision_x(tiles)

        # Jumping
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = -self.jump_power
            self.on_ground = False

        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > self.max_fall_speed:
            self.vel_y = self.max_fall_speed

        # Apply vertical movement
        self.y += self.vel_y
        self.sprite.update_position(self.x, self.y)
        self.on_ground = False
        self.check_collision_y(tiles)

    def check_collision_x(self, tiles):
        for tile in tiles:
            if tile.solid:
                if (self.x < tile.x + tile.width and
                        self.x + self.width > tile.x and
                        self.y < tile.y + tile.height and
                        self.y + self.height > tile.y):

                    if self.vel_x > 0:
                        self.x = tile.x - self.width
                    elif self.vel_x < 0:
                        self.x = tile.x + tile.width

                    self.sprite.update_position(self.x, self.y)
                    self.vel_x = 0

    def check_collision_y(self, tiles):
        for tile in tiles:
            if tile.solid:
                if (self.x < tile.x + tile.width and
                        self.x + self.width > tile.x and
                        self.y < tile.y + tile.height and
                        self.y + self.height > tile.y):

                    if self.vel_y > 0:
                        self.y = tile.y - self.height
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:
                        self.y = tile.y + tile.height
                        self.vel_y = 0

                    self.sprite.update_position(self.x, self.y)

    def check_death(self, map_height, spikes):
        # Fall out of map
        if self.y > map_height * 32 + 100:
            self.alive = False
            return True

        # Check collision with spikes
        for spike in spikes:
            if (self.x < spike.x + spike.width and
                    self.x + self.width > spike.x and
                    self.y < spike.y + spike.height and
                    self.y + self.height > spike.y):
                self.alive = False
                return True

        return False

    def reset(self, spawn_x, spawn_y):
        self.x = spawn_x
        self.y = spawn_y
        self.vel_x = 0
        self.vel_y = 0
        self.alive = True
        self.stars_collected = 0
        self.sprite.update_position(self.x, self.y)

    def render(self, window, camera_x, camera_y):
        if self.alive:
            self.sprite.display(window, camera_x, camera_y)


class Tile:
    def __init__(self, tile_type, x, y):
        self.type = tile_type
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.solid = True

        if tile_type == "1":
            self.sprite = Sprite("img/ground.png", x, y)
        elif tile_type == "2":
            self.sprite = Sprite("img/grass.png", x, y)
        elif tile_type == "3":
            self.sprite = Sprite("img/stone.png", x, y)
        elif tile_type == "4":
            self.sprite = Sprite("img/platform.png", x, y)
            self.solid = True
        elif tile_type == "5":
            self.sprite = Sprite("img/spike.png", x, y)
            self.solid = False
        elif tile_type == "W":
            self.sprite = Sprite("img/wall.png", x, y)
            self.solid = True
        else:
            self.sprite = None
            self.solid = False

    def render(self, window, camera_x, camera_y):
        if self.sprite:
            self.sprite.display(window, camera_x, camera_y)


class Star:
    def __init__(self, x, y):
        self.sprite = Sprite("img/star.png", x, y)
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.collected = False

    def check_collection(self, player):
        if not self.collected:
            if (player.x < self.x + self.width and
                    player.x + player.width > self.x and
                    player.y < self.y + self.height and
                    player.y + player.height > self.y):
                self.collected = True
                return True
        return False

    def render(self, window, camera_x, camera_y):
        if not self.collected:
            self.sprite.display(window, camera_x, camera_y)


class Map:
    def __init__(self, map_file):
        self.tiles = []
        self.stars = []
        self.spikes = []
        self.width = 0
        self.height = 0
        self.player_spawn_x = 64
        self.player_spawn_y = 64
        self.total_stars = 0
        self.load_map(map_file)

    def load_map(self, map_file):
        try:
            with open(map_file, 'r') as f:
                lines = f.readlines()
                self.height = len(lines)

                for y, line in enumerate(lines):
                    line = line.rstrip('\n')
                    if len(line) > self.width:
                        self.width = len(line)

                    for x, char in enumerate(line):
                        if char == 'P':
                            self.player_spawn_x = x * 32
                            self.player_spawn_y = y * 32
                        elif char == 'S':
                            star = Star(x * 32, y * 32)
                            self.stars.append(star)
                            self.total_stars += 1
                        elif char == '5':
                            tile = Tile(char, x * 32, y * 32)
                            self.spikes.append(tile)
                            self.tiles.append(tile)
                        elif char != '0' and char != ' ':
                            tile = Tile(char, x * 32, y * 32)
                            self.tiles.append(tile)

                # Add walls around the map
                for x in range(-1, self.width + 1):
                    self.tiles.append(Tile("W", x * 32, -32))
                    self.tiles.append(Tile("W", x * 32, self.height * 32))

                for y in range(-1, self.height + 1):
                    self.tiles.append(Tile("W", -32, y * 32))
                    self.tiles.append(Tile("W", self.width * 32, y * 32))

        except FileNotFoundError:
            print(f"Map file {map_file} not found!")
            self.create_default_map()

    def create_default_map(self):
        self.width = 25
        self.height = 16
        for x in range(25):
            self.tiles.append(Tile("1", x * 32, 15 * 32))

        self.stars.append(Star(10 * 32, 10 * 32))
        self.stars.append(Star(15 * 32, 8 * 32))
        self.stars.append(Star(20 * 32, 12 * 32))
        self.total_stars = 3

    def reset_stars(self):
        for star in self.stars:
            star.collected = False

    def check_stars(self, player):
        for star in self.stars:
            if star.check_collection(player):
                player.stars_collected += 1
                return True
        return False

    def render(self, window, camera_x, camera_y):
        for tile in self.tiles:
            if -32 < tile.x - camera_x < window.get_width() and -32 < tile.y - camera_y < window.get_height():
                tile.render(window, camera_x, camera_y)

        for star in self.stars:
            star.render(window, camera_x, camera_y)


class Camera:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height

    def update(self, player, map_width, map_height):
        self.x = player.x - self.width // 2 + player.width // 2
        self.y = player.y - self.height // 2 + player.height // 2

        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0
        if self.x > map_width * 32 - self.width:
            self.x = max(0, map_width * 32 - self.width)
        if self.y > map_height * 32 - self.height:
            self.y = max(0, map_height * 32 - self.height)


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
        pygame.draw.rect(window, (0, 0, 0), self.rect, 3)

        font = pygame.font.Font(None, 36)
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        window.blit(text_surf, text_rect)



# Game settings
FPS = 60
clock = pygame.time.Clock()

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_WIN = "win"
STATE_DEAD = "dead"


def scan_levels():
    levels = []
    if os.path.exists("maps"):
        for file in os.listdir("maps"):
            if file.endswith(".map"):
                levels.append(file)
    if not levels:
        levels = ["level1.map"]
    return sorted(levels)


class Game:
    def __init__(self):
        self.state = STATE_MENU
        self.current_level = 1
        self.available_levels = scan_levels()
        self.screen = None
        self.current_map = None
        self.player = None
        self.camera = None
        self.init_menu()

    def init_menu(self):
        # Create a default menu screen size
        self.screen = pygame.display.set_mode((800, 600), 0, 32)
        pygame.display.set_caption("Platformer - Menu")

    def load_level(self, level_index):
        if level_index < 0 or level_index >= len(self.available_levels):
            level_index = 0

        self.current_level = level_index
        level_name = self.available_levels[level_index]
        self.current_map = Map(f"maps/{level_name}")

        # Resize window based on map size
        screen_width = min(self.current_map.width * 32, 1200)
        screen_height = min(self.current_map.height * 32, 800)
        self.screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)
        pygame.display.set_caption(f"Platformer - {level_name}")

        self.player = Player(self.current_map.player_spawn_x, self.current_map.player_spawn_y)
        self.camera = Camera(screen_width, screen_height)
        self.state = STATE_PLAYING

    def restart_level(self):
        self.player.reset(self.current_map.player_spawn_x, self.current_map.player_spawn_y)
        self.current_map.reset_stars()
        self.state = STATE_PLAYING

    def next_level(self):
        next_level = self.current_level + 1
        if next_level < len(self.available_levels):
            self.load_level(next_level)
        else:
            self.state = STATE_MENU

    def render_menu(self):
        self.screen.fill((50, 50, 80))

        font_title = pygame.font.Font(None, 72)

        title = font_title.render("PLATFORMER", True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 100))
        self.screen.blit(title, title_rect)

        # Level buttons
        y_start = 200
        buttons = []
        for i, level in enumerate(self.available_levels):
            btn = Button(250, y_start + i * 70, 300, 50, level[:-4], (70, 130, 180))
            buttons.append(btn)
            btn.check_hover(pygame.mouse.get_pos())
            btn.render(self.screen)

        return buttons

    def render_playing(self):
        self.screen.fill((135, 206, 235))
        self.current_map.render(self.screen, self.camera.x, self.camera.y)
        self.player.render(self.screen, self.camera.x, self.camera.y)

        # UI - Stars collected
        font = pygame.font.Font(None, 48)
        stars_text = font.render(f"Stars: {self.player.stars_collected}/{self.current_map.total_stars}", True,
                                 (255, 215, 0))
        self.screen.blit(stars_text, (10, 10))

        # Controls hint
        hint_font = pygame.font.Font(None, 24)
        hint = hint_font.render("R-Restart  ESC-Menu", True, (255, 255, 255))
        self.screen.blit(hint, (10, self.screen.get_height() - 30))

    def render_win(self):
        self.screen.fill((50, 150, 50))

        # Calculate responsive font sizes and positions
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()

        title_size = min(72, screen_w // 8)
        text_size = min(36, screen_w // 15)

        font_title = pygame.font.Font(None, title_size)
        font_text = pygame.font.Font(None, text_size)

        title = font_title.render("LEVEL COMPLETE!", True, (255, 255, 255))
        title_rect = title.get_rect(center=(screen_w // 2, screen_h * 0.2))
        self.screen.blit(title, title_rect)

        stars = font_text.render(f"Stars: {self.player.stars_collected}/{self.current_map.total_stars}", True,
                                 (255, 215, 0))
        stars_rect = stars.get_rect(center=(screen_w // 2, screen_h * 0.35))
        self.screen.blit(stars, stars_rect)

        # Buttons - responsive sizing
        btn_width = min(250, screen_w - 100)
        btn_height = min(50, screen_h // 12)
        btn_x = screen_w // 2 - btn_width // 2
        btn_spacing = btn_height + 20

        restart_btn = Button(btn_x, int(screen_h * 0.5), btn_width, btn_height, "RESTART", (70, 130, 180))
        if self.current_level+1 < len(self.available_levels):
            next_btn = Button(btn_x, int(screen_h * 0.5) + btn_spacing, btn_width, btn_height, "NEXT LEVEL", (70, 180, 70))
            menu_btn = Button(btn_x, int(screen_h * 0.5) + btn_spacing * 2, btn_width, btn_height, "MENU", (180, 130, 70))
        else:
            menu_btn = Button(btn_x, int(screen_h * 0.5) + btn_spacing, btn_width, btn_height, "MENU", (180, 130, 70))

        mouse_pos = pygame.mouse.get_pos()
        restart_btn.check_hover(mouse_pos)
        if self.current_level+1 < len(self.available_levels):
            next_btn.check_hover(mouse_pos)
        menu_btn.check_hover(mouse_pos)

        restart_btn.render(self.screen)
        if self.current_level+1 < len(self.available_levels):
            next_btn.render(self.screen)
        menu_btn.render(self.screen)

        if self.current_level+1 < len(self.available_levels):
            return restart_btn, next_btn, menu_btn
        else:
            return restart_btn, menu_btn
    def render_dead(self):
        self.screen.fill((100, 50, 50))

        # Calculate responsive font sizes and positions
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()

        title_size = min(72, screen_w // 8)
        font_title = pygame.font.Font(None, title_size)

        title = font_title.render("YOU DIED!", True, (255, 100, 100))
        title_rect = title.get_rect(center=(screen_w // 2, screen_h * 0.3))
        self.screen.blit(title, title_rect)

        # Buttons - responsive sizing
        btn_width = min(250, screen_w - 100)
        btn_height = min(50, screen_h // 12)
        btn_x = screen_w // 2 - btn_width // 2
        btn_spacing = btn_height + 20

        restart_btn = Button(btn_x, int(screen_h * 0.5), btn_width, btn_height, "RESTART", (70, 130, 180))
        menu_btn = Button(btn_x, int(screen_h * 0.5) + btn_spacing, btn_width, btn_height, "MENU", (180, 130, 70))

        mouse_pos = pygame.mouse.get_pos()
        restart_btn.check_hover(mouse_pos)
        menu_btn.check_hover(mouse_pos)

        restart_btn.render(self.screen)
        menu_btn.render(self.screen)

        return restart_btn, menu_btn

    def run(self):
        running = True
        while running:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.state == STATE_PLAYING:
                        if event.key == pygame.K_r:
                            self.restart_level()
                        elif event.key == pygame.K_ESCAPE:
                            self.state = STATE_MENU
                            self.init_menu()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if self.state == STATE_MENU:
                        buttons = self.render_menu()
                        for i, btn in enumerate(buttons):
                            if btn.check_click(mouse_pos):
                                self.load_level(i)

                    elif self.state == STATE_WIN:
                        if self.current_level + 1 < len(self.available_levels):
                            restart_btn, next_btn, menu_btn = self.render_win()
                        else:
                            restart_btn, menu_btn = self.render_win()

                        if self.current_level + 1 < len(self.available_levels):
                            if restart_btn.check_click(mouse_pos):
                                self.restart_level()

                            elif next_btn.check_click(mouse_pos):
                                self.next_level()

                            elif menu_btn.check_click(mouse_pos):
                                self.state = STATE_MENU
                                self.init_menu()

                        else:

                            if restart_btn.check_click(mouse_pos):
                                self.restart_level()

                            elif menu_btn.check_click(mouse_pos):
                                self.state = STATE_MENU
                                self.init_menu()

                    elif self.state == STATE_DEAD:
                        restart_btn, menu_btn = self.render_dead()
                        if restart_btn.check_click(mouse_pos):
                            self.restart_level()
                        elif menu_btn.check_click(mouse_pos):
                            self.state = STATE_MENU
                            self.init_menu()

            # Game logic
            if self.state == STATE_PLAYING:
                keys = pygame.key.get_pressed()
                self.player.move(keys, self.current_map.tiles)
                self.current_map.check_stars(self.player)
                self.camera.update(self.player, self.current_map.width, self.current_map.height)

                # Check win condition
                if self.player.stars_collected >= self.current_map.total_stars:
                    self.state = STATE_WIN

                # Check death
                if self.player.check_death(self.current_map.height, self.current_map.spikes):
                    self.state = STATE_DEAD

            # Rendering
            if self.state == STATE_MENU:
                self.render_menu()
            elif self.state == STATE_PLAYING:
                self.render_playing()
            elif self.state == STATE_WIN:
                self.render_win()
            elif self.state == STATE_DEAD:
                self.render_dead()

            pygame.display.update()