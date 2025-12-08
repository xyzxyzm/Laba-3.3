import pygame
import sys
from src.engine.state_manager import State
from src.config.settings import SETTINGS
from src.ui.ui_elements import Button
from src.engine.resource_manager import RESOURCES



class MenuScene(State):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = []
        self.difficulties = ['easy', 'medium', 'hard']
        self.current_diff_idx = 0
        self.font_title = RESOURCES.get_font(SETTINGS.FONTS['main'], SETTINGS.FONTS['size_large'])
        self._create_ui()
        
    def enter(self):
        # Останавливаем фоновую музыку при возврате в меню
        pygame.mixer.music.stop()
        
    def _create_ui(self):
        self.buttons = [] # Сброс кнопок
        cx = SETTINGS.WIDTH // 2
        cy = SETTINGS.HEIGHT // 2
        w, h = 240, 55 # Немного шире и выше
        gap = 15
        
        # Выбор сложности (Кастомная реализация с использованием кнопок для стрелок)
        diff_name = self.difficulties[self.current_diff_idx].upper()
        
        # Стрелки
        arrow_size = 40
        y_diff = cy - h*2 - gap*2
        
        # Левая стрелка (<)
        self.buttons.append(Button(cx - w//2 - arrow_size - 10, y_diff, arrow_size, h, "<", self._prev_difficulty, style='glass'))
        
        # Отображение сложности (Некликабельная кнопка для стиля)
        # Мы обработаем это, просто нарисовав его, или добавив фиктивную кнопку. 
        # Давайте используем кнопку, но без callback для единообразия внешнего вида
        self.buttons.append(Button(cx - w//2, y_diff, w, h, f"{diff_name}", None, style='glass'))
        
        # Правая стрелка (>)
        self.buttons.append(Button(cx + w//2 + 10, y_diff, arrow_size, h, ">", self._next_difficulty, style='glass'))
        
        # Основные действия
        self.buttons.append(Button(cx - w//2, cy - h - gap, w, h, "CAMPAIGN", self._start_campaign, style='primary'))
        self.buttons.append(Button(cx - w//2, cy, w, h, "SINGLE PLAYER", self._start_single, style='primary'))
        self.buttons.append(Button(cx - w//2, cy + h + gap, w, h, "MULTIPLAYER", self._start_multi, style='primary'))
        
        # Второстепенные действия
        self.buttons.append(Button(cx - w//2, cy + h*2 + gap*2, w, h, "High Scores", self._show_highscores, style='glass'))
        self.buttons.append(Button(cx - w//2, cy + h*3 + gap*3, w, h, "Exit", self._exit_game, style='danger'))
        
    def _prev_difficulty(self):
        self.current_diff_idx = (self.current_diff_idx - 1) % len(self.difficulties)
        self._create_ui()

    def _next_difficulty(self):
        self.current_diff_idx = (self.current_diff_idx + 1) % len(self.difficulties)
        self._create_ui()
        
    def _show_highscores(self):
        from src.scenes.highscores_scene import HighScoresScene
        self.game.state_manager.change_state(HighScoresScene(self.game))
        
    def _cycle_difficulty(self):
        # Устарело, использовалось старой кнопкой
        self._next_difficulty()
        
    def _start_campaign(self):
        from src.scenes.game_scene import GameScene
        self.game.state_manager.change_state(GameScene(self.game, difficulty='campaign', num_players=1))

    def _start_single(self):
        from src.scenes.game_scene import GameScene
        diff = self.difficulties[self.current_diff_idx]
        self.game.state_manager.change_state(GameScene(self.game, difficulty=diff, num_players=1))
        
    def _start_multi(self):
        from src.scenes.game_scene import GameScene
        diff = self.difficulties[self.current_diff_idx]
        self.game.state_manager.change_state(GameScene(self.game, difficulty=diff, num_players=2))
        
    def _exit_game(self):
        self.game.running = False
        
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mouse_pos)
            
    def _draw_background(self, screen):
        # Профессиональный фон в темной теме
        # Глубокая темно-сине-серая основа
        bg_color = (15, 17, 22) 
        screen.fill(bg_color)
        
        # 1. Тонкая сетка
        # Очень слабые, тонкие линии
        grid_color = (255, 255, 255, 3) # Чрезвычайно слабый (альфа 3/255)
        cell_size = 50
        
        # Рисуем линии сетки
        grid_surf = pygame.Surface((SETTINGS.WIDTH, SETTINGS.HEIGHT), pygame.SRCALPHA)
        for x in range(0, SETTINGS.WIDTH, cell_size):
            pygame.draw.line(grid_surf, grid_color, (x, 0), (x, SETTINGS.HEIGHT), 1)
        for y in range(0, SETTINGS.HEIGHT, cell_size):
            pygame.draw.line(grid_surf, grid_color, (0, y), (SETTINGS.WIDTH, y), 1)
        screen.blit(grid_surf, (0,0))
        
        # 2. Виньетка (Значительно затемняем углы)
        # Создаем текстуру радиального градиента
        vignette = pygame.Surface((SETTINGS.WIDTH, SETTINGS.HEIGHT), pygame.SRCALPHA)
        rect = vignette.get_rect()
        # Рисуем большой радиальный градиент вручную или имитируем кругами
        # Центр прозрачный, края черные
        max_dist = (SETTINGS.WIDTH**2 + SETTINGS.HEIGHT**2)**0.5 / 2
        
        # Оптимизация: Просто рисуем несколько больших концентрических эллипсов с низкой альфой
        # чтобы затемнить края.
        center = (SETTINGS.WIDTH//2, SETTINGS.HEIGHT//2)
        
        # Внешний темный слой
        pygame.draw.rect(vignette, (0, 0, 0, 100), rect)
        
        # Вырезаем центр (делаем его прозрачным) - сложно в pygame без режимов смешивания
        # Более простой подход: Рисуем черную поверхность и накладываем "светлую" текстуру с режимом смешивания SUB?
        # Или просто рисуем черные круги с увеличивающейся альфой от центра?
        
        # Давайте используем подход "свечения", но инвертированный.
        # Рисуем большое градиентное свечение в центре, которое немного светлее фона
        glow_surf = pygame.Surface((SETTINGS.WIDTH, SETTINGS.HEIGHT), pygame.SRCALPHA)
        # Светлее сине-серый в центре
        glow_color = (30, 35, 45, 20) 
        pygame.draw.circle(glow_surf, glow_color, center, 500)
        pygame.draw.circle(glow_surf, glow_color, center, 300)
        screen.blit(glow_surf, (0,0))
        
        # 3. Эффект сканлайна (опционально, очень тонкий)
        # Добавляет ощущение "монитора"
        scan_surf = pygame.Surface((SETTINGS.WIDTH, SETTINGS.HEIGHT), pygame.SRCALPHA)
        for y in range(0, SETTINGS.HEIGHT, 4):
            pygame.draw.line(scan_surf, (0, 0, 0, 20), (0, y), (SETTINGS.WIDTH, y), 1)
        screen.blit(scan_surf, (0,0))

    def draw(self, screen):
        self._draw_background(screen)
        
        # Заголовок
        # Рисуем тень
        title_text = SETTINGS.TITLE.upper()
        shadow_surf = self.font_title.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(SETTINGS.WIDTH // 2 + 4, 100 + 4))
        screen.blit(shadow_surf, shadow_rect)
        
        # Рисуем основной заголовок
        title_surf = self.font_title.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SETTINGS.WIDTH // 2, 100))
        screen.blit(title_surf, title_rect)
        
        # Подзаголовок или декоративная линия
        pygame.draw.line(screen, (0, 200, 255), (title_rect.left, title_rect.bottom + 10), (title_rect.right, title_rect.bottom + 10), 3)
        
        for btn in self.buttons:
            btn.draw(screen)
            
    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)
 
    def on_resize(self, width, height):
        self._create_ui()
