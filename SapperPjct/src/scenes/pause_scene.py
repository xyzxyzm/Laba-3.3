import pygame
from src.engine.state_manager import State
from src.config.settings import SETTINGS
from src.ui.ui_elements import Button, Slider
from src.engine.resource_manager import RESOURCES

class PauseScene(State):
    def __init__(self, game, previous_scene):
        super().__init__(game)
        self.previous_scene = previous_scene
        # Активируем паузу в предыдущей сцене
        if hasattr(self.previous_scene, 'pause_game'):
            self.previous_scene.pause_game()
            
        self.buttons = []
        self.sliders = []
        self.font_title = RESOURCES.get_font(SETTINGS.FONTS['main'], SETTINGS.FONTS['size_large'])
        self._create_ui()
        
    def _create_ui(self):
        cx = SETTINGS.WIDTH // 2
        cy = SETTINGS.HEIGHT // 2
        w, h = 240, 55
        gap = 25 # Увеличенный зазор
        
        # Продолжить (Основная)
        self.buttons.append(Button(cx - w//2, cy - h - gap, w, h, "RESUME", self._resume, style='primary'))
        
        # Главное меню (Опасная)
        self.buttons.append(Button(cx - w//2, cy, w, h, "MAIN MENU", self._to_menu, style='danger'))
        
        # Ползунок громкости
        # Получаем текущую громкость (используем громкость музыки как мастер пока что, или среднее)
        current_vol = SETTINGS.game_config['audio']['music_volume']
        # Сдвигаем ползунок вниз, чтобы избежать перекрытия
        self.sliders.append(Slider(cx - w//2, cy + h + gap + 30, w, 20, 0.0, 1.0, current_vol, self._set_volume))
        
    def _set_volume(self, val):
        # Обновляем конфиг
        SETTINGS.game_config['audio']['music_volume'] = val
        # SFX обычно следует за мастером, но давайте оставим пропорционально или просто установим одинаково как запрошенную "мастер-громкость"
        # На самом деле пользователь просил "ползунок для ВСЕЙ громкости"
        SETTINGS.game_config['audio']['sfx_volume'] = val 
        
        # Применяем немедленно
        pygame.mixer.music.set_volume(val)
        # Громкость SFX применяется при воспроизведении, но мы не можем легко обновить играющие звуки. 
        # Будущие звуки будут использовать новую громкость.
        
    def _resume(self):
        if hasattr(self.previous_scene, 'resume_game'):
            self.previous_scene.resume_game()
        self.game.state_manager.change_state(self.previous_scene)
        
    def _to_menu(self):
        from src.scenes.menu_scene import MenuScene
        # Останавливаем музыку если играет (хотя она может быть на паузе)
        pygame.mixer.music.stop()
        self.game.state_manager.change_state(MenuScene(self.game))
        
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)
        for slider in self.sliders:
            slider.update(mouse_pos)
            
    def draw(self, screen):
        # Рисуем фон предыдущей сцены (затемненный)
        self.previous_scene.draw(screen)
        
        # Темное наложение
        overlay = pygame.Surface((SETTINGS.WIDTH, SETTINGS.HEIGHT))
        overlay.set_alpha(200) # Более темное наложение
        overlay.fill((10, 12, 15))
        screen.blit(overlay, (0, 0))
        
        # Стеклянная панель для меню паузы
        panel_w, panel_h = 400, 500
        panel_rect = pygame.Rect((SETTINGS.WIDTH - panel_w)//2, (SETTINGS.HEIGHT - panel_h)//2, panel_w, panel_h)
        
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (30, 30, 30, 150), panel_surf.get_rect(), border_radius=20)
        pygame.draw.rect(panel_surf, (255, 255, 255, 20), panel_surf.get_rect(), 1, border_radius=20)
        screen.blit(panel_surf, panel_rect)
        
        # Заголовок
        title_text = "PAUSED"
        shadow_surf = self.font_title.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(SETTINGS.WIDTH // 2 + 4, panel_rect.top + 80 + 4))
        screen.blit(shadow_surf, shadow_rect)
        
        title_surf = self.font_title.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SETTINGS.WIDTH // 2, panel_rect.top + 80))
        screen.blit(title_surf, title_rect)
        
        # Метка громкости
        vol_label = self.font_title.render("Volume", True, (200, 200, 200)) # Повторное использование большого шрифта, но может слишком большой?
        # Давайте используем меньший шрифт если доступен, или просто уменьшим? 
        # На самом деле ui_elements использует size_medium, давайте возьмем его
        font_med = RESOURCES.get_font(SETTINGS.FONTS['main'], SETTINGS.FONTS['size_medium'])
        vol_surf = font_med.render("Master Volume", True, (200, 200, 200))
        vol_rect = vol_surf.get_rect(center=(SETTINGS.WIDTH // 2, self.sliders[0].rect.top - 20))
        screen.blit(vol_surf, vol_rect)
        
        for btn in self.buttons:
            btn.draw(screen)
        for slider in self.sliders:
            slider.draw(screen)
            
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._resume()
                
        for btn in self.buttons:
            btn.handle_event(event)
        for slider in self.sliders:
            slider.handle_event(event)
