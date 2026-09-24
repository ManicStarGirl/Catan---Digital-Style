# Game Development Progress

## Completed Features

### Phase 1: Core Game Loop
- ✅ Dice rolling with animation (red and yellow dice with independent movement)
- ✅ Multi-player turn system with player color cycling
- ✅ Screen management system (main menu, new game, build, game screen, settings screen)
- ✅ Save/load game system with JSON persistence
- ✅ User settings system with JSON persistence
- ✅ Custom board configuration support

### Phase 2: Building
- ✅ Settlement placement with Catan rules:
  - Distance rule (minimum 1.33 units between settlements)
  - Initial placement phase (first 2 settlements can be placed anywhere valid)
  - After initial placement: must be adjacent to your own road network
- ✅ Road placement with Catan rules:
  - Cannot place on existing roads
  - Must be adjacent to your own settlements or existing roads
  - Road chaining for continuous networks
- ✅ Boat placement on sea and deep sea tiles for maritime routes
- ✅ Building preview system (shows valid positions with transparency)
  - Enhanced settlement/road/boat preview with improved polygon shapes
- ✅ Remove buildings (right-click to remove your own settlements/roads)

### Phase 3: Advanced Mechanics
- ✅ Pause system with quit and main menu navigation
- ✅ Fullscreen toggle
- ✅ View culling for performance
- ✅ Dynamic settings system with real-time modification
  - Automatic button generation for all settings attributes
  - Smart value cycling (presets for scales, wrapping for numeric values)
  - Auto-save on screen exit
- ✅ Color settings screen for UI customization
- ✅ Improved settlement rendering (house-shaped polygons)
- ✅ Centralized UI color configuration
  - Button colors now managed through settings system
  - Greyed-out button states for disabled options
- ✅ New game setup screen with board configuration
- ✅ Build screen for construction operations
- ✅ Smart text color detection for optimal readability

## Recent Updates (September 2026)

### UI Refactoring and Button System
- **Unified Button Management**: Created VerstileButton component in components/genericButton.py
  - Centralized button creation, click handling, and drawing across all screens
  - Simplified mainMenuScreen.py, newGameScreen.py, and GameScreen.py pause menu
  - Reduced code duplication and improved maintainability
- **Screen Navigation Updates**: Changed "new" action to "newGame" in screen manager
  - Updated newGameScreen.py to include "Back" button for main menu return
  - Consistent action naming across screen transitions
- **Button Spacing**: Added self.buttonSpacing to Screen base class
  - Replaced hardcoded spacing values with scalable buttonSpacing
  - Improved settings screen layout consistency

### Smart Board Randomization
- **Intelligent Number Distribution**: Added randomizeBoard() function in hex_grid.py
  - Prevents adjacent 6/8 numbers (red numbers) for balanced gameplay
  - Calculates red number percentage and applies smart placement if < 38%
  - Retries up to 100 times to generate valid board configurations
  - Uses HEX_DIRECTIONS for adjacent hex position calculations
- **Parameter Renaming**: Renamed newTiles() parameter from "rings" to "numberOfRings" for clarity

### Road Connection Logic
- **Automatic Road Position Addition**: Enhanced GameScreen.py road placement
  - When placing a road, automatically calculates and adds 4 connecting road positions
  - Calculates offsets based on road angle (0°, 60°, 120°)
  - Prevents duplicate road positions with existence checks
  - Simplifies road network building for players

### Color and Text Improvements
- **Enhanced Text Contrast**: Improved UIRect text color detection in ui.py
  - Added optional textColor parameter for manual override
  - Checks contrast between textColor and background color
  - Automatically inverts text color if too similar (<60 average difference)
  - Number token colors adapt to tile background:
    - 6/8 tokens: cyan if background is red-like, otherwise red
    - Regular numbers: use tile textColor
    - Invalid/placeholder: yellow if background is blue-like, otherwise blue
- **Color Settings Refactoring**: Renamed variables in colorSettingsScreen.py for clarity
  - sliderR/G/B → redSliderColorValue/greenSliderColorValue/blueSliderColorValue
  - sliderYR/YG/YB → redSliderY/greenSliderY/blueSliderY
  - maxRGB → maxColorValue
  - colorPickerScreen → isColorPickerActive
  - settingButtons → colorSettingButtons
  - Added setColor() method for programmatic color picker control
  - Dynamic save button with conflict warnings and color feedback

