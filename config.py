import pygame, json, os

pygame.init()

DEFAULT_CONFIG = {
    # --- Hex grid geometry ---
    "hexSize": 40,                 # radius/size of a single hex tile
    "defaultRings": 2,             # starting number of rings in the hex map
    "hexWidthRatio": 3/2,          # width ratio for hex tiles
    "hexHeightRatio": 3**(1/2)/2,  # height ratio for hex tiles

    # --- Camera / view controls ---
    "gameScale": 1.0,    # current zoom level
    "zoomFactor": 1.15,  # multiplier applied per zoom step
    "minZoom": 0.05,     # zoom bounds
    "maxZoom": 15,
    "panSpeed": 450,     # camera pan speed (units/sec)

    # --- App / performance settings ---
    "fpsLimit": 60,       # maximum frames per second
    "dragThreshold": 12,  # minimum drag distance before registering as a drag (pixels)

    # --- UI ---
    "selectorColor": (255, 255, 255),    # tile selection highlight color
    "selectorAlpha": 85,                 # tile selection highlight (color, transparency)
    "numberTileColor": (212, 205, 142),  # background color for number tokens
    "uiScale": 1.0,                      # UI scale factor
    "pauseAlpha": 128,                   # transparency for pause overlay (out of 255)
    "diceRedColor": (193, 33, 39),       # catan red color
    "diceYellowColor": (254, 202, 10),   # catan yellow color
    "hoverAlpha": 170,                   # transparency for hover effect (out of 255)

    # --- Resource/tile colors ---
    "desert": (181, 174, 112),
    "sheep": (131, 187, 8),
    "ore": (141, 129, 182),
    "wheat": (251, 194, 51),
    "wood": (8, 100, 23),
    "brick": (255, 106, 42),
    "goldMine": (180, 144, 14),
    "sea": (17, 99, 176),
    "deepSea": (12, 70, 125),
    "fog": (222, 222, 222),
    # --- Number tokens / text ---
    "textSize": 20,  # base font size for number tokens
    "numberList": [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]  # standard Catan number token distribution
}

DEFAULT_CONFIG["colorList"] = [
    DEFAULT_CONFIG["desert"], DEFAULT_CONFIG["sheep"], DEFAULT_CONFIG["ore"], DEFAULT_CONFIG["wheat"], DEFAULT_CONFIG["wood"], DEFAULT_CONFIG["brick"]
]  # tiles that show up in game randomly
DEFAULT_CONFIG["noNumberTiles"] = [
    DEFAULT_CONFIG["desert"], DEFAULT_CONFIG["sea"], DEFAULT_CONFIG["deepSea"]
]  # tiles that don't have numbers
DEFAULT_CONFIG["numberSize"] = pygame.font.Font('assets/fonts/MinionPro-BoldCn.otf', round(DEFAULT_CONFIG["textSize"] * DEFAULT_CONFIG["gameScale"]))  # font object, scaled to current zoom

class UserSettings:
    def __init__(self):
        self.settingsFile = "user_settings.json"

        # --- Camera / view controls ---
        self.gameScale =       DEFAULT_CONFIG["gameScale"]
        self.zoomFactor =      DEFAULT_CONFIG["zoomFactor"]

        # --- App settings ---
        self.fpsLimit =        DEFAULT_CONFIG["fpsLimit"]
        self.numberOfRings =   DEFAULT_CONFIG["defaultRings"]

        # --- UI ---
        self.selectorColor =   DEFAULT_CONFIG["selectorColor"]
        self.selectorAlpha =   DEFAULT_CONFIG["selectorAlpha"]
        self.numberTileColor = DEFAULT_CONFIG["numberTileColor"]
        self.uiScale =         DEFAULT_CONFIG["uiScale"]
        self.pauseAlpha =      DEFAULT_CONFIG["pauseAlpha"]                               
        self.diceRedColor =    DEFAULT_CONFIG["diceRedColor"]
        self.diceYellowColor = DEFAULT_CONFIG["diceYellowColor"]
        self.hoverAlpha =      DEFAULT_CONFIG["hoverAlpha"]

        # --- Resource/tile colors ---
        self.desert =          DEFAULT_CONFIG["desert"]
        self.sheep =           DEFAULT_CONFIG["sheep"]
        self.ore =             DEFAULT_CONFIG["ore"]
        self.wheat =           DEFAULT_CONFIG["wheat"]
        self.wood =            DEFAULT_CONFIG["wood"]
        self.brick =           DEFAULT_CONFIG["brick"]
        self.goldMine =        DEFAULT_CONFIG["goldMine"]
        self.sea =             DEFAULT_CONFIG["sea"]
        self.deepSea =         DEFAULT_CONFIG["deepSea"]
        self.fog =             DEFAULT_CONFIG["fog"]

        self.loadSettings()
    
    def loadSettings(self):
        try:
            with open(self.settingsFile, 'r') as f:
                settings = json.load(f)
            for key, value in settings.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        except FileNotFoundError:
            pass
    
    def saveSettings(self):
        data = {key: value for key, value in self.__dict__.items() 
                if not key.startswith('_') and key != 'settingsFile'}
        with open(self.settingsFile, 'w') as f:
            json.dump(data, f)
    
    def getLists(self):
        return {
            "colorList": [self.sheep, self.ore, self.wheat, self.wood, self.brick, self.desert],
            "noNumberTiles": [self.desert, self.sea, self.deepSea]
        }

settings = UserSettings()

# --- Hex grid geometry ---
hexSize =         DEFAULT_CONFIG["hexSize"]
hexWidthRatio =   DEFAULT_CONFIG["hexWidthRatio"]
hexHeightRatio =  DEFAULT_CONFIG["hexHeightRatio"]

# --- App Settings ---
fpsLimit =        DEFAULT_CONFIG["fpsLimit"]
minZoom =         DEFAULT_CONFIG["minZoom"]
maxZoom =         DEFAULT_CONFIG["maxZoom"]
panSpeed =        DEFAULT_CONFIG["panSpeed"]

# --- Sorting ---
colorList =       DEFAULT_CONFIG["colorList"]
noNumberTiles =   DEFAULT_CONFIG["noNumberTiles"]

# --- Number tokens / text ---
textSize =        DEFAULT_CONFIG["textSize"]
numberList =      DEFAULT_CONFIG["numberList"]
numberSize =      DEFAULT_CONFIG["numberSize"]