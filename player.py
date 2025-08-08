import pygame
from pygame.math import Vector2 as vector
from os import walk
import sys
import time
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.Surface((50, 50))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=pos)
        self.collision_sprites = collision_sprites
