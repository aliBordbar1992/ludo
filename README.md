# Ludo Game Implementation

A complete implementation of the classic Ludo board game with clean separation of concerns. The core game logic is completely independent of any UI, making it suitable for use with any interface (CLI, web, Unity, mobile apps, etc.).

## Features

### Core Game Logic
- **Complete Ludo Rules**: Implements all standard Ludo game rules
- **Four Players**: Support for Red, Green, Yellow, and Blue players
- **Piece Movement**: Proper piece movement with home area, main board, and home stretch
- **Dice Rolling**: 6-sided dice with proper turn mechanics
- **Piece Capture**: Pieces can capture opponents (except on safe positions)
- **Safe Positions**: Certain positions protect pieces from capture
- **Home Stretch**: Final path to victory
- **Win Conditions**: First player to get all 4 pieces home wins

### Architecture
- **Event-Driven**: Clean event system for UI communication
- **State Management**: Comprehensive game state tracking
- **Modular Design**: Separate classes for Game, Player, and Piece
- **Type Safety**: Full type hints for better development experience
- **Extensible**: Easy to extend with custom rules or features

## File Structure

```
├── ludo_game.py      # Core game logic (main implementation)
├── cli_example.py    # Command-line interface example
├── test_ludo.py      # Comprehensive test suite
└── README.md         # This file
```

## Quick Start

### Basic Usage

```python
from ludo_game import LudoGame, PlayerColor

# Create a new game
game = LudoGame()

# Add all four players
game.add_player(PlayerColor.RED)
game.add_player(PlayerColor.GREEN)
game.add_player(PlayerColor.YELLOW)
game.add_player(PlayerColor.BLUE)

# Game automatically starts when all players are added
# Red player goes first

# Roll the dice
dice_value = game.roll_dice()

# Get valid moves for current player
valid_moves = game.get_valid_moves(PlayerColor.RED)

# Move a piece
if valid_moves:
    piece, new_position = valid_moves[0]
    game.move_piece(PlayerColor.RED, piece.piece_id)
```

### Event System

The game uses an event-driven architecture to communicate with the UI:

```python
def handle_game_event(event):
    if event.event_type == EventType.DICE_ROLLED:
        print(f"Dice rolled: {event.data['dice_value']}")
    elif event.event_type == EventType.PIECE_MOVED:
        print(f"Piece moved from {event.data['old_position']} to {event.data['new_position']}")
    elif event.event_type == EventType.GAME_OVER:
        print(f"Winner: {event.data['winner']}")

# Add event listener
game.add_event_listener(handle_game_event)
```

### Game State

Get the current game state for UI rendering:

```python
state = game.get_game_state()
print(f"Current player: {state['current_player']}")
print(f"Game state: {state['game_state']}")
print(f"Dice value: {state['dice_value']}")

# Player information
for color, player_data in state['players'].items():
    print(f"{color}: {player_data['home_count']} pieces home")
    for piece in player_data['pieces']:
        print(f"  Piece {piece['piece_id']}: Position {piece['position']}")
```

## Running the Examples

### CLI Example

```bash
python cli_example.py
```

The CLI example provides two modes:
1. **Auto-play**: Fast automated gameplay
2. **Manual**: Step-by-step gameplay with board display

### Running Tests

```bash
python test_ludo.py
```

The test suite covers:
- Player management
- Dice rolling
- Piece movement
- Capture mechanics
- Safe positions
- Home stretch logic
- Winning conditions
- Event system
- Game state serialization

## Game Rules

### Basic Rules
1. **Objective**: Be the first to get all 4 pieces to the final home
2. **Starting**: Roll a 6 to move a piece from home area to the board
3. **Movement**: Move pieces clockwise around the board
4. **Capture**: Landing on an opponent's piece sends it back to home
5. **Safe Positions**: Pieces on certain positions cannot be captured
6. **Home Stretch**: Complete one full circle to enter the home stretch
7. **Exact Roll**: Need exact roll to reach final home position

### Board Layout
- **52 positions** on the main board (0-51)
- **4 home areas** for each player
- **6 positions** in each home stretch
- **8 safe positions** where pieces cannot be captured

### Player Colors and Positions
- **Red**: Start at position 0, home stretch at 50-55
- **Green**: Start at position 13, home stretch at 63-68
- **Yellow**: Start at position 26, home stretch at 76-81
- **Blue**: Start at position 39, home stretch at 89-94

## Integration Examples

### Web Application
```python
# Flask example
from flask import Flask, jsonify
from ludo_game import LudoGame, PlayerColor

app = Flask(__name__)
game = LudoGame()

@app.route('/api/roll-dice')
def roll_dice():
    dice_value = game.roll_dice()
    return jsonify({'dice_value': dice_value})

@app.route('/api/move-piece/<int:piece_id>')
def move_piece(piece_id):
    success = game.move_piece(game.current_player, piece_id)
    return jsonify({'success': success})
```

### Unity Integration
```csharp
// C# example for Unity
public class LudoGameController : MonoBehaviour
{
    private LudoGame game;
    
    void Start()
    {
        game = new LudoGame();
        game.add_event_listener(HandleGameEvent);
    }
    
    void HandleGameEvent(GameEvent event)
    {
        // Update Unity UI based on game events
        switch(event.event_type)
        {
            case EventType.PIECE_MOVED:
                MovePieceOnBoard(event.data);
                break;
            case EventType.GAME_OVER:
                ShowWinner(event.data["winner"]);
                break;
        }
    }
}
```

## API Reference

### LudoGame Class

#### Core Methods
- `add_player(color: PlayerColor) -> bool`: Add a player to the game
- `remove_player(color: PlayerColor) -> bool`: Remove a player from the game
- `roll_dice() -> int`: Roll the dice and return the value
- `move_piece(player_color: PlayerColor, piece_id: int) -> bool`: Move a specific piece
- `get_valid_moves(player_color: PlayerColor) -> List[Tuple[Piece, int]]`: Get all valid moves
- `get_game_state() -> Dict`: Get current game state
- `reset_game()`: Reset the game to initial state

#### Event System
- `add_event_listener(listener: Callable[[GameEvent], None])`: Add event listener
- `_emit_event(event: GameEvent)`: Emit game event (internal use)

### Player Class
- `color: PlayerColor`: Player's color
- `pieces: List[Piece]`: Player's pieces
- `home_count: int`: Number of pieces in final home
- `has_won() -> bool`: Check if player has won

### Piece Class
- `player_color: PlayerColor`: Piece's owner
- `piece_id: int`: Piece identifier (0-3)
- `position: int`: Current position (-1 for home area)
- `is_home: bool`: Whether piece is in final home
- `is_safe: bool`: Whether piece is on safe position
- `reset()`: Reset piece to starting position

### Enums
- `PlayerColor`: RED, GREEN, YELLOW, BLUE
- `GameState`: WAITING_FOR_PLAYERS, ROLLING_DICE, MOVING_PIECE, GAME_OVER
- `EventType`: Various game events

## Contributing

The code is designed to be easily extensible. Common extensions might include:
- Custom game rules
- AI players
- Network multiplayer
- Tournament systems
- Custom board layouts

## License

This implementation is provided as-is for educational and development purposes.