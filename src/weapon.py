import pygame
from projectile import Projectile, MeleeHitbox, AxeProjectile, AuraHitbox

class WeaponController:
    def __init__(self, player, entity_manager, config_loader, stats):
        self.player = player
        self.entity_manager = entity_manager
        self.all_sprites = entity_manager.all_sprites
        self.projectiles_group = entity_manager.projectiles_group
        self.enemies_group = entity_manager.enemies_group
        self.config_loader = config_loader
        self.stats = stats
        
        # Load all weapon definitions
        self.weapon_configs = self.config_loader.load_weapons()
        
        # Active weapons: list of dicts with state
        self.active_weapons = []
        
        # Global Modifiers
        self.modifiers = {
            'amount': 0,
            'area': 1.0,
            'speed': 1.0,
            'duration': 1.0,
            'cooldown': 1.0
        }
        
    def add_weapon(self, weapon_id):
        # Check if already owned
        for w in self.active_weapons:
            if w['id'] == weapon_id:
                # Level up instead? For now just return
                return

        if weapon_id in self.weapon_configs:
            # Deep copy config so we can modify it per instance if needed
            import copy
            config = copy.deepcopy(self.weapon_configs[weapon_id])
            
            weapon_state = {
                'id': weapon_id,
                'last_fired': 0,
                'level': 1,
                'config': config,
                'instance': None # For persistent weapons like Aura
            }
            
            self.active_weapons.append(weapon_state)
            print(f"Added weapon: {config['name']}")
            
            # Initialize persistent weapons immediately
            if config.get('type') == 'aura':
                self.fire_weapon(weapon_state)

    def update(self):
        current_time = pygame.time.get_ticks()
        
        for weapon in self.active_weapons:
            config = weapon['config']
            
            # Apply cooldown modifier
            base_cooldown = config.get('cooldown', 1000)
            cooldown = base_cooldown * self.modifiers['cooldown']
            
            if current_time - weapon['last_fired'] >= cooldown:
                # For Aura, we don't "fire" repeatedly in the same way, 
                # but we might want to re-trigger or just let it exist.
                # Actually Aura is persistent.
                if config.get('type') != 'aura':
                    weapon['last_fired'] = current_time
                    self.fire_weapon(weapon)
                
    def fire_weapon(self, weapon_state):
        config = weapon_state['config']
        w_type = config.get('type', 'projectile')
        
        # Apply modifiers
        amount = 1 + self.modifiers['amount']
        
        if w_type == 'projectile':
            # Fire multiple projectiles if amount > 1
            for i in range(amount):
                target = self.get_best_target()
                if target:
                    # Add slight spread or delay for multiple?
                    # For simplicity, just fire at same target (or random if multiple)
                    proj = Projectile(self.player.rect.center, target, config)
                    self.all_sprites.add(proj)
                    self.projectiles_group.add(proj)
                    self.stats.shots_fired += 1
                else:
                    target_pos = self.player.rect.center + pygame.math.Vector2(100, 0)
                    proj = Projectile(self.player.rect.center, target_pos, config)
                    self.all_sprites.add(proj)
                    self.projectiles_group.add(proj)
                    self.stats.shots_fired += 1
                
        elif w_type == 'melee':
            # Whip
            # Amount could mean forward and backward?
            melee = MeleeHitbox(self.player, config)
            self.all_sprites.add(melee)
            self.projectiles_group.add(melee)
            self.stats.shots_fired += 1
            
            if amount > 1:
                # Fire backward too?
                # Implementation detail: MeleeHitbox needs to support direction override
                # For now, MVP: just one whip
                pass

        elif w_type == 'axe':
            for i in range(amount):
                axe = AxeProjectile(self.player.rect.center, config)
                # Spread X velocity slightly for multiple axes
                if i > 0:
                    axe.velocity.x += (i * 2) * (-1 if i % 2 == 0 else 1)
                
                self.all_sprites.add(axe)
                self.projectiles_group.add(axe)
                self.stats.shots_fired += 1

        elif w_type == 'aura':
            if weapon_state['instance'] is None or not weapon_state['instance'].alive():
                aura = AuraHitbox(self.player, config)
                self.all_sprites.add(aura)
                self.projectiles_group.add(aura) # Add to projectiles for collision checks
                weapon_state['instance'] = aura

    def get_best_target(self):
        sprites = self.enemies_group.sprites()
        if not sprites:
            return None
            
        player_vec = pygame.math.Vector2(self.player.rect.center)
        candidates = [e for e in sprites if e.hp > e.pending_damage]
        if not candidates:
            candidates = sprites
            
        nearest = min(candidates, key=lambda e: player_vec.distance_to(e.pos))
        return nearest
