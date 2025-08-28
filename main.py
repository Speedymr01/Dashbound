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
        self.image = pygame.image.load('./assets/graphics/player.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 32))  # Ensure it's 32x32
        self.rect = self.image.get_rect(center=pos)
        self.collision_sprites = collision_sprites

        # For pixel-perfect collision
        self.mask = pygame.mask.from_surface(self.image)

        # Movement state
        self.velocity = vector(0, 0)
        self.max_velocity = 1200  # px/s
        self.charge_rate = 1800   # px/s^2
        self.friction = 3000      # px/s^2

        # Charging state (for next move)
        self.charging = False
        self.charge_direction = vector(0, 0)
        self.charge_time = 0
        self.charge_ready = False

    def handle_keydown(self, key, keys):
        # If not already charging, start charging in the direction of the key
        if not self.charging and (
            self.velocity.length_squared() > 0 or self.velocity.length_squared() == 0
        ):
            if key in KEY_UP:
                self.charging = True
                self.charge_direction = vector(0, -1)
                self.charge_time = 0
                self.charge_ready = False
            elif key in KEY_DOWN:
                self.charging = True
                self.charge_direction = vector(0, 1)
                self.charge_time = 0
                self.charge_ready = False
            elif key in KEY_LEFT:
                self.charging = True
                self.charge_direction = vector(-1, 0)
                self.charge_time = 0
                self.charge_ready = False
            elif key in KEY_RIGHT:
                self.charging = True
                self.charge_direction = vector(1, 0)
                self.charge_time = 0
                self.charge_ready = False

    def handle_keyup(self, key, keys):
        # Only finish charging if the released key matches the charge direction
        if self.charging:
            if (key in KEY_UP and self.charge_direction == vector(0, -1)) or \
               (key in KEY_DOWN and self.charge_direction == vector(0, 1)) or \
               (key in KEY_LEFT and self.charge_direction == vector(-1, 0)) or \
               (key in KEY_RIGHT and self.charge_direction == vector(1, 0)):
                # If still moving, mark charge as ready for after movement
                if self.velocity.length_squared() > 0:
                    self.charge_ready = True
                else:
                    # If not moving, launch immediately
                    speed = min(self.charge_time * self.charge_rate, self.max_velocity)
                    self.velocity = self.charge_direction.normalize() * speed
                    self.charge_ready = False
                self.charging = False
                self.charge_direction = vector(0, 0)
                self.charge_time = 0

    def update(self, dt):
        # Charging phase (for next move)
        if self.charging:
            self.charge_time += dt

        # Sliding phase
        if self.velocity.length_squared() > 0:
            move = self.velocity * dt

            # Move axis by axis for precise collision
            # Horizontal
            self.rect.x += move.x
            for sprite in self.collision_sprites:
                if self.rect.colliderect(sprite.rect):
                    if getattr(sprite, 'pixel_perfect', False) and sprite.mask:
                        offset = (self.rect.left - sprite.rect.left, self.rect.top - sprite.rect.top)
                        if sprite.mask.overlap(self.mask, offset):
                            self.velocity.x = 0
                            # Push out of the tile horizontally
                            if move.x > 0:
                                while sprite.mask.overlap(self.mask, (self.rect.left - sprite.rect.left, self.rect.top - sprite.rect.top)):
                                    self.rect.x -= 1
                            elif move.x < 0:
                                while sprite.mask.overlap(self.mask, (self.rect.left - sprite.rect.left, self.rect.top - sprite.rect.top)):
                                    self.rect.x += 1
                    else:
                        if move.x > 0:
                            self.rect.right = sprite.rect.left
                        elif move.x < 0:
                            self.rect.left = sprite.rect.right
                        self.velocity.x = 0

            # Vertical
            self.rect.y += move.y
            for sprite in self.collision_sprites:
                if self.rect.colliderect(sprite.rect):
                    if getattr(sprite, 'pixel_perfect', False) and sprite.mask:
                        offset = (self.rect.left - sprite.rect.left, self.rect.top - sprite.rect.top)
                        if sprite.mask.overlap(self.mask, offset):
                            self.velocity.y = 0
                            # Push out of the tile vertically
                            if move.y > 0:
                                while sprite.mask.overlap(self.mask, (self.rect.left - sprite.rect.left, self.rect.top - sprite.rect.top)):
                                    self.rect.y -= 1
                            elif move.y < 0:
                                while sprite.mask.overlap(self.mask, (self.rect.left - sprite.rect.left, self.rect.top - sprite.rect.top)):
                                    self.rect.y += 1
                    else:
                        if move.y > 0:
                            self.rect.bottom = sprite.rect.top
                        elif move.y < 0:
                            self.rect.top = sprite.rect.bottom
                        self.velocity.y = 0

            # Apply friction
            if self.velocity.length() > 0:
                friction_vec = self.velocity.normalize() * self.friction * dt
                if friction_vec.length() > self.velocity.length():
                    self.velocity = vector(0, 0)
                else:
                    self.velocity -= friction_vec

            # Clamp to window bounds
            self.rect.left = max(self.rect.left, 0)
            self.rect.right = min(self.rect.right, 960)
            self.rect.top = max(self.rect.top, 0)
            self.rect.bottom = min(self.rect.bottom, 960)

            # Stop if velocity is very low
            if self.velocity.length() < 10:
                self.velocity = vector(0, 0)

        # If movement stopped and a charge is ready, launch immediately
        if self.velocity.length_squared() == 0 and self.charge_ready:
            if self.charge_direction.length_squared() > 0:
                speed = min(self.charge_time * self.charge_rate, self.max_velocity)
                self.velocity = self.charge_direction.normalize() * speed
            self.charge_ready = False
            self.charge_time = 0
            self.charge_direction = vector(0, 0)

    def draw_velocity_bar(self, surface):
        # Bar settings
        bar_width = 40
        bar_height = 8
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 16

        # Show charge velocity if charging, else show 0
        velocity_mag = self.charge_time * self.charge_rate if self.charging else 0
        velocity_ratio = min(velocity_mag / self.max_velocity, 1.0)

        # Draw background
        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        # Draw velocity
        pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(bar_width * velocity_ratio), bar_height))
        # Draw border
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

