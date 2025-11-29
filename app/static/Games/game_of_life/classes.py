import pygame, sys

class Sprite:
    image = None
    current_frame = 0
    frame_time = 0

    def __init__(self, img_route, hitbox=None):
        self.imgs = []
        self.img_route = img_route
        if isinstance(hitbox, (list, tuple)) and len(hitbox) == 2:
            self.x = hitbox[0]
            self.y = hitbox[1]
        self.image = pygame.image.load(self.img_route)
        self.imgs.append(self.image)

    def add_anim_stage(self, anim_img_route):
        anim_img = pygame.image.load(anim_img_route)
        self.imgs.append(anim_img)

    def animate(self, anim_time):
        self.frame_time += clock.get_time()
        if self.frame_time >= anim_time * 1000:
            self.current_frame = (self.current_frame + 1) % len(self.imgs)
            self.image = self.imgs[self.current_frame]
            self.frame_time = 0

    def display(self, window, x, y):
        window.blit(self.image, (x, y))

class Square:
    def __init__(self, coords:tuple, alive=False):
        self.status = alive
        self.coords = coords
        if self.status:
            self.sprite = Sprite("img/sq-white.png")
        else:
            self.sprite = Sprite("img/sq-black.png")

    def render(self, window):
        if self.status:
            self.sprite.image = pygame.image.load("img/sq-white.png")
        else:
            self.sprite.image = pygame.image.load("img/sq-black.png")
        self.sprite.display(window, (20 + self.coords[0] * 15), (20 + self.coords[1] * 15))

    def toggle(self):
        self.status = bool(abs(self.status - 1))


class Field:
    def __init__(self, Square, window):
        self.field = []
        self.running = False
        self.window = window
        for x in range(20):
            self.field.append([])
            for y in range(20):
                self.field[x].append(Square((x,y)))

    def render_field(self):
        for row in self.field:
            for box in row:
                box.render(self.window)

    def click_check(self, mouse):
        for row in self.field:
            for box in row:
                if (20 + box.coords[0] * 15) <= mouse[0] <= (35 + box.coords[0] * 15) and (20 + box.coords[1] * 15) <= mouse[1] <= (35 + box.coords[1] * 15):
                    box.toggle()

    def run(self):
        toggle = []
        for x, row in enumerate(self.field):
            for y, box in enumerate(row):
                neighbours = 0
                if 19 > x > 0:
                    neighbours += self.field[x - 1][y].status + self.field[x + 1][y].status
                    if 19 > y > 0:
                        neighbours += self.field[x - 1][y + 1].status + self.field[x - 1][y - 1].status + self.field[x][y + 1].status + self.field[x][y - 1].status + self.field[x + 1][y - 1].status + self.field[x + 1][y + 1].status
                    elif y == 19:
                        neighbours += self.field[x - 1][y - 1].status + self.field[x][y - 1].status + self.field[x + 1][y - 1].status
                    elif y == 0:
                        neighbours += self.field[x - 1][y + 1].status + self.field[x][y + 1].status + self.field[x + 1][y + 1].status

                elif x == 7:
                    neighbours += self.field[x - 1][y].status
                    if 19 > y > 0:
                        neighbours += self.field[x - 1][y + 1].status + self.field[x - 1][y - 1].status + self.field[x][y + 1].status + self.field[x][y - 1].status
                    elif y == 19:
                        neighbours += self.field[x - 1][y - 1].status + self.field[x][y - 1].status
                    elif y == 0:
                        neighbours += self.field[x - 1][y + 1].status + self.field[x][y + 1].status

                elif x == 0:
                    neighbours += self.field[x + 1][y].status
                    if 19 > y > 0:
                        neighbours += self.field[x + 1][y + 1].status + self.field[x + 1][y - 1].status + self.field[x][y + 1].status + self.field[x][y - 1].status
                    elif y == 19:
                        neighbours += self.field[x + 1][y - 1].status + self.field[x][y - 1].status
                    elif y == 0:
                        neighbours += self.field[x + 1][y + 1].status + self.field[x][y + 1].status

                if box.status and (neighbours < 2 or neighbours > 3):
                    toggle.append((x, y))
                elif bool(abs(box.status - 1)) and neighbours == 3:
                    toggle.append((x, y))


        for element in toggle:
            self.field[element[0]][element[1]].toggle()


class Button:
    def __init__(self):
        self.img1 = pygame.image.load("img/button-1.png")
        self.img2 = pygame.image.load("img/button-2.png")
        self.image = self.img1

    def toggle(self):
        if self.image == self.img1:
            self.image = self.img2
        elif self.image == self.img2:
            self.image = self.img1

    def render(self, window):
        window.blit(self.image, (20,340))

class Game:
    def __init__(self):
        pass
    async def run(self):
        import asyncio
        clock = pygame.time.Clock()
        pygame.display.set_caption("Game of life")
        screen = pygame.display.set_mode((340, 440), 0, 32)

        field = Field(Square, screen)
        frame = 0
        button = Button()

        while True:
            clock.tick(20)
            await asyncio.sleep(0)  # Yield control to event loop for pygbag
            frame += 1

            if field.running and not frame % 2:
                field.run()

            screen.fill((118, 61, 217))
            field.render_field()
            button.render(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = pygame.mouse.get_pos()
                    field.click_check(mouse)
                    if 20 < mouse[0] < 320 and 340 < mouse[1] < 400:
                        field.running = bool(abs(field.running - 1))
                        button.toggle()

            pygame.display.update()