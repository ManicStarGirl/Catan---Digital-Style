from screens import Screen
import pygame, json
from ui import UIRect
from config import settings, DEFAULT_CONFIG

class ColorSettings(Screen):
    def __init__(self, screenManager, screen):
        super().__init__(screenManager, screen)
    
    def OnEnter(self):
        super().OnEnter()
        self.verticalScrollOffset = 0
        self.buttonCount = 1
        self.colorSettingButtons = []
        self.isColorPickerActive = False

        self.maxColorValue = 255

        # Color picker state
        self.selectedColorSetting = None  # Which setting is being edited
        self.originalColor = None         # Store original color for reset
        self.redSliderColorValue = 0
        self.greenSliderColorValue = 0  
        self.blueSliderColorValue = 0
        self.isDraggingRedSlider = False
        self.isDraggingGreenSlider = False
        self.isDraggingBlueSlider = False

        # Slider dimensions
        self.sliderWidth = int(self.screen.get_width() * 0.6)
        self.sliderHeight = int(self.screen.get_height() * 0.05)
        self.sliderX = self.screen.get_width()//2 - self.sliderWidth//2
        self.redSliderY = int(self.screen.get_height() * 3/8)
        self.greenSliderY = int(self.screen.get_height() * 4/8)
        self.blueSliderY = int(self.screen.get_height() * 5/8)
        self.handleWidth = int(self.screen.get_width() * 0.02)
        self.handleHeight = int(self.screen.get_height() * 0.07)
        self.redHandleX = int(self.sliderX + (self.redSliderColorValue / self.maxColorValue) * (self.sliderWidth - self.handleWidth))
        self.greenHandleX = int(self.sliderX + (self.greenSliderColorValue / self.maxColorValue) * (self.sliderWidth - self.handleWidth))
        self.blueHandleX = int(self.sliderX + (self.blueSliderColorValue / self.maxColorValue) * (self.sliderWidth - self.handleWidth))

        # Button dimensions
        self.buttonX = int(self.screen.get_width()/2 - self.buttonWidth/2)
        self.buttonRadius = int(self.buttonHeight//10)

        self.redHandleRect =   UIRect(self.redHandleX,   self.redSliderY,   self.handleWidth, self.handleHeight, settings.deepSea)
        self.greenHandleRect = UIRect(self.greenHandleX, self.greenSliderY, self.handleWidth, self.handleHeight, settings.deepSea)
        self.blueHandleRect =  UIRect(self.blueHandleX,  self.blueSliderY,  self.handleWidth, self.handleHeight, settings.deepSea)

        self.resetButton = None
        self.saveButton =  None

        self.saveText = "Save"
        self.saveTextColor = None
        self.warningFontSize = self.screen.get_height()/40

        self.pauseRect = UIRect(0, 0, self.screen.get_width(), self.screen.get_height(), (0, 0, 0), scalable=(False, None), alpha=settings.pauseAlpha)

        # Calculate position for reset/save buttons
        self.colorPickerX = int(self.sliderX - self.screen.get_width() * 0.05)
        self.resetAndSaveButtonY = int(self.redSliderY - self.screen.get_height() * 0.1) + int(self.screen.get_height() * 0.5) + self.buttonSpacing
        self.resetAndSaveButtonWidth = (int(self.sliderWidth + self.screen.get_width() * 0.1) - self.buttonSpacing)/2

        for settingName in dir(settings):
            if not settingName.startswith('_') and settingName != 'settingsFile':
                settingValue = getattr(settings, settingName)
                # Skip non-serializable types like font objects
                if isinstance(settingValue, (tuple, list)):
                    button = UIRect(
                        self.buttonX, 
                        int(self.screen.get_height()*self.buttonCount/8 - self.buttonHeight/2 + self.verticalScrollOffset), 
                        self.buttonWidth, 
                        self.buttonHeight, 
                        settingValue, 
                        settingName, 
                        self.fontSize, 
                        (True, "center"), 
                        borderRadius=self.buttonRadius
                    )
                    self.colorSettingButtons.append(button)
                    self.buttonCount += 1

        doneButton = UIRect(
            self.buttonX, 
            int(self.screen.get_height()*self.buttonCount/8 - self.buttonHeight/2 + self.verticalScrollOffset), 
            self.buttonWidth, 
            self.buttonHeight, 
            settings.buttonColor, 
            "Done", 
            self.fontSize, 
            (True, "center"), 
            borderRadius=self.buttonRadius
        )
        self.colorSettingButtons.append(doneButton)

        # Create reset button
        self.resetButton = UIRect(
            self.colorPickerX,
            self.resetAndSaveButtonY,
            self.resetAndSaveButtonWidth,
            self.buttonHeight,
            (0, 0, 0),
            "Reset",
            self.fontSize,
            (True, "center"),
            borderRadius=self.buttonRadius
        )
        # Create save button
        self.saveButton = UIRect(
            self.colorPickerX + self.resetAndSaveButtonWidth + self.buttonSpacing,
            self.resetAndSaveButtonY,
            self.resetAndSaveButtonWidth,
            self.buttonHeight,
            (0, 0, 0),
            "Save",
            self.warningFontSize,
            (True, "center"),
            borderRadius=self.buttonRadius,
            textColor=self.saveTextColor
        )
            
            
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
            
            if not self.isColorPickerActive:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        settings.saveSettings()  # Save before leaving
                        return "settings"
                    
                elif event.type == pygame.MOUSEWHEEL:
                
                    self.verticalScrollOffset = min(0, max(self.verticalScrollOffset + event.y * 50, -(self.screen.get_height() * (self.buttonCount - 7) / 8)))
                    for i, button in enumerate(self.colorSettingButtons):
                        button.y = self.screen.get_height()*(i+1)/8 - self.buttonHeight/2 + self.verticalScrollOffset
                        button.rect = pygame.Rect(button.x, button.y, button.width, button.height)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mousePosition = pygame.mouse.get_pos()
                        for i, button in enumerate(self.colorSettingButtons):
                            if button.isClicked(mousePosition):
                                if i == len(self.colorSettingButtons) - 1:  # Done button
                                    settings.saveSettings()  # Save before leaving
                                    return "settings"  # Return to settings screen
                                else:
                                    # Color button clicked - open color picker for this setting
                                    button = self.colorSettingButtons[i]
                                    setting_name = button.text
                                    current_color = getattr(settings, setting_name)
                                    self.selectedColorSetting = setting_name
                                    self.originalColor = DEFAULT_CONFIG[setting_name]

                                    self.setColor(current_color)

                                    self.isColorPickerActive = True

            else:  # isColorPickerActive mode
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mousePosition = pygame.mouse.get_pos()
                        
                        if self.resetButton.isClicked(mousePosition):
                            # Reset to original color
                            self.setColor(self.originalColor)

                        elif self.saveButton.isClicked(mousePosition):
                            # Apply the same conflict check as ESC
                            currentColor = (self.redSliderColorValue, self.greenSliderColorValue, self.blueSliderColorValue)
                            conflicts = self.getSimilarColors(currentColor, self.selectedColorSetting)
                            
                            if not conflicts:
                                if self.selectedColorSetting:
                                    new_color = (self.redSliderColorValue, self.greenSliderColorValue, self.blueSliderColorValue)
                                    setattr(settings, self.selectedColorSetting, new_color)
                                    settings.saveSettings()
                                    
                                    for button in self.colorSettingButtons:
                                        if button.text == self.selectedColorSetting:
                                            button.color = new_color
                                            break
                            self.isColorPickerActive = False
                        else:
                            # Check if clicked outside the color picker area
                            pickerAreaX = int(self.sliderX - self.screen.get_width() * 0.05)
                            pickerAreaY = int(self.redSliderY - self.screen.get_height() * 0.1)
                            pickerAreaWidth = int(self.sliderWidth + self.screen.get_width() * 0.1)
                            pickerAreaHeight = int(self.screen.get_height() * 0.5)
                            
                            if (pickerAreaX <= mousePosition[0] <= pickerAreaX + pickerAreaWidth and
                                    pickerAreaY <= mousePosition[1] <= pickerAreaY + pickerAreaHeight):
                                # Check if clicked on slider bars (auto-grab handle)
                                if (self.sliderX <= mousePosition[0] <= self.sliderX + self.sliderWidth):
                                    if (self.redSliderY <= mousePosition[1] <= self.redSliderY + self.sliderHeight):
                                        # Red slider bar clicked
                                        self.isDraggingRedSlider = True
                                        self.redHandleX = max(self.sliderX, min(mousePosition[0], self.sliderX + self.sliderWidth - self.handleWidth))
                                        self.redSliderColorValue = int((self.redHandleX - self.sliderX) / (self.sliderWidth - self.handleWidth) * self.maxColorValue)
                                        self.redHandleRect = UIRect(self.redHandleX, self.redSliderY, self.handleWidth, self.handleHeight, settings.deepSea)
                                    elif (self.greenSliderY <= mousePosition[1] <= self.greenSliderY + self.sliderHeight):
                                        # Green slider bar clicked
                                        self.isDraggingGreenSlider = True
                                        self.greenHandleX = max(self.sliderX, min(mousePosition[0], self.sliderX + self.sliderWidth - self.handleWidth))
                                        self.greenSliderColorValue = int((self.greenHandleX - self.sliderX) / (self.sliderWidth - self.handleWidth) * self.maxColorValue)
                                        self.greenHandleRect = UIRect(self.greenHandleX, self.greenSliderY, self.handleWidth, self.handleHeight, settings.deepSea)
                                    elif (self.blueSliderY <= mousePosition[1] <= self.blueSliderY + self.sliderHeight):
                                        # Blue slider bar clicked
                                        self.isDraggingBlueSlider = True
                                        self.blueHandleX = max(self.sliderX, min(mousePosition[0], self.sliderX + self.sliderWidth - self.handleWidth))
                                        self.blueSliderColorValue = int((self.blueHandleX - self.sliderX) / (self.sliderWidth - self.handleWidth) * self.maxColorValue)
                                        self.blueHandleRect = UIRect(self.blueHandleX, self.blueSliderY, self.handleWidth, self.handleHeight, settings.deepSea)
                                
                                # Check if clicked directly on handles
                                if self.redHandleRect.isClicked(mousePosition):
                                    self.isDraggingRedSlider = True
                                elif self.greenHandleRect.isClicked(mousePosition):
                                    self.isDraggingGreenSlider = True
                                elif self.blueHandleRect.isClicked(mousePosition):
                                    self.isDraggingBlueSlider = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.isDraggingRedSlider = False
                        self.isDraggingGreenSlider = False
                        self.isDraggingBlueSlider = False
                            
                elif event.type == pygame.MOUSEMOTION:
                    mousePosition = pygame.mouse.get_pos()
                    if self.isDraggingRedSlider:
                        self.redHandleX = max(self.sliderX, min(mousePosition[0], self.sliderX + self.sliderWidth - self.handleWidth))
                        self.redSliderColorValue = int((self.redHandleX - self.sliderX) / (self.sliderWidth - self.handleWidth) * self.maxColorValue)
                        self.redHandleRect = UIRect(self.redHandleX, self.redSliderY, self.handleWidth, self.handleHeight, settings.deepSea)
                    elif self.isDraggingGreenSlider:
                        self.greenHandleX = max(self.sliderX, min(mousePosition[0], self.sliderX + self.sliderWidth - self.handleWidth))
                        self.greenSliderColorValue = int((self.greenHandleX - self.sliderX) / (self.sliderWidth - self.handleWidth) * self.maxColorValue)
                        self.greenHandleRect = UIRect(self.greenHandleX, self.greenSliderY, self.handleWidth, self.handleHeight, settings.deepSea)
                    elif self.isDraggingBlueSlider:
                        self.blueHandleX = max(self.sliderX, min(mousePosition[0], self.sliderX + self.sliderWidth - self.handleWidth))
                        self.blueSliderColorValue = int((self.blueHandleX - self.sliderX) / (self.sliderWidth - self.handleWidth) * self.maxColorValue)
                        self.blueHandleRect = UIRect(self.blueHandleX, self.blueSliderY, self.handleWidth, self.handleHeight, settings.deepSea)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Check for conflicts before saving
                        currentColor = (self.redSliderColorValue, self.greenSliderColorValue, self.blueSliderColorValue)
                        conflicts = self.getSimilarColors(currentColor, self.selectedColorSetting)
                        
                        # Only save if there are no conflicts
                        if not conflicts:
                            if self.selectedColorSetting:
                                new_color = (self.redSliderColorValue, self.greenSliderColorValue, self.blueSliderColorValue)
                                setattr(settings, self.selectedColorSetting, new_color)
                                settings.saveSettings()
                                
                                # Update the button to show the new color
                                for button in self.colorSettingButtons:
                                    if button.text == self.selectedColorSetting:
                                        button.color = new_color  # Update button color
                                        break
                        # If there are conflicts, just exit without saving (color reverts to original)
                        self.isColorPickerActive = False

    def Draw(self, screen):
        """Draw the main menu screen"""
        screen.fill(self.background)
        for button in self.colorSettingButtons:
            button.draw(screen)
        if self.isColorPickerActive:
            # Draw pause overlay
            self.pauseRect.draw(screen)

            # Draw color preview rect behind sliders
            currentColor = (self.redSliderColorValue, self.greenSliderColorValue, self.blueSliderColorValue)
            previewRect = UIRect(
                int(self.sliderX - self.screen.get_width() * 0.05),
                int(self.redSliderY - self.screen.get_height() * 0.1),
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
                self.saveText = (f"Too similar to {', '.join(conflicts)}")
                self.saveTextColor = (255, 0, 0)
                self.warningFontSize = self.screen.get_height()/40
            else:
                self.saveText = "Save"
                self.saveTextColor = None
                self.warningFontSize = self.screen.get_height()/20
        
            # Draw sliders
            self.drawSlider(screen, self.sliderX, self.redSliderY, self.sliderWidth, 
                        self.sliderHeight, self.redSliderColorValue, (self.maxColorValue, 0, 0), "Red", currentColor)
            self.drawSlider(screen, self.sliderX, self.greenSliderY, self.sliderWidth, 
                        self.sliderHeight, self.greenSliderColorValue, (0, self.maxColorValue, 0), "Green", currentColor)
            self.drawSlider(screen, self.sliderX, self.blueSliderY, self.sliderWidth, 
                        self.sliderHeight, self.blueSliderColorValue, (0, 0, self.maxColorValue), "Blue", currentColor)

            self.resetButton.color = currentColor
            self.saveButton.color = currentColor
            self.saveButton.text = self.saveText
            self.saveButton.font = pygame.font.Font('assets/fonts/MinionPro-BoldCn.otf', round(self.warningFontSize*settings.uiScale))
            self.saveButton.textColor = self.saveTextColor

            self.resetButton.draw(screen)
            self.saveButton.draw(screen)
    
    
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
        handleX = x + (value / self.maxColorValue) * (width - self.handleWidth)
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
    
    def setColor(self, color):
        self.redSliderColorValue = color[0]
        self.greenSliderColorValue = color[1]
        self.blueSliderColorValue = color[2]
        
        self.redHandleX   = self.sliderX + (self.redSliderColorValue   / self.maxColorValue) * (self.sliderWidth - self.handleWidth)
        self.greenHandleX = self.sliderX + (self.greenSliderColorValue / self.maxColorValue) * (self.sliderWidth - self.handleWidth)
        self.blueHandleX  = self.sliderX + (self.blueSliderColorValue  / self.maxColorValue) * (self.sliderWidth - self.handleWidth)

        self.redHandleRect   = UIRect(self.redHandleX,   self.redSliderY,   self.handleWidth, self.handleHeight, settings.deepSea)
        self.greenHandleRect = UIRect(self.greenHandleX, self.greenSliderY, self.handleWidth, self.handleHeight, settings.deepSea)
        self.blueHandleRect  = UIRect(self.blueHandleX,  self.blueSliderY,  self.handleWidth, self.handleHeight, settings.deepSea)