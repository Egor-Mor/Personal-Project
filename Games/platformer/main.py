from classes import Player, Map, Camera, Button
import pygame
import sys
import os

pygame.init()

# Game settings
FPS = 60
clock = pygame.time.Clock()

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_WIN = "win"
STATE_DEAD = "dead"


class Game:
    def __init__(self):
        self.state = STATE_MENU
        self.current_level = 1
        self.available_levels = self.scan_levels()
        self.screen = None
        self.current_map = None
        self.player = None
        self.camera = None
        self.init_menu()

    def scan_levels(self):
        levels = []
        if os.path.exists("maps"):
            for file in os.listdir("maps"):
                if file.endswith(".map"):
                    levels.append(file)
        if not levels:
            levels = ["level1.map"]
        return sorted(levels)

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
        font_text = pygame.font.Font(None, 36)

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

        # Exit button
        exit_btn = Button(250, y_start + len(self.available_levels) * 70 + 20, 300, 50, "EXIT", (180, 70, 70))
        exit_btn.check_hover(pygame.mouse.get_pos())
        exit_btn.render(self.screen)

        return buttons, exit_btn

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

        font_title = pygame.font.Font(None, 72)
        font_text = pygame.font.Font(None, 36)

        title = font_title.render("LEVEL COMPLETE!", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(title, title_rect)

        stars = font_text.render(f"Stars: {self.player.stars_collected}/{self.current_map.total_stars}", True,
                                 (255, 215, 0))
        stars_rect = stars.get_rect(center=(self.screen.get_width() // 2, 220))
        self.screen.blit(stars, stars_rect)

        # Buttons
        btn_width = 250
        btn_x = self.screen.get_width() // 2 - btn_width // 2

        restart_btn = Button(btn_x, 300, btn_width, 50, "RESTART", (70, 130, 180))
        next_btn = Button(btn_x, 370, btn_width, 50, "NEXT LEVEL", (70, 180, 70))
        menu_btn = Button(btn_x, 440, btn_width, 50, "MENU", (180, 130, 70))

        mouse_pos = pygame.mouse.get_pos()
        restart_btn.check_hover(mouse_pos)
        next_btn.check_hover(mouse_pos)
        menu_btn.check_hover(mouse_pos)

        restart_btn.render(self.screen)
        next_btn.render(self.screen)
        menu_btn.render(self.screen)

        return restart_btn, next_btn, menu_btn

    def render_dead(self):
        self.screen.fill((100, 50, 50))

        font_title = pygame.font.Font(None, 72)

        title = font_title.render("YOU DIED!", True, (255, 100, 100))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(title, title_rect)

        # Buttons
        btn_width = 250
        btn_x = self.screen.get_width() // 2 - btn_width // 2

        restart_btn = Button(btn_x, 300, btn_width, 50, "RESTART", (70, 130, 180))
        menu_btn = Button(btn_x, 370, btn_width, 50, "MENU", (180, 130, 70))

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
                        buttons, exit_btn = self.render_menu()
                        for i, btn in enumerate(buttons):
                            if btn.check_click(mouse_pos):
                                self.load_level(i)
                        if exit_btn.check_click(mouse_pos):
                            pygame.quit()
                            sys.exit()

                    elif self.state == STATE_WIN:
                        restart_btn, next_btn, menu_btn = self.render_win()
                        if restart_btn.check_click(mouse_pos):
                            self.restart_level()
                        elif next_btn.check_click(mouse_pos):
                            self.next_level()
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
                if self.player.check_death(self.current_map.height):
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


if __name__ == "__main__":
    game = Game()
    game.run()