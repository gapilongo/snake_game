# Snake Game

A classic Snake game implementation in Python using Pygame.

## Features

- Classic Snake gameplay
- Score tracking
- Smooth movement and controls
- Grass-pattern background
- Collision detection (walls and self)
- Food spawning system

## Requirements

- Python 3.6 or higher
- Pygame 2.5.2

## Installation

1. Navigate to the snake_game directory:
   ```
   cd snake_game
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## How to Run

### Option 1: Using the batch file (Windows)
Double-click on `run_game.bat` or run it from the command line:
```
run_game.bat
```

### Option 2: Using Python directly
Run the game using Python:
```
python snake_game.py
```

Note: Make sure pygame is installed first:
```
pip install pygame
```

## Controls

- **Arrow Keys**: Control the snake's direction
  - ↑ Up Arrow: Move up
  - ↓ Down Arrow: Move down
  - ← Left Arrow: Move left
  - → Right Arrow: Move right

## Gameplay

- Control the green snake to eat the red food
- Each food eaten increases your score by 1
- The snake grows longer with each food consumed
- Avoid hitting the walls or the snake's own body
- The game ends when the snake collides with a wall or itself

## Game Elements

- **Snake**: Dark green blocks that make up the snake's body
- **Food**: Red blocks that appear randomly on the screen
- **Score**: Displayed at the top center of the screen
- **Background**: Green with a grass pattern

Enjoy playing the Snake game!
