import pygame
from src.config.settings import SETTINGS
from src.ui.ui_elements import Button
from src.engine.resource_manager import RESOURCES

class DebugPanel:
    def __init__(self, game_scene):
        self.game_scene = game_scene
        self.visible = False
        self.buttons = []
        self.width = 200
        self.height = 0 # Будет вычислено
        self.x = SETTINGS.WIDTH - self.width - 70 # Слева от кнопки отладки
        self.y = 70 # Под кнопкой отладки
        
        self._create_buttons()
        
    def _create_buttons(self):
        self.buttons = []
        btn_h = 40
        gap = 10
        current_y = self.y + 10
        
        # Помощник для добавления кнопки
        def add_btn(text, callback):
            nonlocal current_y
            btn = Button(self.x + 10, current_y, self.width - 20, btn_h, text, callback, style='secondary')
            self.buttons.append(btn)
            current_y += btn_h + gap
            
        if self.game_scene.num_players == 1:
            add_btn("Force Win", self.game_scene.debug_force_win)
        else:
            add_btn("P1 Win", lambda: self.game_scene.debug_force_win(player=1))
            add_btn("P2 Win", lambda: self.game_scene.debug_force_win(player=2))
            add_btn("Both Win", lambda: self.game_scene.debug_force_win(player=3))
            
        self.height = current_y - self.y
        
    def toggle(self):
        self.visible = not self.visible
        
    def update(self, mouse_pos):
        if not self.visible: return
        for btn in self.buttons:
            btn.update(mouse_pos)
            
    def handle_event(self, event):
        if not self.visible: return False
        for btn in self.buttons:
            if btn.handle_event(event):
                return True
        return False
        
    def draw(self, surface):
        if not self.visible: return
        
        # Рисуем стеклянную панель
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Фон
        bg_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (20, 20, 25, 230), bg_surf.get_rect(), border_radius=10)
        
        # Граница (Неоновый голубой)
        pygame.draw.rect(bg_surf, (0, 255, 255, 100), bg_surf.get_rect(), 1, border_radius=10)
        
        surface.blit(bg_surf, rect)
        
        # Рисуем кнопки
        for btn in self.buttons:
            btn.draw(surface)
