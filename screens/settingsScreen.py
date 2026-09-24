from screens import Screen
import pygame, json
from ui import UIRect
from config import settings

class Settings(Screen):
    def __init__(self, screenManager, screen):
        super().__init__(screenManager, screen)
    
    def OnEnter(self):
        super().OnEnter()
        self.scrollDistance = 0
        self.numButtons = 1
        self.settingButtons = []

        for attr in dir(settings):
            if not attr.startswith('_') and attr != 'settingsFile':
                value = getattr(settings, attr)
                if isinstance(value, (int, float, str, bool)):
                    buttonSize = self.buttonHeight
                    totalWidth = buttonSize * 2 + self.buttonWidth + self.buttonSpacing * 2
                    startX = self.screen.get_width()/2 - totalWidth/2
                    
                    minusButton = UIRect(
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
                    
                    displayButton = UIRect(
                        startX + buttonSize + self.buttonSpacing, 
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
                    
                    plusButton = UIRect(
                        startX + self.buttonWidth + buttonSize + self.buttonSpacing * 2, 
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
        
        colorButton = UIRect(
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
        
        doneButton = UIRect(
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
        pass
    
    def Update(self, dt, currentTime):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                settings.saveSettings()  
                return "quit"

            elif event.type == pygame.MOUSEWHEEL:
                
                self.scrollDistance = min(0, max(self.scrollDistance + event.y * 50, 
                    -(self.screen.get_height() * (self.numButtons - 7) / 8)))
                for i, button in enumerate(self.settingButtons):
                    if i < len(self.settingButtons) -2:
                        groupIndex = i // 3
                        button.y = self.screen.get_height()*(groupIndex+1)/8 - self.buttonHeight/2 + self.scrollDistance
                    else:
                        navIndex = i - len(self.settingButtons)
                        button.y = self.screen.get_height()*(self.numButtons+navIndex+1)/8 - self.buttonHeight/2 + self.scrollDistance
                    button.rect = pygame.Rect(button.x, button.y, button.width, button.height)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    return "fullscreen"
                elif event.key == pygame.K_ESCAPE:
                    settings.saveSettings()  
                    return "mainMenu"
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  
                    mouse_pos = pygame.mouse.get_pos()
                    for i, button in enumerate(self.settingButtons):
                        if button.isClicked(mouse_pos):
                            if i == len(self.settingButtons) - 1:
                                settings.saveSettings()
                                return "mainMenu"
                            elif i == len(self.settingButtons) - 2:  
                                return "colorSettings"
                            else:
                                settingIndex = (i) // 3
                                buttonInGroup = i % 3
                                if buttonInGroup == 0:
                                    self.changeSetting(settingIndex, -1)
                                elif buttonInGroup == 2:
                                    self.changeSetting(settingIndex, 1)

    def Draw(self, screen):
        screen.fill(self.background)
        for button in self.settingButtons:
            button.draw(screen)

    def changeSetting(self, setting_index, direction):
        displayButton = self.settingButtons[setting_index * 3 + 1]
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
        
        setattr(settings, setting_name, new_value)
        displayButton.text = f"{setting_name}: {new_value}"