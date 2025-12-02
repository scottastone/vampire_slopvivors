import random
import pygame

class UpgradeManager:
    def __init__(self, player, weapon_controller):
        self.player = player
        self.weapon_controller = weapon_controller
        self.possible_upgrades = [
            {'type': 'stat', 'stat': 'speed', 'amount': 0.5, 'name': 'Increase Speed', 'desc': 'Move 10% Faster'},
            {'type': 'stat', 'stat': 'max_hp', 'amount': 20, 'name': 'Max HP Up', 'desc': 'Increase Max HP by 20'},
            {'type': 'weapon_stat', 'stat': 'damage', 'amount': 2, 'name': 'Damage Up', 'desc': 'All weapons deal +2 damage'},
            {'type': 'weapon_stat', 'stat': 'cooldown', 'amount': 0.9, 'name': 'Fire Rate Up', 'desc': 'Weapons fire 10% faster'},
            {'type': 'heal', 'amount': 50, 'name': 'Heal', 'desc': 'Recover 50 HP'},
            # {'type': 'new_weapon', 'id': 'axe', 'name': 'New Weapon: Axe', 'desc': 'Throw axes in an arc'} # Example
        ]

    def get_options(self, count=3):
        # In a real game, you'd filter out maxed upgrades or already owned weapons
        return random.sample(self.possible_upgrades, k=min(count, len(self.possible_upgrades)))

    def apply_upgrade(self, upgrade):
        print(f"Applying upgrade: {upgrade['name']}")
        
        if upgrade['type'] == 'stat':
            current = getattr(self.player, upgrade['stat'])
            setattr(self.player, upgrade['stat'], current + upgrade['amount'])
            
            if upgrade['stat'] == 'max_hp':
                self.player.hp += upgrade['amount'] # heal the amount gained
                
        elif upgrade['type'] == 'heal':
            self.player.hp = min(self.player.max_hp, self.player.hp + upgrade['amount'])
            
        elif upgrade['type'] == 'weapon_stat':
            # Apply to all current and future weapons? 
            # For now, let's update all active weapons
            for weapon in self.weapon_controller.active_weapons:
                config = weapon['config']
                if upgrade['stat'] == 'damage':
                    config['damage'] = config.get('damage', 1) + upgrade['amount']
                elif upgrade['stat'] == 'cooldown':
                    config['cooldown'] = int(config.get('cooldown', 1000) * upgrade['amount'])
            
            # Note: This modifies the instance config in the controller, 
            # ideally we should track multipliers separately to avoid drift or issues with new weapons.
            # But this works for MVP.

    def draw_menu(self, screen, options, selected_index=0):
        # Simple overlay
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        font_title = pygame.font.SysFont(None, 48)
        font_opt = pygame.font.SysFont(None, 36)
        font_desc = pygame.font.SysFont(None, 24)
        
        title = font_title.render("LEVEL UP!", True, (255, 215, 0))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
        
        y = 200
        for i, opt in enumerate(options):
            is_selected = (i == selected_index)
            color = (255, 255, 0) if is_selected else (255, 255, 255)
            prefix = "> " if is_selected else ""
            
            text = f"{prefix}{i+1}. {opt['name']}"
            desc = opt['desc']
            
            surf_text = font_opt.render(text, True, color)
            surf_desc = font_desc.render(desc, True, (200, 200, 200))
            
            screen.blit(surf_text, (screen.get_width()//2 - surf_text.get_width()//2, y))
            screen.blit(surf_desc, (screen.get_width()//2 - surf_desc.get_width()//2, y + 30))
            y += 100
            
        hint = font_desc.render("Press A or Enter to select", True, (150, 150, 150))
        screen.blit(hint, (screen.get_width()//2 - hint.get_width()//2, y + 50))
