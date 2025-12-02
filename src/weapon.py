import pygame
from projectile import Projectile, MeleeHitbox

class WeaponController:
    def __init__(self, player, all_sprites, projectiles_group, enemies_group, config_loader, stats):
        self.player = player
        self.all_sprites = all_sprites
        self.projectiles_group = projectiles_group
        self.enemies_group = enemies_group
        self.config_loader = config_loader
        self.stats = stats
        
        # Load all weapon definitions
        self.weapon_configs = self.config_loader.load_weapons()
        
        # Active weapons: list of dicts with state
        # e.g. {'id': 'wand', 'last_fired': 0, 'level': 1}
        self.active_weapons = []
        
    def add_weapon(self, weapon_id):
        if weapon_id in self.weapon_configs:
            self.active_weapons.append({
                'id': weapon_id,
                'last_fired': 0,
                'level': 1,
                'config': self.weapon_configs[weapon_id]
            })
            print(f"Added weapon: {self.weapon_configs[weapon_id]['name']}")

    def update(self):
        current_time = pygame.time.get_ticks()
        
        for weapon in self.active_weapons:
            config = weapon['config']
            cooldown = config.get('cooldown', 1000)
            
            if current_time - weapon['last_fired'] >= cooldown:
                weapon['last_fired'] = current_time
                self.fire_weapon(config)
                
    def fire_weapon(self, config):
        w_type = config.get('type', 'projectile')
        
        if w_type == 'projectile':
            # Find best target
            target = self.get_best_target()
            if target:
                proj = Projectile(self.player.rect.center, target, config)
                self.all_sprites.add(proj)
                self.projectiles_group.add(proj)
                self.stats.shots_fired += 1
            else:
                # Fire random direction if no enemies? or just right
                target_pos = self.player.rect.center + pygame.math.Vector2(100, 0)
                proj = Projectile(self.player.rect.center, target_pos, config)
                self.all_sprites.add(proj)
                self.projectiles_group.add(proj)
                self.stats.shots_fired += 1
                
        elif w_type == 'melee':
            melee = MeleeHitbox(self.player, config)
            self.all_sprites.add(melee)
            self.projectiles_group.add(melee)
            # Count melee swing as a shot? Sure.
            self.stats.shots_fired += 1

    def get_best_target(self):
        sprites = self.enemies_group.sprites()
        if not sprites:
            return None
            
        player_vec = pygame.math.Vector2(self.player.rect.center)
        
        # Filter enemies that are not "pending dead" (hp > pending_damage)
        candidates = [e for e in sprites if e.hp > e.pending_damage]
        
        if not candidates:
            # If all are pending dead, fallback to any enemy (closest)
            # to avoid not shooting at all (overkill is better than idle)
            candidates = sprites
            
        # Sort by distance
        nearest = min(candidates, key=lambda e: player_vec.distance_to(e.pos))
        return nearest
