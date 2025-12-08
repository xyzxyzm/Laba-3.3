import pygame
from src.config.settings import SETTINGS
from src.engine.resource_manager import RESOURCES

class Button:
    def __init__(self, x, y, width, height, text, callback, style='glass', icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.style = style # 'glass', 'primary', 'danger', 'secondary'
        self.icon = icon
        
        self.font = RESOURCES.get_font(SETTINGS.FONTS['main'], SETTINGS.FONTS['size_medium'])
        self.is_hovered = False
        self.alpha = 0
        
    def update(self, mouse_pos):
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered and self.callback:
                # проигываем звук клика
                sound = RESOURCES.get_sound('click.wav')
                if sound:
                    volume = SETTINGS.game_config['audio']['sfx_volume']
                    sound.set_volume(volume)
                    sound.play()
                self.callback()
                return True
        return False
                
    def draw(self, surface):
        # Профессиональная дизайн-система
        # Стиль: "Кибер-минимализм"
        
        # Цвета и градиенты
        if self.style == 'primary':
            # Голубой/Синий неон
            base_color = (0, 0, 0, 150) # Темная полупрозрачная заливка
            accent_color = (0, 255, 255) # Голубое свечение
            text_color = (255, 255, 255)
        elif self.style == 'danger':
            # Красный неон
            base_color = (0, 0, 0, 150)
            accent_color = (255, 50, 50) # Красное свечение
            text_color = (255, 255, 255)
        else: # glass/secondary
            # Белый/Серый неон
            base_color = (0, 0, 0, 100)
            accent_color = (150, 150, 150) # Белое свечение
            text_color = (200, 200, 200)

        # Логика состояния наведения
        if self.is_hovered:
            # Заливка становится немного светлее/цветной
            r, g, b = accent_color
            fill_color = (r, g, b, 50) # Легкий оттенок
            border_color = accent_color
            border_width = 2
            shadow_alpha = 150
            scale_offset = -1 # Небольшое уменьшение или просто изменение границы? Оставим размер стабильным
        else:
            fill_color = base_color
            border_color = (accent_color[0], accent_color[1], accent_color[2], 100) # Тусклая граница
            border_width = 1
            shadow_alpha = 50

        # 1. Рисуем тень (мягкое свечение позади)
        shadow_rect = self.rect.copy()
        shadow_rect.y += 2
        shadow_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        # Если наведено, тень - цветное свечение
        if self.is_hovered:
            pygame.draw.rect(shadow_surf, (*accent_color, 30), shadow_surf.get_rect(), border_radius=8)
        else:
            pygame.draw.rect(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect(), border_radius=8)
        surface.blit(shadow_surf, shadow_rect)

        # 2. Рисуем тело кнопки
        btn_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Заливка фона
        pygame.draw.rect(btn_surf, fill_color, btn_surf.get_rect(), border_radius=8)
        
        # Граница (Неоновая линия)
        pygame.draw.rect(btn_surf, border_color, btn_surf.get_rect(), border_width, border_radius=8)
        
        # Техно-декор (акценты по углам)
        if self.style == 'primary':
            corner_len = 10
            # Верхний левый
            pygame.draw.line(btn_surf, accent_color, (0, 0), (corner_len, 0), 2)
            pygame.draw.line(btn_surf, accent_color, (0, 0), (0, corner_len), 2)
            # Нижний правый
            w, h = self.rect.width, self.rect.height
            pygame.draw.line(btn_surf, accent_color, (w, h), (w-corner_len, h), 2)
            pygame.draw.line(btn_surf, accent_color, (w, h), (w, h-corner_len), 2)
        
        surface.blit(btn_surf, self.rect)
        
        # 3. Рисуем содержимое
        if self.icon == 'wrench':
            self._draw_wrench_icon(surface, accent_color if self.is_hovered else (200, 200, 200))
        elif not self.text:
            self._draw_pause_icon(surface, accent_color if self.is_hovered else (200, 200, 200))
        else:
            # Текст с опциональным свечением
            text_surf = self.font.render(self.text, True, text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
            
    def _draw_pause_icon(self, surface, color):
        bar_width = 4
        bar_height = self.rect.height // 2.5
        bar_spacing = 5
        center_x = self.rect.centerx
        center_y = self.rect.centery
        
        left_bar = pygame.Rect(center_x - bar_spacing - bar_width, center_y - bar_height // 2, bar_width, bar_height)
        right_bar = pygame.Rect(center_x + bar_spacing, center_y - bar_height // 2, bar_width, bar_height)
        
        pygame.draw.rect(surface, color, left_bar, border_radius=2)
        pygame.draw.rect(surface, color, right_bar, border_radius=2)

    def _draw_wrench_icon(self, surface, color):
        # Рисуем простой гаечный ключ
        cx, cy = self.rect.centerx, self.rect.centery
        size = self.rect.width // 2.5
        
        # Рукоятка (диагональная линия)
        start = (cx - size//2, cy + size//2)
        end = (cx + size//2, cy - size//2)
        pygame.draw.line(surface, color, start, end, 4)
        
        # Головка (форма C вверху справа)
        # Упрощенно: просто круг или толстая линия
        # Рисуем форму "U" на конце
        head_pos = (cx + size//2 - 2, cy - size//2 + 2)
        pygame.draw.circle(surface, color, head_pos, 5)
        pygame.draw.circle(surface, (0,0,0), head_pos, 2) # Отверстие
        
        # Нижняя губа
        jaw_pos = (cx - size//2 + 2, cy + size//2 - 2)
        pygame.draw.circle(surface, color, jaw_pos, 3)

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.callback = callback
        self.dragging = False
        
        self.handle_width = 20
        self.handle_rect = pygame.Rect(0, y - 5, self.handle_width, height + 10)
        self._update_handle_pos()
        
        self.font = RESOURCES.get_font(SETTINGS.FONTS['main'], SETTINGS.FONTS['size_medium'])
        
    def _update_handle_pos(self):
        # Преобразуем значение в позицию X
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        center_x = self.rect.x + ratio * self.rect.width
        self.handle_rect.centerx = center_x
        
    def _update_val_from_pos(self, x):
        # Преобразуем позицию X в значение
        ratio = (x - self.rect.x) / self.rect.width
        ratio = max(0, min(1, ratio))
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        self._update_handle_pos()
        if self.callback:
            self.callback(self.val)
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_val_from_pos(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_val_from_pos(event.pos[0])
                
    def update(self, mouse_pos):
        pass
        
    def draw(self, surface):
        # Рисуем трек
        pygame.draw.rect(surface, (100, 100, 100), self.rect, border_radius=5)
        
        # Рисуем заполненную часть
        filled_rect = self.rect.copy()
        filled_rect.width = self.handle_rect.centerx - self.rect.x
        pygame.draw.rect(surface, SETTINGS.COLORS.get('ui_button', [100, 100, 100]), filled_rect, border_radius=5)
        
        # Рисуем ползунок
        pygame.draw.rect(surface, (200, 200, 200), self.handle_rect, border_radius=5)
        
        # Рисуем текст значения
        val_text = f"{int(self.val * 100)}%"
        text_surf = self.font.render(val_text, True, SETTINGS.COLORS['ui_text'])
        text_rect = text_surf.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
        surface.blit(text_surf, text_rect)
