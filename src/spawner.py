import pygame
import random
from enemy import Enemy

class Spawner:
    def __init__(self, config_loader, player, all_sprites, enemies_group):
        self.config_loader = config_loader
        self.player = player
        self.all_sprites = all_sprites
        self.enemies_group = enemies_group
        
        self.enemy_configs = self.config_loader.load_enemies()
        self.spawn_timer = 0
        self.spawn_interval = 30 # frames, start with 0.5 sec for more action
        self.difficulty_timer = 0
        
        # Boss State
        self.boss_spawned = False
        self.boss_timer = 0
        self.boss_spawn_time = 3600 # 60 seconds (60fps * 60)
        
    def update(self):
        self.spawn_timer += 1
        self.difficulty_timer += 1
        self.boss_timer += 1
        
        # Increase difficulty (spawn rate) over time
        if self.difficulty_timer > 300: # Every 5 seconds (faster ramp up)
            self.difficulty_timer = 0
            self.spawn_interval = max(5, self.spawn_interval - 2) # Cap at 5 frames (12 enemies/sec)
            
        # Limit total enemies to prevent lag if Python struggles (e.g. 300)
        if len(self.enemies_group) >= 300:
            return

        # Spawn Boss
        if not self.boss_spawned and self.boss_timer >= self.boss_spawn_time:
            self.spawn_boss()
            self.boss_spawned = True
            
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_enemy()

    def spawn_boss(self):
        boss_ids = [k for k, v in self.enemy_configs.items() if v.get('is_boss', False)]
        if not boss_ids:
            return
            
        enemy_id = boss_ids[0] # Pick first boss
        config = self.enemy_configs[enemy_id]
        
        # Spawn relative to player
        spawn_radius = 600
        angle = random.uniform(0, 360)
        import math
        rad = math.radians(angle)
        offset_x = math.cos(rad) * spawn_radius
        offset_y = math.sin(rad) * spawn_radius
        spawn_pos = (self.player.rect.centerx + offset_x, self.player.rect.centery + offset_y)
        
        print(f"Spawning Boss: {enemy_id}")
        enemy = Enemy(spawn_pos, enemy_id, config, self.player)
        self.all_sprites.add(enemy)
        self.enemies_group.add(enemy)
            
    def spawn_enemy(self):
        # Pick a random enemy type (weighted could be better, but random for now)
        # Exclude boss from random spawns initially
        available_enemies = [k for k, v in self.enemy_configs.items() if not v.get('is_boss', False)]
        if not available_enemies:
            return
            
        enemy_id = random.choice(available_enemies)
        config = self.enemy_configs[enemy_id]
        
        # Spawn relative to player
        # Radius should be larger than half screen width (400) -> 500-600
        spawn_radius = 600
        angle = random.uniform(0, 360)
        
        # Calculate offset
        import math
        rad = math.radians(angle)
        offset_x = math.cos(rad) * spawn_radius
        offset_y = math.sin(rad) * spawn_radius
        
        spawn_pos = (self.player.rect.centerx + offset_x, self.player.rect.centery + offset_y)
            
        enemy = Enemy(spawn_pos, enemy_id, config, self.player)
        self.all_sprites.add(enemy)
        self.enemies_group.add(enemy)
