import os
var1 = [
    'pygame',
    'pytmx'
]

for var2 in var1:
    try:
        __import__(var2)
    except ImportError:
        command = f"{sys.executable} -m pip install {var2}"
        os.system(command)  # Run the pip install command using os.system
        print(f"{var2} installed successfully.")

import pygame, sys
from pygame.math import Vector2 as vector
from pytmx.util_pygame import load_pygame
from player import Player
import time

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((960, 960))
        pygame.display.set_caption("Dashbound")
        self.clock = pygame.time.Clock()

        # Groups
        self.all_sprites = pygame.sprite.Group()
        self.setup()
    def setup(self):
        self.player = Player((100, 100), [self.all_sprites], [])
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            dt = self.clock.tick() / 1000

            self.all_sprites.update(dt)
            self.display_surface.fill((30, 30, 30))
            self.all_sprites.draw(self.display_surface)
            pygame.display.update()

if __name__ == '__main__':
	game = Game()
	game.run()
