import random, math
from config import desert, colorList, numberList, noNumberTiles, fog
from ui import hex

# Module for generating hexagonal grid layouts and tile configurations

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
    # The six neighbor directions in doubled hex coordinates, ordered
    # so that consecutive entries correspond to consecutive edges of
    # the ring (i.e. turning by one hex-side each time).
    HEX_DIRECTIONS = [(1, 1), (1, -1), (0, -2), (-1, -1), (-1, 1), (0, 2)]

    # A ring of radius 0 is just the center itself, and the walk below
    # isn't meaningful for it, so bail out early.
    if radius == 0:
        return []

    cx, cy = center

    # Start at the hex `radius` steps away from center in the first
    # direction (HEX_DIRECTIONS[0]). This is the "top" corner of the
    # ring and the starting point for the walk around its perimeter.
    x = cx + HEX_DIRECTIONS[0][0] * radius
    y = cy + HEX_DIRECTIONS[0][1] * radius

    # Reorder the directions so the walk starts from the direction
    # "two steps around" from the starting corner. Each direction is
    # then used to walk along one edge of the ring toward the next
    # corner.
    walkDirs = HEX_DIRECTIONS[2:] + HEX_DIRECTIONS[:2]

    results = []
    for dx, dy in walkDirs:
        # Walk `radius` hexes along the current edge, recording each
        # cell visited before moving to the next edge/direction.
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
    # The grid always includes the center hex itself.
    tiles = [center]

    # Build the grid outward one ring at a time, from radius 1 up to
    # numRings, appending each ring's cells to the result.
    for r in range(1, numRings + 1):
        tiles.extend(hexRing(center, r))

    return tiles

def newTiles(rings):
    """
    Generate a randomized set of hex tiles for a board built from
    concentric rings around the origin, assigning a random resource
    color and number to every tile except the center, which is always
    the desert.

    Relies on the following names being defined elsewhere in scope:
        random (module): A random-number module
            used to pick colors/numbers via `random.choice`.
        colorList (list): Pool of possible resource colors to assign
            to non-desert tiles.
        numberList (list): Pool of possible numbers (e.g. dice-roll
            values) to assign to non-desert tiles.
        desert (Any): The color/type value used for the center tile.

    Args:
        rings (int): Number of rings to generate around the center
            hex, passed straight through to hexGrid.

    Returns:
        list[tuple[tuple[int, int], Any, Any]]: One entry per tile in
        the grid, each a tuple of:
            - (x, y): the tile's doubled hex coordinates,
            - color: a random entry from colorList, or `desert` for
              the center tile,
            - number: a random entry from numberList, or None for the
              center tile.
    """
    tileList = []

    # Walk every hex position in the grid (center + all requested rings).
    for tile in hexGrid((0, 0), rings):
        # Center tile is always desert; every other tile gets a random resource color. 
        color = random.choice(colorList) #if tile != (0, 0) else desert
        # Desert, sea, and deep sea tiles don't get a number token.
        # (Could have more tiles if noNumberTiles is edited.)
        tileList.append(hex(tile[0], tile[1], color, "?" if color == fog else random.choice(numberList) if color not in noNumberTiles else None))
    return tileList