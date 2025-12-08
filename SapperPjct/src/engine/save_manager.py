import json
import os
from src.config.settings import SETTINGS

class SaveManager:
    def __init__(self):
        self.data_dir = os.path.join(SETTINGS.base_dir, 'data')
        self.scores_file = os.path.join(self.data_dir, 'highscores.json')
        self.scores = self._load_scores()
        
    def _load_scores(self):
        if not os.path.exists(self.scores_file):
            return {'easy': [], 'medium': [], 'hard': []}
            
        try:
            with open(self.scores_file, 'r') as f:
                return json.load(f)
        except:
            return {'easy': [], 'medium': [], 'hard': []}
            
    def save_score(self, difficulty, time):
        if difficulty not in self.scores:
            self.scores[difficulty] = []
            
        self.scores[difficulty].append(time)
        self.scores[difficulty].sort()
        self.scores[difficulty] = self.scores[difficulty][:5] # Храним топ-5
        
        self._save_to_file()
        
    def _save_to_file(self):
        try:
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
            with open(self.scores_file, 'w') as f:
                json.dump(self.scores, f)
        except Exception as e:
            print(f"Error saving scores: {e}")
            
    def get_best_score(self, difficulty):
        if difficulty in self.scores and self.scores[difficulty]:
            return self.scores[difficulty][0]
        return None

SAVE_MANAGER = SaveManager()
