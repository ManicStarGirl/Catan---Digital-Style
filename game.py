import pygame, json
from ui import hex
from config import fpsLimit
from screens.mainMenuScreen import MainMenu
from screens.GameScreen import GameScreen
from screens.settingsScreen import Settings
from screens.colorSettingsScreen import ColorSettings
from screens.newGameScreen import NewGame
from screens.buildScreen import BuildScreen

# from screens.gameScreen import GameScreen  # when you create it

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
# Initialize pygame
pygame.init()

# Get screen dimensions and create fullscreen window
screenWidth, screenHeight = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.FULLSCREEN)
# Create clock for frame rate control
clock = pygame.time.Clock()

# ---------------------------------------------------------------------------
# Screen manager
# ---------------------------------------------------------------------------
class ScreenManager:
    """Manages screen transitions and game state"""
    def __init__(self):
        self.currentScreen = None
    
    def switchScreen(self, screenName):
        """Switch to a different screen based on screen_name"""
        if screenName == "mainMenu":
            self.currentScreen = MainMenu(self, screen)
            self.currentScreen.OnEnter()
        elif screenName == "new":
            self.currentScreen = NewGame(self, screen)
            self.currentScreen.OnEnter()
        elif screenName == "continue":
            try:
                with open("save.json", "r") as f:
                    savedData = json.load(f)
                tileList = [hex(*t) for t in savedData["tiles"]]
                if savedData["settlements"] is not None:
                    settlements = [[s[0], s[1], tuple(s[2]) if s[2] else None] for s in savedData["settlements"]]
                else:
                    settlements = None
                if savedData["roads"] is not None:
                    roads = [[r[0], r[1], r[2], tuple(r[3]) if r[3] else None] for r in savedData["roads"]]
                else:
                    roads = None
                if savedData["currentPlayer"] is not None:
                    player = (tuple(savedData["currentPlayer"][0]), savedData["currentPlayer"][1])
                else:
                    player = None
                self.currentScreen = GameScreen(self, screen, tileList, settlements, roads, player)
                self.currentScreen.OnEnter()
            except FileNotFoundError:
                pass
        elif screenName == "settings":
            self.currentScreen = Settings(self, screen)
            self.currentScreen.OnEnter()
        elif screenName == "colorSettings":
            self.currentScreen = ColorSettings(self, screen)
            self.currentScreen.OnEnter()
        elif screenName == "singleplayer":
            self.currentScreen = GameScreen(self, screen)
            self.currentScreen.OnEnter()
        elif screenName == "build":
            self.currentScreen = BuildScreen(self, screen)
            self.currentScreen.OnEnter()
        elif screenName == "quit":
            return False  # Signal to quit
        return True

# Initialize screen manager and start at main menu
screenManager = ScreenManager()
screenManager.switchScreen("mainMenu")

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
running = True
fullscreen = True
while running:
    # Calculate delta time (time since last frame) in seconds
    dt = clock.tick(fpsLimit) / 1000
    currentTime = pygame.time.get_ticks()
    
    # Update current screen and handle screen switching
    result = screenManager.currentScreen.Update(dt, currentTime)
    if result == "fullscreen":
        # Toggle fullscreen <-> windowed
        if fullscreen:
            screen = pygame.display.set_mode((1280, 720))
            fullscreen = False
        else:
            screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.FULLSCREEN)
            fullscreen = True
        screenManager.currentScreen.OnEnter()
    elif result:
        running = screenManager.switchScreen(result)
    
    # Draw current screen
    screenManager.currentScreen.Draw(screen)
    
    # Update display
    pygame.display.flip()

# Clean up and quit
pygame.quit()