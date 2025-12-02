import pygame
from config_loader import ConfigLoader

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, enemy_id, config_data, player):
        super().__init__()
        self.player = player
        self.config = config_data
        
        # Load stats
        self.hp = self.config.get('hp', 10)
        self.speed = self.config.get('speed', 1.0)
        self.damage = self.config.get('damage', 5)
        self.xp_value = self.config.get('xp_value', 1)
        self.pending_damage = 0
        
        # Visuals
        width = self.config.get('width', 32)
        height = self.config.get('height', 32)
        sprite_path = self.config.get('sprite', None)
        color = self.config.get('color', [255, 0, 0])
        
        self.image = ConfigLoader.load_image(sprite_path, (width, height))
        if self.image is None:
            self.image = pygame.Surface((width, height))
            self.image.fill(color)
            
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)

    def update(self, enemies_group=None):
        # Simple chase logic
        target_vector = pygame.math.Vector2(self.player.rect.center) - self.pos
        if target_vector.length() > 0:
            target_vector = target_vector.normalize()
        
        # Separation logic (avoid clumping)
        separation_vector = pygame.math.Vector2(0, 0)
        if enemies_group:
            # Check for collisions with other enemies
            # Using a smaller rect for collision to allow some overlap but push center
            hit_rect = self.rect.inflate(-5, -5)
            # We can't pass a rect to spritecollide, so we rely on self.rect
            # Optim: limit check? No, let's try raw spritecollide first.
            # To avoid N^2 every frame, maybe random skip?
            neighbors = pygame.sprite.spritecollide(self, enemies_group, False)
            count = 0
            for neighbor in neighbors:
                if neighbor is not self:
                    # Push away
                    diff = self.pos - neighbor.pos
                    dist = diff.length()
                    if dist < 40 and dist > 0: # Only push if close
                        separation_vector += diff.normalize() / dist
                        count += 1
            
            if count > 0:
                 separation_vector = separation_vector / count
                 
        # Combine vectors
        # Chase weight: 1.0, Separation weight: 20.0 (needs to be strong when close)
        final_vector = target_vector + (separation_vector * 50)
        if final_vector.length() > 0:
            final_vector = final_vector.normalize()
            
        self.pos += final_vector * self.speed
        self.rect.center = self.pos

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            return True # Dead
        return False
