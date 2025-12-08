class StateManager:
    def __init__(self, game):
        self.game = game
        self.state = None
        
    def change_state(self, new_state):
        if self.state:
            self.state.exit()
        self.state = new_state
        if self.state:
            self.state.enter()
            
    def update(self):
        if self.state:
            self.state.update()
            
    def draw(self, screen):
        if self.state:
            self.state.draw(screen)
            
    def handle_event(self, event):
        if self.state:
            self.state.handle_event(event)

class State:
    def __init__(self, game):
        self.game = game
        
    def enter(self):
        pass
        
    def exit(self):
        pass
        
    def update(self):
        pass
        
    def draw(self, screen):
        pass
        
    def handle_event(self, event):
        pass
