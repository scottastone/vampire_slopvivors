import pygame
import random
from chest import Chest
from items import Vacuum, Heart
from gem import Gem

class EntityManager:
    def __init__(self, player, stats, particle_system):
        self.player = player
        self.stats = stats
        self.particle_system = particle_system
        
        # Groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies_group = pygame.sprite.Group()
        self.projectiles_group = pygame.sprite.Group()
        self.gems_group = pygame.sprite.Group()
        self.chests_group = pygame.sprite.Group()
        self.items_group = pygame.sprite.Group()
        
        # Add player to all_sprites
        self.all_sprites.add(self.player)

    def reset(self):
        self.all_sprites.empty()
        self.enemies_group.empty()
        self.projectiles_group.empty()
        self.gems_group.empty()
        self.chests_group.empty()
        self.items_group.empty()
        
        self.all_sprites.add(self.player)

    def update(self):
        self.player.update()
        self.enemies_group.update(self.enemies_group)
        self.projectiles_group.update()
        self.gems_group.update()
        self.items_group.update()
        self.chests_group.update()
        
        self.handle_collisions()

    def draw(self, screen, camera):
        for sprite in self.all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))

    def handle_collisions(self):
        # Collision: Projectiles vs Enemies
        hits = pygame.sprite.groupcollide(self.enemies_group, self.projectiles_group, False, False)
        for enemy, projectiles in hits.items():
            for proj in projectiles:
                damage = proj.damage
                self.stats.damage_dealt += damage
                
                if enemy.take_damage(damage):
                    # Enemy Died
                    self.stats.enemies_killed += 1
                    self.particle_system.create_explosion(enemy.rect.center, enemy.config.get('color', (255,0,0)))
                
                    # Check if boss
                    is_boss = enemy.config.get('is_boss', False)
                    if is_boss:
                        chest = Chest(enemy.rect.center)
                        self.all_sprites.add(chest)
                        self.chests_group.add(chest)
                    else:
                        # Spawn Chest (Very Rare)
                        if random.random() < 0.001: # 0.1% chance
                             chest = Chest(enemy.rect.center)
                             self.all_sprites.add(chest)
                             self.chests_group.add(chest)

                        # Spawn Vacuum (Rare)
                        elif random.random() < 0.005: # 0.5% chance
                            vacuum_item = Vacuum(enemy.rect.center)
                            self.all_sprites.add(vacuum_item)
                            self.items_group.add(vacuum_item)

                        # Spawn Heart (Rare)
                        elif random.random() < 0.005: # 0.5% chance
                            heart_item = Heart(enemy.rect.center)
                            self.all_sprites.add(heart_item)
                            self.items_group.add(heart_item)
                        
                        # Spawn Gem
                        gem = Gem(enemy.rect.center, self.player, enemy.xp_value)
                        self.all_sprites.add(gem)
                        self.gems_group.add(gem)
                    
                    break # Stop processing projectiles for this dead enemy
                else:
                    # Hit effect
                    self.particle_system.create_hit(proj.rect.center)

                # Projectile penetration logic
                if getattr(proj, 'penetration', 1) <= 1:
                    proj.kill()
                else:
                    proj.penetration -= 1

        # Collision: Player vs Items (Vacuum, Heart)
        item_hits = pygame.sprite.spritecollide(self.player, self.items_group, True)
        for item in item_hits:
            if isinstance(item, Vacuum):
                for gem in self.gems_group:
                    gem.vacuum()
            elif isinstance(item, Heart):
                self.player.heal(item.heal_amount)

    def check_player_collisions(self):
        # Returns True if player died
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies_group, False)
        if enemy_hits:
            damage = enemy_hits[0].damage
            if self.player.take_damage(damage):
                return True
        return False

    def check_gem_collisions(self):
        # Returns True if level up
        gem_hits = pygame.sprite.spritecollide(self.player, self.gems_group, True)
        for gem in gem_hits:
            if self.player.gain_xp(gem.value):
                return True
        return False

    def check_chest_collisions(self):
        # Returns True if chest collected
        chest_hits = pygame.sprite.spritecollide(self.player, self.chests_group, True)
        if chest_hits:
            return True
        return False
