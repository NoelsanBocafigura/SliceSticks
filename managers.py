import pygame
import random
from config import *
from core import Singleton, EventBus
from entities import Enemy

class PhysicsManager(metaclass=Singleton):
    def __init__(self):
        self.player = None
        self.enemies = []
        self.arrows = []
        
        EventBus().subscribe("PLAYER_SPAWNED", self._on_player_spawned)
        EventBus().subscribe("ENEMY_SPAWNED", self._on_enemy_spawned)
        EventBus().subscribe("ENTITY_DIED", self._on_entity_died)
        EventBus().subscribe("SPAWN_PROJECTILE", self._on_spawn_projectile)

    def _on_spawn_projectile(self, x, y, facing, damage, **kwargs):
        from entities import Arrow
        self.arrows.append(Arrow(x, y, facing, damage))

    def _on_player_spawned(self, entity, **kwargs):
        self.player = entity

    def _on_enemy_spawned(self, entity, **kwargs):
        self.enemies.append(entity)

    def _on_entity_died(self, entity, **kwargs):
        if entity in self.enemies:
            self.enemies.remove(entity)

    def update(self):
        if not self.player: return

        if self.player.attack_rect and not self.player.has_dealt_damage:
            hit_registered = False
            for enemy in self.enemies:
                if enemy.rect.colliderect(self.player.attack_rect):
                    dmg = self.player.attack_power
                    is_crit = False
                    for fx in self.player.skill_effects:
                        if fx['type'] == 'mana_gloves':
                            dmg += fx['damage_boost']
                            is_crit = True
                    
                    enemy.take_damage(dmg, self.player.x, is_crit)
                    hit_registered = True
            
            if hit_registered:
                self.player.has_dealt_damage = True

        for enemy in self.enemies:
            if enemy.attack_rect and not enemy.has_dealt_damage:
                if self.player.rect.colliderect(enemy.attack_rect):
                    self.player.take_damage(enemy.attack_power, enemy.x)
                    enemy.has_dealt_damage = True

        for arrow in self.arrows[:]:
            arrow.update()
            hit = False
            for enemy in self.enemies:
                if enemy.rect.colliderect(arrow.rect):
                    enemy.take_damage(arrow.damage, arrow.x, False)
                    hit = True
            if hit or arrow.x < 0 or arrow.x > SCREEN_WIDTH:
                self.arrows.remove(arrow)

class CameraManager(metaclass=Singleton):
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0
        self.shake_magnitude = 0
        EventBus().subscribe("ENTITY_DAMAGED", self._on_entity_damaged)

    def _on_entity_damaged(self, damage, is_crit, **kwargs):
        shake_mag = 10 if is_crit else max(3, damage // 2)
        self.apply_shake(shake_mag)

    def apply_shake(self, magnitude):
        self.shake_magnitude = min(self.shake_magnitude + magnitude, 25)

    def update(self):
        if self.shake_magnitude > 0:
            self.offset_x = random.randint(-int(self.shake_magnitude), int(self.shake_magnitude))
            self.offset_y = random.randint(-int(self.shake_magnitude), int(self.shake_magnitude))
            self.shake_magnitude *= 0.85 
            if self.shake_magnitude < 1:
                self.shake_magnitude = 0
                self.offset_x = 0
                self.offset_y = 0

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-6, 6)
        self.vy = random.uniform(-8, 2)
        self.color = color
        self.life = 255
        self.size = random.randint(2, 5)

    def update(self):
        self.vy += GRAVITY * 0.8
        self.x += self.vx
        self.y += self.vy
        self.life -= 12 

    def draw(self, surface):
        if self.life > 0:
            part_surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(part_surf, (*self.color[:3], max(0, self.life)), (self.size, self.size), self.size)
            surface.blit(part_surf, (self.x - self.size, self.y - self.size))

class FloatingText:
    def __init__(self, x, y, text, color=WHITE):
        self.x = x
        self.y = y
        self.vy = -3
        self.text = text
        self.color = color
        self.alpha = 255
        self.font = pygame.font.Font(None, 40)

    def update(self):
        self.y += self.vy
        self.vy *= 0.9 
        self.alpha -= 6

    def draw(self, surface):
        if self.alpha > 0:
            text_surf = self.font.render(self.text, True, self.color)
            text_surf.set_alpha(max(0, self.alpha))
            outline_surf = self.font.render(self.text, True, BLACK)
            outline_surf.set_alpha(max(0, self.alpha))
            for dx in [-1, 1]:
                for dy in [-1, 1]:
                    surface.blit(outline_surf, (self.x + dx, self.y + dy))
            surface.blit(text_surf, (self.x, self.y))

class VFXManager(metaclass=Singleton):
    def __init__(self):
        self.particles = []
        self.texts = []
        self.hit_stop = 0
        EventBus().subscribe("ENTITY_DAMAGED", self._on_entity_damaged)

    def _on_entity_damaged(self, target, damage, is_crit, **kwargs):
        color = YELLOW if is_crit else WHITE
        self.spawn_text(target.x, target.y - 100, str(int(damage)), color)
        self.spawn_particles(target.x, target.y - 30, BLOOD_COLOR, count=15)
        self.hit_stop = 3  

    def spawn_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def spawn_text(self, x, y, text, color):
        self.texts.append(FloatingText(x, y, text, color))

    def update(self):
        if self.hit_stop > 0:
            self.hit_stop -= 1

        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)
                
        for t in self.texts[:]:
            t.update()
            if t.alpha <= 0:
                self.texts.remove(t)

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
        for t in self.texts:
            t.draw(surface)

class WaveManager(metaclass=Singleton):
    def __init__(self):
        self.wave = 0
        self.enemies = []
        self.enemies_to_spawn = 0
        self.spawn_timer = 0
        self.wave_active = False
        self.total_kills = 0
        
        EventBus().subscribe("ENTITY_DIED", self._on_entity_died)
        
    def _on_entity_died(self, entity, **kwargs):
        if isinstance(entity, Enemy):
            if entity in self.enemies:
                self.enemies.remove(entity)

            # --- BOSS SPAWN LOGIC ---
            self.total_kills += 1
            if self.total_kills == BOSS_KILL_THRESHOLD:
                from entities import Boss
                # Spawn the boss right in the middle of the screen
                self.enemies.append(Boss(SCREEN_WIDTH // 2, GROUND_Y, self.wave))

    def start_next_wave(self):
        self.wave += 1
        self.enemies_to_spawn = self.wave + 2
        self.spawn_timer = 60
        self.wave_active = True

    def update(self, player):
        if not self.wave_active: return

        if self.enemies_to_spawn > 0:
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                level = max(1, self.wave + random.randint(-1, 1))
                side = random.choice([-1, 1])
                spawn_x = player.x + (side * 500)
                spawn_x = max(50, min(SCREEN_WIDTH-50, spawn_x))
                self.enemies.append(Enemy(spawn_x, GROUND_Y, level))
                self.enemies_to_spawn -= 1
                self.spawn_timer = 90

        if self.enemies_to_spawn <= 0 and len(self.enemies) == 0:
            self.wave_active = False
            player.tokens += 10 * self.wave