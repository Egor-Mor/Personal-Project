import pygame


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
            if (tile.x - camera_x > -32 and tile.x - camera_x < window.get_width() and
                    tile.y - camera_y > -32 and tile.y - camera_y < window.get_height()):
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