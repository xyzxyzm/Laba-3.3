import pygame
import random
from src.objects.cell import Cell
from src.config.settings import SETTINGS

class Board:
    def __init__(self, rows, cols, mines, x_offset, y_offset, cell_size=None):
        self.rows = rows
        self.cols = cols
        self.total_mines = mines
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.cell_size = cell_size if cell_size else SETTINGS.LAYOUT['cell_size']
        
        self.cells = []
        self.game_over = False
        self.win = False
        self.first_click = True
        self.flags_placed = 0
        
        self._create_grid()
        
    def _create_grid(self):
        self.cells = []
        for r in range(self.rows):
            row_cells = []
            for c in range(self.cols):
                x = self.x_offset + c * self.cell_size
                y = self.y_offset + r * self.cell_size
                row_cells.append(Cell(r, c, x, y, self.cell_size))
            self.cells.append(row_cells)
            
    def update_layout(self, x_offset, y_offset, cell_size):
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.cell_size = cell_size
        
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.cells[r][c]
                cell.x = self.x_offset + c * self.cell_size
                cell.y = self.y_offset + r * self.cell_size
                cell.width = self.cell_size
                cell.height = self.cell_size
                cell.rect = pygame.Rect(cell.x, cell.y, cell.width, cell.height)
            
    def _place_mines(self, safe_row, safe_col):
        mines_placed = 0
        while mines_placed < self.total_mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            
            # Не ставим мину на уже существующую или на безопасную стартовую клетку (и соседей)
            if not self.cells[r][c].is_mine and (abs(r - safe_row) > 1 or abs(c - safe_col) > 1):
                self.cells[r][c].is_mine = True
                mines_placed += 1
                
        # Подсчет соседей
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.cells[r][c].is_mine:
                    self.cells[r][c].neighbor_mines = self._count_neighbors(r, c)

    def _count_neighbors(self, row, col):
        count = 0
        for r in range(max(0, row - 1), min(self.rows, row + 2)):
            for c in range(max(0, col - 1), min(self.cols, col + 2)):
                if self.cells[r][c].is_mine:
                    count += 1
        return count
        
    def handle_click(self, pos, button):
        if self.game_over:
            return

        # Находим нажатую клетку
        clicked_cell = None
        for row in self.cells:
            for cell in row:
                if cell.rect.collidepoint(pos):
                    clicked_cell = cell
                    break
            if clicked_cell:
                break
                
        if not clicked_cell:
            return
            
        if button == 1: # Левый клик
            self._reveal(clicked_cell)
        elif button == 3: # Правый клик
            self._toggle_flag(clicked_cell)
            
        self._check_win()
        
    def _reveal(self, cell):
        if cell.is_open or cell.is_flagged:
            return
            
        if self.first_click:
            self._place_mines(cell.row, cell.col)
            self.first_click = False
        
        # Проигрываем звук клика (тихий), если игра не окончена
        if not self.game_over:
            from src.engine.resource_manager import RESOURCES
            sound = RESOURCES.get_sound('click.wav')
            if sound:
                # Базовая громкость 0.15, умноженная на мастер-громкость эффектов
                volume = SETTINGS.game_config['audio']['sfx_volume']
                sound.set_volume(volume)
                sound.play()
            
        cell.is_open = True
        
        if cell.is_mine:
            self.game_over = True
            self.win = False
            self._reveal_all_mines()
        elif cell.neighbor_mines == 0:
            # Заливка (открытие пустых областей)
            for r in range(max(0, cell.row - 1), min(self.rows, cell.row + 2)):
                for c in range(max(0, cell.col - 1), min(self.cols, cell.col + 2)):
                    neighbor = self.cells[r][c]
                    if not neighbor.is_open:
                        self._reveal(neighbor)
                        
    def _toggle_flag(self, cell):
        if not cell.is_open:
            cell.is_flagged = not cell.is_flagged
            if cell.is_flagged:
                self.flags_placed += 1
            else:
                self.flags_placed -= 1
                
    def _reveal_all_mines(self):
        for row in self.cells:
            for cell in row:
                if cell.is_mine:
                    cell.is_open = True
                    
    def _check_win(self):
        if self.game_over:
            return
            
        covered_cells = 0
        for row in self.cells:
            for cell in row:
                if not cell.is_open and not cell.is_mine:
                    covered_cells += 1
                    
        if covered_cells == 0:
            self.game_over = True
            self.win = True
            
    def draw(self, surface):
        # Обновляем размер шрифта в зависимости от текущего размера клетки
        # Это немного затратно делать каждый кадр, если мы перезагружаем шрифт,
        # но мы можем проверить, изменился ли размер клетки, или сделать это один раз в update_layout
        # Пока просто передаем размер клетки в cell.draw или обрабатываем это там.
        # На самом деле, Cell.draw использует RESOURCES.get_font. Давайте убедимся, что запрашиваем подходящий размер.
        
        # Вычисляем подходящий размер шрифта (например, 80% от высоты клетки)
        font_size = int(self.cell_size * 0.8)
        # Нам нужно передать это в клетку или установить глобальное/статическое свойство
        # Так как Cell использует RESOURCES напрямую, нам может потребоваться изменить Cell.draw или передать его
        
        for row in self.cells:
            for cell in row:
                cell.draw(surface, font_size)
