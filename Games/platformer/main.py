from classes import Player, Map, Camera
import pygame
import sys

pygame.init()

# Game settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

clock = pygame.time.Clock()
pygame.display.set_caption("Platformer Game")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Load map
current_map = Map("maps/level1.map")

# Create player at spawn point
player = Player(current_map.player_spawn_x, current_map.player_spawn_y)

# Create camera
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

# Game loop
running = True
while running:
    clock.tick(FPS)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        
        # Press R to restart level
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                player.x = current_map.player_spawn_x
                player.y = current_map.player_spawn_y
                player.vel_x = 0
                player.vel_y = 0

    # Get keyboard input
    keys = pygame.key.get_pressed()

    # Update player
    player.move(keys, current_map.tiles)

    # Update camera
    camera.update(player, current_map.width, current_map.height)

    # Rendering
    screen.fill((135, 206, 235))  # Sky blue background
    current_map.render(screen, camera.x, camera.y)
    player.render(screen, camera.x, camera.y)

    # Display FPS (optional)
    font = pygame.font.Font(None, 36)
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))

    pygame.display.update()

pygame.quit()
sys.exit()