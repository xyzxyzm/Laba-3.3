import pygame
import os
from src.config.settings import SETTINGS

class ResourceManager:
    def __init__(self):
        self.images = {}
        self.fonts = {}
        self.sounds = {}
        self.base_dir = SETTINGS.base_dir
        self.assets_dir = os.path.join(self.base_dir, 'assets')
        
    def get_image(self, name):
        if name not in self.images:
            path = os.path.join(self.assets_dir, 'images', name)
            if os.path.exists(path):
                self.images[name] = pygame.image.load(path).convert_alpha()
            else:
                # Создаем заглушку, если изображение не найдено
                print(f"Изображение не найдено: {name}, создаем заглушку.")
                surf = pygame.Surface((SETTINGS.LAYOUT['cell_size'], SETTINGS.LAYOUT['cell_size']))
                surf.fill((255, 0, 255)) # Пурпурная заглушка
                self.images[name] = surf
        return self.images[name]

    def get_font(self, name, size):
        key = (name, size)
        if key not in self.fonts:
            # Пока используем системный шрифт или конкретный файл шрифта
            # Если имя - это путь к файлу в assets/fonts, загружаем его. Иначе используем SysFont.
            font_path = os.path.join(self.assets_dir, 'fonts', name)
            if os.path.exists(font_path):
                 self.fonts[key] = pygame.font.Font(font_path, size)
            else:
                self.fonts[key] = pygame.font.SysFont(name, size)
        return self.fonts[key]
    
    def get_sound(self, name):
        if not SETTINGS.game_config['audio']['enabled']:
            return None
            
        if name not in self.sounds:
            path = os.path.join(self.assets_dir, 'sounds', name)
            if os.path.exists(path):
                self.sounds[name] = pygame.mixer.Sound(path)
                self.sounds[name].set_volume(SETTINGS.game_config['audio']['sfx_volume'])
            else:
                print(f"Звуковой файл не найден: {name}")
                self.sounds[name] = None
        return self.sounds[name]

# Глобальный экземпляр
RESOURCES = ResourceManager()
