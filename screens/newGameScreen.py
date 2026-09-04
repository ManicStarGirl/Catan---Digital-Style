from screens import Screen
from ui import UIRect
import pygame, json
from config import settings

class NewGame(Screen):
    """Game options screen"""
    def __init__(self, screenManager, screen):
        super().__init__(screenManager, screen)

    def OnEnter(self):
        super().OnEnter()
        # Recalculate buttons with current screen size
        self.singleplayerButton  = UIRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*3/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonColor,          "Singleplayer",   self.fontSize, (True, "center"), borderRadius=10)
        self.passAndPlayButton   = UIRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*4/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonGreyedOutColor, "Pass and Play",  self.fontSize, (True, "center"), borderRadius=10)
        self.buildButton         = UIRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*5/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonColor,          "Build",          self.fontSize, (True, "center"), borderRadius=10)

    def OnExit(self):
        pass

    def Update(self, dt, currentTime):
        """Handle input events and return screen navigation commands"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    return "fullscreen"
                elif event.key == pygame.K_ESCAPE:
                    return "mainMenu"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    if self.singleplayerButton.isClicked(mouse_pos):
                        return "singleplayer"
                    if self.passAndPlayButton.isClicked(mouse_pos):
                        return "passandplay"
                    if self.buildButton.isClicked(mouse_pos):
                        return "build"

    def Draw(self, screen):
        """Draw the main menu screen"""
        screen.fill(self.background)
        self.singleplayerButton.draw(screen)
        self.passAndPlayButton.draw(screen)
        self.buildButton.draw(screen)