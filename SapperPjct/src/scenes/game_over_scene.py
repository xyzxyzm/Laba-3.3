import pygame
from src.engine.state_manager import State
from src.config.settings import SETTINGS
from src.ui.ui_elements import Button
from src.engine.resource_manager import RESOURCES

class GameOverScene(State):
    def __init__(self, game, result_text, time_taken=None, difficulty=None, num_players=1, level=1):
        super().__init__(game)
        self.result_text = result_text
        self.difficulty = difficulty
        self.num_players = num_players
        self.level = level
        self.buttons = []
        self.font_title = RESOURCES.get_font(SETTINGS.FONTS['main'], SETTINGS.FONTS['size_large'])
        
        if time_taken is not None and difficulty is not None and "Win" in result_text and "Player" not in result_text:
            # Победа в одиночной игре
            from src.engine.save_manager import SAVE_MANAGER
            SAVE_MANAGER.save_score(difficulty, time_taken)
            self.result_text += f" Time: {time_taken}s"
            
        self._create_ui()
        
    def _create_ui(self):
        cx = SETTINGS.WIDTH // 2
        cy = SETTINGS.HEIGHT // 2
        w, h = 200, 50
        gap = 20
        
        self.buttons.append(Button(cx - w//2, cy, w, h, "Restart", self._restart))
        self.buttons.append(Button(cx - w//2, cy + h + gap, w, h, "Menu", self._to_menu))
        
    def _restart(self):
        from src.scenes.game_scene import GameScene
        level_to_start = 1 if self.difficulty == 'campaign' else self.level
        self.game.state_manager.change_state(GameScene(self.game, self.difficulty, self.num_players, level_to_start))
        
    def _to_menu(self):
        from src.scenes.menu_scene import MenuScene
        self.game.state_manager.change_state(MenuScene(self.game))
        
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)
            
    def draw(self, screen):
        screen.fill(SETTINGS.COLORS['background'])
        
        # Текст результата
        text_surf = self.font_title.render(self.result_text, True, SETTINGS.COLORS['ui_text'])
        text_rect = text_surf.get_rect(center=(SETTINGS.WIDTH // 2, SETTINGS.HEIGHT // 3))
        screen.blit(text_surf, text_rect)
        
        for btn in self.buttons:
            btn.draw(screen)
            
    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)
