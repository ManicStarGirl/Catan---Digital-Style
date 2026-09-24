from screens import Screen
import pygame
from config import settings
from components.genericButton import VerstileButton

class NewGame(Screen):
    """Game options screen"""
    def __init__(self, screenManager, screen):
        super().__init__(screenManager, screen)

    def OnEnter(self):
        super().OnEnter()
        self.buttonGroup = VerstileButton(self.screen, self.buttonWidth, self.buttonHeight, self.fontSize)

        # Recalculate buttons with current screen size
        self.buttonGroup.createButton("singleplayer", self.screen.get_height()*5/16,  settings.buttonColor,          "Singleplayer")
        self.buttonGroup.createButton("passAndPlay",  self.screen.get_height()*7/16,  settings.buttonGreyedOutColor, "Pass and Play")
        self.buttonGroup.createButton("build",        self.screen.get_height()*9/16,  settings.buttonColor,          "Build")
        self.buttonGroup.createButton("mainMenu",     self.screen.get_height()*11/16, settings.buttonColor,          "Back")

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
                    action = self.buttonGroup.handleClick(pygame.mouse.get_pos())
                    if action:
                        return action

    def Draw(self, screen):
        """Draw the new game screen"""
        screen.fill(self.background)
        self.buttonGroup.draw(screen)
