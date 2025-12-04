import unittest
import pygame
from entities.player import Player
from entities.enemy import Enemy
from entities.spawner import Spawner
from core.config_loader import ConfigLoader

# Mock pygame
pygame.init()
pygame.display.set_mode((1, 1))

class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player((0, 0))

    def test_initial_stats(self):
        self.assertEqual(self.player.hp, 100)
        self.assertEqual(self.player.level, 1)

    def test_take_damage(self):
        self.player.take_damage(10)
        self.assertEqual(self.player.hp, 90)

    def test_heal(self):
        self.player.hp = 50
        self.player.heal(20)
        self.assertEqual(self.player.hp, 70)
        
    def test_heal_overflow(self):
        self.player.hp = 90
        self.player.heal(20)
        self.assertEqual(self.player.hp, 100)

    def test_xp_gain_and_level_up(self):
        self.player.xp = 0
        self.player.next_level_xp = 10
        leveled_up = self.player.gain_xp(10)
        self.assertTrue(leveled_up)
        self.assertEqual(self.player.level, 2)
        self.assertEqual(self.player.xp, 0)

class TestEnemy(unittest.TestCase):
    def setUp(self):
        self.player = Player((0, 0))
        self.config = {'hp': 10, 'speed': 1, 'damage': 5, 'xp_value': 1}
        self.enemy = Enemy((100, 100), 'test_enemy', self.config, self.player)

    def test_take_damage(self):
        dead = self.enemy.take_damage(5)
        self.assertFalse(dead)
        self.assertEqual(self.enemy.hp, 5)
        
        dead = self.enemy.take_damage(5)
        self.assertTrue(dead)
        self.assertEqual(self.enemy.hp, 0)

        dead = self.enemy.take_damage(5)
        self.assertTrue(dead)
        self.assertEqual(self.enemy.hp, 0)

class TestGameStats(unittest.TestCase):
    def test_time_survived(self):
        from core.stats import GameStats
        stats = GameStats()
        stats.start_ticks = 1000
        stats.end_ticks = 0
        
        # Mock pygame.time.get_ticks
        original_get_ticks = pygame.time.get_ticks
        pygame.time.get_ticks = lambda: 2000
        
        try:
            # Running state
            self.assertEqual(stats.get_time_survived(), 1.0)
            
            # Game over state
            stats.end_ticks = 5000
            self.assertEqual(stats.get_time_survived(), 4.0)
        finally:
            pygame.time.get_ticks = original_get_ticks

if __name__ == '__main__':
    unittest.main()