### Code Organization
- **File Structure Changes**: Moved files to components/ directory
  - game/game.md → components/game.md
  - game/player.py → components/player.py
  - Created components/genericButton.py for reusable button component
- **JSON Formatting**: Added indent=2 to all json.dump() calls
  - config.py, GameScreen.py, buildScreen.py
  - Pretty-printed JSON for better readability in save files

### Boat Rendering
- **Improved Boat Polygon**: Enhanced boat rendering in GameScreen.py
  - Updated baseBoatPoints with better boat shape
  - Proper rotation based on road angle
  - Consistent with road rendering orientation

### Git Configuration
- **Updated .gitignore**: Added .vscode/ directory to ignore

### Resource System Refactoring
- **String-based Resource System**: Migrated from color tuple storage to string-based resource names
  - Terrain types now stored as strings (e.g., "sheep", "ore", "wheat", "wood", "brick", "desert", "sea", "deepSea", "fog")
  - Color lookup performed at render time via getattr(settings, resourceName)
  - Simplified hex initialization with default string "deepSea" instead of settings.deepSea
  - Updated hex.draw() to use getattr(settings, self.resource) for dynamic color resolution
  - Improved maintainability and easier resource type management
- **Dictionary-based Tile Storage**: Changed tileList from list to dictionary
  - Tiles now keyed by (x, y) coordinate tuples for O(1) lookup performance
  - Updated all iteration to use tileList.values()
  - Simplified tile deletion with del tileList[coords] instead of list comprehensions
  - Improved save/load system to handle dictionary structure
  - Better performance for large boards with frequent coordinate lookups
- **Configuration Simplification**: Moved colorList and noNumberTiles to static string lists in DEFAULT_CONFIG
  - Removed UserSettings.getLists() method
  - Direct imports of colorList and noNumberTiles from config
  - Cleaner separation between configuration and runtime settings

### Build Screen Enhancements
- **Continuous Hex Editing**: Added ability to place/remove hexes while holding mouse buttons
  - Left-click and drag to continuously place hexes of selected terrain type
  - Right-click and drag to continuously remove hexes
  - Middle-click to drag camera (previously left-click)
  - Improved hex placement logic with better state management
- **Terrain Selection System**: Enhanced hex type selection interface
  - Click hex selector in top-right corner to choose terrain type
  - Visual feedback showing currently selected terrain
  - Supports all terrain types including sea, deep sea, and fog
- **Improved State Management**: Refactored build screen state variables
  - `choosingHex` (was `placing`) - for selecting hex type from palette
  - `placingHex` - for continuous hex placement while mouse is held
  - `removingHex` - for continuous hex removal while right mouse button is held
- **Sea Tile Overwriting**: Added ability to overwrite sea tiles with other terrain types
  - Enables board editing flexibility for custom map creation
  - Maintains proper number token assignment rules
- **Refactored placeHex Method**: Extracted hex placement logic into dedicated method
  - Cleaner separation of concerns in build screen
  - Improved code organization and maintainability
  - Consistent with string-based resource system

### New Game Flow and Screens
- **New Game Screen**: Added dedicated screen for game setup and board configuration
  - Replaces direct game start from main menu
  - Supports custom board selection from boards/ directory
  - Provides game mode selection (singleplayer, etc.)
- **Build Screen**: New dedicated screen for construction and building operations
  - Separates building mechanics from main game screen
  - Enhanced user interface for building decisions
- **Screen Management**: Updated routing system to support new screen flow
  - "new" → NewGame screen instead of direct GameScreen
  - "singleplayer" → GameScreen for standard gameplay
  - "build" → BuildScreen for construction

### Board Configuration System
- **Custom Board Support**: Added boards/ directory for custom JSON board configurations
  - Boards stored as JSON files with tile data, resources, and number tokens
  - Supports multiple custom board layouts
  - Custom boards ignored in .gitignore (except boards/custom/ subdirectory)
- **Board Management**: Removed default.json in favor of custom board system
  - More flexible board configuration approach
  - Easier board sharing and modification

### Visual Enhancements
- **Dynamic Text Color Detection**: Enhanced contrast-based text color system
  - Automatic white/black text selection based on background luminance
  - Applies to both number tokens and fog of war markers
  - Uses luminance formula: 0.299*R + 0.587*G + 0.114*B for optimal readability
- **Enhanced Rendering**: Improved hex.draw() method with showToken parameter
  - Better control over token visibility and rendering
  - Supports both numeric and string-based number tokens

