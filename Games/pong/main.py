from classes import Game
import pygame, asyncio

pygame.init()

async def main():
    game = Game()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())