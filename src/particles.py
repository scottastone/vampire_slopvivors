import pygame
import random

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, color, speed=2, duration=30):
        super().__init__()
        self.image = pygame.Surface((4, 4))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        
        angle = random.uniform(0, 360)
        speed = random.uniform(speed * 0.5, speed * 1.5)
        
        import math
        rad = math.radians(angle)
        self.velocity = pygame.math.Vector2(math.cos(rad) * speed, math.sin(rad) * speed)
        
        self.spawn_time = pygame.time.get_ticks()
        self.duration = duration * (1000/60) # frames to ms approx or direct ms

    def update(self):
        self.pos += self.velocity
        self.rect.center = self.pos
        
        # Fade out? For now just kill after time
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill()

class ParticleSystem:
    def __init__(self, all_sprites):
        self.all_sprites = all_sprites
        self.particles_group = pygame.sprite.Group()

    def create_explosion(self, pos, color, count=10):
        for _ in range(count):
            p = Particle(pos, color)
            self.all_sprites.add(p)
            self.particles_group.add(p)
    
    def create_hit(self, pos, color=(255, 255, 255), count=3):
        for _ in range(count):
            p = Particle(pos, color, speed=4, duration=10)
            self.all_sprites.add(p)
            self.particles_group.add(p)
            
    def update(self):
        self.particles_group.update()
