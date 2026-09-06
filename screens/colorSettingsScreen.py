from screens import Screen
import pygame, json
from ui import UIRect
from config import settings, DEFAULT_CONFIG

class ColorSettings(Screen):
    def __init__(self, screenManager, screen):
        super().__init__(screenManager, screen)
    
    def OnEnter(self):
        super().OnEnter()
        self.scrollDistance = 0
        self.numButtons = 1
        self.settingButtons = []
        self.colorPickerScreen = False

        self.maxRGB = 255

        # Color picker state
        self.selectedColorSetting = None  # Which setting is being edited
        self.originalColor = None         # Store original color for reset
        self.sliderR = 0
        self.sliderG = 0  
        self.sliderB = 0
        self.draggingR = False
        self.draggingG = False
        self.draggingB = False

        # Slider dimensions
        self.sliderWidth = int(self.screen.get_width() * 0.6)
        self.sliderHeight = int(self.screen.get_height() * 0.05)
        self.sliderX = self.screen.get_width()//2 - self.sliderWidth//2
        self.sliderYR = int(self.screen.get_height() * 3/8)
        self.sliderYG = int(self.screen.get_height() * 4/8)
        self.sliderYB = int(self.screen.get_height() * 5/8)
        self.handleWidth = int(self.screen.get_width() * 0.02)
        self.handleHeight = int(self.screen.get_height() * 0.07)
        self.handleXR = int(self.sliderX + (self.sliderR / self.maxRGB) * (self.sliderWidth - self.handleWidth))
        self.handleXG = int(self.sliderX + (self.sliderG / self.maxRGB) * (self.sliderWidth - self.handleWidth))
        self.handleXB = int(self.sliderX + (self.sliderB / self.maxRGB) * (self.sliderWidth - self.handleWidth))

        self.handleRectR = UIRect(self.handleXR, self.sliderYR, self.handleWidth, self.handleHeight, settings.deepSea)
        self.handleRectG = UIRect(self.handleXG, self.sliderYG, self.handleWidth, self.handleHeight, settings.deepSea)
        self.handleRectB = UIRect(self.handleXB, self.sliderYB, self.handleWidth, self.handleHeight, settings.deepSea)

        self.resetButton = None

        for attr in dir(settings):
            if not attr.startswith('_') and attr != 'settingsFile':
                value = getattr(settings, attr)
                # Skip non-serializable types like font objects
                if isinstance(value, (tuple, list)):
                    # Calculate positions for 3 buttons
                    buttonSize = self.buttonHeight  # Use buttonHeight for square buttons
                    spacing = int(self.screen.get_width() * 0.02)
                    totalWidth = buttonSize * 2 + self.buttonWidth + spacing * 2
                    startX = int(self.screen.get_width()/2 - totalWidth/2)
                    
                    button = UIRect(
                        int(startX + buttonSize + spacing), 
                        int(self.screen.get_height()*self.numButtons/8 - self.buttonHeight/2 + self.scrollDistance), 
                        self.buttonWidth, 
                        self.buttonHeight, 
                        value, 
                        attr, 
                        self.fontSize, 
                        (True, "center"), 
                        borderRadius=int(self.buttonHeight//10)
                    )
                    self.settingButtons.append(button)
                    self.numButtons += 1

        doneButton = UIRect(
            int(self.screen.get_width()/2 - self.buttonWidth/2), 
            int(self.screen.get_height()*self.numButtons/8 - self.buttonHeight/2 + self.scrollDistance), 
            self.buttonWidth, 
            self.buttonHeight, 
            settings.buttonColor, 
            "Done", 
            self.fontSize, 
            (True, "center"), 
            borderRadius=int(self.buttonHeight//10)
        )
        self.settingButtons.append(doneButton)
            
    def OnExit(self):
        pass
    
    def Update(self, dt, currentTime):
        """Handle input events and return screen navigation commands"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                settings.saveSettings()  # Save before leaving
                return "quit"

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    return "fullscreen"
            
            if not self.colorPickerScreen:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        settings.saveSettings()  # Save before leaving
                        return "settings"
                    
                elif event.type == pygame.MOUSEWHEEL:
                
                    self.scrollDistance = min(0, max(self.scrollDistance + event.y * 50, 
                        -(self.screen.get_height() * (self.numButtons - 7) / 8)))
                    for i, button in enumerate(self.settingButtons):
                        button.y = self.screen.get_height()*(i+1)/8 - self.buttonHeight/2 + self.scrollDistance
                        button.rect = pygame.Rect(button.x, button.y, button.width, button.height)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mousePos = pygame.mouse.get_pos()
                        for i, button in enumerate(self.settingButtons):
                            if button.isClicked(mousePos):
                                if i == len(self.settingButtons) - 1:  # Done button
                                    settings.saveSettings()  # Save before leaving
                                    return "settings"
                                else:
                                    # Color button clicked - open color picker for this setting
                                    button = self.settingButtons[i]
                                    setting_name = button.text
                                    current_color = getattr(settings, setting_name)
                                    self.selectedColorSetting = setting_name
                                    self.originalColor = DEFAULT_CONFIG[setting_name]

                                    # Create reset button
                                    resetButtonY = int(self.sliderYR - self.screen.get_height() * 0.1) + int(self.screen.get_height() * 0.55)
                                    self.resetButton = UIRect(
                                        int(self.sliderX + self.sliderWidth//2 - self.buttonWidth//2),
                                        resetButtonY,
                                        self.buttonWidth,
                                        self.buttonHeight,
                                        settings.buttonColor,
                                        "Reset",
                                        self.fontSize,
                                        (True, "center"),
                                        borderRadius=int(self.buttonHeight//10)
                                    )

                                    self.sliderR, self.sliderG, self.sliderB = current_color
                                    self.handleXR = self.sliderX + (self.sliderR / self.maxRGB) * (self.sliderWidth - self.handleWidth)
                                    self.handleXG = self.sliderX + (self.sliderG / self.maxRGB) * (self.sliderWidth - self.handleWidth)
                                    self.handleXB = self.sliderX + (self.sliderB / self.maxRGB) * (self.sliderWidth - self.handleWidth)
                                    self.handleRectR = UIRect(self.handleXR, self.sliderYR, self.handleWidth, self.handleHeight, settings.deepSea)
                                    self.handleRectG = UIRect(self.handleXG, self.sliderYG, self.handleWidth, self.handleHeight, settings.deepSea)
                                    self.handleRectB = UIRect(self.handleXB, self.sliderYB, self.handleWidth, self.handleHeight, settings.deepSea)
                                    self.colorPickerScreen = True
            else:  # colorPickerScreen mode
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mousePos = pygame.mouse.get_pos()
                        
                        if self.resetButton.isClicked(mousePos):
                            # Reset to original color
                            self.sliderR, self.sliderG, self.sliderB = self.originalColor
                            self.handleXR = self.sliderX + (self.sliderR / self.maxRGB) * (self.sliderWidth - self.handleWidth)
                            self.handleXG = self.sliderX + (self.sliderG / self.maxRGB) * (self.sliderWidth - self.handleWidth)
                            self.handleXB = self.sliderX + (self.sliderB / self.maxRGB) * (self.sliderWidth - self.handleWidth)
                            self.handleRectR = UIRect(self.handleXR, self.sliderYR, self.handleWidth, self.handleHeight, settings.deepSea)
                            self.handleRectG = UIRect(self.handleXG, self.sliderYG, self.handleWidth, self.handleHeight, settings.deepSea)
                            self.handleRectB = UIRect(self.handleXB, self.sliderYB, self.handleWidth, self.handleHeight, settings.deepSea)
                        else:
                            # Check if clicked outside the color picker area
                            pickerAreaX = int(self.sliderX - self.screen.get_width() * 0.05)
                            pickerAreaY = int(self.sliderYR - self.screen.get_height() * 0.1)
                            pickerAreaWidth = int(self.sliderWidth + self.screen.get_width() * 0.1)
                            pickerAreaHeight = int(self.screen.get_height() * 0.5)
                            
                            if not (pickerAreaX <= mousePos[0] <= pickerAreaX + pickerAreaWidth and
                                    pickerAreaY <= mousePos[1] <= pickerAreaY + pickerAreaHeight):
                                # Apply the same conflict check as ESC
                                currentColor = (self.sliderR, self.sliderG, self.sliderB)
                                conflicts = self.getSimilarColors(currentColor, self.selectedColorSetting)
                                
                                if not conflicts:
                                    if self.selectedColorSetting:
                                        new_color = (self.sliderR, self.sliderG, self.sliderB)
                                        setattr(settings, self.selectedColorSetting, new_color)
                                        settings.saveSettings()
                                        
                                        for button in self.settingButtons:
                                            if button.text == self.selectedColorSetting:
                                                button.color = new_color
                                                break
                                self.colorPickerScreen = False
                            else:
                                # Check if clicked on slider bars (auto-grab handle)
                                if (self.sliderX <= mousePos[0] <= self.sliderX + self.sliderWidth):
                                    if (self.sliderYR <= mousePos[1] <= self.sliderYR + self.sliderHeight):
                                        # Red slider bar clicked
                                        self.draggingR = True
                                        self.handleXR = max(self.sliderX, min(mousePos[0], self.sliderX + self.sliderWidth - self.handleWidth))
                                        self.sliderR = int((self.handleXR - self.sliderX) / (self.sliderWidth - self.handleWidth) * self.maxRGB)
                                        self.handleRectR = UIRect(self.handleXR, self.sliderYR, self.handleWidth, self.handleHeight, settings.deepSea)
                                    elif (self.sliderYG <= mousePos[1] <= self.sliderYG + self.sliderHeight):
                                        # Green slider bar clicked
                                        self.draggingG = True
                                        self.handleXG = max(self.sliderX, min(mousePos[0], self.sliderX + self.sliderWidth - self.handleWidth))
                                        self.sliderG = int((self.handleXG - self.sliderX) / (self.sliderWidth - self.handleWidth) * self.maxRGB)
                                        self.handleRectG = UIRect(self.handleXG, self.sliderYG, self.handleWidth, self.handleHeight, settings.deepSea)
                                    elif (self.sliderYB <= mousePos[1] <= self.sliderYB + self.sliderHeight):
                                        # Blue slider bar clicked
                                        self.draggingB = True
                                        self.handleXB = max(self.sliderX, min(mousePos[0], self.sliderX + self.sliderWidth - self.handleWidth))
                                        self.sliderB = int((self.handleXB - self.sliderX) / (self.sliderWidth - self.handleWidth) * self.maxRGB)
                                        self.handleRectB = UIRect(self.handleXB, self.sliderYB, self.handleWidth, self.handleHeight, settings.deepSea)
                                
                                # Check if clicked directly on handles
                                if self.handleRectR.isClicked(mousePos):
                                    self.draggingR = True
                                elif self.handleRectG.isClicked(mousePos):
                                    self.draggingG = True
                                elif self.handleRectB.isClicked(mousePos):
                                    self.draggingB = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.draggingR = False
                        self.draggingG = False
                        self.draggingB = False
                            
                elif event.type == pygame.MOUSEMOTION:
                    mousePos = pygame.mouse.get_pos()
                    if self.draggingR:
                        self.handleXR = max(self.sliderX, min(mousePos[0], self.sliderX + self.sliderWidth - self.handleWidth))
                        self.sliderR = int((self.handleXR - self.sliderX) / (self.sliderWidth - self.handleWidth) * self.maxRGB)
                        self.handleRectR = UIRect(self.handleXR, self.sliderYR, self.handleWidth, self.handleHeight, settings.deepSea)
                    elif self.draggingG:
                        self.handleXG = max(self.sliderX, min(mousePos[0], self.sliderX + self.sliderWidth - self.handleWidth))
                        self.sliderG = int((self.handleXG - self.sliderX) / (self.sliderWidth - self.handleWidth) * self.maxRGB)
                        self.handleRectG = UIRect(self.handleXG, self.sliderYG, self.handleWidth, self.handleHeight, settings.deepSea)
                    elif self.draggingB:
                        self.handleXB = max(self.sliderX, min(mousePos[0], self.sliderX + self.sliderWidth - self.handleWidth))
                        self.sliderB = int((self.handleXB - self.sliderX) / (self.sliderWidth - self.handleWidth) * self.maxRGB)
                        self.handleRectB = UIRect(self.handleXB, self.sliderYB, self.handleWidth, self.handleHeight, settings.deepSea)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Check for conflicts before saving
                        currentColor = (self.sliderR, self.sliderG, self.sliderB)
                        conflicts = self.getSimilarColors(currentColor, self.selectedColorSetting)
                        
                        # Only save if there are no conflicts
                        if not conflicts:
                            if self.selectedColorSetting:
                                new_color = (self.sliderR, self.sliderG, self.sliderB)
                                setattr(settings, self.selectedColorSetting, new_color)
                                settings.saveSettings()
                                
                                # Update the button to show the new color
                                for button in self.settingButtons:
                                    if button.text == self.selectedColorSetting:
                                        button.color = new_color  # Update button color
                                        break
                        # If there are conflicts, just exit without saving (color reverts to original)
                        self.colorPickerScreen = False

    def Draw(self, screen):
        """Draw the main menu screen"""
        screen.fill(self.background)
        for button in self.settingButtons:
            button.draw(screen)
        if self.colorPickerScreen:
            # Draw pause overlay
            pauseRect = UIRect(0, 0, screen.get_width(), screen.get_height(), (0, 0, 0), scalable=(False, None), alpha=settings.pauseAlpha)
            pauseRect.draw(screen)

            # Draw color preview rect behind sliders
            currentColor = (self.sliderR, self.sliderG, self.sliderB)
            previewRect = UIRect(
                int(self.sliderX - self.screen.get_width() * 0.05),
                int(self.sliderYR - self.screen.get_height() * 0.1),
                int(self.sliderWidth + self.screen.get_width() * 0.1),
                int(self.screen.get_height() * 0.5),
                currentColor,
                scalable=(False, None),
                borderRadius=int(self.buttonHeight//2)
            )
            previewRect.draw(screen)
            
            # Check for color conflicts and show warning if needed
            conflicts = self.getSimilarColors(currentColor, self.selectedColorSetting)
            if conflicts:
                warningFont = pygame.font.Font('assets/fonts/MinionPro-BoldCn.otf', 20)
                warningText = warningFont.render(f"Warning: Too similar to {', '.join(conflicts)}", True, (255, 0, 0))
                # Position text under the previewRect
                textX = int(self.sliderX - self.screen.get_width() * 0.05)
                textY = int(self.sliderYR - self.screen.get_height() * 0.1) + int(self.screen.get_height() * 0.5) + 10
                screen.blit(warningText, (textX, textY))
        
            # Draw sliders
            self.drawSlider(screen, self.sliderX, self.sliderYR, self.sliderWidth, 
                        self.sliderHeight, self.sliderR, (self.maxRGB, 0, 0), "R", currentColor)
            self.drawSlider(screen, self.sliderX, self.sliderYG, self.sliderWidth, 
                        self.sliderHeight, self.sliderG, (0, self.maxRGB, 0), "G", currentColor)
            self.drawSlider(screen, self.sliderX, self.sliderYB, self.sliderWidth, 
                        self.sliderHeight, self.sliderB, (0, 0, self.maxRGB), "B", currentColor)

            # Draw reset button
            if self.colorPickerScreen and self.resetButton:
                self.resetButton.draw(screen)
    
    
    def drawSlider(self, surface, x, y, width, height, value, baseColor, label, currentColor):
        """Draw a color slider with gradient"""
        # Draw slider track
        pygame.draw.rect(surface, (200, 200, 200), (x, y, width, height))
        pygame.draw.rect(surface, (100, 100, 100), (x, y, width, height), 2)
        
        # Draw gradient
        for i in range(width):
            gradientColor = [
                int(baseColor[0] * (i / width)),
                int(baseColor[1] * (i / width)),
                int(baseColor[2] * (i / width))
            ]
            pygame.draw.line(surface, gradientColor, (x + i, y), (x + i, y + height))
        
        # Draw handle
        handleX = x + (value / self.maxRGB) * (width - self.handleWidth)
        handleRect = pygame.Rect(handleX, y - (self.handleHeight - self.sliderHeight)//2, self.handleWidth, self.handleHeight)
        pygame.draw.rect(surface, (50, 50, 50), handleRect, border_radius=int(self.buttonHeight//10))
        pygame.draw.rect(surface, (0, 0, 0), handleRect, 2, border_radius=int(self.buttonHeight//10))
        
        # Draw value
        font = pygame.font.Font('assets/fonts/MinionPro-BoldCn.otf', 30)
        if (0.299 * currentColor[0] + 0.587 * currentColor[1] + 0.114 * currentColor[2]) >= 128:
            textColor = (0, 0, 0)
        else:
            textColor = (255, 255, 255)
        valueText = font.render(str(value), True, textColor)
        surface.blit(valueText, (x + width + 10, y + self.sliderHeight//2 - valueText.get_height()//2))
    
    def getSimilarColors(self, currentColor, currentSettingName):
        """Find all colors that are too similar to the current color"""
        similarColors = []
        threshold = 30

        # Define color groups that actually interact with each other
        colorGroups = {
            'Dice & Background': ['diceRedColor', 'diceYellowColor', 'deepSea'],
            'Terrain Tiles': ['desert', 'sheep', 'ore', 'wheat', 'wood', 'brick', 'goldMine', 'sea', 'deepSea', 'fog'],
            'UI Elements': ['buttonColor', 'buttonGreyedOutColor', 'deepSea']
        }

        currentGroups = []
        for groupName, colorNames in colorGroups.items():
            if currentSettingName in colorNames:
                currentGroups.append(groupName)
        
        colorsToCheck = set()
        for groupName in currentGroups:
            colorsToCheck.update(colorGroups[groupName])
        
        for attr in dir(settings):
            if not attr.startswith('_') and attr != 'settingsFile' and attr != currentSettingName and attr in colorsToCheck:
                value = getattr(settings, attr)
                if isinstance(value, (tuple, list)) and len(value) == 3:
                    if set([currentSettingName, attr]) == set(['sea', 'deepSea']):
                        continue

                    redDiff = abs(currentColor[0] - value[0])
                    greenDiff = abs(currentColor[1] - value[1])
                    blueDiff = abs(currentColor[2] - value[2])
                    averageDiff = (redDiff + greenDiff + blueDiff) / 3
                    
                    if averageDiff < threshold:
                        similarColors.append(attr)
        
        return similarColors