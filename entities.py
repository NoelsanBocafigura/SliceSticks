import pygame
import math
import random
from abc import ABC, abstractmethod
from config import *
from core import EventBus
from skills import ManaGlovesSkill, ManaSurgeSkill

SILVER_WHITE = (230, 235, 245)

IDLE_POSES = [
    ((6, 22), (9, 45), (-6, 22), (-9, 45), (6, 25), (12, 50), (-6, 25), (-12, 50), 0),   
    ((8, 24), (11, 48), (-8, 24), (-11, 48), (8, 22), (15, 48), (-8, 22), (-15, 48), 3) 
]

WALK_POSES = [
    ((-12, 22), (-25, 42), (12, 22), (25, 42), (15, 25), (25, 48), (-10, 25), (-25, 48), 0), 
    ((0, 24), (0, 46), (0, 24), (0, 46), (0, 25), (0, 50), (15, 20), (5, 35), 4),            
    ((12, 22), (25, 42), (-12, 22), (-25, 42), (-10, 25), (-25, 48), (15, 25), (25, 48), 0), 
    ((0, 24), (0, 46), (0, 24), (0, 46), (15, 20), (5, 35), (0, 25), (0, 50), 4),            
]

WINDUP_ARMS = ((-15, 18), (-20, 10), (6, 18), (12, 24))
STRIKE_ARMS = ((25, -5), (48, -5), (-15, 22), (-10, 15))

# Both arms stretched forward. Slightly offset from each other for 3D depth!
CHARGE_ARMS = ((25, 0), (45, 0), (20, 5), (40, 5))

SWORD_WINDUP = ((-5, -22), (-10, -45), (5, 22), (10, 44))
SWORD_DOWN_SLASH = ((20, -11), (40, 5), (-5, 22), (-10, 44))
SWORD_SWEEP_WINDUP = ((-15, 17), (-30, 34), (15, 17), (30, 34))
SWORD_SWEEP = ((22, 6), (44, 12), (-15, 17), (-30, 34))

# Axe utilizes heavy overhead and sweeping extensions
AXE_WINDUP = ((-10, -20), (-20, -40), (5, 22), (10, 44))
AXE_DOWN = ((22, 6), (44, 15), (-5, 22), (-10, 44))
AXE_UP_WINDUP = ((22, 6), (44, 15), (-5, 22), (-10, 44))
AXE_UP = ((-10, -20), (-20, -40), (5, 22), (10, 44))
AXE_SWEEP = ((22, 6), (44, 12), (-15, 17), (-30, 34))

BOW_DRAW = ((23, 0), (46, 0), (-20, 11), (0, 0))

class Arrow:
    def __init__(self, x, y, facing, damage):
        self.x = x
        self.y = y
        self.facing = facing
        self.damage = damage
        self.speed = 15
        self.rect = pygame.Rect(x, y, 30, 10)
        self.active = True

    def update(self):
        self.x += self.speed * self.facing
        self.rect.x = self.x

    def draw(self, surface):
        end_x = self.x + 30 * self.facing
        pygame.draw.line(surface, SILVER_WHITE, (self.x, self.y), (end_x, self.y), 3)
        # Arrowhead
        pygame.draw.polygon(surface, WHITE, [(end_x, self.y), (end_x - 5*self.facing, self.y - 4), (end_x - 5*self.facing, self.y + 4)])

