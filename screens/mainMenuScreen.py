from screens import Screen
from ui import uiRect
import pygame, json
from config import settings

class MainMenu(Screen):
    """Main menu screen with game options"""
    def __init__(self, screenManager, screen): # Assets, fonts, static button positions, things that never change
        super().__init__(screenManager, screen)
        # Only setup things that don't depend on screen size here

    def OnEnter(self): # Reset game state, start animations, recalculate responsive positions
        super().OnEnter()
        # Recalculate buttons with current screen size
        self.newButton        = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*1/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonColor,          "New Game",   self.fontSize, (True, "center"), borderRadius=10)
        self.joinButton       = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*3/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonGreyedOutColor, "Online",     self.fontSize, (True, "center"), borderRadius=10)
        self.settingsButton   = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*4/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonColor,          "Settings",   self.fontSize, (True, "center"), borderRadius=10)
        self.statisticsButton = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*5/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonGreyedOutColor, "Statistics", self.fontSize, (True, "center"), borderRadius=10)
        self.quitButton       = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*6/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonColor,          "Quit",       self.fontSize, (True, "center"), borderRadius=10)
        self.tutorialButton   = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*7/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonGreyedOutColor, "Tutorial",   self.fontSize, (True, "center"), borderRadius=10)
        # Check if save file exists to enable/disable continue button
        try:
            with open("save.json", "r") as f:
                content = json.load(f)
            self.continueButton = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*2/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonColor, "Continue", self.fontSize, (True, "center"), borderRadius=10)
        except FileNotFoundError:
            self.continueButton = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*2/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonGreyedOutColor, "Continue", self.fontSize, (True, "center"), borderRadius=10)


    def OnExit(self):
        pass # Likely nothing here

    def Update(self, dt, currentTime):
        """Handle input events and return screen navigation commands"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    return "fullscreen"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    if self.newButton.isClicked(mouse_pos):
                        return "new"
                    if self.continueButton.isClicked(mouse_pos):
                        return "continue"
                    if self.joinButton.isClicked(mouse_pos):
                        return "join"
                    if self.settingsButton.isClicked(mouse_pos):
                        return "settings"
                    if self.statisticsButton.isClicked(mouse_pos):
                        return "statistics"
                    if self.quitButton.isClicked(mouse_pos):
                        return "quit"
                    if self.tutorialButton.isClicked(mouse_pos):
                        return "tutorial"

    def Draw(self, screen):
        """Draw the main menu screen"""
        screen.fill(self.background)
        self.newButton.draw(screen)
        self.continueButton.draw(screen)
        self.joinButton.draw(screen)
        self.settingsButton.draw(screen)
        self.statisticsButton.draw(screen)
        self.quitButton.draw(screen)
        self.tutorialButton.draw(screen)