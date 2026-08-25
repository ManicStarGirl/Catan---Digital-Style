import pygame, json
from ui import hex
from config import fpsLimit
from screens.mainMenu import MainMenu
from screens.GameScreen import GameScreen
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
        self.current_screen = None
    
    def switch_screen(self, screen_name):
        """Switch to a different screen based on screen_name"""
        if screen_name == "main_menu":
            self.current_screen = MainMenu(self, screen)
            self.current_screen.OnEnter()
        elif screen_name == "new":
            self.current_screen = GameScreen(self, screen)
            self.current_screen.OnEnter()
        elif screen_name == "continue":
            try:
                with open("save.json", "r") as f:
                    savedData = json.load(f)
                tileList = [hex(*t) for t in savedData["tiles"]]
                self.current_screen = GameScreen(self, screen, tileList)
                self.current_screen.OnEnter()
            except FileNotFoundError:
                pass
        elif screen_name == "quit":
            return False  # Signal to quit
        return True

# Initialize screen manager and start at main menu
screenManager = ScreenManager()
screenManager.switch_screen("main_menu")

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
    result = screenManager.current_screen.Update(dt, currentTime)
    if result == "fullscreen":
        # Toggle fullscreen <-> windowed
        if fullscreen:
            screen = pygame.display.set_mode((1280, 720))
            fullscreen = False
        else:
            screen = pygame.display.set_mode((screenWidth, screenHeight), pygame.FULLSCREEN)
            fullscreen = True
        screenManager.current_screen.OnEnter()
    elif result:
        running = screenManager.switch_screen(result)
    
    # Draw current screen
    screenManager.current_screen.Draw(screen)
    
    # Update display
    pygame.display.flip()

# Clean up and quit
pygame.quit()