###################################################################################################

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, *groups, pixel_perfect=False):
        super().__init__(*groups)
        self.image = surf.convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.pixel_perfect = pixel_perfect
        if pixel_perfect:
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.mask = None

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
        for obj in self.tmx_data.objects:
            if obj.name == "Player":
                player_pos = (obj.x, obj.y)
                break

        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'tiles'):
                pixel_perfect = (layer.name == "collision-diagonal")
                for x, y, surf in layer.tiles():
                    Tile(
                        (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight),
                        surf,
                        self.all_sprites,
                        self.collision_sprites,
                        pixel_perfect=pixel_perfect
                    )

        self.player = Player(player_pos, [self.all_sprites], self.collision_sprites)

    def draw_map(self):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'tiles'):
                for x, y, surf in layer.tiles():
                    self.display_surface.blit(surf, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))
        # Draw objects from object layers (like "Objects")
        for layer in self.tmx_data.layers:
            if layer.__class__.__name__ == "TiledObjectGroup" and layer.name == "Objects":
                for obj in layer:
                    print(vars(obj))  # See what attributes are available
                    if hasattr(obj, 'gid') and obj.gid:
                        surf = self.tmx_data.get_tile_image_by_gid(obj.gid)
                        if surf:
                            self.display_surface.blit(surf, (obj.x, obj.y))
                    elif hasattr(obj, 'image') and obj.image:
                        self.display_surface.blit(obj.image, (obj.x, obj.y))
                    elif hasattr(obj, 'image') and obj.image is None and hasattr(obj, 'source') and obj.source:
                        # Try to load manually
                        import os
                        image_path = os.path.join(os.path.dirname(self.tmx_data.filename), obj.source)
                        if os.path.exists(image_path):
                            surf = pygame.image.load(image_path).convert_alpha()
                            self.display_surface.blit(surf, (obj.x, obj.y))

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
            self.display_surface.fill((222, 222, 222))

            # Draw the map
            self.draw_map()

            self.all_sprites.draw(self.display_surface)
            self.player.draw_velocity_bar(self.display_surface)
            pygame.display.update()

if __name__ == '__main__':
	game = Game()
	game.run()