class Animator:
    def __init__(self, color):
        self.color = color
        self.hit_flash = 0
        self.squash = 1.0
        self.stretch = 1.0
        self.frame_index = 0.0  
        self.current_state = "IDLE"

        # Specific attributes for boss character
        self.thickness_mult = 1.0
        self.scale_mult = 1.0
        self.fixed_opacity = None

    def _lerp(self, a, b, t):
        if isinstance(a, tuple):
            return tuple(self._lerp(a_val, b_val, t) for a_val, b_val in zip(a, b))
        return a + (b - a) * t

    def _draw_limb(self, surface, color, start, end, thickness):
        start_int = (int(start[0]), int(start[1]))
        end_int = (int(end[0]), int(end[1]))
        pygame.draw.line(surface, color, start_int, end_int, int(thickness))

        radius = thickness // 2
        if radius > 0:
            pygame.draw.circle(surface, color, start, radius)
            pygame.draw.circle(surface, color, end, radius)

    def _draw_weapon(self, surface, x, y, facing, weapon_name, hand_pos, elbow_pos, attack_type, hand2_pos=None):
        hx, hy = x + hand_pos[0] * facing, y + hand_pos[1]
        ex, ey = x + elbow_pos[0] * facing, y + elbow_pos[1]
        dx, dy = hx - ex, hy - ey
        dist = math.hypot(dx, dy) or 1
        nx, ny = dx / dist, dy / dist
        
        if weapon_name == "Sword":
            sword_len = 45
            tip_x, tip_y = hx + nx * sword_len, hy + ny * sword_len
            pygame.draw.line(surface, SILVER_WHITE, (hx, hy), (tip_x, tip_y), 4)
            gx, gy = -ny * 8, nx * 8
            pygame.draw.line(surface, YELLOW, (hx + nx*5 - gx, hy + ny*5 - gy), (hx + nx*5 + gx, hy + ny*5 + gy), 3)

        elif weapon_name == "Axe":
            handle_len = 40
            tip_x, tip_y = hx + nx * handle_len, hy + ny * handle_len
            pygame.draw.line(surface, (139, 69, 19), (hx - nx*10, hy - ny*10), (tip_x, tip_y), 5)
            bx, by = tip_x - nx*10, tip_y - ny*10
            cx1, cy1 = bx + nx*15 - ny*15, by + ny*15 + nx*15
            cx2, cy2 = bx + ny*12, by - nx*12
            pygame.draw.polygon(surface, SILVER_WHITE, [(bx, by), (cx1, cy1), (cx2, cy2)])

        elif weapon_name == "Bow":
            bow_len = 3
            top_x, top_y = hx - nx*10 - ny * bow_len, hy - ny*10 + nx * bow_len
            bot_x, bot_y = hx - nx*10 + ny * bow_len, hy - ny*10 - nx * bow_len
            
            # Center the grip precisely on the hand coordinates (hx, hy)
            mid_top_x, mid_top_y = hx - ny*20, hy + nx*20
            mid_bot_x, mid_bot_y = hx + ny*20, hy - nx*20
            
            pygame.draw.line(surface, (139, 69, 19), (top_x, top_y), (mid_top_x, mid_top_y), 3)
            
            pygame.draw.line(surface, (139, 69, 19), (top_x, top_y), (mid_top_x, mid_top_y), 3)
            pygame.draw.line(surface, (139, 69, 19), (mid_top_x, mid_top_y), (mid_bot_x, mid_bot_y), 3)
            pygame.draw.line(surface, (139, 69, 19), (mid_bot_x, mid_bot_y), (bot_x, bot_y), 3)
            
            pull_x, pull_y = x - 5 * facing, y - 5
            if attack_type == "BOW_DRAW" and hand2_pos:
                # The string dynamically follows the second hand's X and Y positionn
                pull_x = x + hand2_pos[0] * facing 
                pull_y = y + hand2_pos[1]
                
                pygame.draw.line(surface, WHITE, (top_x, top_y), (pull_x, pull_y), 1)
                pygame.draw.line(surface, WHITE, (bot_x, bot_y), (pull_x, pull_y), 1)
                # Draw the arrow resting on the string
                pygame.draw.line(surface, SILVER_WHITE, (pull_x, pull_y), (hx + nx*5, hy + ny*5), 2)
            else:
                # Resting string state
                pygame.draw.line(surface, WHITE, (top_x, top_y), (bot_x, bot_y), 1)

    def update(self, is_grounded, vy, vx, attack_cd):
        if self.hit_flash > 0: self.hit_flash -= 1
            
        prev_state = self.current_state
        if abs(vx) > 0.1 and is_grounded:
            self.current_state = "WALK"
            anim_speed = abs(vx) * 0.03  
        else:
            self.current_state = "IDLE"
            anim_speed = 0.08

        if prev_state != self.current_state:
            self.frame_index = 0

        poses = IDLE_POSES if self.current_state == "IDLE" else WALK_POSES
        self.frame_index = (self.frame_index + anim_speed) % len(poses)

        target_s = (1.0, 1.0) 
        self.stretch += (target_s[0] - self.stretch) * 0.3
        self.squash += (target_s[1] - self.squash) * 0.3

    def draw(self, surface, x, y, facing, attack_cd, level, weapon="Fists", attack_type=""):
        base_thickness = int(max(4, level // 2 + 4) * self.thickness_mult)
        
        if self.fixed_opacity is not None:
            opacity = self.fixed_opacity
        else:
            opacity = min(255, 100 + level * 15)

        draw_color = (*(WHITE if self.hit_flash > 0 else self.color)[:3], opacity)

        poses = IDLE_POSES if self.current_state == "IDLE" else WALK_POSES
        idx = int(self.frame_index)
        next_idx = (idx + 1) % len(poses)
        t = self.frame_index - idx 

        p1, p2 = poses[idx], poses[next_idx]
        elbow1 = self._lerp(p1[0], p2[0], t)
        hand1  = self._lerp(p1[1], p2[1], t)
        elbow2 = self._lerp(p1[2], p2[2], t)
        hand2  = self._lerp(p1[3], p2[3], t)
        knee1  = self._lerp(p1[4], p2[4], t)
        foot1  = self._lerp(p1[5], p2[5], t)
        knee2  = self._lerp(p1[6], p2[6], t)
        foot2  = self._lerp(p1[7], p2[7], t)
        bob    = self._lerp(p1[8], p2[8], t)

        if attack_cd > 0:
            base_arms = (elbow1, hand1, elbow2, hand2)
            
            if attack_type == "CHARGE":
                current_arms = CHARGE_ARMS
            elif weapon == "Sword":
                if attack_type == "SWORD_SLASH":
                    if attack_cd > 12: 
                        lerp_t = (20 - attack_cd) / 8.0
                        current_arms = self._lerp(base_arms, SWORD_WINDUP, lerp_t)
                    elif attack_cd > 8: 
                        lerp_t = (12 - attack_cd) / 4.0
                        current_arms = self._lerp(SWORD_WINDUP, SWORD_DOWN_SLASH, lerp_t)
                    else: 
                        lerp_t = (8 - attack_cd) / 8.0
                        current_arms = self._lerp(SWORD_DOWN_SLASH, base_arms, lerp_t)
                else:
                    if attack_cd > 12: 
                        lerp_t = (20 - attack_cd) / 8.0
                        current_arms = self._lerp(base_arms, SWORD_SWEEP_WINDUP, lerp_t)
                    elif attack_cd > 8: 
                        lerp_t = (12 - attack_cd) / 4.0
                        current_arms = self._lerp(SWORD_SWEEP_WINDUP, SWORD_SWEEP, lerp_t)
                    else: 
                        lerp_t = (8 - attack_cd) / 8.0
                        current_arms = self._lerp(SWORD_SWEEP, base_arms, lerp_t)
            elif weapon == "Axe":
                if attack_type == "AXE_SLASH":
                    if attack_cd > 16: 
                        lerp_t = (25 - attack_cd) / 9.0
                        current_arms = self._lerp(base_arms, AXE_WINDUP, lerp_t)
                    elif attack_cd > 10: 
                        lerp_t = (16 - attack_cd) / 6.0
                        current_arms = self._lerp(AXE_WINDUP, AXE_DOWN, lerp_t)
                    else: 
                        lerp_t = (10 - attack_cd) / 10.0
                        current_arms = self._lerp(AXE_DOWN, base_arms, lerp_t)
                elif attack_type == "AXE_UP":
                    if attack_cd > 16: 
                        lerp_t = (25 - attack_cd) / 9.0
                        current_arms = self._lerp(base_arms, AXE_UP_WINDUP, lerp_t)
                    elif attack_cd > 10: 
                        lerp_t = (16 - attack_cd) / 6.0
                        current_arms = self._lerp(AXE_UP_WINDUP, AXE_UP, lerp_t)
                    else: 
                        lerp_t = (10 - attack_cd) / 10.0
                        current_arms = self._lerp(AXE_UP, base_arms, lerp_t)
                else: 
                    if attack_cd > 16: 
                        lerp_t = (25 - attack_cd) / 9.0
                        current_arms = self._lerp(base_arms, AXE_WINDUP, lerp_t)
                    elif attack_cd > 10: 
                        lerp_t = (16 - attack_cd) / 6.0
                        current_arms = self._lerp(AXE_WINDUP, AXE_SWEEP, lerp_t)
                    else: 
                        lerp_t = (10 - attack_cd) / 10.0
                        current_arms = self._lerp(AXE_SWEEP, base_arms, lerp_t)
            elif weapon == "Bow":
                if attack_cd > 5: 
                    lerp_t = min(1.0, (25 - attack_cd) / 10.0)
                    current_arms = self._lerp(base_arms, BOW_DRAW, lerp_t)
                else: 
                    lerp_t = (5 - attack_cd) / 5.0
                    current_arms = self._lerp(BOW_DRAW, base_arms, lerp_t)
            else: 
                if attack_cd > 11: 
                    lerp_t = (15 - attack_cd) / 4.0
                    current_arms = self._lerp(base_arms, WINDUP_ARMS, lerp_t)
                elif attack_cd > 6: 
                    lerp_t = (11 - attack_cd) / 5.0
                    current_arms = self._lerp(WINDUP_ARMS, STRIKE_ARMS, lerp_t)
                else: 
                    lerp_t = (6 - attack_cd) / 6.0
                    current_arms = self._lerp(STRIKE_ARMS, base_arms, lerp_t)
                
            elbow1, hand1, elbow2, hand2 = current_arms

        fig_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        cx, cy = 100, 100
        
        head_y, neck_y, hip_y, sh_y = cy-60+bob, cy-44+bob, cy+10+bob, cy-40+bob

        self._draw_limb(fig_surf, draw_color, (cx, sh_y), (cx + elbow2[0], sh_y + elbow2[1]), base_thickness)
        self._draw_limb(fig_surf, draw_color, (cx + elbow2[0], sh_y + elbow2[1]), (cx + hand2[0], sh_y + hand2[1]), base_thickness)
        
        self._draw_limb(fig_surf, draw_color, (cx, hip_y), (cx + knee2[0], hip_y + knee2[1]), base_thickness)
        self._draw_limb(fig_surf, draw_color, (cx + knee2[0], hip_y + knee2[1]), (cx + foot2[0], hip_y + foot2[1]), base_thickness)

        pygame.draw.circle(fig_surf, draw_color, (cx, head_y), 16, base_thickness)
        self._draw_limb(fig_surf, draw_color, (cx, neck_y), (cx, hip_y), base_thickness)

        self._draw_limb(fig_surf, draw_color, (cx, hip_y), (cx + knee1[0], hip_y + knee1[1]), base_thickness)
        self._draw_limb(fig_surf, draw_color, (cx + knee1[0], hip_y + knee1[1]), (cx + foot1[0], hip_y + foot1[1]), base_thickness)
        
        self._draw_limb(fig_surf, draw_color, (cx, sh_y), (cx + elbow1[0], sh_y + elbow1[1]), base_thickness)
        self._draw_limb(fig_surf, draw_color, (cx + elbow1[0], sh_y + elbow1[1]), (cx + hand1[0], sh_y + hand1[1]), base_thickness)

        if weapon != "Fists":
            self._draw_weapon(fig_surf, cx, sh_y, 1, weapon, hand1, elbow1, attack_type, hand2)
        elif attack_cd > 0 and 6 < attack_cd <= 10:
            pygame.draw.line(fig_surf, (*SILVER_WHITE[:3], opacity), (cx + 30, sh_y - 5), (cx + 60, sh_y - 5), 6)

        if facing == -1: fig_surf = pygame.transform.flip(fig_surf, True, False)

        sw, sh = int(200 * self.squash * self.scale_mult), int(200 * self.stretch * self.scale_mult)
        surface.blit(pygame.transform.scale(fig_surf, (sw, sh)), (x - 100*self.squash*self.scale_mult, y - 150*self.stretch*self.scale_mult))

class StickFigure(ABC):
    def __init__(self, x, y, color, level=1):
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0
        self.level, self.facing = level, 1  
        self.is_dead, self.is_grounded = False, False
        self.max_hp = 50 + level * 10
        self.hp = self.max_hp
        self.display_hp = self.max_hp 
        self.attack_power = 10 + level * 2
        self.defense = 5 + level * 1
        self.max_mana = 30 + level * 5
        self.mana = self.max_mana
        self.attack_cooldown, self.attack_rect = 0, None
        self.has_dealt_damage = False 
        self.knockback_vx, self.knockback_vy = 0, 0
        self.animator = Animator(color)
        self.skill_effects = []
        self.rect = pygame.Rect(x - 20, y - 60, 40, 80)

    def update(self):
        self.vy += GRAVITY
        self.knockback_vx *= 0.85
        self.x += self.vx + self.knockback_vx
        self.y += self.vy + self.knockback_vy

        if self.y >= GROUND_Y:
            self.y, self.vy, self.knockback_vy, self.is_grounded = GROUND_Y, 0, 0, True
        else:
            self.is_grounded = False

        self.rect.x, self.rect.y = self.x - 20, self.y - 80

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            if 5 < self.attack_cooldown <= 8:
                aw = 50 + self.level * 2  
                rx = self.x if self.facing == 1 else self.x - aw
                self.attack_rect = pygame.Rect(rx, self.y - 60, aw, 60)
            else:
                self.attack_rect = None
        else:
            self.has_dealt_damage = False
            self.attack_rect = None

        if self.display_hp > self.hp:
            self.display_hp -= max(0.5, (self.display_hp - self.hp) * 0.1)

        self.animator.update(self.is_grounded, self.vy, self.vx, self.attack_cooldown)

        for fx in self.skill_effects[:]:
            fx['duration'] -= 1
            if fx['duration'] <= 0:
                if 'remove' in fx: fx['remove']()
                self.skill_effects.remove(fx)

    def draw(self, surface):
        weapon = getattr(self, 'weapon', 'Fists')
        attack_type = getattr(self, 'current_attack', '')
        
        self.animator.draw(surface, self.x, self.y, self.facing, self.attack_cooldown, self.level, weapon, attack_type)
        
        if self.display_hp < self.max_hp and not self.is_dead:
            bar_w = 60
            
            scale = getattr(self.animator, 'scale_mult', 1.0)
            stretch = getattr(self.animator, 'stretch', 1.0)
            y_pos = self.y - (140 * stretch * scale)
            bar_x = self.x - (bar_w // 2)
            
            # Draw the UI bars
            pygame.draw.rect(surface, DARK_GRAY, (bar_x, y_pos, bar_w, 6))
            pygame.draw.rect(surface, YELLOW, (bar_x, y_pos, int((self.display_hp / self.max_hp) * bar_w), 6))
            pygame.draw.rect(surface, RED, (bar_x, y_pos, int((max(0, self.hp) / self.max_hp) * bar_w), 6))

    def attack(self):
        if self.attack_cooldown <= 0:
            self.attack_cooldown, self.has_dealt_damage = 15, False 
            return True
        return False

    def take_damage(self, amount, source_x, is_crit=False):
        dmg = max(1, amount - self.defense)
        self.hp -= dmg
        self.animator.hit_flash = 5
        self.knockback_vx = (1 if self.x > source_x else -1) * 8
        self.y, self.knockback_vy, self.is_grounded = self.y - 5, -4, False
        EventBus().publish("ENTITY_DAMAGED", target=self, damage=dmg, is_crit=is_crit)
        if self.hp <= 0 and not self.is_dead:
            self.is_dead = True
            self.on_death()
        return dmg

    def on_death(self): EventBus().publish("ENTITY_DIED", entity=self)
    def is_alive(self): return self.hp > 0

class Player(StickFigure):
    def __init__(self, x, y):
        super().__init__(x, y, BLACK, level=1)
        self.exp, self.exp_next, self.tokens, self.sp, self.stat_points = 0, 100, 500, 0, 0
        self.skills = {'mana_gloves': ManaGlovesSkill(), 'mana_surge': ManaSurgeSkill()}
        self.weapon = "Fists"
        self.owned_weapons = ["Fists"]
        self.is_dead = False
        EventBus().publish("PLAYER_SPAWNED", entity=self)

    def draw(self, surface):
        weapon = getattr(self, 'weapon', 'Fists')
        attack_type = getattr(self, 'current_attack', '')
        self.animator.draw(surface, self.x, self.y, self.facing, self.attack_cooldown, self.level, weapon, attack_type)
        if self.display_hp < self.max_hp and not self.is_dead:
            bar_w, y_pos = 60, self.y - 140
            pygame.draw.rect(surface, DARK_GRAY, (self.x - 30, y_pos, bar_w, 6))
            pygame.draw.rect(surface, YELLOW, (self.x - 30, y_pos, (self.display_hp / self.max_hp) * bar_w, 6))
            pygame.draw.rect(surface, RED, (self.x - 30, y_pos, (max(0, self.hp) / self.max_hp) * bar_w, 6))

    def jump(self):
        if self.is_grounded: self.vy = JUMP_FORCE

    def gain_exp(self, amount):
        self.exp += amount
        while self.exp >= self.exp_next: self.level_up()

    def level_up(self):
        self.level += 1
        self.exp, self.exp_next = self.exp - self.exp_next, int(self.exp_next * 1.5)
        self.max_hp += 15
        self.hp, self.attack_power, self.defense, self.max_mana = self.max_hp, self.attack_power+4, self.defense+2, self.max_mana+10
        self.mana, self.sp, self.stat_points = self.max_mana, self.sp+1, self.stat_points+3

    def use_skill(self, name):
        sk = self.skills.get(name)
        if sk and sk.can_use(self):
            sk.activate(self)
            return True
        return False

    def on_death(self):
        """Override base on_death to additionally trigger the PLAYER_DIED event."""
        super().on_death()
        EventBus().publish("PLAYER_DIED", entity=self)

    def update(self):
        super().update()
        if self.mana < self.max_mana: 
            self.mana += 0.05
            
        if self.attack_cooldown > 0:
            weapon = getattr(self, 'weapon', 'Fists')
            
            if weapon == "Sword":
                if 8 < self.attack_cooldown < 12:
                    w, h = (60, 40) if getattr(self, 'current_attack', '') == "SWORD_SLASH" else (70, 30)
                    facing_offset = 15 if self.facing == 1 else -(15 + w)
                    self.attack_rect = pygame.Rect(self.x + facing_offset, self.y - 60, w, h)
                else:
                    self.attack_rect = None
                    
            elif weapon == "Axe":
                if 10 < self.attack_cooldown < 16:
                    w, h = (50, 60) if getattr(self, 'current_attack', '') in ["AXE_SLASH", "AXE_UP"] else (80, 40)
                    facing_offset = 10 if self.facing == 1 else -(10 + w)
                    self.attack_rect = pygame.Rect(self.x + facing_offset, self.y - 70, w, h)
                else:
                    self.attack_rect = None
                    
            elif weapon == "Bow":
                if self.attack_cooldown == 5:
                    EventBus().publish("SPAWN_PROJECTILE", x=self.x + 20*self.facing, y=self.y-80, facing=self.facing, damage=self.attack_power)
                    self.current_attack = ""
                self.attack_rect = None

    def attack(self):
        if self.attack_cooldown <= 0:
            self.has_dealt_damage = False
            weapon = getattr(self, 'weapon', 'Fists')
            
            if weapon == "Sword":
                self.attack_cooldown = 20
                self.current_attack = "SWORD_SWEEP" if getattr(self, 'current_attack', '') == "SWORD_SLASH" else "SWORD_SLASH"
            elif weapon == "Axe":
                self.attack_cooldown = 25
                self.current_attack = random.choice(["AXE_SLASH", "AXE_UP", "AXE_SWEEP"])
            elif weapon == "Bow":
                self.attack_cooldown = 25
                self.current_attack = "BOW_DRAW"
            else:
                self.attack_cooldown = 15
                self.current_attack = "FISTS"

class Enemy(StickFigure):
    def __init__(self, x, y, level):
        super().__init__(x, y, DARK_RED, level)
        self.ai_timer = random.randint(0, 30)
        EventBus().publish("ENEMY_SPAWNED", entity=self)

    def update(self, player):
        super().update()
        if self.is_dead: return
        self.ai_timer += 1
        if player:
            dx = player.x - self.x
            if abs(dx) > 80:
                self.vx, self.facing = (2.5 if dx > 0 else -2.5), (1 if dx > 0 else -1)
            else:
                self.vx = 0
                if self.ai_timer % 40 == 0: self.attack()
        else: self.vx = 0

class Boss(Enemy):
    def __init__(self, x, y, level):
        super().__init__(x, y, level)
        self.max_hp *= 5 
        self.hp = self.max_hp
        self.attack_power *= 3
        
        # Boss visuals
        self.animator.thickness_mult = 2
        self.animator.scale_mult = 1.2
        self.animator.fixed_opacity = 255
        
        # CHARGE SKILL VARIABLES
        self.charge_timer = 0
        self.is_charging = False
        self.charge_duration = 0

    def update(self, player):
        if self.is_dead:
            super().update(player)
            return

        # --- CHARGE STATE LOGIC ---
        if self.is_charging:
            self.charge_duration -= 1
            
            # Massive speed boost!
            self.vx = 12 * self.facing  
            
            # Visual flair: Switch to walk cycle, let the high vx speed up the legs!
            self.animator.current_state = "WALK"

            self.attack_cooldown = 2  
            self.current_attack = "CHARGE"
            
            if player and self.rect.colliderect(player.rect):
                player.take_damage(self.attack_power * 2, self.x)
                
                self.is_charging = False
                self.vx = 0
                
            # Stop charging if time runs out and he missed
            if self.charge_duration <= 0:
                self.is_charging = False
                self.vx = 0

            # Bypass the normal Enemy AI while charging, just update physics
            StickFigure.update(self)
            return

        # --- NORMAL AI ---
        # If not charging, run the normal Enemy tracking and walking
        super().update(player)

        # --- CHARGE TRIGGER LOGIC ---
        # At 60 FPS, 3 seconds is 180 frames.
        self.charge_timer += 1
        if self.charge_timer >= 180:
            self.charge_timer = 0
            
            if random.randint(1, 100) <= 80:
                self.is_charging = True
                self.charge_duration = 40
                
                # Make sure he faces the player right before he launches!
                if player:
                    self.facing = 1 if player.x > self.x else -1

    def draw(self, surface):
        if getattr(self, 'is_charging', False):
            self.attack_cooldown = 2
            self.current_attack = "CHARGE"
            self.weapon = "Fists"
            
        super().draw(surface)                    