from config import deepSea

class Screen:
    """Base class for all game screens"""
    def __init__(self, screenManager, screen):
        self.screenManager = screenManager
        self.screen = screen
        self.background = deepSea
    
    def OnEnter(self):
        """Called when screen is entered - sets up common UI elements"""
        # Common UI setup for all screens
        self.buttonWidth = self.screen.get_width() / 2.5
        self.buttonHeight = self.screen.get_height() / 10
        self.buttonColor = (255, 255, 255)
        self.buttonHoverColor = (200, 200, 200)
        self.buttonGreyedOutColor = (150, 150, 150)
        self.fontSize = self.screen.get_height() / 20
    
    def OnExit(self):
        """Called when screen is exited - cleanup can be done here"""
        pass
    
    def Update(self, dt):
        """Update screen logic - called every frame with delta time"""
        pass
    
    def Draw(self):
        """Draw screen content - called every frame"""
        pass