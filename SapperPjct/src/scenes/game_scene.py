import pygame
import os
from src.engine.state_manager import State
from src.objects.board import Board
from src.config.settings import SETTINGS
from src.engine.resource_manager import RESOURCES

class GameScene(State):
    def __init__(self, game, difficulty='easy', num_players=1, level=1):
        super().__init__(game)
        self.difficulty = difficulty
        self.num_players = num_players
        self.level = level
        self.boards = []
        self.game_over_timer = 0
        self.start_time = pygame.time.get_ticks()
        self.font_hud = RESOURCES.get_font(SETTINGS.FONTS['main'], SETTINGS.FONTS['size_medium'])
        
        self.pause_btn = None
        self.p1_lost_triggered = False
        self.p2_lost_triggered = False
        self._setup_boards()
        self._create_ui()
        
        # Запускаем фоновую музыку (сначала пробуем OGG, затем MP3)
        if SETTINGS.game_config['audio']['enabled']:
            music_loaded = False
            for music_file in ['bgm.ogg', 'bgm.mp3']:
                music_path = os.path.join(RESOURCES.assets_dir, 'sounds', music_file)
                if os.path.exists(music_path):
                    try:
                        pygame.mixer.music.load(music_path)
                        pygame.mixer.music.set_volume(SETTINGS.game_config['audio']['music_volume'])
                        pygame.mixer.music.play(-1) # Зацикливаем навсегда
                        music_loaded = True
                        print(f"Играет фоновая музыка: {music_file}")
                        break
                    except pygame.error as e:
                        print(f"Не удалось загрузить {music_file}: {e}")
            
            if not music_loaded:
                print("Фоновая музыка не найдена. Добавьте bgm.ogg или bgm.mp3 в assets/sounds/")
                
    def _create_ui(self):
        from src.ui.ui_elements import Button
        from src.ui.debug_panel import DebugPanel
        
        # Кнопка паузы в правом верхнем углу (только иконка, квадратная)
        w, h = 40, 40 
        x = SETTINGS.WIDTH - w - 20
        y = 20
        self.pause_btn = Button(x, y, w, h, "", self._pause_game, style='glass')
        
        # Кнопка отладки (иконка гаечного ключа) рядом с паузой
        debug_x = x - w - 10
        self.debug_btn = Button(debug_x, y, w, h, "", self._toggle_debug, style='glass', icon='wrench')
        
        self.debug_panel = DebugPanel(self)
        
    def _toggle_debug(self):
        self.debug_panel.toggle()
        
    def debug_force_win(self, player=1):
        # Логика принудительной победы
        if self.num_players == 1:
            self.boards[0].win = True
            self.boards[0].game_over = True
            self.boards[0]._reveal_all_mines() # Опционально: показать мины как при победе? Или просто закончить.
        else:
            if player == 1:
                self.boards[0].win = True
                self.boards[0].game_over = True
                # Принудительное поражение P2 для немедленного завершения игры? 
                # Или просто ждать P2? 
                # Пользователь сказал "Player 1 Win", обычно подразумевается, что игра заканчивается победой P1.
                # В нашей логике игра заканчивается, когда ОБА закончат.
                # Поэтому, вероятно, стоит завершить P2 как проигравшего?
                self.boards[1].game_over = True
                self.boards[1].win = False
            elif player == 2:
                self.boards[1].win = True
                self.boards[1].game_over = True
                self.boards[0].game_over = True
                self.boards[0].win = False
            elif player == 3: # Оба выиграли
                self.boards[0].win = True
                self.boards[0].game_over = True
                self.boards[1].win = True
                self.boards[1].game_over = True
                
    def _pause_game(self):
        from src.scenes.pause_scene import PauseScene
        self.game.state_manager.change_state(PauseScene(self.game, self))
        
    def _setup_boards(self):
        if self.difficulty == 'campaign':
            # Прогрессия кампании: начинаем с малого, увеличиваем/усложняем
            rows = 5 + self.level * 2
            cols = 5 + self.level * 2
            mines = int(rows * cols * 0.15) # 15% мин
        else:
            diff_config = SETTINGS.game_config['difficulty_levels'][self.difficulty]
            rows = diff_config['rows']
            cols = diff_config['cols']
            mines = diff_config['mines']
            
        # Создаем доски изначально (позиции будут установлены в _apply_layout)
        self.boards = []
        if self.num_players == 1:
            self.boards.append(Board(rows, cols, mines, 0, 0))
        else:
            self.boards.append(Board(rows, cols, mines, 0, 0))
            self.boards.append(Board(rows, cols, mines, 0, 0))
            
        self._apply_layout()
        
    def _apply_layout(self):
        if not self.boards: return
        
        board = self.boards[0]
        rows = board.rows
        cols = board.cols
        
        # Вычисляем размер доски
        board_w = cols * SETTINGS.LAYOUT['cell_size']
        board_h = rows * SETTINGS.LAYOUT['cell_size']
        
        # Корректируем Y, чтобы освободить место для HUD
        hud_height = 80 # Увеличено для лучшего интервала
        margin = 30
        
        # Вычисляем требуемый размер
        if self.num_players == 1:
            req_w = board_w + margin * 2
            req_h = board_h + hud_height + margin * 2
        else:
            gap = 60 # Увеличенный зазор для мультиплеера, чтобы избежать перекрытия
            req_w = board_w * 2 + gap + margin * 2
            req_h = board_h + hud_height + margin * 2
            
        # Вычисляем масштаб
        self.scale = 1.0
        if req_w > SETTINGS.WIDTH or req_h > SETTINGS.HEIGHT:
            scale_w = SETTINGS.WIDTH / req_w
            scale_h = SETTINGS.HEIGHT / req_h
            self.scale = min(scale_w, scale_h)
            
        scaled_cell_size = int(SETTINGS.LAYOUT['cell_size'] * self.scale)
        scaled_board_w = cols * scaled_cell_size
        scaled_board_h = rows * scaled_cell_size
        
        if self.num_players == 1:
            x = (SETTINGS.WIDTH - scaled_board_w) // 2
            y = (SETTINGS.HEIGHT - scaled_board_h + hud_height) // 2
            self.boards[0].update_layout(x, y, scaled_cell_size)
        else:
            gap = 60 * self.scale # Масштабируем зазор тоже
            total_w = scaled_board_w * 2 + gap
            start_x = (SETTINGS.WIDTH - total_w) // 2
            y = (SETTINGS.HEIGHT - scaled_board_h + hud_height) // 2
            
            self.boards[0].update_layout(start_x, y, scaled_cell_size)
            self.boards[1].update_layout(start_x + scaled_board_w + gap, y, scaled_cell_size)
            
    def on_resize(self, width, height):
        self._apply_layout()
        self._create_ui() # Пересоздаем UI для обновления позиции кнопок

    def pause_game(self):
        self.paused = True
        self.pause_start_time = pygame.time.get_ticks()
        pygame.mixer.music.pause()
        
    def resume_game(self):
        self.paused = False
        if hasattr(self, 'pause_start_time'):
            pause_duration = pygame.time.get_ticks() - self.pause_start_time
            self.start_time += pause_duration # Сдвигаем время старта, чтобы игнорировать длительность паузы
        pygame.mixer.music.unpause()
             
    def update(self):
        if self.debug_panel:
            self.debug_panel.update(pygame.mouse.get_pos())
            
        if self.pause_btn:
            self.pause_btn.update(pygame.mouse.get_pos())
        if self.debug_btn:
            self.debug_btn.update(pygame.mouse.get_pos())
            
        # Если активен эффект проигрыша, обновляем его
        if hasattr(self, 'losing') and self.losing:
            now = pygame.time.get_ticks()
            diff = now - self.lose_start
            duration = getattr(self, 'lose_duration', 1500)
            
            if diff > duration:
                from src.scenes.game_over_scene import GameOverScene
                winner_text = getattr(self, 'lose_winner_text', 'You Lose!')
                self.game.state_manager.change_state(GameOverScene(self.game, winner_text, self.lose_elapsed, self.difficulty, self.num_players, self.level))
                self.losing = False
            return # Не обрабатываем логику игры во время затемнения
        
        # Проверяем условия окончания игры
        all_finished = True
        any_lost = False
        for board in self.boards:
            if not board.game_over:
                all_finished = False
            elif not board.win:
                any_lost = True
                
        # Запускаем эффект проигрыша немедленно, если какая-либо доска проиграла (и эффект еще не активен)
        if self.num_players == 1:
            if any_lost and not hasattr(self, 'losing'):
                 # Останавливаем музыку и играем звук взрыва
                pygame.mixer.music.stop()
                sound = RESOURCES.get_sound('explode.wav')
                if sound:
                    sound.set_volume(SETTINGS.game_config['audio']['sfx_volume'])
                    sound.play()
                
                elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
                self._show_lose_effect(elapsed, 'lose.png', 2000)
                return
        else:
            # Логика мультиплеера
            p1 = self.boards[0]
            p2 = self.boards[1]
            
            p1_finished = p1.game_over
            p2_finished = p2.game_over
            
            # Ждем пока ОБА закончат
            if p1_finished and p2_finished and not hasattr(self, 'losing'):
                pygame.mixer.music.stop()
                
                p1_win = p1.win
                p2_win = p2.win
                
                img_name = 'mp_draw.png'
                sound_name = 'explode.wav'
                
                if p1_win and p2_win:
                    # Оба выиграли -> Используем mp_win.png
                    img_name = 'mp_win.png'
                    sound_name = 'mp_lose.wav'
                elif not p1_win and not p2_win:
                    # Оба проиграли -> Ничья
                    img_name = 'mp_draw.png'
                elif p1_win and not p2_win:
                    # P1 выиграл, P2 проиграл -> Показать проигрыш P2
                    img_name = 'p2_lose.png'
                    sound_name = 'mp_lose.wav'
                elif not p1_win and p2_win:
                    # P1 проиграл, P2 выиграл -> Показать проигрыш P1
                    img_name = 'p1_lose.png'
                    sound_name = 'mp_lose.wav'
                    
                sound = RESOURCES.get_sound(sound_name)
                if sound:
                    sound.set_volume(SETTINGS.game_config['audio']['sfx_volume'])
                    sound.play()
                
                # MP win/lose изображения: 9 секунд, другие: 2 секунды
                if img_name in ['mp_win.png', 'p1_lose.png', 'p2_lose.png']:
                    duration = 9000  # 9 секунд
                else:
                    duration = 2000  # 2 секунды
                
                # Определяем текст победителя для GameOverScene
                if img_name == 'p1_lose.png':
                    winner_text = 'Player 2 Wins!'
                elif img_name == 'p2_lose.png':
                    winner_text = 'Player 1 Wins!'
                elif img_name == 'mp_win.png':
                    winner_text = 'Both Players Win!'
                elif img_name == 'mp_draw.png':
                    winner_text = 'Draw - Both Lost!'
                else:
                    winner_text = 'You Lose!'
                
                elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
                self._show_lose_effect(elapsed, img_name, duration, winner_text)
                return

        if all_finished:
            self.game_over_timer += 1
            if self.game_over_timer > 60: # Ждем ~1 секунду
                from src.scenes.game_over_scene import GameOverScene
                # Определяем победителя для MP
                winner_text = "Game Over"
                elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
                
                if self.num_players == 1:
                    if self.boards[0].win:
                        winner_text = "You Win!"
                        # Останавливаем музыку и играем звук победы
                        pygame.mixer.music.stop()
                        sound = RESOURCES.get_sound('win.wav')
                        if sound:
                            sound.set_volume(SETTINGS.game_config['audio']['sfx_volume'])
                            sound.play()
                        
                        if self.difficulty == 'campaign':
                             # Проверяем максимальный уровень
                             MAX_CAMPAIGN_LEVEL = 10
                             if self.level >= MAX_CAMPAIGN_LEVEL:
                                 winner_text = "Campaign Complete!"
                                 self.game.state_manager.change_state(GameOverScene(self.game, winner_text, elapsed, self.difficulty, self.num_players, self.level))
                                 return
                             
                             # Переходим на следующий уровень
                             self.game.state_manager.change_state(GameScene(self.game, 'campaign', 1, self.level + 1))
                             return
                        self.game.state_manager.change_state(GameOverScene(self.game, winner_text, elapsed, self.difficulty, self.num_players, self.level))
                    else:
                        pass
                        
                else:
                    p1_win = self.boards[0].win
                    p2_win = self.boards[1].win
                    if p1_win and p2_win: winner_text = "Draw!"
                    elif p1_win: winner_text = "Player 1 Wins!"
                    elif p2_win: winner_text = "Player 2 Wins!"
                    else: winner_text = "Both Lost!"
                    
                    # Останавливаем музыку для мультиплеера тоже
                    pygame.mixer.music.stop()
                    self.game.state_manager.change_state(GameOverScene(self.game, winner_text, None, self.difficulty, self.num_players, self.level))
                    
    def _show_lose_effect(self, elapsed, image_name='lose.png', duration=2000, winner_text='You Lose!'):
        # Это блокирующий эффект для простоты, или мы можем добавить состояние
        # Давайте сделаем простой цикл здесь или, лучше, добавим подсостояние
        # Пока просто рисуем это в главном цикле, устанавливая флаг
        self.losing = True
        self.lose_image_name = image_name
        self.lose_start = pygame.time.get_ticks()
        self.lose_elapsed = elapsed
        self.lose_duration = duration
        self.lose_winner_text = winner_text
        
    def draw(self, screen):
        # 1. Рисуем фон
        bg_name = None
        if os.path.exists(os.path.join(RESOURCES.assets_dir, 'images', 'background.png')):
            bg_name = 'background.png'
        elif os.path.exists(os.path.join(RESOURCES.assets_dir, 'images', 'background.jpg')):
            bg_name = 'background.jpg'
            
        if bg_name:
            # Рисуем темную основу
            screen.fill((20, 20, 20))
            
            bg_img = RESOURCES.get_image(bg_name)
            bg_scaled = pygame.transform.scale(bg_img, (SETTINGS.WIDTH, SETTINGS.HEIGHT))
            
            # Рисуем фон полностью непрозрачным сначала
            screen.blit(bg_scaled, (0, 0))
            
            # Добавляем глобальное темное наложение, чтобы UI выделялся
            # Не слишком темное, чтобы не скрыть крутое изображение, но достаточно, чтобы уменьшить шум
            overlay = pygame.Surface((SETTINGS.WIDTH, SETTINGS.HEIGHT))
            overlay.set_alpha(100) # ~40% затемнения
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
        else:
            # Запасная сетка
            bg_color = (15, 17, 22) 
            screen.fill(bg_color)
            grid_color = (255, 255, 255, 3)
            cell_size = 50
            grid_surf = pygame.Surface((SETTINGS.WIDTH, SETTINGS.HEIGHT), pygame.SRCALPHA)
            for x in range(0, SETTINGS.WIDTH, cell_size):
                pygame.draw.line(grid_surf, grid_color, (x, 0), (x, SETTINGS.HEIGHT), 1)
            for y in range(0, SETTINGS.HEIGHT, cell_size):
                pygame.draw.line(grid_surf, grid_color, (0, y), (SETTINGS.WIDTH, y), 1)
            screen.blit(grid_surf, (0,0))
            
        # 2. Рисуем полупрозрачное наложение позади досок (Эффект стекла)
        for board in self.boards:
            # Область доски
            bx = board.cells[0][0].rect.left - 15
            by = board.cells[0][0].rect.top - 15
            bw = board.cols * board.cell_size + 30
            bh = board.rows * board.cell_size + 30
            
            # Стеклянная панель - Темнее для контраста
            panel_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
            pygame.draw.rect(panel_surf, (10, 10, 10, 180), panel_surf.get_rect(), border_radius=15) # Темнее и более непрозрачно
            pygame.draw.rect(panel_surf, (255, 255, 255, 20), panel_surf.get_rect(), 1, border_radius=15) # Тонкая граница
            screen.blit(panel_surf, (bx, by))
        
        # 3. Рисуем HUD (Таймер)
        if hasattr(self, 'paused') and self.paused:
            elapsed = (self.pause_start_time - self.start_time) // 1000
        else:
            elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        timer_text = f"TIME: {elapsed:03}"
        
        # Панель таймера
        # Белый текст для максимальной читаемости
        timer_surf = self.font_hud.render(timer_text, True, (255, 255, 255)) 
        padding_x, padding_y = 20, 10
        timer_w = timer_surf.get_width() + padding_x * 2
        timer_h = timer_surf.get_height() + padding_y * 2
        timer_x = SETTINGS.WIDTH // 2 - timer_w // 2
        timer_y = 10
        
        timer_bg = pygame.Surface((timer_w, timer_h), pygame.SRCALPHA)
        # Темный фон для панели
        pygame.draw.rect(timer_bg, (0, 0, 0, 200), timer_bg.get_rect(), border_radius=10)
        # Голубая акцентная граница
        pygame.draw.rect(timer_bg, (0, 255, 255, 100), timer_bg.get_rect(), 1, border_radius=10) 
        screen.blit(timer_bg, (timer_x, timer_y))
        screen.blit(timer_surf, (timer_x + padding_x, timer_y + padding_y))
        
        for i, board in enumerate(self.boards):
            board.draw(screen)
            # Рисуем счетчик мин для каждой доски
            mines_left = board.total_mines - board.flags_placed
            mines_text = f"MINES: {mines_left}"
            
            # Панель мин
            # Белый текст
            mines_surf = self.font_hud.render(mines_text, True, (255, 255, 255))
            
            # Позиция над доской
            bx = board.cells[0][0].rect.left
            by = board.cells[0][0].rect.top - 75
            
            padding_x, padding_y = 15, 8
            mines_w = mines_surf.get_width() + padding_x * 2
            mines_h = mines_surf.get_height() + padding_y * 2
            
            mines_bg = pygame.Surface((mines_w, mines_h), pygame.SRCALPHA)
            # Темный фон
            pygame.draw.rect(mines_bg, (0, 0, 0, 200), mines_bg.get_rect(), border_radius=8)
            # Красная акцентная граница
            pygame.draw.rect(mines_bg, (255, 80, 80, 100), mines_bg.get_rect(), 1, border_radius=8) 
            
            screen.blit(mines_bg, (bx, by))
            screen.blit(mines_surf, (bx + padding_x, by + padding_y))
            
        if hasattr(self, 'losing') and self.losing:
            # Рисуем изображение проигрыша с затуханием
            now = pygame.time.get_ticks()
            diff = now - self.lose_start
            duration = getattr(self, 'lose_duration', 1500)
            
            # Для MP изображений (9сек), показываем полную непрозрачность 8.8с, затем быстрое затухание 0.2с
            # Для других изображений (2сек), затухание на протяжении всего времени
            img_name = getattr(self, 'lose_image_name', 'lose.png')
            
            if img_name in ['mp_win.png', 'p1_lose.png', 'p2_lose.png']:
                # Показываем полную непрозрачность 8800мс, затем затухание в последние 200мс
                display_time = 8800
                fade_time = 200
                
                if diff < display_time:
                    alpha = 255  # Полная непрозрачность
                else:
                    # Быстрое затухание в последние 200мс
                    fade_progress = (diff - display_time) / fade_time
                    alpha = max(0, int(255 * (1 - fade_progress)))
            else:
                # Нормальное затухание на протяжении всего времени
                alpha = max(0, 255 - int((diff / duration) * 255))
            
            lose_img = RESOURCES.get_image(img_name).copy() # Копируем, чтобы избежать изменения кэшированной версии
            
            # Масштабируем изображение, чтобы оно было меньше (макс 600x600)
            img_w, img_h = lose_img.get_size()
            max_size = 600
            if img_w > max_size or img_h > max_size:
                scale = max_size / max(img_w, img_h)
                new_w = int(img_w * scale)
                new_h = int(img_h * scale)
                lose_img = pygame.transform.scale(lose_img, (new_w, new_h))
            
            # Центрируем изображение
            img_rect = lose_img.get_rect(center=(SETTINGS.WIDTH//2, SETTINGS.HEIGHT//2))
            
            # Применяем альфа-канал
            lose_img.set_alpha(alpha)
            screen.blit(lose_img, img_rect)
            
        if self.pause_btn:
            self.pause_btn.draw(screen)
        if self.debug_btn:
            self.debug_btn.draw(screen)
        if self.debug_panel:
            self.debug_panel.draw(screen)
            
    def handle_event(self, event):
        if self.debug_panel and self.debug_panel.handle_event(event):
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Проверяем кнопку паузы сначала
            if self.pause_btn and self.pause_btn.handle_event(event):
                return
            if self.debug_btn and self.debug_btn.handle_event(event):
                return
 
            # В MP, мы можем захотеть ограничить клики конкретными областями или использовать разные вводы?
            # Пока что клики мышью работают на любой доске
            for board in self.boards:
                board.handle_click(event.pos, event.button)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Открываем меню паузы
                from src.scenes.pause_scene import PauseScene
                self.game.state_manager.change_state(PauseScene(self.game, self))
