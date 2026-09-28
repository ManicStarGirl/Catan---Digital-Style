from ui import UIRect

class VerstileButton:
    def __init__(self, screen, buttonWidth, buttonHeight, fontSize):
        self.screen = screen
        self.buttonWidth = buttonWidth
        self.buttonHeight = buttonHeight
        self.fontSize = fontSize
        self.buttons = {}
        self.buttonRadius = int(self.buttonHeight//8)
    
    def createButton(self, name, yPos, color, text):
        """Create a button and store it by name"""
        self.buttons[name] = UIRect(
            self.screen.get_width()/2 - self.buttonWidth/2,
            yPos - self.buttonHeight/2,
            self.buttonWidth,
            self.buttonHeight,
            color,
            text,
            self.fontSize,
            (True, "center"),
            borderRadius=self.buttonRadius
        )
    
    def handleClick(self, mouse_pos):
        """Check if any button was clicked and return its action"""
        for button_name, button in self.buttons.items():
            if button.isClicked(mouse_pos):
                return button_name
        return None
    
    def draw(self, screen):
        """Draw all buttons"""
        for button in self.buttons.values():
            button.draw(screen)
