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
        duration = self.end_ticks - self.start_ticks
        return duration / 1000.0
