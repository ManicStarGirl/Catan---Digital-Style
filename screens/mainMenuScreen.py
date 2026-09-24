from screens import Screen
from ui import UIRect
import pygame, json
from config import settings
from components.genericButton import VerstileButton

class MainMenu(Screen):
    """Main menu screen with game options"""
    def __init__(self, screenManager, screen):
        super().__init__(screenManager, screen)

    def OnEnter(self):
        super().OnEnter()
        self.buttonGroup = VerstileButton(self.screen, self.buttonWidth, self.buttonHeight, self.fontSize)

        # Recalculate buttons with current screen size
        self.buttonGroup.createButton("newGame",    self.screen.get_height()*1/8, settings.buttonColor,          "New Game")
        self.buttonGroup.createButton("online",     self.screen.get_height()*3/8, settings.buttonGreyedOutColor, "Online")
        self.buttonGroup.createButton("settings",   self.screen.get_height()*4/8, settings.buttonColor,          "Settings")
        self.buttonGroup.createButton("statistics", self.screen.get_height()*5/8, settings.buttonGreyedOutColor, "Statistics")
        self.buttonGroup.createButton("quit",       self.screen.get_height()*6/8, settings.buttonColor,          "Quit")
        self.buttonGroup.createButton("tutorial",   self.screen.get_height()*7/8, settings.buttonGreyedOutColor, "Tutorial")
        
        # Check if save file exists to enable/disable continue button
        try:
            with open("save.json", "r") as f:
                json.load(f)
            self.buttonGroup.createButton("continue", self.screen.get_height()*2/8, settings.buttonColor, "Continue")
        except FileNotFoundError:
            self.buttonGroup.createButton("continue", self.screen.get_height()*2/8, settings.buttonGreyedOutColor, "Continue")


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
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    action = self.buttonGroup.handleClick(pygame.mouse.get_pos())
                    if action:
                        return action

    def Draw(self, screen):
        """Draw the main menu screen"""
        screen.fill(self.background)
        self.buttonGroup.draw(screen)
