import pygame
import random
from entities.enemy import Enemy

class Spawner:
    def __init__(self, config_loader, player, entity_manager, director=None):
        self.config_loader = config_loader
        self.player = player
        self.entity_manager = entity_manager
        self.director = director
        self.all_sprites = entity_manager.all_sprites
        self.enemies_group = entity_manager.enemies_group
        
        self.enemy_configs = self.config_loader.load_enemies()
        self.spawn_timer = 0
        
        # Wave Management
        self.game_time = 0 # seconds
        self.start_ticks = pygame.time.get_ticks()
        
        # Boss State
        self.boss_spawned = False
        self.boss_timer = 0
        self.boss_spawn_time = 300 # 5 minutes for boss? Or keep simple
        
        # Wave Definitions
        # (Start Time, End Time, Spawn Interval, [Enemy IDs])
        self.waves = [
            {'time': 0, 'interval': 60, 'enemies': ['goblin']},
            {'time': 30, 'interval': 50, 'enemies': ['goblin', 'bat']},
            {'time': 60, 'interval': 40, 'enemies': ['goblin', 'bat', 'slime']},
            {'time': 120, 'interval': 30, 'enemies': ['bat', 'ghost', 'slime']},
            {'time': 180, 'interval': 25, 'enemies': ['ghost', 'orc', 'wolf']},
            {'time': 300, 'interval': 20, 'enemies': ['orc', 'mage', 'wolf']},
            {'time': 420, 'interval': 15, 'enemies': ['orc', 'mage', 'necromancer']},
            {'time': 600, 'interval': 10, 'enemies': ['mage', 'necromancer', 'tank_orc']},
        ]
        
    def update(self):
        current_ticks = pygame.time.get_ticks()
        self.game_time = (current_ticks - self.start_ticks) / 1000.0
        
        self.spawn_timer += 1
        
        # Determine current wave
        # Determine current wave
        current_wave = None
        # Iterate backwards to find the latest wave that has started
        for i in range(len(self.waves) - 1, -1, -1):
            if self.game_time >= self.waves[i]['time']:
                current_wave = self.waves[i]
                break
                
        if current_wave:
            interval = current_wave['interval']
            # Ramp up difficulty within wave?
            # Director Multiplier
            if hasattr(self, 'director') and self.director: # Check if director exists and is not None
                interval /= self.director.get_spawn_rate_multiplier()
                
            if self.spawn_timer >= interval:
                self.spawn_timer = 0
                self.spawn_enemy(current_wave['enemies'])
                
        # Horde Event (Every 60 seconds, spawn 30 enemies)
        if int(self.game_time) > 0 and int(self.game_time) % 60 == 0:
             if not hasattr(self, 'last_horde_time') or self.game_time - self.last_horde_time > 5:
                 self.spawn_horde()
                 self.last_horde_time = self.game_time

        # Boss Spawn (at 5 minutes / 300s)
        if not self.boss_spawned and self.game_time >= 300:
            self.spawn_boss()
            self.boss_spawned = True
            
        # Limit total enemies
        cap = 500
        if hasattr(self, 'director') and self.director: # Check if director exists and is not None
            cap *= self.director.get_enemy_cap_multiplier()
            
        if len(self.enemies_group) >= cap:
            return

    def spawn_horde(self):
        print("HORDE SPAWNED!")
        # Spawn 30 enemies in a circle
        count = 30
        radius = 500
        import math
        
        # Determine enemy type for horde based on time
        enemy_id = 'bat'
        if self.game_time > 120: enemy_id = 'wolf'
        elif self.game_time > 60: enemy_id = 'goblin'
        
        if enemy_id not in self.enemy_configs: return
        config = self.enemy_configs[enemy_id]

        for i in range(count):
            angle = (360 / count) * i
            rad = math.radians(angle)
            offset_x = math.cos(rad) * radius
            offset_y = math.sin(rad) * radius
            spawn_pos = (self.player.rect.centerx + offset_x, self.player.rect.centery + offset_y)
            
            enemy = Enemy(spawn_pos, enemy_id, config, self.player, self.entity_manager)
            self.all_sprites.add(enemy)
            self.enemies_group.add(enemy)

    def spawn_boss(self):
        boss_ids = [k for k, v in self.enemy_configs.items() if v.get('is_boss', False)]
        if not boss_ids:
            return
            
        enemy_id = boss_ids[0] 
        config = self.enemy_configs[enemy_id]
        
        spawn_pos = self.get_spawn_pos()
        print(f"Spawning Boss: {enemy_id}")
        enemy = Enemy(spawn_pos, enemy_id, config, self.player, self.entity_manager)
        self.all_sprites.add(enemy)
        self.enemies_group.add(enemy)
            
    def spawn_enemy(self, allowed_enemies):
        if not allowed_enemies:
            return
            
        enemy_id = random.choice(allowed_enemies)
        if enemy_id not in self.enemy_configs:
            return
            
        config = self.enemy_configs[enemy_id]
        spawn_pos = self.get_spawn_pos()
            
        enemy = Enemy(spawn_pos, enemy_id, config, self.player, self.entity_manager)
        self.all_sprites.add(enemy)
        self.enemies_group.add(enemy)

    def get_spawn_pos(self):
        spawn_radius = 600
        angle = random.uniform(0, 360)
        import math
        rad = math.radians(angle)
        offset_x = math.cos(rad) * spawn_radius
        offset_y = math.sin(rad) * spawn_radius
        
        return (self.player.rect.centerx + offset_x, self.player.rect.centery + offset_y)
