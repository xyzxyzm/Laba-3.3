import json
import os

class Settings:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.config_dir = os.path.join(self.base_dir, 'src', 'config')
        
        self.game_config = self._load_json('game_config.json')
        self.graphics_config = self._load_json('graphics.json')
        
        # Быстрый доступ к настройкам
        self.WIDTH = self.game_config['game']['width']
        self.HEIGHT = self.game_config['game']['height']
        self.FPS = self.game_config['game']['fps']
        self.TITLE = self.game_config['game']['title']
        
        self.COLORS = self.graphics_config['colors']
        self.FONTS = self.graphics_config['fonts']
        self.LAYOUT = self.graphics_config['layout']

    def _load_json(self, filename):
        path = os.path.join(self.config_dir, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Файл конфигурации не найден: {path}")
            return {}
        except json.JSONDecodeError:
            print(f"Ошибка декодирования JSON: {path}")
            return {}

# Глобальный экземпляр настроек
SETTINGS = Settings()
