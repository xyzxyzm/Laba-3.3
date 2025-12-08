import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.engine.game import Game

if __name__ == "__main__":
    game = Game()
    from src.scenes.menu_scene import MenuScene
    game.state_manager.change_state(MenuScene(game)) 
    game.run()
