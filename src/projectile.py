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
             if self.target_enemy.alive():
                 self.target_enemy.pending_damage -= self.damage
             self.target_enemy = None 
        super().kill()

class EnemyProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, target_pos, damage=10):
        super().__init__()
        self.damage = damage
        
        size = 6
        color = (150, 0, 150) # Purple
        
        self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size, size), size)
            
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        
        # Movement
        speed = 4.0
        direction = pygame.math.Vector2(target_pos) - self.pos
        if direction.length() > 0:
            self.velocity = direction.normalize() * speed
        else:
            self.velocity = pygame.math.Vector2(1, 0) * speed
            
        # Lifetime
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 3000

    def update(self):
        self.pos += self.velocity
        self.rect.center = self.pos
        
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill()

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
            self.image.fill(color)
            
        self.rect = self.image.get_rect(center=player.rect.center)
        
        # Lifetime
        self.spawn_time = pygame.time.get_ticks()
        self.duration = self.config.get('duration', 200)
        self.damage = self.config.get('damage', 10)
        self.penetration = 999 

        # Determine offset based on facing
        self.offset = pygame.math.Vector2(60, 0)
        if self.player.last_move.x < 0:
            self.offset.x = -60
            # Flip image if needed
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        self.rect.center = self.player.rect.center + self.offset
        
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill()

class AxeProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, config):
        super().__init__()
        self.config = config
        self.damage = self.config.get('damage', 15)
        
        size = self.config.get('size', 10)
        color = self.config.get('color', [139, 69, 19])
        sprite_path = self.config.get('sprite', None)
        
        self.image = ConfigLoader.load_image(sprite_path, (size*2, size*2))
        if self.image is None:
            self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, color, (size, size), size)
            
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        
        # Physics
        # Initial velocity: Up and slightly random X
        import random
        self.velocity = pygame.math.Vector2(random.uniform(-2, 2), -self.config.get('speed', 12.0))
        self.gravity = 0.5
        
        self.spawn_time = pygame.time.get_ticks()
        self.duration = self.config.get('duration', 3000)
        self.penetration = 999 

    def update(self):
        self.velocity.y += self.gravity
        self.pos += self.velocity
        self.rect.center = self.pos
        
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill()
            
class AuraHitbox(pygame.sprite.Sprite):
    def __init__(self, player, config):
        super().__init__()
        self.player = player
        self.config = config
        
        area = self.config.get('area', [100, 100])
        color = self.config.get('color', [255, 255, 200])
        sprite_path = self.config.get('sprite', None)
        
        # Semi-transparent circle
        self.image = ConfigLoader.load_image(sprite_path, tuple(area))
        if self.image is None:
            self.image = pygame.Surface(area, pygame.SRCALPHA)
            pygame.draw.circle(self.image, (*color, 50), (area[0]//2, area[1]//2), area[0]//2)
            
        self.rect = self.image.get_rect(center=player.rect.center)
        
        self.damage = self.config.get('damage', 3)
        self.penetration = 999
        self.tick_timer = 0
        self.tick_rate = self.config.get('cooldown', 200)

    def update(self):
        self.rect.center = self.player.rect.center
        
        self.tick_timer += 16 # approx 60fps
        if self.tick_timer >= self.tick_rate:
            self.tick_timer = 0
            self.active_damage_frame = True
        else:
            self.active_damage_frame = False