### Sea Tile Handling
- **Building Position Validation**: Updated settlement and road placement logic
  - Sea and deep sea tiles excluded from valid building positions
  - getSettlementPositions() now filters out sea tiles
  - getRoadPositions() now filters out sea tiles
  - Proper resource type checking using settings.sea and settings.deepSea
- **Boat Position Calculation**: Added getBoatPositions() function
  - Calculates valid boat positions on sea and deep sea tiles
  - Enables maritime route planning and placement
  - Uses same coordinate system as road placement for consistency

### Coordinate System Improvements
- **Mutable Position Lists**: Updated coordinate functions to return mutable lists
  - getRoadPositions() now returns list of lists instead of set
  - getBoatPositions() returns list of lists for consistency
  - Better integration with game state management

### Save System Improvements
- **Null Safety**: Enhanced save/load system with null checks
  - Handles missing settlements, roads, and currentPlayer data gracefully
  - Prevents crashes when loading incomplete save files
  - More robust error handling for save.json parsing

### UI/UX Improvements
- **Settings Screen Overhaul**: Complete rewrite to support dynamic setting modification
  - Replaced hardcoded buttons with automatically generated controls
  - 3-button layout per setting: [-] [display] [+]
  - Added "Color Settings" navigation button
  - Improved scrolling with dynamic button repositioning
  - ESC key to return to main menu with auto-save
- **Color Settings Screen**: New dedicated screen for UI customization
  - RGB slider controls with gradient visualization
  - Real-time color preview
  - Conflict detection for similar colors
  - Reset button to restore default colors
  - Drag-and-drop slider handles
- **Smart Text Color Detection**: Automatic contrast-based text color
  - White text on dark backgrounds, black text on light backgrounds
  - Uses luminance formula for optimal readability

### Visual Enhancements
- **Settlement Rendering**: Changed from square markers to house-shaped polygons
  - 7-point polygon representing house structure
  - Better visual recognition on the game board
  - Consistent scaling with game zoom
- **City Rendering**: Added distinct city polygon shape
  - 7-point polygon representing city structure
  - Different visual from settlements for game clarity
- **Road Rendering**: Reduced width from 6 to 4 pixels for better aesthetics
- **Boat Rendering**: Added boat polygon shape for maritime routes
  - 9-point polygon representing boat structure
  - Enables visual representation of sea-based connections
- **Building Preview**: Enhanced preview system with transparent house/city/boat shapes
  - Improved variable naming (settlementPoints, roadPoints, boatPoints)

### Code Organization
- **File Renaming**: `mainMenu.py` → `mainMenuScreen.py` for consistency
- **Color Management**: Centralized button colors in settings configuration
- **Settings File**: Renamed from `user_settings.json` to `userSettings.json`
- **Git Configuration**: Added `userSettings.json` to .gitignore
- **Class Name Fixes**: Fixed uiRect → UIRect typo in colorSettingsScreen.py
  - Corrected 3 instances of incorrect class name
  - Ensures proper UI element rendering in color customization

### Configuration System
- **New Settings**: Added `buttonColor` and `buttonGreyedOutColor` to config
- **Terrain Configuration**: Added sea and deep sea resource types for building validation
  - `settings.sea` and `settings.deepSea` for tile type identification
  - Used in coordinate calculations to exclude water tiles from building positions
- **Smart Value Handling**: Different modification logic for different setting types
  - Float values: cycle through presets (gameScale, zoomFactor, uiScale)
  - FPS limit: 30-120 range with 10-step increments
  - Number of rings: 2-10 range
  - Color values: 0-255 range with wrapping
- **Auto-save**: Settings automatically saved on screen exit

## Planned Features

### Resource Collection
- When dice roll matches tile numbers, give resources to players with settlements on those tiles
- Resource tracking per player (wood, brick, sheep, wheat, ore)

### Building Costs
- Settlement cost: 1 wood, 1 brick, 1 sheep, 1 wheat
- Road cost: 1 wood, 1 brick
- City cost: 2 wheat, 2 ore (upgrade from settlement)
- Building UI to show current resources and building buttons

### Robber Mechanics
- On roll of 7, move robber to a tile
- Block production on tile with robber
- Steal resources from adjacent player

### Victory Points
- Track settlements (1 VP each)
- Cities (2 VP each)
- Longest road (2 VP)
- Largest army (2 VP from development cards)
- Win condition: First to 10 VP wins

### Development Cards
- Knight cards (for largest army)
- Victory point cards
- Resource cards
- Road building cards
- Monopoly cards