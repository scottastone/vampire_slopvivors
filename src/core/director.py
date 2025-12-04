import pygame

class Director:
    def __init__(self, player, stats):
        self.player = player
        self.stats = stats
        self.difficulty_multiplier = 1.0
        self.last_check_time = 0
        self.check_interval = 5000 # Check every 5 seconds
        
        # Metrics
        self.last_kills = 0
        self.last_damage = 0
        
    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_check_time > self.check_interval:
            self.adjust_difficulty()
            self.last_check_time = current_time
            
    def adjust_difficulty(self):
        # Calculate Kills Per Second (KPS) over the last interval
        kills_diff = self.stats.enemies_killed - self.last_kills
        self.last_kills = self.stats.enemies_killed
        
        kps = kills_diff / (self.check_interval / 1000.0)
        
        # Base multiplier increase over time (Game gets harder naturally)
        self.difficulty_multiplier += 0.05
        
        # Adaptive Logic
        if kps > 2.0: # Killing very fast
            self.difficulty_multiplier += 0.1
            print(f"Director: High Intensity! Increasing difficulty to {self.difficulty_multiplier:.2f}")
        elif kps < 0.5 and self.player.hp < self.player.max_hp * 0.3: # Struggling
            self.difficulty_multiplier = max(1.0, self.difficulty_multiplier - 0.05)
            print(f"Director: Low Intensity. Reducing difficulty to {self.difficulty_multiplier:.2f}")
            
        # Cap multiplier
        self.difficulty_multiplier = min(5.0, self.difficulty_multiplier)

    def get_spawn_rate_multiplier(self):
        return self.difficulty_multiplier

    def get_enemy_cap_multiplier(self):
        # Increase cap slower than spawn rate
        return 1.0 + (self.difficulty_multiplier - 1.0) * 0.5
