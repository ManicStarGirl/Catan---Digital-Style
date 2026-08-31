# Catan - Digital Style

A Python-based hexagonal grid visualization inspired by the board game Catan. Built with Pygame, this project renders a procedurally generated hex map with terrain types, number tokens, and interactive camera controls.

## Current Status

This is a work-in-progress visualization. Core game mechanics (resource collection, 
building costs, win conditions) are planned but not yet implemented. Currently supports 
board generation, camera controls, player turn system, dice rolling with animation, 
settlement and road placement with proper Catan rules, save/load functionality, and 
a user settings system with JSON persistence.

## Planned Features

- Resource collection system based on dice rolls
- Building cost validation
- Robber mechanics
- Trading system between players
- Development cards
- Complete game rules implementation and win conditions

## Features

- **Screen management system** with main menu and game screens
- **Procedural hex grid generation** using ring-based spiral algorithm
- **Random terrain assignment** with proper Catan resource distribution (sheep, ore, wheat, wood, brick, desert, gold mine)
- **Number token placement** with standard Catan dice roll distribution
- **Interactive camera controls**:
  - Pan with WASD or arrow keys
  - Zoom with mouse wheel (centered on cursor)
  - Drag to pan with mouse
  - Hold Shift for faster panning
- **Settlement and road placement** with left-click to place and right-click to remove buildings
  - Settlement placement follows Catan distance rules (minimum spacing between settlements)
  - Initial placement phase: first 2 settlements can be placed anywhere valid
  - After initial placement: settlements must be adjacent to your own road network
  - Road placement must be adjacent to your own settlements or existing roads (road chaining)
  - Players can only remove their own buildings
- **Multi-player turn system** with player color cycling
- **Animated dice rolling** with red and yellow dice featuring independent randomized bouncing animation and pip display
- **Save/load game system** for persistent game state (tiles, settlements, roads, current player)
- **User settings system** with JSON persistence for customizable game options
- **Fullscreen toggle** with F11
- **Pause system** with ESC (includes quit button and main menu navigation)
- **View culling** for performance (only draws visible hexes)

## Requirements

- Python 3.x
- Pygame

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ManicStarGirl/Catan---Digital-Style.git
cd Catan---Digital-Style
```

2. Install Pygame:
```bash
pip install pygame
```

3. Run the game:
```bash
python game.py
```

## Controls

| Key/Mouse | Action |
|-----------|--------|
| W / ↑ | Pan up |
| S / ↓ | Pan down |
| A / ← | Pan left |
| D / → | Pan right |
| Shift | Hold to pan faster |
| Mouse wheel | Zoom in/out |
| Left-click drag | Pan camera |
| Left-click corner/edge | Place settlement/road (shows preview for valid positions) |
| Right-click corner/edge | Remove settlement/road (only your own buildings) |
| Click dice | Roll dice with animation |
| End Turn button | Cycle to next player (border shows current player color) |
| Right-click End Turn | Cycle to previous player |
| F11 | Toggle fullscreen |
| Escape | Toggle pause / Quit from pause menu |

## Project Structure

- `game.py` - Main entry point with screen manager and game loop
- `screens/` - Screen management system
  - `__init__.py` - Base Screen class with common UI setup and enhanced dice animation variables (independent red/yellow dice movement with randomized shaking)
  - `mainMenu.py` - Main menu screen with navigation buttons and save/load functionality
  - `GameScreen.py` - Game screen with hex grid, camera controls, settlement/road placement with Catan rules, player turn system, animated dice rolling, and pause system
  - `settingsScreen.py` - Settings screen for user configuration
- `game/` - Game logic and data
  - `player.py` - Player class with resources, buildings, and victory points
  - `game.md` - Game development documentation
- `config.py` - Configuration system with UserSettings class for JSON persistence, default constants (colors, zoom settings, hex geometry, UI settings, dice colors)
- `hex_grid.py` - Hex grid generation algorithms (ring-based, terrain/number assignment)
- `coordinates.py` - Hex coordinate system conversions (pixel ↔ hex, rounding), settlement/road position calculations (returns mutable lists)
- `ui.py` - UI components (uiRect class for scalable UI elements, hex class for tile rendering)
- `assets/fonts/` - Font files for number tokens

## Technical Details

- **Coordinate system**: Uses doubled hex coordinates for grid logic, converts to axial for mouse interaction with rounded precision for consistent positioning
- **Settlement validation**: Enforces Catan spacing rules (1 position of space between settlements) to prevent adjacent settlements
- **Rendering**: Pointy-topped hexagons with proper aspect ratio (3:2 width, √3/2 height)
- **Performance**: Implements view culling to avoid drawing off-screen hexes
- **Frame-rate independence**: Movement uses delta time for consistent speed across framerates
- **Save system**: JSON-based game state persistence including tiles, settlements, roads, and current player

Disclaimer: Ive used AI to write the comments (and this readme), but all of the code comes from me :3