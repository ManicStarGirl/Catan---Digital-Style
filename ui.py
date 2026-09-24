import pygame
from config import hexSize, hexWidthRatio, hexHeightRatio, settings

# Module for UI components and hex rendering

class UIRect:
    """UI rectangle component with optional text and scaling support"""
    def __init__(self, x, y, width, height, color, text=None, fontSize=0, scalable=(True, "center"), alpha=None, borderRadius=0, thickness=0, textColor=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.scalable = scalable
        self.alpha = alpha
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font('assets/fonts/MinionPro-BoldCn.otf', round(fontSize*settings.uiScale))
        self.borderRadius = borderRadius
        self.thickness = thickness
        self.textColor = textColor

    def draw(self, screen):
        """Draw the UI rectangle with optional transparency and text"""
        x, y, width, height = self.x, self.y, self.width, self.height
        if self.scalable[0]:
            anchor = self.scalable[1]
            if anchor == "bottom":
                y += (height * (1 - settings.uiScale))
            if anchor == "left":
                x += (width * (1 - settings.uiScale))
            if anchor == "top" or anchor == "bottom" or anchor == "center":
                x -= (width * (settings.uiScale - 1) / 2)
            if anchor == "left" or anchor == "right" or anchor == "center":
                y -= (height * (settings.uiScale - 1) / 2)
            height *= settings.uiScale
            width *= settings.uiScale
        if self.alpha is not None:
            alphaSurface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(alphaSurface, self.color + (self.alpha,), (0, 0, width, height), border_radius=self.borderRadius, width=self.thickness)
            screen.blit(alphaSurface, (x, y))
        else:
            pygame.draw.rect(screen, self.color, (x, y, width, height), border_radius=self.borderRadius, width=self.thickness)
        if self.text != None:
            if self.textColor is None:
                if (0.299 * self.color[0] + 0.587 * self.color[1] + 0.114 * self.color[2]) >= 128:
                    self.textColor = (0, 0, 0)
                else:
                    self.textColor = (255, 255, 255)
            else:
                if (abs(self.textColor[0] - self.color[0]) + abs(self.textColor[1] - self.color[1]) + abs(self.textColor[2] - self.color[2])) / 3 < 60:
                    self.textColor = (255 - self.textColor[0], 255 - self.textColor[1], 255 - self.textColor[2])
            text = self.font.render(self.text, True, self.textColor)
            textRect = text.get_rect(center=(self.x + self.width/2, self.y + self.height/2))
            screen.blit(text, textRect)

    def isClicked(self, mousePos):
        """Check if the given mouse position is within this rectangle"""
        x, y, width, height = self.x, self.y, self.width, self.height
        if self.scalable[0]:
            anchor = self.scalable[1]
            if anchor == "center":
                x -= (width * (settings.uiScale - 1) / 2)
                y -= (height * (settings.uiScale - 1) / 2)
            if anchor == "bottom":
                y += (height * (1 - settings.uiScale))
            if anchor == "top" or anchor == "bottom" or anchor == "center":
                height *= settings.uiScale
            if anchor == "left":
                x +=(width * (1 - settings.uiScale))
            if anchor == "right" or anchor == "left" or anchor == "center":
                width *= settings.uiScale
        if x <= mousePos[0] <= x + width and y <= mousePos[1] <= y + height:
            return True
        return False

class hex:
    """Hexagonal tile class for rendering game board tiles"""
    def __init__(self, x, y, resource="deepSea", number=None):
        self.x = x
        self.y = y
        self.number = number
        self.resource = resource
    
    def draw(self, screen, gamePos, gameScale, numberSize=None, alpha=None, showToken=False):
        """Draw the hex tile with optional transparency and number token"""
        shapeSize = hexSize * gameScale
        alphaSurfaceSize = shapeSize * 2
        realX = shapeSize * hexWidthRatio * self.x
        realY = shapeSize * hexHeightRatio * self.y

        if alpha is None:
            pygame.draw.polygon(screen, getattr(settings, self.resource), [
                (shapeSize + realX, 0 + realY) + gamePos, 
                (0.5 * shapeSize + realX, hexHeightRatio * shapeSize + realY) + gamePos, 
                (-0.5 * shapeSize + realX, hexHeightRatio * shapeSize + realY) + gamePos, 
                (-1 * shapeSize + realX, 0 + realY) + gamePos, 
                (-0.5 * shapeSize + realX, -hexHeightRatio * shapeSize + realY) + gamePos, 
                (0.5 * shapeSize + realX, -hexHeightRatio * shapeSize + realY) + gamePos
            ])
        else:
            alphaSurface = pygame.Surface((alphaSurfaceSize, alphaSurfaceSize), pygame.SRCALPHA)
            pygame.draw.polygon(alphaSurface, tuple(getattr(settings, self.resource)) + (alpha,), [
                (alphaSurfaceSize, alphaSurfaceSize/2), 
                (hexWidthRatio * shapeSize, hexHeightRatio * shapeSize + alphaSurfaceSize/2), 
                (0.5 * shapeSize, hexHeightRatio * shapeSize + alphaSurfaceSize/2), 
                (0, alphaSurfaceSize/2), 
                (0.5 * shapeSize, -hexHeightRatio * shapeSize + shapeSize), 
                (hexWidthRatio * shapeSize, -hexHeightRatio * shapeSize + shapeSize)
            ])
            screen.blit(alphaSurface, (realX - shapeSize, realY - shapeSize) + gamePos)
        if self.number is not None:
            if not isinstance(self.number, str) or showToken:
                pygame.draw.circle(screen, settings.numberTileColor, (realX, realY) + gamePos, shapeSize/3)
                if (0.299 * settings.numberTileColor[0] + 0.587 * settings.numberTileColor[1] + 0.114 * settings.numberTileColor[2]) >= 128:
                    self.textColor = (0, 0, 0)
                else:
                    self.textColor = (255, 255, 255)
            else:
                if (0.299 * settings.fog[0] + 0.587 * settings.fog[1] + 0.114 * settings.fog[2]) >= 128:
                    self.textColor = (0, 0, 0)
                else:
                    self.textColor = (255, 255, 255)

            if self.number in [6, 8]:
                if (abs(settings.numberTileColor[0] - 255) + abs(settings.numberTileColor[1]) + abs(settings.numberTileColor[2])) / 3 < 60:
                    tokenTextColor = (0, 255, 255)
                else:
                    tokenTextColor = (255, 0, 0)
            elif isinstance(self.number, str) or (2 <= self.number <= 12 and self.number != 7):
                tokenTextColor = self.textColor
            else:
                if (abs(settings.numberTileColor[0]) + abs(settings.numberTileColor[1]) + abs(settings.numberTileColor[2] - 255)) / 3 < 60:
                    tokenTextColor = (255, 255, 0)
                else:
                    tokenTextColor = (0, 0, 255)

            tokenNumber = numberSize.render(str(self.number), True, tokenTextColor)
            numberRect = tokenNumber.get_rect(center=(realX, realY) + gamePos)
            screen.blit(tokenNumber, numberRect)