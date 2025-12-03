import pygame

class Vacuum(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        self.image.fill((148, 0, 211)) # Dark Violet
        # Draw a simple "M" or magnet shape
        pygame.draw.circle(self.image, (255, 255, 255), (8, 8), 6, 2)
        
        self.rect = self.image.get_rect(center=pos)

class Heart(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Draw a heart shape
        color = (255, 50, 50)
        pygame.draw.circle(self.image, color, (4, 6), 4)
        pygame.draw.circle(self.image, color, (12, 6), 4)
        pygame.draw.polygon(self.image, color, [(0, 8), (8, 16), (16, 8)])
        
        self.rect = self.image.get_rect(center=pos)
        self.heal_amount = 30
