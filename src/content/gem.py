import pygame

class Gem(pygame.sprite.Sprite):
    def __init__(self, pos, player, value=1):
        super().__init__()
        self.player = player
        self.value = value
        self.image = pygame.Surface((8, 8))
        self.image.fill((0, 255, 255)) # Cyan gem
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)
        
        self.speed = 0
        self.max_speed = 12
        self.acceleration = 0.5
        self.magnet_radius = 150
        self.being_vacuumed = False
        
    def vacuum(self):
        self.being_vacuumed = True

    def update(self):
        # Check distance to player
        player_pos = pygame.math.Vector2(self.player.rect.center)
        diff = player_pos - self.pos
        dist_sq = diff.length_squared()
        
        # 150^2 = 22500
        should_move = self.being_vacuumed or (dist_sq < self.magnet_radius**2)
        
        if should_move:
            if dist_sq > 0:
                direction = diff.normalize()
                self.speed = min(self.speed + self.acceleration, self.max_speed)
                self.pos += direction * self.speed
                self.rect.center = self.pos
        else:
            self.speed = 0
