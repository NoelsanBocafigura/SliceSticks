import pygame
from config import *
from managers import WaveManager

class Button:
    def __init__(self, rect, text, callback, color=GRAY):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.color = color
        self.font = pygame.font.Font(None, 24)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        text_surf = self.font.render(self.text, True, SILVER_WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

class PauseMenu:
    def __init__(self, on_resume, on_quit):
        self.buttons = [
            Button((300, 200, 200, 50), "Resume", on_resume),
            Button((300, 280, 200, 50), "Quit Game", on_quit, color=RED)
        ]
    def handle_event(self, event):
        for btn in self.buttons: btn.handle_event(event)
    def draw(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(DARK_BLOOD)
        surface.blit(overlay, (0,0))
        font = pygame.font.Font(None, 48)
        surface.blit(font.render("PAUSED", True, WHITE), (325, 120))
        for btn in self.buttons: btn.draw(surface)

class StatMenu:
    def __init__(self, player, on_close):
        self.player = player
        self.on_close = on_close
        x, y, w, h = 300, 180, 180, 40
        self.buttons = [
            Button((x, y, w, h), f"HP (+15)", self.inc_hp),
            Button((x, y+50, w, h), f"Attack (+3)", self.inc_attack),
            Button((x, y+100, w, h), f"Defense (+2)", self.inc_defense),
            Button((x, y+150, w, h), f"Mana (+10)", self.inc_mana),
            Button((x, y+220, w, h), "Back to Fight", self.on_close, color=GREEN)
        ]
    def inc_hp(self):
        if self.player.stat_points > 0: self.player.max_hp += 15; self.player.hp += 15; self.player.stat_points -= 1
    def inc_attack(self):
        if self.player.stat_points > 0: self.player.attack_power += 3; self.player.stat_points -= 1
    def inc_defense(self):
        if self.player.stat_points > 0: self.player.defense += 2; self.player.stat_points -= 1
    def inc_mana(self):
        if self.player.stat_points > 0: self.player.max_mana += 10; self.player.mana += 10; self.player.stat_points -= 1
    def handle_event(self, event):
        for btn in self.buttons: btn.handle_event(event)
    def draw(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(DARK_BLOOD)
        surface.blit(overlay, (0,0))
        for btn in self.buttons: btn.draw(surface)
        font = pygame.font.Font(None, 36)
        surface.blit(font.render(f"Available Stat Points: {self.player.stat_points}", True, WHITE), (260, 130))

class SkillMenu:
    def __init__(self, player, on_close):
        self.player = player
        self.on_close = on_close
        x, y, w, h = 250, 180, 300, 40
        self.buttons = [
            Button((x, y, w, h), "Upgrade Mana Gloves (1 SP)", self.up_gloves),
            Button((x, y+60, w, h), "Upgrade Mana Surge (1 SP)", self.up_surge),
            Button((x, y+140, w, h), "Back to Fight", self.on_close, color=GREEN)
        ]
    def up_gloves(self):
        if self.player.sp > 0: self.player.skills['mana_gloves'].level += 1; self.player.sp -= 1
    def up_surge(self):
        if self.player.sp > 0: self.player.skills['mana_surge'].level += 1; self.player.sp -= 1
    def handle_event(self, event):
        for btn in self.buttons: btn.handle_event(event)
    def draw(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(DARK_BLOOD)
        surface.blit(overlay, (0,0))
        for btn in self.buttons: btn.draw(surface)
        font = pygame.font.Font(None, 36)
        surface.blit(font.render(f"Available SP: {self.player.sp}", True, WHITE), (250, 130))

class HUD:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.Font(None, 24)

    def draw(self, surface):
        pygame.draw.rect(surface, DARK_GRAY, (10, 10, 300, 25))
        yellow_w = (self.player.display_hp / self.player.max_hp) * 300
        pygame.draw.rect(surface, YELLOW, (10, 10, yellow_w, 25))
        red_w = max(0, self.player.hp / self.player.max_hp) * 300
        pygame.draw.rect(surface, RED, (10, 10, red_w, 25))
        pygame.draw.rect(surface, BLACK, (10, 10, 300, 25), 2) 
        
        pygame.draw.rect(surface, DARK_GRAY, (10, 40, 250, 15))
        mp_pct = self.player.mana / self.player.max_mana
        pygame.draw.rect(surface, CRIMSON, (10, 40, 250 * mp_pct, 15))

        stats = [
            f"Wave: {WaveManager().wave}",
            f"Level: {self.player.level}",
            f"Tokens: {self.player.tokens}",
            f"Stat Points: {self.player.stat_points}",
            f"SP: {self.player.sp}"
        ]
        for i, txt in enumerate(stats):
            surf = self.font.render(txt, True, DARK_RED)
            surface.blit(surf, (10, 65 + i*20))
            
        hints = ["A: Attack", "S: Mana Gloves", "D: Mana Surge", "SPACE: Jump", "M: Stats", "K: Skills", "P: Pause", "B: Shop"]
        for i, txt in enumerate(hints):
            surf = self.font.render(txt, True, YELLOW)
            surface.blit(surf, (SCREEN_WIDTH - 150, 10 + i*20))

class MainMenu:
    def __init__(self, on_play, on_quit):
        self.buttons = [
            Button((300, 200, 200, 50), "Start Game", on_play, color=GREEN),
            Button((300, 280, 200, 50), "Quit Game", on_quit, color=RED)
        ]

    def handle_event(self, event):
        for btn in self.buttons: 
            btn.handle_event(event)

    def draw(self, surface):
        surface.fill(DEEP_RED)
        font = pygame.font.Font(None, 64)
        title_surf = font.render("STICK FIGHTER", True, WHITE)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 100))
        for btn in self.buttons: 
            btn.draw(surface)

class GameOverMenu:
    def __init__(self, on_restart, on_quit):
        self.buttons = [
            Button((300, 250, 200, 50), "Restart", on_restart, color=GREEN),
            Button((300, 330, 200, 50), "Quit Game", on_quit, color=RED)
        ]

    def handle_event(self, event):
        for btn in self.buttons: 
            btn.handle_event(event)

    def draw(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(DARK_BLOOD)
        surface.blit(overlay, (0, 0))
        font = pygame.font.Font(None, 64)
        title_surf = font.render("GAME OVER", True, RED)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 150))
        for btn in self.buttons: 
            btn.draw(surface)

class WeaponMenu:
    def __init__(self, player, on_close):
        self.player = player
        self.on_close = on_close
        self.buttons = []
        self.weapons = {
            "Fists": {"cost": 0, "atk": 0},
            "Sword": {"cost": 50, "atk": 10},
            "Axe": {"cost": 100, "atk": 25},
            "Bow": {"cost": 150, "atk": 15}
        }
        self.update_buttons()

    def update_buttons(self):
        self.buttons.clear()
        x, y, w, h = 300, 150, 200, 40
        
        for i, (w_name, stats) in enumerate(self.weapons.items()):
            btn_y = y + i * 60
            if w_name in getattr(self.player, 'owned_weapons', []):
                text = f"Equiped {w_name}"
                color = RED if getattr(self.player, 'weapon', 'Fists') == w_name else DARK_GRAY
                self.buttons.append(Button((x, btn_y, w, h), text, lambda n=w_name: self.equip(n), color=color))
            else:
                text = f"Buy {w_name} ({stats['cost']}T)"
                self.buttons.append(Button((x, btn_y, w, h), text, lambda n=w_name, c=stats['cost'], a=stats['atk']: self.buy(n, c, a), color=YELLOW))
        
        self.buttons.append(Button((x, y + 260, w, h), "Close", self.on_close, color=GREEN))

    def buy(self, name, cost, atk_boost):
        if getattr(self.player, 'tokens', 0) >= cost:
            self.player.tokens -= cost
            self.player.owned_weapons.append(name)
            self.player.attack_power += atk_boost
            self.equip(name)

    def equip(self, name):
        self.player.weapon = name
        self.update_buttons()

    def handle_event(self, event):
        for btn in self.buttons: 
            btn.handle_event(event)

    def draw(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((40, 0, 0, 220))
        surface.blit(overlay, (0,0))
        
        font = pygame.font.Font(None, 48)
        surface.blit(font.render("WEAPON STORE", True, WHITE), (275, 80))
        
        # Draw vector icons next to buttons
        for i, (w_name, _) in enumerate(self.weapons.items()):
            self._draw_vector_icon(surface, w_name, 250, 170 + i * 60)
            
        for btn in self.buttons:
            btn.draw(surface)

    def _draw_vector_icon(self, surface, name, x, y):
        if name == "Sword":
            pygame.draw.line(surface, SILVER_WHITE, (x-10, y+10), (x+20, y-10), 4)
            pygame.draw.line(surface, YELLOW, (x-5, y), (x+5, y+10), 3)
        elif name == "Axe":
            pygame.draw.line(surface, (139, 69, 19), (x-10, y+15), (x+15, y-15), 4)
            pygame.draw.polygon(surface, SILVER_WHITE, [(x+10, y-10), (x+20, y-20), (x+5, y-15)])
        elif name == "Bow":
            pygame.draw.arc(surface, (139, 69, 19), (x-15, y-15, 30, 30), -1.5, 1.5, 3)
            pygame.draw.line(surface, WHITE, (x, y-15), (x, y+15), 1)