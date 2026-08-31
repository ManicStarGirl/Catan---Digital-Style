from config import settings
import random

class Screen:
    """Base class for all game screens"""
    def __init__(self, screenManager, screen):
        self.screenManager = screenManager
        self.screen = screen
        self.background = settings.deepSea
        
        # dice animation variables
        self.diceList = [1, 2, 3, 4, 5, 6]
        self.isRolling = False
        self.rollStartTime = 0
        self.ROLL_DURATION = 880  # Duration of the roll in milliseconds
        self.SHUFFLE_DELAY = 80    # Milliseconds between number switches during animation
        self.lastShuffleTime = 0
        self.redYOffset = 0
        self.yellowYOffset = 0
        self.redShakeOffset = random.randint(10, 20)
        self.yellowShakeOffset = random.randint(10, 20)
        self.redNumShakes = random.randint(2, 5)
        self.yellowNumShakes = random.randint(2, 5)
        self.currentRedValue = random.choice(self.diceList)
        self.currentYellowValue = random.choice(self.diceList)
    
    def OnEnter(self):
        """Called when screen is entered - sets up common UI elements"""
        # Common UI setup for all screens
        self.buttonWidth = self.screen.get_width() / 2.5
        self.buttonHeight = self.screen.get_height() / 10
        self.buttonColor = (255, 255, 255)
        self.buttonHoverColor = (200, 200, 200)
        self.buttonGreyedOutColor = (150, 150, 150)
        self.fontSize = self.screen.get_height() / 20
        self.scrollDistance = 0
    
    def OnExit(self):
        """Called when screen is exited - cleanup can be done here"""
        pass
    
    def Update(self, dt, currentTime):
        """Update screen logic - called every frame with delta time"""
        pass
    
    def Draw(self):
        """Draw screen content - called every frame"""
        pass