import pygame
import numpy as np
import math

class SoundGenerator:
    def __init__(self):
        self.sample_rate = 44100
        self.bits = 16
        pygame.mixer.pre_init(self.sample_rate, -self.bits, 1) 
        
    def _make_sound(self, wave):
        audio = wave.astype(np.int16)
        if pygame.mixer.get_init()[2] == 2: # Проверить, является ли стерео
            audio = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(audio)

    def generate_beep(self, frequency=440, duration=0.1, volume=0.5):
        n_samples = int(self.sample_rate * duration)
        # Сгенерировать синусоидальную волну
        t = np.linspace(0, duration, n_samples, False)
        wave = np.sin(2 * np.pi * frequency * t) * volume * (2**(self.bits-1) - 1)
        return self._make_sound(wave)
        
    def generate_noise(self, duration=0.1, volume=0.5):
        n_samples = int(self.sample_rate * duration)
        wave = np.random.uniform(-1, 1, n_samples) * volume * (2**(self.bits-1) - 1)
        return self._make_sound(wave)

    def get_click_sound(self):
        return self.generate_beep(800, 0.05, 0.3)
        
    def get_explosion_sound(self):
        return self.generate_noise(0.5, 0.5)
        
    def get_win_sound(self):
        s1 = self.generate_beep(523.25, 0.1, 0.4) # C5
        s2 = self.generate_beep(659.25, 0.1, 0.4) # E5
        s3 = self.generate_beep(783.99, 0.2, 0.4) # G5
        return s1 
        return self.generate_beep(1000, 0.3, 0.4)

SOUND_GEN = SoundGenerator()
