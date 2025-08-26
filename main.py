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
from settings import *

###################################################################################################

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.collision_sprites = collision_sprites
        self.slowmo_direction = vector(0, 0)  # Direction for slowmo movement

    def slide_in_direction(self, direction):
        dx, dy = int(direction.x), int(direction.y)
        while True:
            next_rect = self.rect.move(dx, dy)
            if next_rect.left < 0 or next_rect.right > 960 or next_rect.top < 0 or next_rect.bottom > 960:
                break
            collision = False
            for sprite in self.collision_sprites:
                if next_rect.colliderect(sprite.rect):
                    collision = True
                    break
            if collision:
                break
            self.rect = next_rect

    def handle_keydown(self, key, keys):
        # If space is held, set slowmo direction
        if keys[KEY_ABILITY]:
            if key in KEY_UP:
                self.slowmo_direction = vector(0, -1)
            elif key in KEY_DOWN:
                self.slowmo_direction = vector(0, 1)
            elif key in KEY_LEFT:
                self.slowmo_direction = vector(-1, 0)
            elif key in KEY_RIGHT:
                self.slowmo_direction = vector(1, 0)
        else:
            # Instant slide if not holding space
            if key in KEY_UP:
                self.slide_in_direction(vector(0, -1))
            elif key in KEY_DOWN:
                self.slide_in_direction(vector(0, 1))
            elif key in KEY_LEFT:
                self.slide_in_direction(vector(-1, 0))
            elif key in KEY_RIGHT:
                self.slide_in_direction(vector(1, 0))

    def handle_keyup(self, key, keys):
        # If a direction key or space is released, stop slowmo
        if key == KEY_ABILITY or key in KEY_UP + KEY_DOWN + KEY_LEFT + KEY_RIGHT:
            self.slowmo_direction = vector(0, 0)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[KEY_ABILITY] and self.slowmo_direction.length_squared() > 0:
            move = self.slowmo_direction.normalize() * 1500 * dt
            # Move axis by axis for precise collision
            # Horizontal
            self.rect.x += move.x
            for sprite in self.collision_sprites:
                if self.rect.colliderect(sprite.rect):
                    if move.x > 0:
                        self.rect.right = sprite.rect.left
                    elif move.x < 0:
                        self.rect.left = sprite.rect.right
            # Vertical
            self.rect.y += move.y
            for sprite in self.collision_sprites:
                if self.rect.colliderect(sprite.rect):
                    if move.y > 0:
                        self.rect.bottom = sprite.rect.top
                    elif move.y < 0:
                        self.rect.top = sprite.rect.bottom
            # Clamp to window bounds
            self.rect.left = max(self.rect.left, 0)
            self.rect.right = min(self.rect.right, 960)
            self.rect.top = max(self.rect.top, 0)
            self.rect.bottom = min(self.rect.bottom, 960)

###################################################################################################

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, *groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)

###################################################################################################

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((960, 960))
        pygame.display.set_caption("Dashbound")
        self.clock = pygame.time.Clock()

        # Load TMX map
        self.tmx_data = load_pygame('./assets/data/map.tmx')

        # Groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.setup()

    def setup(self):
        # Default position in case marker is not found
        player_pos = (100, 100)
        # Search for the 'Player' marker in object layers
        for obj in self.tmx_data.objects:
            if obj.name == "Player":
                player_pos = (obj.x, obj.y)
                break

        # Add collidable tiles from a layer named "collision"
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'tiles') and layer.name == "collision":
                for x, y, surf in layer.tiles():
                    Tile(
                        (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight),
                        surf,
                        self.all_sprites,
                        self.collision_sprites
                    )

        self.player = Player(player_pos, [self.all_sprites], self.collision_sprites)

    def draw_map(self):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'tiles'):
                for x, y, surf in layer.tiles():
                    self.display_surface.blit(surf, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))

    def run(self):
        while True:
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self.player.handle_keydown(event.key, keys)
                if event.type == pygame.KEYUP:
                    self.player.handle_keyup(event.key, keys)

            dt = self.clock.tick(60) / 1000  # Cap at 60 FPS

            self.all_sprites.update(dt)
            self.display_surface.fill((30, 30, 30))

            # Draw the map
            self.draw_map()

            self.all_sprites.draw(self.display_surface)
            pygame.display.update()

if __name__ == '__main__':
	game = Game()
	game.run()
