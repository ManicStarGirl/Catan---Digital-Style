def pixelToFractionalHex(gamePos, coord, size):
    """
    Convert a pixel/screen coordinate into fractional axial hex
    coordinates (q, r), i.e. the "pointy-top" axial hex position that
    the given pixel falls on, before any rounding to a whole hex cell.

    This is the inverse of the usual axial-to-pixel conversion, using
    the standard formulas for pointy-topped hexagons.

    Relies on the following names being defined elsewhere in scope:
        gamePos (tuple/pygame.Vector2 or similar): Pixel offset of the
            game board's origin on screen, subtracted out so the
            coordinate is relative to the board rather than the
            window.

    Args:
        coord (tuple[float, float]): The (x, y) pixel/screen
            coordinate to convert (e.g. a mouse position).
        size (float): The size (radius) of a hex tile, in pixels,
            matching whatever scale the board was drawn at.

    Returns:
        tuple[float, float]: The fractional axial hex coordinates
        (q, r) corresponding to `coord`. These are not yet rounded to
        an actual hex cell — the caller is expected to round q, r
        (and the implied third cube coordinate) to get the nearest
        whole hex.
    """
    # Shift the pixel coordinate so it's relative to the board's
    # on-screen origin rather than the window's origin.
    x, y = coord[0] - gamePos[0], coord[1] - gamePos[1]

    # Apply the standard pointy-top axial hex "pixel to hex" formulas
    # to recover fractional axial coordinates (q, r) from the pixel
    # position.
    q = (2/3 * x) / size
    r = (-1/3 * x + (3)**(1/2)/3 * y) / size

    return (q, r)

def hexRound(coords):
    """
    Round fractional axial hex coordinates to the nearest actual hex
    cell, using cube-coordinate rounding to guarantee a consistent
    result, then convert back to this project's doubled coordinate
    system.

    Naively rounding q and r independently can land on a cell whose
    implied cube coordinates don't satisfy q + r + s == 0, which would
    produce an invalid/inconsistent hex. Converting to cube
    coordinates, rounding all three, and correcting the component with
    the largest rounding error avoids that problem.

    Args:
        coords (tuple[float, float]): Fractional axial hex coordinates
            (q, r), meant to be used with the output of
            pixelToFractionalHex.

    Returns:
        tuple[int, int]: The rounded hex position expressed in this
        project's doubled coordinate system, as (x, y) where x is the
        rounded axial q and y = 2*r + q.
    """
    fracQ, fracR = coords

    # Calculate 3D cube coordinates
    fracS = -fracQ - fracR

    # Round each coordinate to the nearest integer
    q = round(fracQ)
    r = round(fracR)
    s = round(fracS)

    # Measure the difference between float and rounded integer
    q_diff = abs(q - fracQ)
    r_diff = abs(r - fracR)
    s_diff = abs(s - fracS)

    # Reset the coordinate with the largest difference to satisfy q + r + s = 0.
    # Whichever of q, r, s was rounded the most inaccurately gets
    # recomputed from the other two (which were rounded more reliably),
    # restoring the cube-coordinate invariant.
    if (q_diff > r_diff and q_diff > s_diff):
        q = -r - s
    elif (r_diff > s_diff):
        r = -q - s
    else:
        s = -q - r

    # Convert the rounded axial coordinates (q, r) back into this
    # project's doubled coordinate system, matching the format used by
    # hexRing/hexGrid/drawHexagon elsewhere.
    return q, 2 * r + q

def getSettlementPositions(tileList):
    """Calculate all valid settlement positions (corners) for a given tile list"""
    positions = set()
    for tile in tileList:
        for dx, dy in [(1/3, -1), (-1/3, -1), (-2/3, 0), (2/3, 0), (1/3, 1), (-1/3, 1)]:
            x = round(tile.x + dx, 2)
            y = round(tile.y + dy, 2)
            positions.add((x, y, None))
    return [list(pos) for pos in positions]

def getRoadPositions(tileList):
    """Calculate all valid road positions (edges) for a given tile list"""
    positions = set()
    for tile in tileList:
        for dx, dy, angle in [(0, -1, 0), (0.5, -0.5, 60), (0.5, 0.5, 120), (0, 1, 0), (-0.5, 0.5, 60), (-0.5, -0.5, 120)]:
            x = round(tile.x + dx, 2)
            y = round(tile.y + dy, 2)
            positions.add((x, y, angle, None))
    return [list(pos) for pos in positions]