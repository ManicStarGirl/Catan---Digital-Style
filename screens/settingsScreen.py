from screens import Screen
import pygame, json
from ui import uiRect
from config import settings

class Settings(Screen):
    def __init__(self, screenManager, screen): # Assets, fonts, static button positions, things that never change
        super().__init__(screenManager, screen)
        # Only setup things that don't depend on screen size here
    
    def OnEnter(self): # Reset game state, start animations, recalculate responsive positions
        super().OnEnter()
        self.scrollDistance = 0
        self.numButtons = 1
        self.settingButtons = []

        for attr in dir(settings):
            if not attr.startswith('_') and attr != 'settingsFile':
                value = getattr(settings, attr)
                # Skip non-serializable types like font objects
                if isinstance(value, (int, float, str, bool)):
                    # Calculate positions for 3 buttons
                    buttonSize = self.buttonHeight  # Use buttonHeight for square buttons
                    spacing = 10
                    totalWidth = buttonSize * 2 + self.buttonWidth + spacing * 2
                    startX = self.screen.get_width()/2 - totalWidth/2
                    
                    # "-" button
                    minusButton = uiRect(
                        startX, 
                        self.screen.get_height()*self.numButtons/8 - self.buttonHeight/2 + self.scrollDistance, 
                        buttonSize, 
                        buttonSize, 
                        settings.buttonColor, 
                        "-", 
                        self.fontSize, 
                        (True, "center"), 
                        borderRadius=10
                    )
                    self.settingButtons.append(minusButton)
                    
                    # Display button (center)
                    displayButton = uiRect(
                        startX + buttonSize + spacing, 
                        self.screen.get_height()*self.numButtons/8 - self.buttonHeight/2 + self.scrollDistance, 
                        self.buttonWidth, 
                        self.buttonHeight, 
                        settings.buttonColor, 
                        f"{attr}: {value}", 
                        self.fontSize, 
                        (True, "center"), 
                        borderRadius=10
                    )
                    self.settingButtons.append(displayButton)
                    
                    # "+" button
                    plusButton = uiRect(
                        startX + self.buttonWidth + buttonSize + spacing * 2, 
                        self.screen.get_height()*self.numButtons/8 - self.buttonHeight/2 + self.scrollDistance, 
                        buttonSize, 
                        buttonSize, 
                        settings.buttonColor, 
                        "+", 
                        self.fontSize, 
                        (True, "center"), 
                        borderRadius=10
                    )
                    self.settingButtons.append(plusButton)
                    
                    self.numButtons += 1
        # Add Done and Color Settings button
        colorButton = uiRect(
            self.screen.get_width()/2 - self.buttonWidth/2, 
            self.screen.get_height()*self.numButtons/8 - self.buttonHeight/2 + self.scrollDistance, 
            self.buttonWidth, 
            self.buttonHeight, 
            settings.buttonColor, 
            "Color Settings", 
            self.fontSize, 
            (True, "center"), 
            borderRadius=10
        )
        self.settingButtons.append(colorButton)
        self.numButtons += 1
        
        doneButton = uiRect(
            self.screen.get_width()/2 - self.buttonWidth/2, 
            self.screen.get_height()*self.numButtons/8 - self.buttonHeight/2 + self.scrollDistance, 
            self.buttonWidth, 
            self.buttonHeight, 
            settings.buttonColor, 
            "Done", 
            self.fontSize, 
            (True, "center"), 
            borderRadius=10
        )
        self.settingButtons.append(doneButton)
            
    def OnExit(self):
        pass # Likely nothing here
    
    def Update(self, dt, currentTime):
        """Handle input events and return screen navigation commands"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                settings.saveSettings()  # Save before leaving
                return "quit"

            elif event.type == pygame.MOUSEWHEEL:
                
                self.scrollDistance = min(0, max(self.scrollDistance + event.y * 50, 
                    -(self.screen.get_height() * (self.numButtons - 7) / 8)))
                for i, button in enumerate(self.settingButtons):
                    if i < len(self.settingButtons) -2:
                        # Group buttons by 3s for vertical positioning
                        groupIndex = i // 3
                        button.y = self.screen.get_height()*(groupIndex+1)/8 - self.buttonHeight/2 + self.scrollDistance
                    else:
                        navIndex = i - len(self.settingButtons)  # 0 for Color Settings, 1 for Done
                        button.y = self.screen.get_height()*(self.numButtons+navIndex+1)/8 - self.buttonHeight/2 + self.scrollDistance
                    button.rect = pygame.Rect(button.x, button.y, button.width, button.height)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    return "fullscreen"
                elif event.key == pygame.K_ESCAPE:
                    settings.saveSettings()  # Save before leaving
                    return "mainMenu"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    for i, button in enumerate(self.settingButtons):
                        if button.isClicked(mouse_pos):
                            if i == len(self.settingButtons) - 1:  # Done button
                                settings.saveSettings()  # Save before leaving
                                return "mainMenu"
                            elif i == len(self.settingButtons) - 2:  # Color Settings button
                                return "colorSettings"
                            else:
                                # Handle setting buttons (grouped in 3s)
                                # Skip display buttons (middle of each group)
                                settingIndex = (i) // 3  # Which setting group
                                buttonInGroup = i % 3    # 0 = minus, 1 = display, 2 = plus
                                
                                if buttonInGroup == 0:  # "-" button
                                    self.changeSetting(settingIndex, -1)
                                elif buttonInGroup == 2:  # "+" button
                                    self.changeSetting(settingIndex, 1)

    def Draw(self, screen):
        """Draw the main menu screen"""
        screen.fill(self.background)
        for button in self.settingButtons:
            button.draw(screen)

    def changeSetting(self, setting_index, direction):
        """Change a setting value by direction (-1 for decrement, 1 for increment)"""
        # Get the setting name from the display button text
        displayButton = self.settingButtons[setting_index * 3 + 1]  # Middle button
        setting_name = displayButton.text.split(":")[0].strip()
        
        current_value = getattr(settings, setting_name)
        new_value = current_value
        
        if isinstance(current_value, float):
            if setting_name == "gameScale":
                values = [0.5, 1.0, 1.5, 2.0]
                idx = values.index(current_value) if current_value in values else 0
                new_value = values[(idx + direction) % len(values)]
            elif setting_name == "zoomFactor":
                values = [1.1, 1.15, 1.2, 1.25]
                idx = values.index(current_value) if current_value in values else 0
                new_value = values[(idx + direction) % len(values)]
            elif setting_name == "uiScale":
                values = [0.8, 1.0, 1.2, 1.5]
                idx = values.index(current_value) if current_value in values else 0
                new_value = values[(idx + direction) % len(values)]
            else:
                new_value = current_value + (direction * 0.1)
                
        elif isinstance(current_value, int):
            if setting_name == "fpsLimit":
                new_value = current_value + (direction * 10)
                if new_value > 120: new_value = 30
                if new_value < 30: new_value = 120
            elif setting_name == "numberOfRings":
                new_value = current_value + direction
                if new_value > 10: new_value = 2
                if new_value < 2: new_value = 10
            else:
                new_value = current_value + (direction * 10)
                if new_value > 255: new_value = 0
                if new_value < 0: new_value = 255
        
        # Update the setting
        setattr(settings, setting_name, new_value)
        
        # Update display button text
        displayButton.text = f"{setting_name}: {new_value}"