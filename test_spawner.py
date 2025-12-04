import pygame
import unittest
from entities.spawner import Spawner
from core.config_loader import ConfigLoader

class MockPlayer:
    def __init__(self):
        self.rect = pygame.Rect(0,0,32,32)

class MockEntityManager:
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()
    def spawn_enemy(self, enemy): pass
    def add_enemy(self, enemy): pass

class TestSpawnerWaves(unittest.TestCase):
    def test_wave_selection(self):
        pygame.init()
        config_loader = ConfigLoader()
        player = MockPlayer()
        entity_manager = MockEntityManager()
        spawner = Spawner(config_loader, player, entity_manager)
        
        # Mock time to 10 seconds (Wave 0)
        spawner.game_time = 10
        spawner.update() # Should not crash
        
        # Mock time to 40 seconds (Wave 1)
        spawner.game_time = 40
        spawner.update() # Should not crash
        
        pygame.quit()

if __name__ == '__main__':
    unittest.main()
