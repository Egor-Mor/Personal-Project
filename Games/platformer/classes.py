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

    def move(self, keys, tiles):
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
                    
                    if self.vel_x > 0:  # Moving right
                        self.x = tile.x - self.width
                    elif self.vel_x < 0:  # Moving left
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
                    
                    if self.vel_y > 0:  # Falling down
                        self.y = tile.y - self.height
                        self.vel_y = 0
                        self.on_ground = True
                    elif self.vel_y < 0:  # Jumping up
                        self.y = tile.y + tile.height
                        self.vel_y = 0
                    
                    self.sprite.update_position(self.x, self.y)

    def render(self, window, camera_x, camera_y):
        self.sprite.display(window, camera_x, camera_y)


class Tile:
    def __init__(self, tile_type, x, y):
        self.type = tile_type
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.solid = True
        
        if tile_type == "1":  # Ground/Dirt
            self.sprite = Sprite("img/ground.png", x, y)
        elif tile_type == "2":  # Grass
            self.sprite = Sprite("img/grass.png", x, y)
        elif tile_type == "3":  # Stone
            self.sprite = Sprite("img/stone.png", x, y)
        elif tile_type == "4":  # Platform (one-way)
            self.sprite = Sprite("img/platform.png", x, y)
            self.solid = True
        elif tile_type == "5":  # Spike/Hazard
            self.sprite = Sprite("img/spike.png", x, y)
            self.solid = False
        else:
            self.sprite = None
            self.solid = False

    def render(self, window, camera_x, camera_y):
        if self.sprite:
            self.sprite.display(window, camera_x, camera_y)


class Map:
    def __init__(self, map_file):
        self.tiles = []
        self.width = 0
        self.height = 0
        self.player_spawn_x = 64
        self.player_spawn_y = 64
        self.load_map(map_file)

    def load_map(self, map_file):
        try:
            with open(map_file, 'r') as f:
                lines = f.readlines()
                self.height = len(lines)
                
                for y, line in enumerate(lines):
                    line = line.strip()
                    if len(line) > self.width:
                        self.width = len(line)
                    
                    for x, char in enumerate(line):
                        if char == 'P':  # Player spawn point
                            self.player_spawn_x = x * 32
                            self.player_spawn_y = y * 32
                        elif char != '0' and char != ' ':  # Not empty space
                            tile = Tile(char, x * 32, y * 32)
                            self.tiles.append(tile)
        except FileNotFoundError:
            print(f"Map file {map_file} not found!")
            self.create_default_map()

    def create_default_map(self):
        # Create a simple default map if file not found
        for x in range(25):
            self.tiles.append(Tile("1", x * 32, 15 * 32))

    def render(self, window, camera_x, camera_y):
        for tile in self.tiles:
            # Only render tiles that are visible on screen
            if (tile.x - camera_x > -32 and tile.x - camera_x < 800 and
                tile.y - camera_y > -32 and tile.y - camera_y < 600):
                tile.render(window, camera_x, camera_y)


class Camera:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height

    def update(self, player, map_width, map_height):
        # Center camera on player
        self.x = player.x - self.width // 2 + player.width // 2
        self.y = player.y - self.height // 2 + player.height // 2

        # Keep camera within map bounds
        if self.x < 0:
            self.x = 0
        if self.y < 0:
            self.y = 0
        if self.x > map_width * 32 - self.width:
            self.x = map_width * 32 - self.width
        if self.y > map_height * 32 - self.height:
            self.y = map_height * 32 - self.height