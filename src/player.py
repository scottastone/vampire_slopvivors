import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, joystick=None):
        super().__init__()
        self.joystick = joystick
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 255, 255)) # Cyan player
        self.rect = self.image.get_rect(center=pos)
        
        # Stats
        self.speed = 3.0
        self.hp = 100
        self.max_hp = 100
        self.xp = 0
        self.level = 1
        self.next_level_xp = 10
        self.weapons = []
        
        # Movement vector
        self.velocity = pygame.math.Vector2(0, 0)
        self.last_move = pygame.math.Vector2(1, 0) # Default facing right
        
        # Invulnerability
        self.last_hit_time = 0
        self.iframe_duration = 500 # ms

    def take_damage(self, amount):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time > self.iframe_duration:
            self.hp -= amount
            self.last_hit_time = current_time
            print(f"Player took {amount} damage. HP: {self.hp}")
            if self.hp <= 0:
                self.hp = 0
                return True # Dead
        return False

    def heal(self, amount):
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        healed = self.hp - old_hp
        if healed > 0:
            print(f"Player healed {healed}. HP: {self.hp}")
            return True
        return False

    def get_input(self):
        self.velocity.x = 0
        self.velocity.y = 0
        
        # Keyboard Input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity.x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity.x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velocity.y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity.y = 1
            
        # Joystick Input
        if self.joystick:
            # Axis 0 is usually Left Stick X, Axis 1 is Left Stick Y
            jx = self.joystick.get_axis(0)
            jy = self.joystick.get_axis(1)
            
            # Deadzone
            if abs(jx) < 0.1: jx = 0
            if abs(jy) < 0.1: jy = 0
            
            if jx != 0 or jy != 0:
                self.velocity.x = jx
                self.velocity.y = jy

        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize() * self.speed
            self.last_move = self.velocity.copy()

    def update(self):
        self.get_input()
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        # Removed clamping to allow infinite movement
        
    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.next_level_xp:
            self.xp -= self.next_level_xp
            return self.level_up()
        return False

    def level_up(self):
        self.level += 1
        self.next_level_xp = int(self.next_level_xp * 1.5)
        print(f"Level Up! Level {self.level}")
        return True # Signal that level up happened
