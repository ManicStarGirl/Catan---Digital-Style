from config import settings, numberSize, panSpeed, hexSize, hexWidthRatio, hexHeightRatio, minZoom, maxZoom, textSize
from screens import Screen
from ui import UIRect, hex
from hex_grid import newTiles
from coordinates import hexRound, pixelToFractionalHex, getSettlementPositions, getRoadPositions
import pygame, json, math, random

class GameScreen(Screen):
    """Main game screen for playing Catan"""
    def __init__(self, screenManager, screen, tileList=None, settlements=None, roads=None, currentPlayer=None):
        super().__init__(screenManager, screen)
        # Generate the initial hex map (a spiral/ring-based board of `numberOfRings` rings)
        self.tileList = tileList if tileList is not None else newTiles(settings.numberOfRings)
        self.settlements = settlements if settlements is not None else getSettlementPositions(self.tileList)
        self.roads = roads if roads is not None else getRoadPositions(self.tileList)
        # List of player colors and current player tracking
        self.playerList = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (0, 0, 0), (255, 255, 255)]
        self.currentPlayer = currentPlayer if currentPlayer is not None else (self.playerList[0], 0)

    def OnEnter(self):
        super().OnEnter()
        self.paused = False
        self.dragging = False
        # Center the game board on screen
        self.gamePos = pygame.Vector2(self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.mouseDownPos = None
        self.offsetX = 0
        self.offsetY = 0
        self.gameScale = settings.gameScale
        self.numberSize = numberSize

        self.diceSideLength = self.screen.get_width() / 25
        self.diceDistance = self.screen.get_width() / 24 - self.diceSideLength / 2
        self.dicePipSize = self.diceSideLength / 10
        self.dicePipSpacing = self.diceSideLength / 5

        # Recalculate buttons with current screen size
        self.continueButton = UIRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height() * 3/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonColor, "Continue", self.fontSize, (True, "center"), borderRadius=10)
        self.mainMenuButton = UIRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height() * 4/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonColor, "Main Menu", self.fontSize, (True, "center"), borderRadius=10)
        self.quitButton = UIRect(self.screen.get_width()/2 - self.buttonWidth/2, self.screen.get_height() * 5/8 - self.buttonHeight/2, self.buttonWidth, self.buttonHeight, settings.buttonColor, "Quit", self.fontSize, (True, "center"), borderRadius=10)
        self.endTurnButton = UIRect(self.screen.get_width() * 15/16 - self.buttonWidth/8, self.screen.get_height()/16 - self.buttonHeight/4, self.buttonWidth/4, self.buttonHeight/2, settings.buttonColor, "End Turn", self.fontSize/2, (True, "center"), borderRadius=5)
        self.endTurnBorder = UIRect(self.screen.get_width() * 15/16 - self.buttonWidth/8, self.screen.get_height()/16 - self.buttonHeight/4, self.buttonWidth/4, self.buttonHeight/2, self.currentPlayer[0], scalable=(True, "center"), borderRadius=5, thickness=6)
        self.redDice = UIRect(self.diceDistance, self.diceDistance + self.redYOffset, self.diceSideLength, self.diceSideLength, settings.diceRedColor, scalable=(True, "center"), borderRadius=12)
        self.redDiceBorder = UIRect(self.diceDistance, self.diceDistance + self.redYOffset, self.diceSideLength, self.diceSideLength, (0, 0, 0), scalable=(True, "center"), borderRadius=12, thickness=3)
        self.yellowDice = UIRect(self.diceDistance * 3/2 + self.diceSideLength, self.diceDistance + self.yellowYOffset, self.diceSideLength, self.diceSideLength, settings.diceYellowColor, scalable=(True, "center"), borderRadius=12)
        self.yellowDiceBorder = UIRect(self.diceDistance * 3/2 + self.diceSideLength, self.diceDistance + self.yellowYOffset, self.diceSideLength, self.diceSideLength, (0, 0, 0), scalable=(True, "center"), borderRadius=12, thickness=3)

    def OnExit(self):
        pass

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
                        self.gameScale *= settings.zoomFactor
                        if self.gameScale > maxZoom:
                            self.gameScale = maxZoom
                    else:
                        self.gameScale /= settings.zoomFactor
                        if self.gameScale < minZoom:
                            self.gameScale = minZoom

                    # Re-anchor gamePos so the same world point stays under the mouse after zooming.
                    self.gamePos = mousePos - worldPos * self.gameScale

                    # Number tokens are drawn from a font, so their size must be regenerated whenever zoom level changes
                    self.numberSize = pygame.font.Font('assets/fonts/MinionPro-BoldCn.otf', round(textSize * self.gameScale))

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mousePos = pygame.mouse.get_pos()
                    mouseWorldPos = (pygame.Vector2(mousePos) - self.gamePos) / self.gameScale
                    closestCorner, closestRoad = self.findClosestIntersection(mouseWorldPos)
                    if event.button == 1:
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
                                        pos[2] = self.currentPlayer[0]
                                        break
                        elif closestRoad:
                            # Find and update the road position
                            for pos in self.roads:
                                if pos[0] == closestRoad[0] and pos[1] == closestRoad[1]:
                                    if self.validRoad(pos):
                                        pos[3] = self.currentPlayer[0]
                                        break
                            
                        # Start a drag: remember the offset between the mouse and gamePos
                        self.mouseDownPos = event.pos
                        self.offsetX = self.gamePos.x - self.mouseDownPos[0]
                        self.offsetY = self.gamePos.y - self.mouseDownPos[1]
                        self.dragging = True
                    elif event.button == 3:  # Right click
                        if self.endTurnButton.isClicked(mousePos):
                            self.currentPlayer = (self.playerList[(self.currentPlayer[1] - 1) % len(self.playerList)], self.currentPlayer[1] - 1)
                        mousePos = pygame.mouse.get_pos()
                        mouseWorldPos = (pygame.Vector2(mousePos) - self.gamePos) / self.gameScale
                        closestCorner, closestRoad = self.findClosestIntersection(mouseWorldPos)
                        if closestCorner:
                            # Find and update the settlement position
                            for pos in self.settlements:
                                if pos[0] == closestCorner[0] and pos[1] == closestCorner[1]:
                                    if pos[2] == self.currentPlayer[0]:
                                        pos[2] = None
                                        break
                        elif closestRoad:
                            # Find and update the road position
                            for pos in self.roads:
                                if pos[0] == closestRoad[0] and pos[1] == closestRoad[1]:
                                    if pos[3] == self.currentPlayer[0]:
                                        pos[3] = None
                                        break
                        

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        mouseX, mouseY = event.pos
                        self.gamePos.x = mouseX + self.offsetX
                        self.gamePos.y = mouseY + self.offsetY

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False
                        self.mouseDownPos = None
            else:
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
        
        if not self.paused:
            if self.isRolling:
                progress = (currentTime - self.rollStartTime) / self.rollDuration
                self.redYOffset = math.sin(progress * math.pi * 2 * self.redNumShakes) * self.redShakeOffset
                self.yellowYOffset = math.sin(progress * math.pi * 2 * self.yellowNumShakes) * self.yellowShakeOffset
                # Check if rolling duration has expired
                if currentTime - self.rollStartTime > self.rollDuration:
                    self.isRolling = False
                    self.currentRedValue = random.choice(self.diceList)
                    self.currentYellowValue = random.choice(self.diceList)
                # Shuffle face values quickly during the roll interval
                elif currentTime - self.lastShuffleTime > self.shuffleDelay:
                    self.currentRedValue = random.choice([n for n in self.diceList if n != self.currentRedValue])
                    self.currentYellowValue = random.choice([n for n in self.diceList if n != self.currentYellowValue])
                    self.lastShuffleTime = currentTime
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

        for settlement in self.settlements:
            if settlement[2] is not None:
                cornerWorld = pygame.Vector2(
                    settlement[0] * hexSize * hexWidthRatio,
                    settlement[1] * hexSize * hexHeightRatio
                )
                screenPos = cornerWorld * self.gameScale + self.gamePos
                # Scale the house shape (base size around 20x20 pixels, scaled by gameScale)
                baseSize = 14 * self.gameScale
                offsetX = screenPos.x - baseSize / 2
                offsetY = screenPos.y - baseSize / 2

                housePoints = [
                    (offsetX + 1 * baseSize/6, offsetY + 6 * baseSize/6),
                    (offsetX + 1 * baseSize/6, offsetY + 3 * baseSize/6),
                    (offsetX + 0 * baseSize/6, offsetY + 3 * baseSize/6),
                    (offsetX + 3 * baseSize/6, offsetY + 0 * baseSize/6),
                    (offsetX + 6 * baseSize/6, offsetY + 3 * baseSize/6),
                    (offsetX + 5 * baseSize/6, offsetY + 3 * baseSize/6),
                    (offsetX + 5 * baseSize/6, offsetY + 6 * baseSize/6),
                ]
                
                pygame.draw.polygon(screen, settlement[2], housePoints)
        for road in self.roads:
            if road[3] is not None:
                cornerWorld = pygame.Vector2(
                    road[0] * hexSize * hexWidthRatio,
                    road[1] * hexSize * hexHeightRatio
                )
                screenPos = cornerWorld * self.gameScale + self.gamePos
                roadLength = 20 * self.gameScale
                roadWidth = 4 * self.gameScale

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
                    baseSize = 14 * self.gameScale
                    offsetX = screenPos.x - baseSize / 2
                    offsetY = screenPos.y - baseSize / 2

                    settlementPoints = [
                        (offsetX + 1 * baseSize/6, offsetY + 6 * baseSize/6),
                        (offsetX + 1 * baseSize/6, offsetY + 3 * baseSize/6),
                        (offsetX + 0 * baseSize/6, offsetY + 3 * baseSize/6),
                        (offsetX + 3 * baseSize/6, offsetY + 0 * baseSize/6),
                        (offsetX + 6 * baseSize/6, offsetY + 3 * baseSize/6),
                        (offsetX + 5 * baseSize/6, offsetY + 3 * baseSize/6),
                        (offsetX + 5 * baseSize/6, offsetY + 6 * baseSize/6),
                    ]

                    cityPoints = [
                        (offsetX + 0 * baseSize/6, offsetY + 6 * baseSize/6),
                        (offsetX + 0 * baseSize/6, offsetY + 2 * baseSize/6),
                        (offsetX + 2 * baseSize/6, offsetY + 0 * baseSize/6),
                        (offsetX + 4 * baseSize/6, offsetY + 2 * baseSize/6),
                        (offsetX + 4 * baseSize/6, offsetY + 3 * baseSize/6),
                        (offsetX + 6 * baseSize/6, offsetY + 3 * baseSize/6),
                        (offsetX + 6 * baseSize/6, offsetY + 6 * baseSize/6),
                    ]
                    
                    self.drawTransparentPolygon(screen, settlementPoints, self.currentPlayer[0], settings.hoverAlpha)

            # Draw road preview if close enough
            if closestRoad:
                if self.validRoad(closestRoad):
                    roadWorld = pygame.Vector2(
                        closestRoad[0] * hexSize * hexWidthRatio,
                        closestRoad[1] * hexSize * hexHeightRatio
                    )
                    screenPos = roadWorld * self.gameScale + self.gamePos
                    roadLength = 20 * self.gameScale
                    roadWidth = 4 * self.gameScale

                    angleRad = math.radians(closestRoad[2])

                    # Direction vector along the road
                    dirX = math.cos(angleRad)
                    dirY = math.sin(angleRad)

                    # Perpendicular vector (for width)
                    perpX = -dirY
                    perpY = dirX
                    
                    boatPoints = [
                        (offsetX + 0   * baseSize/6, offsetY + 4 * baseSize/6),
                        (offsetX + 3   * baseSize/6, offsetY + 4 * baseSize/6),
                        (offsetX + 3   * baseSize/6, offsetY + 3 * baseSize/6),
                        (offsetX + 1.5 * baseSize/6, offsetY + 3 * baseSize/6),
                        (offsetX + 3.5 * baseSize/6, offsetY + 0 * baseSize/6),
                        (offsetX + 3.5 * baseSize/6, offsetY + 4 * baseSize/6),
                        (offsetX + 6   * baseSize/6, offsetY + 4 * baseSize/6),
                        (offsetX + 5   * baseSize/6, offsetY + 5 * baseSize/6),
                        (offsetX + 1   * baseSize/6, offsetY + 5 * baseSize/6),
                    ]

                    # Calculate 4 corners
                    roadPoints = [
                        (screenPos.x - dirX * roadLength/2 + perpX * roadWidth/2,
                        screenPos.y - dirY * roadLength/2 + perpY * roadWidth/2),
                        (screenPos.x + dirX * roadLength/2 + perpX * roadWidth/2,
                        screenPos.y + dirY * roadLength/2 + perpY * roadWidth/2),
                        (screenPos.x + dirX * roadLength/2 - perpX * roadWidth/2,
                        screenPos.y + dirY * roadLength/2 - perpY * roadWidth/2),
                        (screenPos.x - dirX * roadLength/2 - perpX * roadWidth/2,
                        screenPos.y - dirY * roadLength/2 - perpY * roadWidth/2)
                    ]

                    self.drawTransparentPolygon(screen, roadPoints, self.currentPlayer[0], settings.hoverAlpha)
            
        # Draw end turn button
        self.endTurnBorder = UIRect(self.screen.get_width() * 15/16 - self.buttonWidth/8, self.screen.get_height()/16 - self.buttonHeight/4, self.buttonWidth/4, self.buttonHeight/2, self.currentPlayer[0], scalable=(True, "center"), borderRadius=5, thickness=6)
        self.endTurnButton.draw(screen)
        self.endTurnBorder.draw(screen)
        
        # Draw dice buttons
        self.redDice = UIRect(self.diceDistance, self.diceDistance + self.redYOffset, self.diceSideLength, self.diceSideLength, settings.diceRedColor, scalable=(True, "center"), borderRadius=12)
        self.yellowDice = UIRect(self.diceDistance * 3/2 + self.diceSideLength, self.diceDistance + self.yellowYOffset, self.diceSideLength, self.diceSideLength, settings.diceYellowColor, scalable=(True, "center"), borderRadius=12)
        self.redDiceBorder = UIRect(self.diceDistance, self.diceDistance + self.redYOffset, self.diceSideLength, self.diceSideLength, (0, 0, 0), scalable=(True, "center"), borderRadius=12, thickness=3)
        self.yellowDiceBorder = UIRect(self.diceDistance * 3/2 + self.diceSideLength, self.diceDistance + self.yellowYOffset, self.diceSideLength, self.diceSideLength, (0, 0, 0), scalable=(True, "center"), borderRadius=12, thickness=3)
        self.redDice.draw(screen)
        self.redDiceBorder.draw(screen)
        self.yellowDice.draw(screen)
        self.yellowDiceBorder.draw(screen)

        # draw dice pips
        self.drawDicePips(screen, self.redDice.rect, self.dicePipSpacing, self.dicePipSize, self.currentRedValue, settings.diceYellowColor)
        self.drawDicePips(screen, self.yellowDice.rect, self.dicePipSpacing, self.dicePipSize, self.currentYellowValue, settings.diceRedColor)

        if self.paused:
            # Draw pause overlay
            pauseRect = UIRect(0, 0, screen.get_width(), screen.get_height(), (0, 0, 0), scalable=(False, None), alpha=settings.pauseAlpha)
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
    
    def drawDicePips(self, screen, diceRect, pipSpacing, pipSize, value, pipColor):
        """Draw pips on a dice based on its value"""

        dicePipPositions = {
            1: [(0, 0)],
            2: [(-1, -1), (1, 1)],
            3: [(-1, -1), (0, 0), (1, 1)],
            4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
            5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
            6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]
        }

        centerX, centerY = diceRect.center
        positions = dicePipPositions[value]
        
        for i, (offsetX, offsetY) in enumerate(positions):
            pipCenter = (
                centerX + offsetX * pipSpacing,
                centerY + offsetY * pipSpacing
            )
            # Use hexagon for single pip (the 1), circles for everything else
            if value == 1:
                points = []
                for i in range(6):
                    angle = math.radians(60 * i + 30)
                    x = pipCenter[0] + pipSize * 3/2 * math.cos(angle)
                    y = pipCenter[1] + pipSize * 3/2 * math.sin(angle)
                    points.append((x, y))
                pygame.draw.polygon(screen, pipColor, points)
            else:
                pygame.draw.circle(screen, pipColor, pipCenter, pipSize)
            
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
        """Check if a settlement position is valid according to Catan rules.
        
        Rules:
        1. Cannot place on a spot that already has a settlement
        2. Must be at least 1.33 units away from any existing settlement (distance rule, 2 spaces away)
        3. During initial placement (< 2 settlements): can place anywhere valid
        4. After initial placement: must be adjacent to your own road network
        
        Args:
            position: Tuple (x, y, player_color) representing the settlement position
            
        Returns:
            bool: True if settlement placement is valid, False otherwise
        """
        if position[2] is not None:  # Already has a settlement
            return False
        
        # Check distance to all existing settlements (Catan distance rule)
        for settlement in self.settlements:
            if settlement[2] is not None:  # Only check placed settlements
                # Calculate distance between positions using Pythagorean theorem
                dx = position[0] - settlement[0]
                dy = position[1] - settlement[1]
                distance = (dx**2 + dy**2) ** (1/2)
                
                # In Catan, settlements must be at least ~1.33 units apart in this coordinate system
                if distance < 1.33:
                    return False

        # Count how many settlements the current player has placed
        playerSettlements = 0
        for settlement in self.settlements:
            if settlement[2] == self.currentPlayer[0]:
                playerSettlements += 1

        # During initial placement phase (first 2 settlements), free placement is allowed
        if playerSettlements < 2:
            return True

        # After initial placement, settlements must be adjacent to your road network
        for road in self.roads:
            if road[3] == self.currentPlayer[0]:  # Only check your own roads
                dx = position[0] - road[0]
                dy = position[1] - road[1]
                distance = (dx**2 + dy**2) ** (1/2)
                
                # Settlement is valid if it's adjacent to one of your roads
                if distance < 0.7:
                    return True
                    
        # If not adjacent to any of your roads, placement is invalid
        return False

    def validRoad(self, position):
        """Check if a road position is valid according to Catan rules.
        
        Rules:
        1. Cannot place on a spot that already has a road
        2. Must be adjacent to your own settlements or existing roads
        3. Road chaining: roads can connect to form a continuous network
        
        Args:
            position: Tuple (x, y, angle, player_color) representing the road position
            
        Returns:
            bool: True if road placement is valid, False otherwise
        """
        if position[3] is not None:  # Already has a road
            return False
        
        # Extract road coordinates (angle not needed for distance checking)
        roadX, roadY = position[0], position[1]

        # Check if road is adjacent to your own settlements
        for settlement in self.settlements:
            if settlement[2] == self.currentPlayer[0]:  # Only check your own settlements
                # Calculate distance between road and settlement
                dx = roadX - settlement[0]
                dy = roadY - settlement[1]
                distance = (dx**2 + dy**2) ** (1/2)
                
                # Roads should be adjacent to settlements (roughly 0.67 units in this coordinate system)
                if distance < 0.7:
                    return True
        
        # Check if road can connect to your existing roads (road chaining)
        for road in self.roads:
            if road[3] == self.currentPlayer[0]:  # Only check your own roads
                dx = roadX - road[0]
                dy = roadY - road[1]
                distance = (dx**2 + dy**2) ** (1/2)
                
                # Roads can connect to existing roads at specific distances
                if distance < 1:  # Most connections are within this range
                    return True
                elif distance == 1:  # Special case: some valid connections are exactly at distance 1
                    # Additional heuristic: Y coordinates must differ to filter false positives
                    if roadY != road[1]:
                        return True

        return False

    def drawTransparentPolygon(self, screen, corners, color, alpha):
        """
        Draw a polygon with transparency on a surface and blit it to the screen.
        
        Args:
            screen: The pygame screen to blit to
            corners: List of (x, y) tuples defining the polygon corners
            color: RGB tuple (r, g, b) for the polygon color
            alpha: Alpha value (0-255) for transparency
        """
        # Calculate bounding box for the transparent surface
        min_x = min(corner[0] for corner in corners)
        max_x = max(corner[0] for corner in corners)
        min_y = min(corner[1] for corner in corners)
        max_y = max(corner[1] for corner in corners)
        
        # Create transparent surface sized to fit the polygon
        surfaceWidth = int(max_x - min_x) + 2
        surfaceHeight = int(max_y - min_y) + 2
        transSurface = pygame.Surface((surfaceWidth, surfaceHeight), pygame.SRCALPHA)
        
        # Adjust corners to be relative to the surface
        adjustedCorners = [
            (corner[0] - min_x + 1, corner[1] - min_y + 1)
            for corner in corners
        ]
        
        # Draw the polygon with transparency on the surface
        pygame.draw.polygon(transSurface, (*color, alpha), adjustedCorners)
        
        # Blit the transparent surface to the screen
        screen.blit(transSurface, (min_x - 1, min_y - 1))