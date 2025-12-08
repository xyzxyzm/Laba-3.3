import pygame
from src.config.settings import SETTINGS
from src.engine.resource_manager import RESOURCES

class Cell:
    def __init__(self, row, col, x, y, size):
        self.row = row
        self.col = col
        self.rect = pygame.Rect(x, y, size, size)
        
        self.is_mine = False
        self.is_open = False
        self.is_flagged = False
        self.neighbor_mines = 0
        
        # Визуальные параметры
        self.colors = SETTINGS.COLORS
        self.font = RESOURCES.get_font(SETTINGS.FONTS['main'], SETTINGS.FONTS['size_small'])
        
    def draw(self, surface, font_size=None):
        # Фон
        if self.is_open:
            if self.is_mine:
                color = self.colors['mine']
            else:
                color = self.colors['cell_opened']
        else:
            color = self.colors['cell_closed']
            
        # Рисуем клетку с небольшим отступом для эффекта сетки
        draw_rect = self.rect.inflate(-2, -2)
        pygame.draw.rect(surface, color, draw_rect, border_radius=3)
        
        # Содержимое
        if self.is_open:
            if self.is_mine:
                # Рисуем мину (круг с шипами)
                center = self.rect.center
                radius = self.rect.width // 4
                pygame.draw.circle(surface, (50, 0, 0), center, radius)
                pygame.draw.circle(surface, (0, 0, 0), center, radius // 2)
            elif self.neighbor_mines > 0:
                # Используем переданный размер шрифта или стандартный
                if font_size:
                    font = RESOURCES.get_font(SETTINGS.FONTS['main'], font_size)
                else:
                    font = self.font
                    
                text_surf = font.render(str(self.neighbor_mines), True, self._get_number_color(self.neighbor_mines))
                text_rect = text_surf.get_rect(center=self.rect.center)
                surface.blit(text_surf, text_rect)
        elif self.is_flagged:
            # Рисуем флаг, масштабированный под размер клетки
            # Древко
            pole_top = self.rect.top + self.rect.height * 0.15
            pole_bottom = self.rect.bottom - self.rect.height * 0.15
            pygame.draw.line(surface, (0, 0, 0), (self.rect.centerx, pole_top), (self.rect.centerx, pole_bottom), max(1, int(self.rect.width * 0.05)))
            
            # Полотнище флага
            fp1 = (self.rect.centerx, pole_top)
            fp2 = (self.rect.right - self.rect.width * 0.2, pole_top + self.rect.height * 0.15)
            fp3 = (self.rect.centerx, pole_top + self.rect.height * 0.3)
            pygame.draw.polygon(surface, self.colors['flag'], [fp1, fp2, fp3])
            
    def _get_number_color(self, n):
        colors = {
            1: (0, 0, 255),
            2: (0, 128, 0),
            3: (255, 0, 0),
            4: (0, 0, 128),
            5: (128, 0, 0),
            6: (0, 128, 128),
            7: (0, 0, 0),
            8: (128, 128, 128)
        }
        return colors.get(n, (0, 0, 0))
