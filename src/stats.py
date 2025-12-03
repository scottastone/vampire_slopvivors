class GameStats:
    def __init__(self):
        self.reset()

    def reset(self):
        self.enemies_killed = 0
        self.damage_dealt = 0
        self.shots_fired = 0
        self.start_ticks = 0
        self.end_ticks = 0
        
    def get_time_survived(self):
        # Returns seconds
        import pygame
        current = self.end_ticks if self.end_ticks > 0 else pygame.time.get_ticks()
        duration = current - self.start_ticks
        return duration / 1000.0
