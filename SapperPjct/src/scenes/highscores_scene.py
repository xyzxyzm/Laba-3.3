import pygame
from src.engine.state_manager import State
from src.config.settings import SETTINGS
from src.ui.ui_elements import Button
from src.engine.resource_manager import RESOURCES
from src.engine.save_manager import SAVE_MANAGER

class HighScoresScene(State):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self.font_title = RESOURCES.get_font(SETTINGS.FONTS['main'], SETTINGS.FONTS['size_large'])
        self.font_text = RESOURCES.get_font(SETTINGS.FONTS['main'], SETTINGS.FONTS['size_medium'])
        self._create_ui()
        
    def _create_ui(self):
        cx = SETTINGS.WIDTH // 2
        cy = SETTINGS.HEIGHT - 100
        w, h = 200, 50
        
        self.buttons.append(Button(cx - w//2, cy, w, h, "BACK", self._to_menu, style='danger'))
        
    def _to_menu(self):
        from src.scenes.menu_scene import MenuScene
        self.game.state_manager.change_state(MenuScene(self.game))
        
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)
            
    def _draw_background(self, screen):
        # Повторно используем профессиональный фон из MenuScene
        # В идеале это должно быть в общей утилите или базовом классе, но пока дублируем или импортируем
        # Давайте продублируем логику для независимости и небольших вариаций, если потребуется
        bg_color = (15, 17, 22) 
        screen.fill(bg_color)
        
        # Сетка
        grid_color = (255, 255, 255, 3)
        cell_size = 50
        grid_surf = pygame.Surface((SETTINGS.WIDTH, SETTINGS.HEIGHT), pygame.SRCALPHA)
        for x in range(0, SETTINGS.WIDTH, cell_size):
            pygame.draw.line(grid_surf, grid_color, (x, 0), (x, SETTINGS.HEIGHT), 1)
        for y in range(0, SETTINGS.HEIGHT, cell_size):
            pygame.draw.line(grid_surf, grid_color, (0, y), (SETTINGS.WIDTH, y), 1)
        screen.blit(grid_surf, (0,0))
        
        # Виньетка/Свечение
        center = (SETTINGS.WIDTH//2, SETTINGS.HEIGHT//2)
        glow_surf = pygame.Surface((SETTINGS.WIDTH, SETTINGS.HEIGHT), pygame.SRCALPHA)
        glow_color = (30, 35, 45, 20) 
        pygame.draw.circle(glow_surf, glow_color, center, 500)
        screen.blit(glow_surf, (0,0))

    def draw(self, screen):
        self._draw_background(screen)
        
        # Заголовок
        title_text = "HIGH SCORES"
        # Тень
        shadow_surf = self.font_title.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(SETTINGS.WIDTH // 2 + 4, 50 + 4))
        screen.blit(shadow_surf, shadow_rect)
        
        title_surf = self.font_title.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SETTINGS.WIDTH // 2, 50))
        screen.blit(title_surf, title_rect)
        
        # Рисуем очки
        scores = SAVE_MANAGER.scores
        difficulties = ['easy', 'medium', 'hard']
        
        col_width = SETTINGS.WIDTH // 3
        start_y = 120
        
        for i, diff in enumerate(difficulties):
            x = i * col_width + col_width // 2
            
            # Панель колонки (Эффект стекла)
            panel_w = 250
            panel_h = 400
            panel_rect = pygame.Rect(x - panel_w//2, start_y - 10, panel_w, panel_h)
            
            panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel_surf, (30, 30, 30, 100), panel_surf.get_rect(), border_radius=15)
            pygame.draw.rect(panel_surf, (100, 100, 100, 50), panel_surf.get_rect(), 1, border_radius=15)
            screen.blit(panel_surf, panel_rect)
            
            # Заголовок
            header_text = diff.upper()
            header_surf = self.font_text.render(header_text, True, (0, 255, 255)) # Голубой
            header_rect = header_surf.get_rect(center=(x, start_y + 20))
            screen.blit(header_surf, header_rect)
            
            # Разделитель
            pygame.draw.line(screen, (0, 255, 255, 100), (x - 50, start_y + 45), (x + 50, start_y + 45), 2)
            
            # Время
            diff_scores = scores.get(diff, [])
            for j, score in enumerate(diff_scores):
                if j >= 5: break # Показываем топ 5
                time_str = f"{j+1}. {score}s"
                
                # Подсветка топ 1
                color = (255, 215, 0) if j == 0 else (200, 200, 200)
                
                score_surf = self.font_text.render(time_str, True, color)
                score_rect = score_surf.get_rect(center=(x, start_y + 70 + j * 40))
                screen.blit(score_surf, score_rect)
        
        for btn in self.buttons:
            btn.draw(screen)
            
    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)
