from config import (
    numberOfRings, hexSize, gameScale, hexWidthRatio, hexHeightRatio,
    selectorColor, selectorAlpha, zoomFactor, maxZoom, minZoom, textSize,
    numberSize, pauseAlpha, panSpeed, diceRedColor, diceYellowColor
)
from screens import Screen
from ui import uiRect, hex
from hex_grid import newTiles
from coordinates import hexRound, pixelToFractionalHex, getSettlementPositions, getRoadPositions
import pygame, json, math, random

class GameScreen(Screen):
    """Main game screen for playing Catan"""
    def __init__(self, screenManager, screen, tileList=None, settlements=None, roads=None, currentPlayer=None): # Assets, fonts, static button positions, things that never change
        super().__init__(screenManager, screen)
        # Only setup things that don't depend on screen size here
        # Generate the initial hex map (a spiral/ring-based board of `numberOfRings` rings)
        self.tileList = tileList if tileList is not None else newTiles(numberOfRings)
        self.settlements = settlements if settlements is not None else getSettlementPositions(self.tileList)
        self.roads = roads if roads is not None else getRoadPositions(self.tileList)
        # List of player colors and current player tracking
        self.playerList = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (0, 0, 0), (255, 255, 255)]
        self.currentPlayer = currentPlayer if currentPlayer is not None else (self.playerList[0], 0)

    def OnEnter(self): # Reset game state, start animations, recalculate responsive positions
        super().OnEnter()
        self.paused = False
        self.dragging = False
        # Center the game board on screen
        self.gamePos = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.mouse_down_pos = None
        self.offset_x = 0
        self.offset_y = 0
        self.gameScale = gameScale
        self.numberSize = numberSize

        self.diceSideLength = self.screen.get_width() / 25
        self.diceDistance = self.screen.get_width() / 24 - self.diceSideLength / 2
        self.dicePipSize = self.diceSideLength / 10
        self.dicePipSpacing = self.diceSideLength / 5

        # Recalculate buttons with current screen size
        self.continueButton = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height() * 3/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, self.buttonColor, "Continue", self.fontSize, (True, "center"), borderRadius=10)
        self.mainMenuButton = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height() * 4/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, self.buttonColor, "Main Menu", self.fontSize, (True, "center"), borderRadius=10)
        self.quitButton = uiRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height() * 5/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, self.buttonColor, "Quit", self.fontSize, (True, "center"), borderRadius=10)
        self.endTurnButton = uiRect(self.screen.get_width() * 15/16 - self.buttonWidth/8, self.screen.get_height()/16 - self.buttonHeight/4, self.buttonWidth/4, self.buttonHeight/2, self.buttonColor, "End Turn", self.fontSize/2, (True, "center"), borderRadius=5)
        self.endTurnBorder = uiRect(self.screen.get_width() * 15/16 - self.buttonWidth/8, self.screen.get_height()/16 - self.buttonHeight/4, self.buttonWidth/4, self.buttonHeight/2, self.currentPlayer[0], scalable=(True, "center"), borderRadius=5, thickness=6)
        self.redDice = uiRect(self.diceDistance, self.diceDistance + self.redYOffset, self.diceSideLength, self.diceSideLength, diceRedColor, scalable=(True, "center"), borderRadius=12)
        self.redDiceBorder = uiRect(self.diceDistance, self.diceDistance + self.redYOffset, self.diceSideLength, self.diceSideLength, (0, 0, 0), scalable=(True, "center"), borderRadius=12, thickness=3)
        self.yellowDice = uiRect(self.diceDistance * 3/2 + self.diceSideLength, self.diceDistance + self.yellowYOffset, self.diceSideLength, self.diceSideLength, diceYellowColor, scalable=(True, "center"), borderRadius=12)
        self.yellowDiceBorder = uiRect(self.diceDistance * 3/2 + self.diceSideLength, self.diceDistance + self.yellowYOffset, self.diceSideLength, self.diceSideLength, (0, 0, 0), scalable=(True, "center"), borderRadius=12, thickness=3)

    def OnExit(self):
        pass # Likely nothing here

    def Update(self, dt, currentTime):
        """Handle game input and update game state"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.saveGame()
                return "quit"
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                elif event.key == pygame.K_F11:
                    return "fullscreen"

            # When the game is running (not paused)
            if not self.paused:
                if event.type == pygame.MOUSEWHEEL:
                    # Zoom in/out, keeping the point under the mouse cursor fixed in place.
                    mousePos = pygame.Vector2(pygame.mouse.get_pos())

                    # Where in "world space" the mouse currently points, before the zoom changes.
                    worldPos = (mousePos - self.gamePos) / self.gameScale

                    if event.y > 0:
                        self.gameScale *= zoomFactor
                        if self.gameScale > maxZoom:
                            self.gameScale = maxZoom
                    else:
                        self.gameScale /= zoomFactor
                        if self.gameScale < minZoom:
                            self.gameScale = minZoom

                    # Re-anchor gamePos so the same world point stays under the mouse after zooming.
                    self.gamePos = mousePos - worldPos * self.gameScale

                    # Number tokens are drawn from a font, so their size must be regenerated
                    # whenever zoom level changes.
                    self.numberSize = pygame.font.Font('assets/fonts/MinionPro-BoldCn.otf', round(textSize * self.gameScale))

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mousePos = pygame.mouse.get_pos()
                        mouseWorldPos = (pygame.Vector2(mousePos) - self.gamePos) / self.gameScale
                        closestCorner, closestRoad = self.findClosestIntersection(mouseWorldPos)
                        if self.endTurnButton.isClicked(mousePos):
                            self.currentPlayer = (self.playerList[(self.currentPlayer[1] + 1) % len(self.playerList)], self.currentPlayer[1] + 1)
                        elif self.redDice.isClicked(mousePos) or self.yellowDice.isClicked(mousePos):
                            self.isRolling = True
                            self.rollStartTime = currentTime
                            self.lastShuffleTime = currentTime
                            self.redShakeOffset = random.randint(10, 20)
                            self.yellowShakeOffset = random.randint(10, 20)
                            self.redNumShakes = random.randint(2, 5)
                            self.yellowNumShakes = random.randint(2, 5)
                        elif closestCorner:
                            # Find and update the settlement position
                            for pos in self.settlements:
                                if pos[0] == closestCorner[0] and pos[1] == closestCorner[1]:
                                    if self.validSettlement(pos):
                                        pos[2] = self.currentPlayer[0]  # Replace None with player color
                                        break
                        elif closestRoad:
                            # Find and update the road position
                            for pos in self.roads:
                                if pos[0] == closestRoad[0] and pos[1] == closestRoad[1]:
                                    if pos[3] == None:
                                        pos[3] = self.currentPlayer[0]  # Replace None with player color
                                        break
                            
                        # Start a drag: remember the offset between the mouse and gamePos
                        self.mouse_down_pos = event.pos
                        self.offset_x = self.gamePos.x - self.mouse_down_pos[0]
                        self.offset_y = self.gamePos.y - self.mouse_down_pos[1]
                        self.dragging = True
                    elif event.button == 3:  # Right click
                        mousePos = pygame.mouse.get_pos()
                        mouseWorldPos = (pygame.Vector2(mousePos) - self.gamePos) / self.gameScale
                        closestCorner, closestRoad = self.findClosestIntersection(mouseWorldPos)
                        if closestCorner:
                            # Find and update the settlement position
                            for pos in self.settlements:
                                if pos[0] == closestCorner[0] and pos[1] == closestCorner[1]:
                                    if pos[2] == self.currentPlayer[0]:
                                        pos[2] = None  # Replace player color with None
                                        break
                        elif closestRoad:
                            # Find and update the road position
                            for pos in self.roads:
                                print(pos[0] == closestRoad[0] and pos[1] == closestRoad[1], pos, closestRoad)
                                if pos[0] == closestRoad[0] and pos[1] == closestRoad[1]:
                                    print(pos[3] == self.currentPlayer[0], pos[3], self.currentPlayer[0])
                                    if pos[3] == self.currentPlayer[0]:
                                        pos[3] = None  # Replace player color with None
                                        break
                        

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        mouse_x, mouse_y = event.pos
                        self.gamePos.x = mouse_x + self.offset_x
                        self.gamePos.y = mouse_y + self.offset_y

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False
                        self.mouse_down_pos = None
            else:
                # Handle pause menu input
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_pos = pygame.mouse.get_pos()
                        if self.continueButton.isClicked(mouse_pos):
                            self.paused = False
                        elif self.mainMenuButton.isClicked(mouse_pos):
                            self.saveGame()
                            return "main_menu"
                        elif self.quitButton.isClicked(mouse_pos):
                            self.saveGame()
                            return "quit"
        
        if not self.paused:
            if self.isRolling:
                progress = (currentTime - self.rollStartTime) / self.ROLL_DURATION
                self.redYOffset = math.sin(progress * math.pi * 2 * self.redNumShakes) * self.redShakeOffset
                self.yellowYOffset = math.sin(progress * math.pi * 2 * self.yellowNumShakes) * self.yellowShakeOffset
                # Check if rolling duration has expired
                if currentTime - self.rollStartTime > self.ROLL_DURATION:
                    self.isRolling = False
                    self.currentRedValue = random.choice(self.diceList)  # Final landing value
                    self.currentYellowValue = random.choice(self.diceList)  # Final landing value
                # Shuffle face values quickly during the roll interval
                elif currentTime - self.lastShuffleTime > self.SHUFFLE_DELAY:
                    self.currentRedValue = random.choice([n for n in self.diceList if n != self.currentRedValue])
                    self.currentYellowValue = random.choice([n for n in self.diceList if n != self.currentYellowValue])
                    self.lastShuffleTime = currentTime
            # Handle keyboard panning
            keys = pygame.key.get_pressed()

            # Hold shift to pan faster.
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
        
        # Visible world-space bounds, used to cull hexes that are off-screen.
        min_x = -self.gamePos.x - buffer
        max_x = -self.gamePos.x + gameWidth + buffer
        min_y = -self.gamePos.y - buffer
        max_y = -self.gamePos.y + gameHeight + buffer

        # Draw all visible hex tiles
        for tile in self.tileList:
            tile_x = tile.x * shapeSize * hexWidthRatio
            tile_y = tile.y * shapeSize * hexHeightRatio

            # Only draw hexes that are within (or near) the visible screen area.
            if min_x <= tile_x <= max_x and min_y <= tile_y <= max_y:
                tile.draw(screen, self.gamePos, self.gameScale, self.numberSize)

        for settlement in self.settlements:
            if settlement[2] is not None:
                cornerWorld = pygame.Vector2(
                    settlement[0] * hexSize * hexWidthRatio,
                    settlement[1] * hexSize * hexHeightRatio
                )
                screenPos = cornerWorld * self.gameScale + self.gamePos
                squareSize = 12 * self.gameScale
                rect = pygame.Rect(
                    screenPos.x - squareSize/2,
                    screenPos.y - squareSize/2,
                    squareSize,
                    squareSize
                )
                pygame.draw.rect(screen, settlement[2], rect)
        for road in self.roads:
            if road[3] is not None:
                cornerWorld = pygame.Vector2(
                    road[0] * hexSize * hexWidthRatio,
                    road[1] * hexSize * hexHeightRatio
                )
                screenPos = cornerWorld * self.gameScale + self.gamePos
                roadLength = 20 * self.gameScale
                roadWidth = 6 * self.gameScale

                angleRad = math.radians(road[2])
                
                # Direction vector along the road
                dirX = math.cos(angleRad)
                dirY = math.sin(angleRad)
                
                # Perpendicular vector (for width)
                perpX = -dirY
                perpY = dirX
                
                # Calculate 4 corners
                corners = [
                    (screenPos.x - dirX * roadLength/2 + perpX * roadWidth/2,
                    screenPos.y - dirY * roadLength/2 + perpY * roadWidth/2),
                    (screenPos.x + dirX * roadLength/2 + perpX * roadWidth/2,
                    screenPos.y + dirY * roadLength/2 + perpY * roadWidth/2),
                    (screenPos.x + dirX * roadLength/2 - perpX * roadWidth/2,
                    screenPos.y + dirY * roadLength/2 - perpY * roadWidth/2),
                    (screenPos.x - dirX * roadLength/2 - perpX * roadWidth/2,
                    screenPos.y - dirY * roadLength/2 - perpY * roadWidth/2)
                ]

                pygame.draw.polygon(screen, road[3], corners)

        # uiBase = uiRect(0, screen.get_height()*5/6, screen.get_width(), screen.get_height()/6, (255, 255, 255), scalable=(True, "bottom"))
        # uiBase.draw(screen)
        if not self.paused:
            # Handle placement preview when not paused
            mousePos = pygame.mouse.get_pos()
            mouseWorldPos = (pygame.Vector2(mousePos) - self.gamePos) / self.gameScale
            closestCorner, closestRoad = self.findClosestIntersection(mouseWorldPos)

            # Draw settlement preview if close enough
            if closestCorner:
                if self.validSettlement(closestCorner):
                    cornerWorld = pygame.Vector2(
                        closestCorner[0] * hexSize * hexWidthRatio,
                        closestCorner[1] * hexSize * hexHeightRatio
                    )
                    screenPos = cornerWorld * self.gameScale + self.gamePos
                    squareSize = 12 * self.gameScale
                    rect = pygame.Rect(
                        screenPos.x - squareSize/2,
                        screenPos.y - squareSize/2,
                        squareSize,
                        squareSize
                    )
                    pygame.draw.rect(screen, self.currentPlayer[0], rect)

            # Draw road preview if close enough
            if closestRoad:
                roadWorld = pygame.Vector2(
                    closestRoad[0] * hexSize * hexWidthRatio,
                    closestRoad[1] * hexSize * hexHeightRatio
                )
                screenPos = roadWorld * self.gameScale + self.gamePos
                roadLength = 20 * self.gameScale
                roadWidth = 6 * self.gameScale

                angleRad = math.radians(closestRoad[2])
                
                # Direction vector along the road
                dirX = math.cos(angleRad)
                dirY = math.sin(angleRad)
                
                # Perpendicular vector (for width)
                perpX = -dirY
                perpY = dirX
                
                # Calculate 4 corners
                corners = [
                    (screenPos.x - dirX * roadLength/2 + perpX * roadWidth/2,
                    screenPos.y - dirY * roadLength/2 + perpY * roadWidth/2),
                    (screenPos.x + dirX * roadLength/2 + perpX * roadWidth/2,
                    screenPos.y + dirY * roadLength/2 + perpY * roadWidth/2),
                    (screenPos.x + dirX * roadLength/2 - perpX * roadWidth/2,
                    screenPos.y + dirY * roadLength/2 - perpY * roadWidth/2),
                    (screenPos.x - dirX * roadLength/2 - perpX * roadWidth/2,
                    screenPos.y - dirY * roadLength/2 - perpY * roadWidth/2)
                ]

                pygame.draw.polygon(screen, self.currentPlayer[0], corners)
            
            # Highlight the hex currently under the mouse cursor.
            # hoveredHexCoords = hexRound(pixelToFractionalHex(self.gamePos, mousePos, hexSize * self.gameScale))
            # hoveredHex = hex(hoveredHexCoords[0], hoveredHexCoords[1], selectorColor)
            # hoveredHex.draw(screen, self.gamePos, self.gameScale, alpha=selectorAlpha)


        # Draw end turn button
        self.endTurnBorder = uiRect(self.screen.get_width() * 15/16 - self.buttonWidth/8, self.screen.get_height()/16 - self.buttonHeight/4, self.buttonWidth/4, self.buttonHeight/2, self.currentPlayer[0], scalable=(True, "center"), borderRadius=5, thickness=6)
        self.endTurnButton.draw(screen)
        self.endTurnBorder.draw(screen)
        
        # Draw dice buttons
        self.redDice = uiRect(self.diceDistance, self.diceDistance + self.redYOffset, self.diceSideLength, self.diceSideLength, diceRedColor, scalable=(True, "center"), borderRadius=12)
        self.yellowDice = uiRect(self.diceDistance * 3/2 + self.diceSideLength, self.diceDistance + self.yellowYOffset, self.diceSideLength, self.diceSideLength, diceYellowColor, scalable=(True, "center"), borderRadius=12)
        self.redDiceBorder = uiRect(self.diceDistance, self.diceDistance + self.redYOffset, self.diceSideLength, self.diceSideLength, (0, 0, 0), scalable=(True, "center"), borderRadius=12, thickness=3)
        self.yellowDiceBorder = uiRect(self.diceDistance * 3/2 + self.diceSideLength, self.diceDistance + self.yellowYOffset, self.diceSideLength, self.diceSideLength, (0, 0, 0), scalable=(True, "center"), borderRadius=12, thickness=3)
        self.redDice.draw(screen)
        self.redDiceBorder.draw(screen)
        self.yellowDice.draw(screen)
        self.yellowDiceBorder.draw(screen)

        # draw dice pips
        self.draw_dice_pips(screen, self.redDice.rect, self.dicePipSpacing, self.dicePipSize, self.currentRedValue, diceYellowColor)
        self.draw_dice_pips(screen, self.yellowDice.rect, self.dicePipSpacing, self.dicePipSize, self.currentYellowValue, diceRedColor)

        if self.paused:
            # Draw pause overlay
            pauseRect = uiRect(0, 0, screen.get_width(), screen.get_height(), (0, 0, 0), scalable=(False, None), alpha=pauseAlpha)
            pauseRect.draw(screen)

            # Draw quit button and text
            self.continueButton.draw(screen)
            self.mainMenuButton.draw(screen)
            self.quitButton.draw(screen)

    def saveGame(self):
        """Save current game state to JSON file"""
        save_data = {
            "tiles": [(t.x, t.y, t.resource, t.number) for t in self.tileList],
            "settlements": self.settlements,
            "roads": self.roads,
            "currentPlayer": self.currentPlayer
        }
        with open("save.json", "w") as f:
            json.dump(save_data, f)
    
    def draw_dice_pips(self, screen, diceRect, pipSpacing, pipSize, value, pipColor):
        """Draw pips on a dice based on its value"""

        DICE_PIP_POSITIONS = {
            1: [(0, 0)],
            2: [(-1, -1), (1, 1)],
            3: [(-1, -1), (0, 0), (1, 1)],
            4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
            5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
            6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]
        }

        center_x, center_y = diceRect.center
        positions = DICE_PIP_POSITIONS[value]
        
        for i, (offset_x, offset_y) in enumerate(positions):
            pip_center = (
                center_x + offset_x * pipSpacing,
                center_y + offset_y * pipSpacing
            )
            # Use hexagon for single pip (the 1), circles for everything else
            if value == 1:
                points = []
                for i in range(6):
                    angle = math.radians(60 * i + 30)
                    x = pip_center[0] + pipSize * 3/2 * math.cos(angle)
                    y = pip_center[1] + pipSize * 3/2 * math.sin(angle)
                    points.append((x, y))
                pygame.draw.polygon(screen, pipColor, points)
            else:
                pygame.draw.circle(screen, pipColor, pip_center, pipSize)
            
    def findClosestIntersection(self, mouseWorldPos):
        """Find the closest intersection to the mouse position"""
        closestCorner = None
        closestRoad = None
        minDistance = float("inf")

        for pos in self.settlements:
            cornerWorld = pygame.Vector2(
                pos[0] * hexSize * hexWidthRatio,
                pos[1] * hexSize * hexHeightRatio
            )
            dist = mouseWorldPos.distance_to(cornerWorld)
            if dist < minDistance and dist < hexSize * 0.2:
                minDistance = dist
                closestCorner = pos
        
        for pos in self.roads:
            road_world = pygame.Vector2(
                pos[0] * hexSize * hexWidthRatio,
                pos[1] * hexSize * hexHeightRatio
            )
            dist = mouseWorldPos.distance_to(road_world)
            if dist < minDistance and dist < hexSize * 0.2:
                minDistance = dist
                closestRoad = pos
        return closestCorner, closestRoad

    def validSettlement(self, position):
        """Check if a settlement position is valid (not adjacent to existing settlements)"""
        if position[2] is not None:  # Already has a settlement
            return False
        
        # Check distance to all existing settlements
        for settlement in self.settlements:
            if settlement[2] is not None:  # Only check placed settlements
                # Calculate distance between positions
                dx = position[0] - settlement[0]
                dy = position[1] - settlement[1]
                distance = (dx**2 + dy**2) ** (1/2) # Pythagorean theorem
                
                # In Catan, settlements must be at least ~1.33 units apart in this coordinate system
                if distance < 1.33:
                    return False
        
        return True