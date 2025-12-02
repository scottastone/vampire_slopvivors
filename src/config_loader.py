import yaml
import os
import sys
import pygame

class ConfigLoader:
    _image_cache = {}

    def __init__(self, config_dir="config"):
        self.base_path = self.get_resource_path("")
        self.config_dir = os.path.join(self.base_path, config_dir)
        self.enemies = {}
        self.weapons = {}

    @staticmethod
    def get_resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
        
    def load_enemies(self):
        filepath = os.path.join(self.config_dir, "enemies.yaml")
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found.")
            return {}
        
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
            
        if data and 'enemies' in data:
            for enemy in data['enemies']:
                self.enemies[enemy['id']] = enemy
        return self.enemies

    def load_weapons(self):
        filepath = os.path.join(self.config_dir, "weapons.yaml")
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found.")
            return {}
            
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
            
        if data and 'weapons' in data:
            for weapon in data['weapons']:
                self.weapons[weapon['id']] = weapon
        return self.weapons

    @staticmethod
    def load_image(path, size=None):
        """Helper to load image or return None if not found/invalid. Caches images."""
        if not path: 
            return None
            
        # Handle resource path for frozen exe
        full_path = ConfigLoader.get_resource_path(path)
            
        # Create a cache key based on path and size
        cache_key = (full_path, size)
        
        if cache_key in ConfigLoader._image_cache:
            return ConfigLoader._image_cache[cache_key]
            
        if not os.path.exists(full_path):
            # Try relative to CWD if not found in meipass (fallback)
            if os.path.exists(path):
                full_path = path
            else:
                return None
            
        try:
            image = pygame.image.load(full_path).convert_alpha()
            if size:
                image = pygame.transform.scale(image, size)
            
            ConfigLoader._image_cache[cache_key] = image
            return image
        except pygame.error as e:
            print(f"Error loading image {full_path}: {e}")
            return None

# Simple test if run directly
if __name__ == "__main__":
    loader = ConfigLoader()
    print("Enemies:", loader.load_enemies().keys())
    print("Weapons:", loader.load_weapons().keys())
