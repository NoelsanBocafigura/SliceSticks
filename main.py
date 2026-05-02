import pygame
import sys
from config import *
from core import EventBus
from managers import CameraManager, VFXManager, WaveManager, PhysicsManager
from entities import Player, Enemy
from ui import HUD, StatMenu, SkillMenu, PauseMenu, MainMenu, GameOverMenu, WeaponMenu

# ---------------------------- Main Game Controller ----------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.world_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Stick Fighter - Independent Physics")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Start at Main Menu
        self.state = GameState.MAIN_MENU

        self.event_bus = EventBus()
        self.camera = CameraManager()
        self.vfx = VFXManager()
        self.wave_manager = WaveManager()
        self.physics = PhysicsManager()
        
        # Initialize Menu Screens
        self.main_menu = MainMenu(self.start_game, self.quit_game)
        self.pause_menu = PauseMenu(self.resume_game, self.quit_game)
        self.game_over_menu = GameOverMenu(self.restart_game, self.quit_game)
        
        self.weapon_menu = None
        self.stat_menu = None
        self.skill_menu = None
        self.player = None
        self.hud = None

        self.init_game()
        
        self.event_bus.subscribe("ENTITY_DIED", self._on_entity_died)
        self.event_bus.subscribe("PLAYER_DIED", self._on_player_died)

    def init_game(self):
        self.player = Player(400, GROUND_Y)
        
        # Defensive assignment to guarantee these exist upon restart
        self.player.tokens = getattr(self.player, 'tokens', 0)
        self.player.weapon = getattr(self.player, 'weapon', "Fists")
        self.player.owned_weapons = getattr(self.player, 'owned_weapons', ["Fists"])
        self.player.is_dead = False
        self.wave_manager.total_kills = 0
        
        self.hud = HUD(self.player)
        
        self.wave_manager.wave = 0
        self.wave_manager.enemies.clear()
        
        self.physics.enemies.clear()
        self.physics.player = self.player
        
        self.wave_manager.start_next_wave()

    def start_game(self):
        self.state = GameState.PLAYING

    def restart_game(self):
        self.init_game()
        self.state = GameState.PLAYING

    def resume_game(self):
        self.state = GameState.PLAYING

    def quit_game(self):
        self.running = False

    def _on_player_died(self, entity, **kwargs):
        if entity == self.player:
            self.state = GameState.GAME_OVER

    def _on_entity_died(self, entity, **kwargs):
        if isinstance(entity, Enemy):
            self.player.gain_exp(30 * entity.level)
            self.player.tokens += 10 * entity.level

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if self.state == GameState.MAIN_MENU:
                self.main_menu.handle_event(event)
            elif self.state == GameState.GAME_OVER:
                self.game_over_menu.handle_event(event)
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        if self.state == GameState.PLAYING:
                            self.stat_menu = StatMenu(self.player, self.resume_game)
                            self.state = GameState.STAT_MENU
                        elif self.state == GameState.STAT_MENU:
                            self.resume_game()
                    elif event.key == pygame.K_k:
                        if self.state == GameState.PLAYING:
                            self.skill_menu = SkillMenu(self.player, self.resume_game)
                            self.state = GameState.SKILL_MENU
                        elif self.state == GameState.SKILL_MENU:
                            self.resume_game()
                    elif event.key == pygame.K_b:
                        if self.state == GameState.PLAYING:
                            self.weapon_menu = WeaponMenu(self.player, self.resume_game)
                            self.state = GameState.WEAPON_MENU
                        elif self.state == GameState.WEAPON_MENU:
                            self.resume_game()
                    elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        if self.state == GameState.PLAYING:
                            self.state = GameState.PAUSED
                        elif self.state == GameState.PAUSED:
                            self.resume_game()
                    elif event.key == pygame.K_SPACE and self.state == GameState.PLAYING:
                        self.player.jump()

                if self.state == GameState.STAT_MENU and self.stat_menu:
                    self.stat_menu.handle_event(event)
                elif self.state == GameState.SKILL_MENU and self.skill_menu:
                    self.skill_menu.handle_event(event)
                elif self.state == GameState.WEAPON_MENU and self.weapon_menu:
                    self.weapon_menu.handle_event(event)
                elif self.state == GameState.PAUSED:
                    self.pause_menu.handle_event(event)

    def update(self):
        if self.state == GameState.PLAYING:
            self.camera.update()
            self.vfx.update()

            if self.vfx.hit_stop > 0:
                return 

            keys = pygame.key.get_pressed()
            self.player.vx = 0
            if keys[pygame.K_LEFT]:
                self.player.vx = -7 
                self.player.facing = -1
            if keys[pygame.K_RIGHT]:
                self.player.vx = 7
                self.player.facing = 1
            if keys[pygame.K_a]:
                self.player.attack()
            if keys[pygame.K_s]:
                self.player.use_skill('mana_gloves')
            if keys[pygame.K_d]:
                self.player.use_skill('mana_surge')

            # Entity Updates
            self.player.update()
            for skill in self.player.skills.values():
                skill.update_cooldown()
            for enemy in self.wave_manager.enemies:
                enemy.update(self.player)
                
            # Delegate all collision/hit-detection logic to the PhysicsManager
            self.physics.update()

            self.wave_manager.update(self.player)
            if not self.wave_manager.wave_active and not self.wave_manager.enemies:
                self.wave_manager.start_next_wave()

    def draw(self):
        if self.state == GameState.MAIN_MENU:
            self.main_menu.draw(self.screen)
            pygame.display.flip()
            return
            
        self.world_surface.fill(GRAY)
        pygame.draw.rect(self.world_surface, DARK_GRAY, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        pygame.draw.line(self.world_surface, BLACK, (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 4)

        for enemy in self.wave_manager.enemies:
            enemy.draw(self.world_surface)
            
        for arrow in self.physics.arrows:
            arrow.draw(self.world_surface)
            
        self.player.draw(self.world_surface)

        self.vfx.draw(self.world_surface)
        self.screen.blit(self.world_surface, (self.camera.offset_x, self.camera.offset_y))

        self.hud.draw(self.screen)
        
        if self.state == GameState.STAT_MENU and self.stat_menu:
            self.stat_menu.draw(self.screen)
        elif self.state == GameState.SKILL_MENU and self.skill_menu:
            self.skill_menu.draw(self.screen)
        elif self.state == GameState.WEAPON_MENU and self.weapon_menu:
            self.weapon_menu.draw(self.screen)
        elif self.state == GameState.PAUSED:
            self.pause_menu.draw(self.screen)
        elif self.state == GameState.GAME_OVER:
            self.game_over_menu.draw(self.screen)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()