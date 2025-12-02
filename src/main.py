import pygame
import sys
from player import Player
from spawner import Spawner
from config_loader import ConfigLoader
from weapon import WeaponController
from gem import Gem
from camera import Camera
from upgrades import UpgradeManager
from chest import Chest
from particles import ParticleSystem
from items import Vacuum
from stats import GameStats
import random

def main():
    pygame.init()
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Vampire Slopvivors")
    clock = pygame.time.Clock()

    # Config
    config_loader = ConfigLoader()

    # Joystick / Controller Setup
    pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    active_joystick = None
    if joysticks:
        active_joystick = joysticks[0]
        active_joystick.init()
        print(f"Detected controller: {active_joystick.get_name()}")

    # Stats
    stats = GameStats()
    stats.start_ticks = pygame.time.get_ticks()

    # Camera
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Groups
    all_sprites = pygame.sprite.Group()
    enemies_group = pygame.sprite.Group()
    projectiles_group = pygame.sprite.Group()
    gems_group = pygame.sprite.Group()
    chests_group = pygame.sprite.Group()
    items_group = pygame.sprite.Group()
    
    # Player (spawn at 0,0 world coordinates)
    player = Player((0, 0), joystick=active_joystick)
    all_sprites.add(player)

    # Weapon Controller
    weapon_controller = WeaponController(player, all_sprites, projectiles_group, enemies_group, config_loader, stats)
    weapon_controller.add_weapon('whip') # Start with whip
    weapon_controller.add_weapon('wand') # And wand for fun testing

    # Spawner
    spawner = Spawner(config_loader, player, all_sprites, enemies_group)

    # Particles
    particle_system = ParticleSystem(all_sprites)

    # Upgrades
    upgrade_manager = UpgradeManager(player, weapon_controller)
    game_state = "PLAYING" # PLAYING, LEVEL_UP, GAME_OVER, PAUSED
    upgrade_options = []
    selected_upgrade_index = 0
    
    # Input timer for menu navigation to prevent super fast scrolling
    menu_input_timer = 0
    MENU_INPUT_DELAY = 150 # ms

    running = True
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == "GAME_OVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                         # Restart Logic
                         # Reset Groups
                        all_sprites.empty()
                        enemies_group.empty()
                        projectiles_group.empty()
                        gems_group.empty()
                        chests_group.empty()
                        items_group.empty()
                        
                        # Reset Player
                        player = Player((0, 0), joystick=active_joystick)
                        all_sprites.add(player)
                        
                        # Reset Stats
                        stats.reset()
                        stats.start_ticks = pygame.time.get_ticks()
                        
                        # Reset Weapon Controller
                        weapon_controller = WeaponController(player, all_sprites, projectiles_group, enemies_group, config_loader, stats)
                        weapon_controller.add_weapon('whip')
                        weapon_controller.add_weapon('wand')
                        
                        # Reset Spawner
                        spawner = Spawner(config_loader, player, all_sprites, enemies_group)
                        
                        # Reset Upgrades
                        upgrade_manager = UpgradeManager(player, weapon_controller)
                        
                        # Reset Camera
                        camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
                        
                        game_state = "PLAYING"
                        continue # Skip other checks
                
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0: # A Button
                         # Restart Logic (Duplicate - ideally refactor into function but copy-paste safe for script)
                        all_sprites.empty()
                        enemies_group.empty()
                        projectiles_group.empty()
                        gems_group.empty()
                        chests_group.empty()
                        items_group.empty()
                        
                        player = Player((0, 0), joystick=active_joystick)
                        all_sprites.add(player)
                        
                        stats.reset()
                        stats.start_ticks = pygame.time.get_ticks()
                        
                        weapon_controller = WeaponController(player, all_sprites, projectiles_group, enemies_group, config_loader, stats)
                        weapon_controller.add_weapon('whip')
                        weapon_controller.add_weapon('wand')
                        
                        spawner = Spawner(config_loader, player, all_sprites, enemies_group)
                        upgrade_manager = UpgradeManager(player, weapon_controller)
                        camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
                        
                        game_state = "PLAYING"
                        continue

            # Pause Toggle
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    if game_state == "PLAYING":
                        game_state = "PAUSED"
                    elif game_state == "PAUSED":
                        game_state = "PLAYING"
            
            elif event.type == pygame.JOYBUTTONDOWN:
                # Start button is often 7 (Xbox/PS menu) or 9 (PS options)
                # We can check a range or specific button
                if event.button in [7, 9]: 
                    if game_state == "PLAYING":
                        game_state = "PAUSED"
                    elif game_state == "PAUSED":
                        game_state = "PLAYING"

            if game_state == "LEVEL_UP":
                choice = -1
                if event.type == pygame.KEYDOWN:
                    # Direct selection
                    if event.key == pygame.K_1: choice = 0
                    elif event.key == pygame.K_2: choice = 1
                    elif event.key == pygame.K_3: choice = 2
                    # Confirm selection
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        choice = selected_upgrade_index
                    # Navigation
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                         selected_upgrade_index = max(0, selected_upgrade_index - 1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                         selected_upgrade_index = min(len(upgrade_options) - 1, selected_upgrade_index + 1)
                
                elif event.type == pygame.JOYBUTTONDOWN:
                    # Button 0 is usually A/Cross -> Confirm
                    if event.button == 0:
                        choice = selected_upgrade_index
                    
                if choice != -1 and choice < len(upgrade_options):
                    upgrade_manager.apply_upgrade(upgrade_options[choice])
                    game_state = "PLAYING"

        if game_state == "PLAYING":
            # Update
            spawner.update()
            weapon_controller.update()
            particle_system.update()
            
            # Update Sprites
            # Manually update enemies to pass the group for separation logic
            # This is slightly inefficient iterating twice (once in update, once in draw/move) 
            # but update() needs group context now.
            # Actually all_sprites.update() calls update on everyone. 
            # We can override the update call or just loop.
            
            player.update()
            enemies_group.update(enemies_group) # Pass group to enemies
            projectiles_group.update()
            gems_group.update()
            items_group.update()
            chests_group.update()
            
            # Update Camera
            camera.update(player)

            # Collision: Projectiles vs Enemies
            hits = pygame.sprite.groupcollide(enemies_group, projectiles_group, False, False)
            for enemy, projectiles in hits.items():
                for proj in projectiles:
                    # Check if projectile already hit this enemy (for piercing logic if needed)
                    # For now simple:
                    damage = proj.damage
                    stats.damage_dealt += damage
                    
                    if enemy.take_damage(damage):
                        # Enemy Died
                        stats.enemies_killed += 1
                        particle_system.create_explosion(enemy.rect.center, enemy.config.get('color', (255,0,0)))
                    
                        # Check if boss (hacky check for now, can be improved)
                        is_boss = enemy.config.get('is_boss', False)
                        if is_boss:
                            chest = Chest(enemy.rect.center)
                            all_sprites.add(chest)
                            chests_group.add(chest)
                        else:
                            # Spawn Vacuum (Rare)
                            if random.random() < 0.005: # 0.5% chance
                                vacuum_item = Vacuum(enemy.rect.center)
                                all_sprites.add(vacuum_item)
                                items_group.add(vacuum_item)
                            
                            # Spawn Gem
                            gem = Gem(enemy.rect.center, player, enemy.xp_value)
                            all_sprites.add(gem)
                            gems_group.add(gem)
                        
                        break # Stop processing projectiles for this dead enemy
                    else:
                        # Hit effect
                        particle_system.create_hit(proj.rect.center)

                    # If projectile is not piercing, kill it (unless it's melee which usually pierces)
                    if getattr(proj, 'penetration', 1) <= 1:
                        proj.kill()
                    else:
                        proj.penetration -= 1

            # Collision: Player vs Enemies
            enemy_hits = pygame.sprite.spritecollide(player, enemies_group, False)
            if enemy_hits:
                # Just take damage from the first one for simplicity, or sum them up?
                # Usually collisions are continuous, so 1 hit per frame check is enough with iframes
                damage = enemy_hits[0].damage
                if player.take_damage(damage):
                    game_state = "GAME_OVER"
                    stats.end_ticks = pygame.time.get_ticks()
                    print("Game Over")
                else:
                    # Player hit effect if not dead (and maybe even if i-frames are active? no, only when dmg taken)
                    # But take_damage returns True only on death. We need to check if dmg was actually taken for particles.
                    pass # TODO: Add visual feedback for player damage

            # Collision: Player vs Gems
            gem_hits = pygame.sprite.spritecollide(player, gems_group, True)
            for gem in gem_hits:
                if player.gain_xp(gem.value): # Returns True if level up
                     game_state = "LEVEL_UP"
                     upgrade_options = upgrade_manager.get_options()

            # Collision: Player vs Chests
            chest_hits = pygame.sprite.spritecollide(player, chests_group, True)
            if chest_hits:
                # Treat like a level up but maybe better options?
                # For now reuse level up logic for simplicity
                game_state = "LEVEL_UP"
                upgrade_options = upgrade_manager.get_options(5) # Get 5 options for chest

            # Collision: Player vs Items (Vacuum)
            item_hits = pygame.sprite.spritecollide(player, items_group, True)
            for item in item_hits:
                if isinstance(item, Vacuum):
                    for gem in gems_group:
                        gem.vacuum()

        # Draw
        screen.fill((30, 30, 30))
        
        # Draw Grid/Background (Simple infinite grid)
        # We draw lines based on camera position to give movement sensation
        grid_size = 64
        start_x = (camera.camera.x % grid_size)
        start_y = (camera.camera.y % grid_size)
        
        for x in range(start_x, SCREEN_WIDTH, grid_size):
            pygame.draw.line(screen, (40, 40, 40), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(start_y, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(screen, (40, 40, 40), (0, y), (SCREEN_WIDTH, y))

        # Draw all sprites with camera offset
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))
        
        # UI
        font = pygame.font.SysFont(None, 24)
        hp_text = font.render(f"HP: {player.hp}/{player.max_hp}", True, (255, 255, 255))
        xp_text = font.render(f"LVL: {player.level} XP: {player.xp}/{player.next_level_xp}", True, (255, 255, 255))
        screen.blit(hp_text, (10, 10))
        screen.blit(xp_text, (10, 40))
        
        if game_state == "LEVEL_UP":
            # Handle continuous joystick input for menu navigation
            current_time = pygame.time.get_ticks()
            if current_time - menu_input_timer > MENU_INPUT_DELAY:
                if active_joystick:
                    # Check axes (Left Stick or D-Pad)
                    axis_y = active_joystick.get_axis(1)
                    hat_y = 0
                    if active_joystick.get_numhats() > 0:
                        hat_y = active_joystick.get_hat(0)[1] # Tuple (x, y), y is usually flipped? Up is 1, Down is -1 usually?
                        # Pygame hats: (x, y). y: 1 is up, -1 is down.
                        
                    if axis_y < -0.5 or hat_y == 1: # Up
                        if selected_upgrade_index > 0:
                            selected_upgrade_index -= 1
                            menu_input_timer = current_time
                    elif axis_y > 0.5 or hat_y == -1: # Down
                        if selected_upgrade_index < len(upgrade_options) - 1:
                            selected_upgrade_index += 1
                            menu_input_timer = current_time

            upgrade_manager.draw_menu(screen, upgrade_options, selected_upgrade_index)
        
        if game_state == "PAUSED":
            # Pause Overlay
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            font_title = pygame.font.SysFont(None, 64)
            title = font_title.render("PAUSED", True, (255, 255, 255))
            screen.blit(title, (screen.get_width()//2 - title.get_width()//2, screen.get_height()//2))
            
        if game_state == "GAME_OVER":
            # Simple Game Over Screen
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((50, 0, 0, 230))
            screen.blit(overlay, (0, 0))
            
            font_title = pygame.font.SysFont(None, 64)
            font_stats = pygame.font.SysFont(None, 32)
            
            title = font_title.render("GAME OVER", True, (255, 0, 0))
            screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
            
            # Stats
            time_survived = stats.get_time_survived()
            lines = [
                f"Time Survived: {int(time_survived//60)}:{int(time_survived%60):02d}",
                f"Enemies Killed: {stats.enemies_killed}",
                f"Damage Dealt: {stats.damage_dealt}",
                f"Shots Fired: {stats.shots_fired}",
                f"Level Reached: {player.level}"
            ]
            
            y = 200
            for line in lines:
                text = font_stats.render(line, True, (255, 255, 255))
                screen.blit(text, (screen.get_width()//2 - text.get_width()//2, y))
                y += 40
                
            # Restart Prompt
            y += 50
            restart_text = font_stats.render("Press R or Button A to Restart", True, (255, 255, 0))
            screen.blit(restart_text, (screen.get_width()//2 - restart_text.get_width()//2, y))
        
        # Debug Info
        # font = pygame.font.SysFont(None, 24)
        # img = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
        # screen.blit(img, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
