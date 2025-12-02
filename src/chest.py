import pygame

class Chest(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 215, 0)) # Gold
        # Draw a simple chest look
        pygame.draw.rect(self.image, (139, 69, 19), (2, 10, 28, 20)) # Brown box
        pygame.draw.circle(self.image, (139, 69, 19), (16, 10), 14) # Lid
        
        self.rect = self.image.get_rect(center=pos)
