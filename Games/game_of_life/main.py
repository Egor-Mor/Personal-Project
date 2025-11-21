from classes import Square, Button, Field
import pygame, sys
import time

pygame.init()

clock = pygame.time.Clock()
pygame.display.set_caption("Game of life")
screen = pygame.display.set_mode((340, 440), 0, 32)


field = Field(Square, screen)
frame = 0
button = Button()

while True:

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
                field.running = bool(abs(field.running-1))
                button.toggle()


    pygame.display.update()
    clock.tick(20)