from config import settings, numberSize, panSpeed, hexSize, hexWidthRatio, hexHeightRatio, minZoom, maxZoom, textSize, DEFAULT_CONFIG
from screens import Screen
from ui import UIRect, hex
from coordinates import hexRound, pixelToFractionalHex
import pygame, json, random

class BuildScreen(Screen):
    """Main game screen for playing Catan"""
    def __init__(self, screenManager, screen):
        super().__init__(screenManager, screen)
        self.tileList = []
        self.hexLayout = {
            (0, 0): ("desert", settings.desert), (1, 0): ("sheep", settings.sheep), (2, 0): ("ore", settings.ore),
            (0, 1): ("wheat", settings.wheat),   (1, 1): ("wood", settings.wood),   (2, 1): ("brick", settings.brick),
            (0, 2): ("goldMine", settings.goldMine), (1, 2): ("sea", settings.sea), (2, 2): ("fog", settings.fog)
        }

    def OnEnter(self):
        super().OnEnter()
        self.paused = False
        self.dragging = False
        self.choosingHex = False
        self.placingHex = False
        self.removingHex = False
        self.currentHex = settings.desert

        # Center the game board on screen
        self.gamePos = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.mouseDownPos = None
        self.offsetX = 0
        self.offsetY = 0
        self.gameScale = settings.gameScale
        self.numberSize = numberSize
        self.textSize = pygame.font.Font('assets/fonts/MinionPro-BoldCn.otf', self.screen.get_width() // 40)

        # Recalculate buttons with current screen size
        self.continueButton = UIRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height() * 3/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonColor, "Continue", self.fontSize, (True, "center"), borderRadius=10)
        self.mainMenuButton = UIRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height() * 4/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonColor, "Main Menu", self.fontSize, (True, "center"), borderRadius=10)
        self.quitButton = UIRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height() * 5/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonColor, "Save and Quit", self.fontSize, (True, "center"), borderRadius=10)

    def OnExit(self):
        pass

    def Update(self, dt, currentTime):
        """Handle game input and update game state"""

        for event in pygame.event.get():
            mousePos = pygame.Vector2(pygame.mouse.get_pos())
            if event.type == pygame.QUIT:
                self.saveGame()
                return "quit"
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    return "fullscreen"
                if not self.choosingHex:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.placingHex = False
                elif event.button == 2:
                    self.dragging = False
                    self.mouseDownPos = None
                elif event.button == 3:
                    self.removingHex = False

            # When the game is running (not paused)
            if self.paused: # paused
                # Handle pause menu input
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_pos = pygame.mouse.get_pos()
                        if self.continueButton.isClicked(mouse_pos):
                            self.paused = False
                        elif self.mainMenuButton.isClicked(mouse_pos):
                            self.saveGame()
                            return "mainMenu"
                        elif self.quitButton.isClicked(mouse_pos):
                            self.saveGame()
                            return "quit"
            elif self.choosingHex: # choosing hex
                if event.type == pygame.MOUSEBUTTONDOWN:
                    shapeSize = hexSize * self.screen.get_width() / 800  # same formula draw() uses
                    for coord, (name, color) in self.hexLayout.items():
                        x, y = coord
                        pos = pygame.Vector2(self.screen.get_width() * (x+1)/4, self.screen.get_height() * (y+1)/4)
                        if mousePos.distance_to(pos) <= shapeSize:
                            self.currentHex = color
                            self.choosingHex = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.choosingHex = False
            elif self.placingHex:
                self.hexCoords = hexRound(pixelToFractionalHex(self.gamePos, mousePos, hexSize * self.gameScale))
                if self.currentHex == settings.sea or self.hexCoords not in [(tile.x, tile.y) for tile in self.tileList] or [tile for tile in self.tileList if (tile.x, tile.y) == self.hexCoords and tile.resource == settings.sea]:
                    if self.currentHex not in settings.getLists()["noNumberTiles"] and self.currentHex != settings.fog:
                        self.tileList.append(hex(self.hexCoords[0], self.hexCoords[1], self.currentHex, random.choice(DEFAULT_CONFIG["numberList"])))
                    elif self.currentHex == settings.fog:
                        self.tileList.append(hex(self.hexCoords[0], self.hexCoords[1], self.currentHex, "?"))
                    else:
                        self.tileList.append(hex(self.hexCoords[0], self.hexCoords[1], self.currentHex, None))
            elif self.removingHex:
                self.hexCoords = hexRound(pixelToFractionalHex(self.gamePos, mousePos, hexSize * self.gameScale))
                if self.hexCoords in [(tile.x, tile.y) for tile in self.tileList]:
                    self.tileList = [tile for tile in self.tileList if (tile.x, tile.y) != self.hexCoords]
                
            else:
                if event.type == pygame.MOUSEWHEEL:
                    # Zoom in/out, keeping the point under the mouse cursor fixed in place
                    # Where in "world space" the mouse currently points, before the zoom changes
                    worldPos = (mousePos - self.gamePos) / self.gameScale

                    if event.y > 0:
                        self.gameScale *= settings.zoomFactor
                        if self.gameScale > maxZoom:
                            self.gameScale = maxZoom
                    else:
                        self.gameScale /= settings.zoomFactor
                        if self.gameScale < minZoom:
                            self.gameScale = minZoom

                    # Re-anchor gamePos so the same world point stays under the mouse after zooming
                    self.gamePos = mousePos - worldPos * self.gameScale

                    # Number tokens are drawn from a font, so their size must be regenerated whenever zoom level changes
                    self.numberSize = pygame.font.Font('assets/fonts/MinionPro-BoldCn.otf', round(textSize * self.gameScale))

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    shapeSize = hexSize * self.screen.get_width() / 800  # same formula draw() uses
                    if event.button == 1:
                        x, y = self.screen.get_width() - shapeSize * 6/4, shapeSize * 5/4
                        pos = pygame.Vector2(x, y)
                        if mousePos.distance_to(pos) <= shapeSize:
                            self.choosingHex = True
                        else:
                            self.placingHex = True
                            self.hexCoords = hexRound(pixelToFractionalHex(self.gamePos, mousePos, hexSize * self.gameScale))
                            if self.currentHex == settings.sea or self.hexCoords not in [(tile.x, tile.y) for tile in self.tileList] or [tile for tile in self.tileList if (tile.x, tile.y) == self.hexCoords and tile.resource == settings.sea]:
                                if self.currentHex not in settings.getLists()["noNumberTiles"] and self.currentHex != settings.fog:
                                    self.tileList.append(hex(self.hexCoords[0], self.hexCoords[1], self.currentHex, random.choice(DEFAULT_CONFIG["numberList"])))
                                elif self.currentHex == settings.fog:
                                    self.tileList.append(hex(self.hexCoords[0], self.hexCoords[1], self.currentHex, "?"))
                                else:
                                    self.tileList.append(hex(self.hexCoords[0], self.hexCoords[1], self.currentHex, None))
                    elif event.button == 2:  # Middle click
                        self.mouseDownPos = event.pos
                        self.offsetX = self.gamePos.x - self.mouseDownPos[0]
                        self.offsetY = self.gamePos.y - self.mouseDownPos[1]
                        self.dragging = True
                    elif event.button == 3:  # Right click
                        self.removingHex = True
                        self.hexCoords = hexRound(pixelToFractionalHex(self.gamePos, mousePos, hexSize * self.gameScale))
                        if self.hexCoords in [(tile.x, tile.y) for tile in self.tileList]:
                            self.tileList = [tile for tile in self.tileList if (tile.x, tile.y) != self.hexCoords]

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        mouseX, mouseY = event.pos
                        self.gamePos.x = mouseX + self.offsetX
                        self.gamePos.y = mouseY + self.offsetY

        
        if not self.paused:
            # Handle keyboard panning
            keys = pygame.key.get_pressed()
            # Hold shift to pan faster
            if keys[pygame.K_RSHIFT] or keys[pygame.K_LSHIFT]:
                speed = panSpeed * 2
            else:
                speed = panSpeed

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.gamePos.y += speed * dt
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.gamePos.y -= speed * dt
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.gamePos.x += speed * dt
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.gamePos.x -= speed * dt

    def Draw(self, screen):
        """Draw the game screen including hex grid, UI elements, and pause overlay"""
        screen.fill(self.background)
        gameWidth, gameHeight = screen.get_size()
        shapeSize = hexSize * self.gameScale
        buffer = shapeSize  # extra margin so hexes just off-screen still get drawn (avoids pop-in)

        # Visible world-space bounds, used to cull hexes that are off-screen
        min_x = -self.gamePos.x - buffer
        max_x = -self.gamePos.x + gameWidth + buffer
        min_y = -self.gamePos.y - buffer
        max_y = -self.gamePos.y + gameHeight + buffer

        # Draw all visible hex tiles
        for tile in self.tileList:
            tile_x = tile.x * shapeSize * hexWidthRatio
            tile_y = tile.y * shapeSize * hexHeightRatio

            # Only draw hexes that are within (or near) the visible screen area
            if min_x <= tile_x <= max_x and min_y <= tile_y <= max_y:
                tile.draw(screen, self.gamePos, self.gameScale, self.numberSize)

        if self.paused:
            # Draw pause overlay
            pauseRect = UIRect(0, 0, screen.get_width(), screen.get_height(), (0, 0, 0), scalable=(False, None), alpha=settings.pauseAlpha)
            pauseRect.draw(screen)

            # Draw quit button and text
            self.continueButton.draw(screen)
            self.mainMenuButton.draw(screen)
            self.quitButton.draw(screen)

        elif self.choosingHex:
            # Draw placement overlay
            placementRect = UIRect(0, 0, screen.get_width(), screen.get_height(), (0, 0, 0), scalable=(False, None), alpha=settings.pauseAlpha)
            placementRect.draw(screen)

            for coord, (name, color) in self.hexLayout.items():
                x, y = self.screen.get_width() * (coord[0]+1)/4, self.screen.get_height() * (coord[1]+1)/4
                resourceHex = hex(0, 0, tuple(color), name)
                resourceHex.draw(screen, pygame.Vector2(x, y), self.screen.get_width() / 800, numberSize=self.textSize)

        else:
            mousePos = pygame.mouse.get_pos()
            # Highlight the hex currently under the mouse cursor.
            hoveredHexCoords = hexRound(pixelToFractionalHex(self.gamePos, mousePos, hexSize * self.gameScale))
            hoveredHex = hex(hoveredHexCoords[0], hoveredHexCoords[1], tuple(settings.selectorColor))
            hoveredHex.draw(screen, self.gamePos, self.gameScale, alpha=settings.selectorAlpha)

            shapeSize = hexSize * self.screen.get_width() / 800  # same formula draw() uses
            x, y = self.screen.get_width() - shapeSize * 6/4, shapeSize * 5/4
            if self.currentHex not in settings.getLists()["noNumberTiles"] and self.currentHex != settings.fog:
                shownHex = hex(0, 0, tuple(self.currentHex), "?")
                shownHex.draw(screen, pygame.Vector2(x, y), self.screen.get_width() / 800, numberSize=self.textSize, showToken=True)
            elif self.currentHex == settings.fog:
                shownHex = hex(0, 0, tuple(self.currentHex), "?")
                shownHex.draw(screen, pygame.Vector2(x, y), self.screen.get_width() / 800, numberSize=self.textSize)
            else:
                shownHex = hex(0, 0, tuple(self.currentHex))
                shownHex.draw(screen, pygame.Vector2(x, y), self.screen.get_width() / 800, numberSize=self.textSize)
        

    def saveGame(self):
        """Save current game state to JSON file"""
        save_data = {
            "tiles": [(t.x, t.y, t.resource, t.number) for t in self.tileList],
            "settlements": None,
            "roads": None,
            "currentPlayer": None
        }
        with open("save.json", "w") as f:
            json.dump(save_data, f)