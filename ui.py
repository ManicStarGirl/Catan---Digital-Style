import pygame
from config import hexSize, hexWidthRatio, hexHeightRatio, numberTileColor, uiScale, deepSea

# Module for UI components and hex rendering

class uiRect:
    """UI rectangle component with optional text and scaling support"""
    def __init__(self, x, y, width, height, color, text=None, fontSize=0, scalable=(True, "center"), alpha=None, borderRadius=0, thickness=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.scalable = scalable
        self.alpha = alpha
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font('assets/fonts/MinionPro-BoldCn.otf', round(fontSize*uiScale))
        self.textColor = (0, 0, 0)
        self.borderRadius = borderRadius
        self.thickness = thickness

    def draw(self, screen):
        """Draw the UI rectangle with optional transparency and text"""
        # Create local copies to avoid mutating the original
        x, y, width, height = self.x, self.y, self.width, self.height
        if self.scalable[0]:
            anchor = self.scalable[1]
            if anchor == "bottom":
                y += (height * (1 - uiScale))
            if anchor == "left":
                x += (width * (1 - uiScale))
            if anchor == "top" or anchor == "bottom" or anchor == "center":
                x -= (width * (uiScale - 1) / 2)
            if anchor == "left" or anchor == "right" or anchor == "center":
                y -= (height * (uiScale - 1) / 2)
            height *= uiScale
            width *= uiScale
        if self.alpha is not None:
            alphaSurface = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(alphaSurface, self.color + (self.alpha,), (0, 0, width, height), border_radius=self.borderRadius, width=self.thickness)
            screen.blit(alphaSurface, (x, y))
        else:
            pygame.draw.rect(screen, self.color, (x, y, width, height), border_radius=self.borderRadius, width=self.thickness)
        if self.text != None:
            text = self.font.render(self.text, True, self.textColor)
            textRect = text.get_rect(center=(self.x + self.width/2, self.y + self.height/2))
            screen.blit(text, textRect)

    def isClicked(self, mousePos):
        """Check if the given mouse position is within this rectangle"""
        # Create local copies to avoid mutating the original
        x, y, width, height = self.x, self.y, self.width, self.height
        if self.scalable[0]:
            anchor = self.scalable[1]
            if anchor == "center":
                x -= (width * (uiScale - 1) / 2)
                y -= (height * (uiScale - 1) / 2)
            if anchor == "bottom":
                y += (height * (1 - uiScale))
            if anchor == "top" or anchor == "bottom" or anchor == "center":
                height *= uiScale
            if anchor == "left":
                x +=(width * (1 - uiScale))
            if anchor == "right" or anchor == "left" or anchor == "center":
                width *= uiScale
        if x <= mousePos[0] <= x + width and y <= mousePos[1] <= y + height:
            return True
        return False

class hex:
    """Hexagonal tile class for rendering game board tiles"""
    def __init__(self, x, y, resource=deepSea, number=None):
        self.x = x
        self.y = y
        self.number = number
        self.resource = resource
    
    def draw(self, screen, gamePos, gameScale, numberSize=None, alpha=None):
        """Draw the hex tile with optional transparency and number token"""
        # transparency is only used for hovering over tiles, which is currently removed

        # Compute the on-screen size of a hex tile after applying global scaling
        shapeSize = hexSize * gameScale

        # the size of the temporary surface used for transparent drawing (generously oversized to fit the hexagon).
        alphaSurfaceSize = shapeSize * 2

        # convert the hex-grid coordinate into a pixel offset from the board's origin.
        realX = shapeSize * hexWidthRatio * self.x
        realY = shapeSize * hexHeightRatio * self.y

        if alpha is None:
            # Opaque path: draw the hexagon's 6 vertices directly onto the
            # given screen, offset by both the tile's position (x, y) and
            # the board's overall pan offset (gamePos). Vertices go
            # clockwise starting from the rightmost point.
            pygame.draw.polygon(screen, self.resource, [
                (shapeSize + realX, 0 + realY) + gamePos, 
                (0.5 * shapeSize + realX, hexHeightRatio * shapeSize + realY) + gamePos, 
                (-0.5 * shapeSize + realX, hexHeightRatio * shapeSize + realY) + gamePos, 
                (-1 * shapeSize + realX, 0 + realY) + gamePos, 
                (-0.5 * shapeSize + realX, -hexHeightRatio * shapeSize + realY) + gamePos, 
                (0.5 * shapeSize + realX, -hexHeightRatio * shapeSize + realY) + gamePos
            ])
        else:
            # Transparent path: draw onto a separate per-pixel-alpha
            # surface first (since pygame.draw doesn't support alpha
            # blending directly onto the main screen), then blit that
            # surface onto the given screen at the correct position.
            alphaSurface = pygame.Surface((alphaSurfaceSize, alphaSurfaceSize), pygame.SRCALPHA)

            # Vertices here are expressed relative to the small alpha
            # surface itself (not the main screen/gamePos), roughly
            # centered within it.
            pygame.draw.polygon(alphaSurface, self.resource + (alpha,), [
                (alphaSurfaceSize, alphaSurfaceSize/2), 
                (hexWidthRatio * shapeSize, hexHeightRatio * shapeSize + alphaSurfaceSize/2), 
                (0.5 * shapeSize, hexHeightRatio * shapeSize + alphaSurfaceSize/2), 
                (0, alphaSurfaceSize/2), 
                (0.5 * shapeSize, -hexHeightRatio * shapeSize + shapeSize), 
                (hexWidthRatio * shapeSize, -hexHeightRatio * shapeSize + shapeSize)
            ])

            # Blit the alpha surface onto the given screen, positioned so
            # the hexagon drawn on it lines up with (x, y) plus the
            # board's pan offset, accounting for the surface being
            # centered on the tile (hence the `- shapeSize` correction).
            screen.blit(alphaSurface, (realX - shapeSize, realY - shapeSize) + gamePos)
        if self.number is not None:
            # Draw the token's circular background, centered on the tile.
            if self.number != "?":
                pygame.draw.circle(screen, numberTileColor, (realX, realY) + gamePos, shapeSize/3)

            # Color the number text based on how "hot" the roll is: 6 and 8
            # are the most probable non-7 rolls on two dice, so they're
            # highlighted in red; other valid production numbers (2-12,
            # excluding 7, which triggers the robber rather than production)
            # are black; anything else (e.g. a placeholder/invalid value)
            # falls back to blue.
            if self.number in [6, 8]:
                tokenNumber = numberSize.render(str(self.number), True, "red")
            elif self.number == "?" or (2 <= self.number <= 12 and self.number != 7):
                tokenNumber = numberSize.render(str(self.number), True, "black")
            else:
                tokenNumber = numberSize.render(str(self.number), True, "blue")
            
            # Center the rendered text on the tile and draw it on top of the
            # circular background.
            numberRect = tokenNumber.get_rect(center=(realX, realY) + gamePos)
            screen.blit(tokenNumber, numberRect)