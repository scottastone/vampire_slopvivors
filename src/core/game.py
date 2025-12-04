import pygame
import sys
from entities.player import Player
from entities.spawner import Spawner
from core.config_loader import ConfigLoader
from content.weapon import WeaponController
from core.camera import Camera
from content.upgrades import UpgradeManager
from content.particles import ParticleSystem
from core.stats import GameStats
from core.state_manager import StateManager
from entities.entity_manager import EntityManager
from core.profiler import Profiler
from core.director import Director

class Game:
    def __init__(self):
        pygame.init()
        self.SCREEN_WIDTH = 1280
        self.SCREEN_HEIGHT = 720
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Vampire Slopvivors")
        self.clock = pygame.time.Clock()
        
        # Config
        self.config_loader = ConfigLoader()
        
        # Joystick
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        self.active_joystick = None
        if self.joysticks:
            self.active_joystick = self.joysticks[0]
            self.active_joystick.init()
            print(f"Detected controller: {self.active_joystick.get_name()}")
            
        # Managers
        self.state_manager = StateManager()
        self.stats = GameStats()
        self.stats.start_ticks = pygame.time.get_ticks()
        self.profiler = Profiler()
        
        # Camera
        self.camera = Camera(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Menu vars
        self.upgrade_options = []
        self.selected_upgrade_index = 0
        self.menu_input_timer = 0
        self.MENU_INPUT_DELAY = 150
        
        # Initialize Game World
        self.init_game()
        
    def init_game(self):
        # Player
        self.player = Player((0, 0), joystick=self.active_joystick)
        
        # Entity Manager (Particle System set later to resolve circular dependency)
        self.entity_manager = EntityManager(self.player, self.stats, None)
        
        # Particles
        self.particle_system = ParticleSystem(self.entity_manager.all_sprites)
        self.entity_manager.particle_system = self.particle_system
        
        # Weapon Controller
        self.weapon_controller = WeaponController(self.player, self.entity_manager, self.config_loader, self.stats)
        self.weapon_controller.add_weapon('whip')
        self.weapon_controller.add_weapon('wand')
        
        # Director
        self.director = Director(self.player, self.stats)
        
        # Spawner
        self.spawner = Spawner(self.config_loader, self.player, self.entity_manager, self.director)
        
        # Upgrades
        self.upgrade_manager = UpgradeManager(self.player, self.weapon_controller)
        
        self.state_manager.change_state("PLAYING")

    def reset_game(self):
        self.stats.reset()
        self.stats.start_ticks = pygame.time.get_ticks()
        self.camera = Camera(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.init_game()

    def run(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.state_manager.is_state("GAME_OVER") or self.state_manager.is_state("VICTORY"):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                         self.reset_game()
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0: # A Button
                         self.reset_game()

            # Pause Toggle
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    if self.state_manager.is_state("PLAYING"):
                        self.state_manager.change_state("PAUSED")
                    elif self.state_manager.is_state("PAUSED"):
                        self.state_manager.change_state("PLAYING")
                
                elif event.key == pygame.K_F3:
                    self.profiler.toggle()
                
                # Debug Commands (Only if Profiler is enabled)
                if self.profiler.enabled:
                    if event.key == pygame.K_h:
                        self.spawner.spawn_horde()
                        print("Debug: Spawned Horde")
                    elif event.key == pygame.K_k:
                        self.entity_manager.kill_all_enemies()
                        print("Debug: Killed All Enemies")
                    elif event.key == pygame.K_i:
                        self.player.invincible = not self.player.invincible
                        print(f"Debug: Invincibility {'ON' if self.player.invincible else 'OFF'}")
            
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button in [7, 9]: 
                    if self.state_manager.is_state("PLAYING"):
                        self.state_manager.change_state("PAUSED")
                    elif self.state_manager.is_state("PAUSED"):
                        self.state_manager.change_state("PLAYING")

            if self.state_manager.is_state("LEVEL_UP"):
                self.handle_levelup_input(event)

    def handle_levelup_input(self, event):
        choice = -1
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: choice = 0
            elif event.key == pygame.K_2: choice = 1
            elif event.key == pygame.K_3: choice = 2
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                choice = self.selected_upgrade_index
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                 self.selected_upgrade_index = max(0, self.selected_upgrade_index - 1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                 self.selected_upgrade_index = min(len(self.upgrade_options) - 1, self.selected_upgrade_index + 1)
        
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                choice = self.selected_upgrade_index
            
        if choice != -1 and choice < len(self.upgrade_options):
            self.upgrade_manager.apply_upgrade(self.upgrade_options[choice])
            self.state_manager.change_state("PLAYING")

    def update(self):
        self.profiler.update()
        
        if self.state_manager.is_state("PLAYING"):
            self.profiler.start("update")
            self.director.update()
            self.spawner.update()
            self.weapon_controller.update()
            self.particle_system.update()
            self.entity_manager.update()
            self.camera.update(self.player)
            self.profiler.stop("update")
            
            # Check Game Over
            if self.entity_manager.check_player_collisions():
                self.state_manager.change_state("GAME_OVER")
                self.stats.end_ticks = pygame.time.get_ticks()
                print("Game Over")

            # Check Victory (15 Minutes)
            if self.stats.get_time_survived() >= 900: # 15 mins
                self.state_manager.change_state("VICTORY")
                self.stats.end_ticks = pygame.time.get_ticks()
                print("Victory!")

            # Check Level Up (Gems)
            if self.entity_manager.check_gem_collisions():
                self.state_manager.change_state("LEVEL_UP")
                self.upgrade_options = self.upgrade_manager.get_options()

            # Check Chests
            if self.entity_manager.check_chest_collisions():
                self.state_manager.change_state("LEVEL_UP")
                self.upgrade_options = self.upgrade_manager.get_options(5)

        elif self.state_manager.is_state("LEVEL_UP"):
            # Continuous input for menu
            current_time = pygame.time.get_ticks()
            if current_time - self.menu_input_timer > self.MENU_INPUT_DELAY:
                if self.active_joystick:
                    axis_y = self.active_joystick.get_axis(1)
                    hat_y = 0
                    if self.active_joystick.get_numhats() > 0:
                        hat_y = self.active_joystick.get_hat(0)[1]
                        
                    if axis_y < -0.5 or hat_y == 1: # Up
                        if self.selected_upgrade_index > 0:
                            self.selected_upgrade_index -= 1
                            self.menu_input_timer = current_time
                    elif axis_y > 0.5 or hat_y == -1: # Down
                        if self.selected_upgrade_index < len(self.upgrade_options) - 1:
                            self.selected_upgrade_index += 1
                            self.menu_input_timer = current_time

    def draw(self):
        self.screen.fill((30, 30, 30))
        
        # Grid
        grid_size = 64
        start_x = (self.camera.camera.x % grid_size)
        start_y = (self.camera.camera.y % grid_size)
        
        for x in range(start_x, self.SCREEN_WIDTH, grid_size):
            pygame.draw.line(self.screen, (40, 40, 40), (x, 0), (x, self.SCREEN_HEIGHT))
        for y in range(start_y, self.SCREEN_HEIGHT, grid_size):
            pygame.draw.line(self.screen, (40, 40, 40), (0, y), (self.SCREEN_WIDTH, y))

        # Entities
        self.entity_manager.draw(self.screen, self.camera)
        
        # UI
        self.draw_hud()
        
    def draw_hud(self):
        # Top Bar Background
        pygame.draw.rect(self.screen, (20, 20, 20), (0, 0, self.SCREEN_WIDTH, 60))
        pygame.draw.line(self.screen, (100, 100, 100), (0, 60), (self.SCREEN_WIDTH, 60), 2)
        
        font = pygame.font.SysFont(None, 24)
        font_large = pygame.font.SysFont(None, 36)
        
        # HP Bar (Top Left)
        hp_pct = max(0, self.player.hp / self.player.max_hp)
        bar_width = 200
        bar_height = 20
        x = 20
        y = 10
        
        # Background
        pygame.draw.rect(self.screen, (50, 0, 0), (x, y, bar_width, bar_height))
        # Foreground
        pygame.draw.rect(self.screen, (200, 0, 0), (x, y, int(bar_width * hp_pct), bar_height))
        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)
        
        hp_text = font.render(f"{int(self.player.hp)} / {self.player.max_hp}", True, (255, 255, 255))
        self.screen.blit(hp_text, (x + bar_width + 10, y + 2))
        
        # XP Bar (Below HP)
        xp_pct = max(0, self.player.xp / self.player.next_level_xp)
        y += 25
        
        # Background
        pygame.draw.rect(self.screen, (0, 0, 50), (x, y, bar_width, bar_height))
        # Foreground
        pygame.draw.rect(self.screen, (0, 100, 255), (x, y, int(bar_width * xp_pct), bar_height))
        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)
        
        lvl_text = font.render(f"LVL {self.player.level}", True, (255, 255, 0))
        self.screen.blit(lvl_text, (x + bar_width + 10, y + 2))
        
        # Timer (Top Center)
        time_survived = self.stats.get_time_survived()
        minutes = int(time_survived // 60)
        seconds = int(time_survived % 60)
        timer_text = font_large.render(f"{minutes:02d}:{seconds:02d}", True, (255, 255, 255))
        self.screen.blit(timer_text, (self.SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 15))
        
        # Kills (Top Right)
        kills_text = font_large.render(f"Kills: {self.stats.enemies_killed}", True, (255, 200, 200))
        self.screen.blit(kills_text, (self.SCREEN_WIDTH - kills_text.get_width() - 20, 15))
        
        self.profiler.draw(self.screen)
        
        if self.player.invincible:
            inv_text = font.render("INVINCIBLE", True, (255, 255, 0))
            self.screen.blit(inv_text, (self.SCREEN_WIDTH // 2 - inv_text.get_width() // 2, 50))
        
        if self.state_manager.is_state("LEVEL_UP"):
            self.upgrade_manager.draw_menu(self.screen, self.upgrade_options, self.selected_upgrade_index)
        
        if self.state_manager.is_state("PAUSED"):
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            font_title = pygame.font.SysFont(None, 64)
            title = font_title.render("PAUSED", True, (255, 255, 255))
            self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, self.screen.get_height()//2))
            
        if self.state_manager.is_state("GAME_OVER"):
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((50, 0, 0, 230))
            self.screen.blit(overlay, (0, 0))
            
            font_title = pygame.font.SysFont(None, 64)
            font_stats = pygame.font.SysFont(None, 32)
            
            title = font_title.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
            
            time_survived = self.stats.get_time_survived()
            lines = [
                f"Time Survived: {int(time_survived//60)}:{int(time_survived%60):02d}",
                f"Enemies Killed: {self.stats.enemies_killed}",
                f"Damage Dealt: {self.stats.damage_dealt}",
                f"Shots Fired: {self.stats.shots_fired}",
                f"Level Reached: {self.player.level}"
            ]
            
            y = 200
            for line in lines:
                text = font_stats.render(line, True, (255, 255, 255))
                self.screen.blit(text, (self.screen.get_width()//2 - text.get_width()//2, y))
                y += 40
                
            y += 50
            restart_text = font_stats.render("Press R or Button A to Restart", True, (255, 255, 0))
            self.screen.blit(restart_text, (self.screen.get_width()//2 - restart_text.get_width()//2, y))
            
        if self.state_manager.is_state("VICTORY"):
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 50, 0, 230))
            self.screen.blit(overlay, (0, 0))
            
            font_title = pygame.font.SysFont(None, 64)
            font_stats = pygame.font.SysFont(None, 32)
            
            title = font_title.render("VICTORY!", True, (255, 255, 0))
            self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 100))
            
            time_survived = self.stats.get_time_survived()
            lines = [
                f"Time Survived: {int(time_survived//60)}:{int(time_survived%60):02d}",
                f"Enemies Killed: {self.stats.enemies_killed}",
                f"Damage Dealt: {self.stats.damage_dealt}",
                f"Level Reached: {self.player.level}"
            ]
            
            y = 200
            for line in lines:
                text = font_stats.render(line, True, (255, 255, 255))
                self.screen.blit(text, (self.screen.get_width()//2 - text.get_width()//2, y))
                y += 40
                
            y += 50
            restart_text = font_stats.render("Press R or Button A to Restart", True, (255, 255, 0))
            self.screen.blit(restart_text, (self.screen.get_width()//2 - restart_text.get_width()//2, y))
        
        pygame.display.flip()
