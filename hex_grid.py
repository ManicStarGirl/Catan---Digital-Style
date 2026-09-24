import random
from config import settings, numberList, colorList, noNumberTiles
from ui import hex

# Module for generating hexagonal grid layouts and tile configurations

# Hex directions for adjacent tile calculations
HEX_DIRECTIONS = [(1, 1), (1, -1), (0, -2), (-1, -1), (-1, 1), (0, 2)]

def hexRing(center, radius):
    """
    Return the coordinates of every hex cell forming a ring at a given
    radius around a center hex, using "doubled" hex coordinates.

    Args:
        center (tuple[int, int]): (x, y) doubled coordinates of the
            center hex.
        radius (int): Ring distance from the center, in hex steps.
            radius == 0 refers to just the center hex itself.

    Returns:
        list[tuple[int, int]]: The (x, y) doubled coordinates of all
        hexes exactly `radius` steps from `center`, ordered by walking
        around the ring one edge at a time. Returns an empty list when
        radius == 0 (a ring of radius 0 has no surrounding cells).
    """
    if radius == 0:
        return []

    cx, cy = center

    x = cx + HEX_DIRECTIONS[0][0] * radius
    y = cy + HEX_DIRECTIONS[0][1] * radius

    walkDirs = HEX_DIRECTIONS[2:] + HEX_DIRECTIONS[:2]

    results = []
    for dx, dy in walkDirs:
        for _ in range(radius):
            results.append((x, y))
            x += dx
            y += dy

    return results

def hexGrid(center, numRings):
    """
    Return the coordinates of every hex cell in a hexagonal grid made up
    of concentric rings around a center hex.

    Args:
        center (tuple[int, int]): (x, y) coordinates of the
            center hex.
        numRings (int): Number of rings to include around the center.
            0 returns just the center hex; 1 returns the center plus
            its immediate 6 neighbors; and so on.

    Returns:
        list[tuple[int, int]]: The (x, y) coordinates of every
        hex in the grid, starting with the center and then followed by
        each successive ring (radius 1, 2, ..., numRings), each ring's
        cells ordered by walking around its perimeter.
    """
    tiles = [center]

    for r in range(1, numRings + 1):
        tiles.extend(hexRing(center, r))

    return tiles

def newTiles(numberOfRings):
    """
    Generate a randomized set of hex tiles for a board built from
    concentric rings around the origin, assigning a random resource
    color and number to every tile.

    Args:
        numberOfRings (int): Number of rings to generate around the center hex.

    Returns:
        dict: Dictionary mapping (x, y) coordinates to hex objects.
    """
    tileList = {}

    for tile in hexGrid((0, 0), numberOfRings):
        tileX, tileY = tile[0], tile[1]
        color = random.choice(colorList) #if tile != (0, 0) else "desert"
        tileList[tile] = hex(tileX, tileY, color, "?" if color == "fog" else random.choice(numberList) if color not in noNumberTiles else None)
    return tileList

def randomizeBoard(board):
    """
    Randomize tile colors and numbers on an existing board while preventing
    adjacent 6/8 numbers if the red number percentage is below 38%.

    Args:
        board: Dictionary of hex objects keyed by position.

    Returns:
        dict: New randomized board configuration.
    """
    totalTiles = []
    numberList = []
    tilePositions = []
    totalNumbers = 0
    totalRedNumbers = 0

    for tile in board:
        totalTiles.append(tile.color)
        if tile.number is not None:
            numberList.append(tile.number)
            totalNumbers += 1
            if tile.number in [6, 8]:
                totalRedNumbers += 1
        tilePositions.append((tile.x, tile.y))
    
    redNumbersPercent = totalRedNumbers / totalNumbers * 100

    def hasAdjacentRedNumber(pos, tileList):
        """Check if any adjacent tile has a 6 or 8"""
        for dx, dy in HEX_DIRECTIONS:
            neighbor = (pos[0] + dx, pos[1] + dy)
            if neighbor in tileList:
                neighborNumber = tileList[neighbor].number
                if neighborNumber in [6, 8]:
                    return True
        return False

    if redNumbersPercent < 38:
        maxRetries = 100
        for _ in range(maxRetries):
            tileList = {}
            tilesCopy = totalTiles.copy()
            numbersCopy = numberList.copy()

            for position in tilePositions:
                color = random.choice(tilesCopy)
                tilesCopy.remove(color)
                if color == "desert":
                    number = None
                else:
                    attempts = 0
                    while attempts < 100:
                        number = random.choice(numbersCopy)
                        if number in [6, 8] and hasAdjacentRedNumber(position, tileList):
                            attempts += 1
                            continue
                        break
                    if attempts >= 100:
                        break
                    numbersCopy.remove(number)
                
                tileList[position] = hex(position[0], position[1], color, number)
            else:
                return tileList
        
        print(f"Failed to generate valid board after {maxRetries} attempts")
        return tileList
    else:
        tileList = {}
        tilesCopy = totalTiles.copy()
        numbersCopy = numberList.copy()
        for position in tilePositions:
            color = random.choice(tilesCopy)
            tilesCopy.remove(color)
            if color == "desert":
                number = None
            else:
                number = random.choice(numbersCopy)
                numbersCopy.remove(number)
            tileList[position] = hex(position[0], position[1], color, number)
        return tileList