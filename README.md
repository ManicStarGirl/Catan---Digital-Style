# Catan - Digital Style

A Python-based hexagonal grid visualization inspired by the board game Catan. Built with Pygame, this project renders a procedurally generated hex map with terrain types, number tokens, and interactive camera controls.

## Current Status

This is a work-in-progress visualization. Core game mechanics (dice rolling, 
resource collection, building costs, win conditions) are planned but not yet 
implemented. Currently supports board generation, camera controls, player turn 
system, placement previews, and save/load functionality.

## Planned Features

- Dice rolling and resource collection system
- Building placement with cost validation and actual placement
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
- **Settlement and road placement preview** with hover highlighting on valid corners and edges
- **Multi-player turn system** with player color cycling
- **Save/load game system** for persistent game state
- **Fullscreen toggle** with F11
- **Pause system** with ESC (includes quit button and main menu navigation)
- **View culling** for performance (only draws visible hexes)

## Requirements

- Python 3.x
- Pygame

## Installation

1. Clone the repository:
```bash
git clone https://github.com/XxFakeMan64xX/Catan---Digital-Style.git
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
| End Turn button | Cycle to next player |
| F11 | Toggle fullscreen |
| Escape | Toggle pause / Quit from pause menu |

## Project Structure

- `game.py` - Main entry point with screen manager and game loop
- `screens/` - Screen management system
  - `__init__.py` - Base Screen class with common UI setup
  - `mainMenu.py` - Main menu screen with navigation buttons and save/load functionality
  - `GameScreen.py` - Game screen with hex grid, camera controls, settlement/road placement preview, player turn system, and pause system
- `game/` - Game logic and data
  - `player.py` - Player class with resources, buildings, and victory points
  - `game.md` - Game development documentation
- `config.py` - Configuration constants (colors, zoom settings, hex geometry, UI settings)
- `hex_grid.py` - Hex grid generation algorithms (ring-based, terrain/number assignment)
- `coordinates.py` - Hex coordinate system conversions (pixel ↔ hex, rounding), settlement/road position calculations
- `ui.py` - UI components (uiRect class for scalable UI elements, hex class for tile rendering)
- `assets/fonts/` - Font files for number tokens

## Technical Details

- **Coordinate system**: Uses doubled hex coordinates for grid logic, converts to axial for mouse interaction
- **Rendering**: Pointy-topped hexagons with proper aspect ratio (3:2 width, √3/2 height)
- **Performance**: Implements view culling to avoid drawing off-screen hexes
- **Frame-rate independence**: Movement uses delta time for consistent speed across framerates
- **Save system**: JSON-based game state persistence including tiles, settlements, roads, and current player

Disclaimer: Ive used AI to write the comments (and this readme), but all of the code comes from me :3