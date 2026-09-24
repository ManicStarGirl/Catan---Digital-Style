class Player:
    """Represents a player in the Catan game"""
    def __init__(self):
        # Initialize player's resource inventory
        self.resources = {
            "wood": 0,
            "brick": 0,
            "sheep": 0,
            "wheat": 0,
            "ore": 0
        }
        # Initialize available buildings (remaining counts)
        self.buildings = {
            "settlements": 5,
            "cities": 4,
            "roads": 15,
            "boats": 15
        }
        self.victoryPoints = 0
        self.developmentCardPoints = 0
        self.longestRoad = False
        self.largestArmy = False
    
    def getVictoryPoints(self):
        """Calculate total victory points from all sources"""
        # settlements (1 VP each), cities (2 VP each), longest road (2 VP), largest army (2 VP), development cards (1 VP sometimes)
        placedSettlements = 5 - self.buildings["settlements"]
        placedCities = 4 - self.buildings["cities"]
        self.victoryPoints = placedSettlements + (placedCities * 2) + (2 if self.longestRoad else 0) + (2 if self.largestArmy else 0) + self.developmentCardPoints
        return self.victoryPoints