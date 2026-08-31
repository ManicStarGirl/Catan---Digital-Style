from screens import Screen
import pygame
from ui import uiRect

class Settings(Screen):
    def __init__(self, screenManager, screen): # Assets, fonts, static button positions, things that never change
        super().__init__(screenManager, screen)
        # Only setup things that don't depend on screen size here
        self.numButtons = 12
    
    def OnEnter(self): # Reset game state, start animations, recalculate responsive positions
        super().OnEnter()
        # Recalculate buttons with current screen size
        self.button1    = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*1/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
        self.button2    = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*2/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
        self.button3    = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*3/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
        self.button4    = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*4/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
        self.button5    = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*5/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
        self.button6    = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*6/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
        self.button7    = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*7/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
        self.button8    = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*8/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
        self.button9    = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*9/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
        self.button10   = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*10/8 - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
        self.button11   = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*11/8 - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
        self.doneButton = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*12/8 - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonColor,          "Done",   self.fontSize, (True, "center"), borderRadius=10)
    
    def OnExit(self):
        pass # Likely nothing here
    
    def Update(self, dt, currentTime):
        """Handle input events and return screen navigation commands"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            elif event.type == pygame.MOUSEWHEEL:
                self.scrollDistance = min(0, max(self.scrollDistance + event.y * 50, -(self.screen.get_height() * (self.numButtons - 7) / 8)))
                # Recalculate buttons with current screen size
                self.button1        = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*1/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
                self.button2        = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*2/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
                self.button3        = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*3/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
                self.button4        = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*4/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
                self.button5        = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*5/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
                self.button6        = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*6/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
                self.button7        = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*7/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
                self.button8        = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*8/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
                self.button9        = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*9/8  - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
                self.button10       = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*10/8 - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
                self.button11       = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*11/8 - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonGreyedOutColor, "button", self.fontSize, (True, "center"), borderRadius=10)
                self.doneButton     = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height()*12/8 - self.buttonHeight/2 + self.scrollDistance, self.buttonWidth, self.buttonHeight, self.buttonColor,          "Done",   self.fontSize, (True, "center"), borderRadius=10)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    return "fullscreen"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    if self.doneButton.isClicked(mouse_pos):
                        return "mainMenu"

    def Draw(self, screen):
        """Draw the main menu screen"""
        screen.fill(self.background)
        self.button1.draw(screen)
        self.button2.draw(screen)
        self.button3.draw(screen)
        self.button4.draw(screen)
        self.button5.draw(screen)
        self.button6.draw(screen)
        self.button7.draw(screen)
        self.button8.draw(screen)
        self.button9.draw(screen)
        self.button10.draw(screen)
        self.button11.draw(screen)
        self.doneButton.draw(screen)