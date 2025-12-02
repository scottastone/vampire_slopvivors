import pygame
import math
from config_loader import ConfigLoader

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, target, config):
        super().__init__()
        self.config = config
        self.target_enemy = None
        
        # Determine target position and handle predictive targeting
        target_pos = target
        self.damage = self.config.get('damage', 10)
        
        # Check if target is an entity with pending_damage (duck typing)
        if hasattr(target, 'rect') and hasattr(target, 'pending_damage'):
            self.target_enemy = target
            target_pos = target.rect.center
            self.target_enemy.pending_damage += self.damage
            
        # Visuals
        size = self.config.get('size', 8)
        color = self.config.get('color', [255, 255, 0])
        sprite_path = self.config.get('sprite', None)
        
        self.image = ConfigLoader.load_image(sprite_path, (size*2, size*2))
        if self.image is None:
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, color, (size, size), size)
            
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        
        # Movement
        speed = self.config.get('speed', 5.0)
        direction = pygame.math.Vector2(target_pos) - self.pos
        if direction.length() > 0:
            self.velocity = direction.normalize() * speed
        else:
            self.velocity = pygame.math.Vector2(1, 0) * speed
            
        # Lifetime
        self.spawn_time = pygame.time.get_ticks()
        self.duration = self.config.get('duration', 2000)
        self.penetration = self.config.get('penetration', 1)

    def update(self):
        self.pos += self.velocity
        self.rect.center = self.pos
        
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill()

    def kill(self):
        if self.target_enemy:
             # Ensure we don't double decrement if kill called multiple times or race conditions
             # pending_damage is just a heuristic, so simple check is fine
             # We check if enemy is alive to be safe, though python obj persists
             if self.target_enemy.alive():
                 self.target_enemy.pending_damage -= self.damage
             self.target_enemy = None # Clear ref
        super().kill()

class MeleeHitbox(pygame.sprite.Sprite):
    def __init__(self, player, config):
        super().__init__()
        self.player = player
        self.config = config
        
        area = self.config.get('area', [50, 50])
        color = self.config.get('color', [255, 0, 0])
        sprite_path = self.config.get('sprite', None)
        
        self.image = ConfigLoader.load_image(sprite_path, tuple(area))
        if self.image is None:
            self.image = pygame.Surface(area, pygame.SRCALPHA)
            self.image.fill(color) # Should be partially transparent ideally?
            
        # Determine position based on player facing direction (simplified: always right for now or based on movement)
        # For simplicity, let's make it follow the player centered or offset
        self.rect = self.image.get_rect(center=player.rect.center)
        
        # Lifetime
        self.spawn_time = pygame.time.get_ticks()
        self.duration = self.config.get('duration', 200)
        self.damage = self.config.get('damage', 10)
        self.penetration = 999 # Melee hits everything in area

    def update(self):
        # Follow player
        # A simple whip might appear in the direction of movement
        offset = pygame.math.Vector2(50, 0)
        if self.player.velocity.length() > 0:
             offset = self.player.velocity.normalize() * 50
        
        self.rect.center = self.player.rect.center + offset
        
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill()
