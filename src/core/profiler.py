import pygame
import time

class Profiler:
    def __init__(self):
        self.enabled = False
        self.frame_count = 0
        self.last_time = time.time()
        self.fps = 0
        self.frame_time = 0
        self.timers = {}
        self.start_times = {}

    def toggle(self):
        self.enabled = not self.enabled
        print(f"Profiler {'Enabled' if self.enabled else 'Disabled'}")

    def start(self, name):
        if not self.enabled: return
        self.start_times[name] = time.perf_counter()

    def stop(self, name):
        if not self.enabled: return
        if name in self.start_times:
            duration = (time.perf_counter() - self.start_times[name]) * 1000 # ms
            self.timers[name] = duration

    def update(self):
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_time = current_time
            
        # Calculate frame time (approx)
        self.frame_time = 1000.0 / max(1, self.fps) if self.fps > 0 else 0

    def draw(self, screen):
        if not self.enabled: return
        
        font = pygame.font.SysFont("Consolas", 16)
        y = 80
        
        # Draw FPS and Frame Time
        fps_text = font.render(f"FPS: {self.fps}  Frame: {self.frame_time:.2f}ms", True, (0, 255, 0))
        screen.blit(fps_text, (10, y))
        y += 20
        
        # Draw Timers
        for name, duration in self.timers.items():
            color = (255, 255, 255)
            if duration > 10: color = (255, 100, 100) # Highlight slow
            text = font.render(f"{name}: {duration:.2f}ms", True, color)
            screen.blit(text, (10, y))
            y += 20
            
        # Entity Count (if available via game reference, or just generic)
        # We can add custom debug info here later
