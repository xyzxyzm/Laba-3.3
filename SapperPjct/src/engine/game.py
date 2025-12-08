import pygame
import sys
from src.config.settings import SETTINGS
from src.engine.state_manager import StateManager
from src.engine.resource_manager import RESOURCES

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.WIDTH = SETTINGS.WIDTH
        self.HEIGHT = SETTINGS.HEIGHT
        
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(f"{SETTINGS.TITLE} v{SETTINGS.game_config['game']['version']}")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.state_manager = StateManager(self)
        self.state_manager = StateManager(self)
        # Начальное состояние будет установлено в main.py
        
    def run(self):
        while self.running:
            self.clock.tick(SETTINGS.FPS)
            self._handle_events()
            self._update()
            self._draw()
            
        pygame.quit()
        sys.exit()
        
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.WIDTH, self.HEIGHT = event.w, event.h
                SETTINGS.WIDTH, SETTINGS.HEIGHT = event.w, event.h
                self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
                # Уведомляем текущее состояние если нужно
                if hasattr(self.state_manager.state, 'on_resize'):
                    self.state_manager.state.on_resize(self.WIDTH, self.HEIGHT)
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    # Переключение полноэкранного режима
                    is_fullscreen = self.screen.get_flags() & pygame.FULLSCREEN
                    if is_fullscreen:
                        self.screen = pygame.display.set_mode((SETTINGS.WIDTH, SETTINGS.HEIGHT), pygame.RESIZABLE)
                    else:
                        # Сохраняем размер окна если нужно, но пока используем текущие настройки
                        self.screen = pygame.display.set_mode((SETTINGS.WIDTH, SETTINGS.HEIGHT), pygame.FULLSCREEN)
                    
                    # Уведомляем состояние об изменении размера
                    # Обновляем ширину/высоту из поверхности
                    self.WIDTH, self.HEIGHT = self.screen.get_size()
                    SETTINGS.WIDTH, SETTINGS.HEIGHT = self.WIDTH, self.HEIGHT
                    
                    if hasattr(self.state_manager.state, 'on_resize'):
                        self.state_manager.state.on_resize(self.WIDTH, self.HEIGHT)
                    
            self.state_manager.handle_event(event)
                
    def _update(self):
        self.state_manager.update()
        
    def _draw(self):
        self.screen.fill(SETTINGS.COLORS['background'])
        self.state_manager.draw(self.screen)
        pygame.display.flip()
