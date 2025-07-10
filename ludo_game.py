"""
Ludo Game Core Logic

This module provides a complete implementation of the Ludo board game
with clean separation from UI concerns. The game logic can be used
with any UI implementation (CLI, web, Unity, etc.).
"""

from enum import Enum
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass
import random


class PlayerColor(Enum):
    """Player colors in Ludo game"""
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"


class GameState(Enum):
    """Possible game states"""
    WAITING_FOR_PLAYERS = "waiting_for_players"
    ROLLING_DICE = "rolling_dice"
    MOVING_PIECE = "moving_piece"
    GAME_OVER = "game_over"


class EventType(Enum):
    """Game events that can be emitted"""
    GAME_STARTED = "game_started"
    DICE_ROLLED = "dice_rolled"
    PIECE_MOVED = "piece_moved"
    PLAYER_TURN_CHANGED = "player_turn_changed"
    GAME_OVER = "game_over"
    INVALID_MOVE = "invalid_move"
    PIECE_CAPTURED = "piece_captured"
    PIECE_HOME = "piece_home"


@dataclass
class GameEvent:
    """Represents a game event with data"""
    event_type: EventType
    data: Dict
    player_color: Optional[PlayerColor] = None


class Piece:
    """Represents a game piece"""
    
    def __init__(self, player_color: PlayerColor, piece_id: int):
        self.player_color = player_color
        self.piece_id = piece_id
        self.position = -1  # -1 means in home area
        self.is_home = False
        self.is_safe = False  # Safe from capture
    
    def __str__(self):
        return f"{self.player_color.value.capitalize()} Piece {self.piece_id}"
    
    def reset(self):
        """Reset piece to starting position"""
        self.position = -1
        self.is_home = False
        self.is_safe = False


class Player:
    """Represents a player in the game"""
    
    def __init__(self, color: PlayerColor):
        self.color = color
        self.pieces = [Piece(color, i) for i in range(4)]
        self.home_count = 0
        self.start_position = self._get_start_position()
        self.home_position = self._get_home_position()
    
    def _get_start_position(self) -> int:
        """Get the starting position for this player's pieces"""
        positions = {
            PlayerColor.RED: 0,
            PlayerColor.GREEN: 13,
            PlayerColor.YELLOW: 26,
            PlayerColor.BLUE: 39
        }
        return positions[self.color]
    
    def _get_home_position(self) -> int:
        """Get the home stretch starting position"""
        positions = {
            PlayerColor.RED: 50,
            PlayerColor.GREEN: 63,
            PlayerColor.YELLOW: 76,
            PlayerColor.BLUE: 89
        }
        return positions[self.color]
    
    def get_pieces_in_home(self) -> List[Piece]:
        """Get pieces that are in the home area"""
        return [piece for piece in self.pieces if piece.position == -1]
    
    def get_pieces_on_board(self) -> List[Piece]:
        """Get pieces that are on the main board"""
        return [piece for piece in self.pieces if piece.position >= 0 and not piece.is_home]
    
    def get_pieces_in_final_home(self) -> List[Piece]:
        """Get pieces that have reached the final home"""
        return [piece for piece in self.pieces if piece.is_home]
    
    def has_won(self) -> bool:
        """Check if player has won (all pieces in final home)"""
        return len(self.get_pieces_in_final_home()) == 4


class LudoGame:
    """Main Ludo game class with core logic"""
    
    def __init__(self):
        self.players: Dict[PlayerColor, Player] = {}
        self.current_player: Optional[PlayerColor] = None
        self.game_state = GameState.WAITING_FOR_PLAYERS
        self.dice_value = 0
        self.board_size = 52  # Main board positions (0-51)
        self.event_listeners: List[Callable[[GameEvent], None]] = []
        
        # Board positions for each player's home stretch
        self.home_stretch_positions = {
            PlayerColor.RED: list(range(50, 56)),
            PlayerColor.GREEN: list(range(63, 69)),
            PlayerColor.YELLOW: list(range(76, 82)),
            PlayerColor.BLUE: list(range(89, 95))
        }
        
        # Safe positions (cannot be captured)
        self.safe_positions = {0, 8, 13, 21, 26, 34, 39, 47}
    
    def add_player(self, color: PlayerColor) -> bool:
        """Add a player to the game"""
        if color in self.players:
            return False
        
        self.players[color] = Player(color)
        
        if len(self.players) == 4:
            self._start_game()
        
        return True
    
    def remove_player(self, color: PlayerColor) -> bool:
        """Remove a player from the game"""
        if color not in self.players:
            return False
        
        del self.players[color]
        return True
    
    def add_event_listener(self, listener: Callable[[GameEvent], None]):
        """Add an event listener to receive game events"""
        self.event_listeners.append(listener)
    
    def _emit_event(self, event: GameEvent):
        """Emit a game event to all listeners"""
        for listener in self.event_listeners:
            listener(event)
    
    def _start_game(self):
        """Start the game with all players"""
        if len(self.players) != 4:
            return
        
        self.game_state = GameState.ROLLING_DICE
        self.current_player = PlayerColor.RED  # Red always starts
        
        self._emit_event(GameEvent(
            EventType.GAME_STARTED,
            {"players": [color.value for color in self.players.keys()]},
            self.current_player
        ))
    
    def roll_dice(self) -> int:
        """Roll the dice and return the value"""
        if self.game_state != GameState.ROLLING_DICE:
            return 0
        
        self.dice_value = random.randint(1, 6)
        self.game_state = GameState.MOVING_PIECE
        
        self._emit_event(GameEvent(
            EventType.DICE_ROLLED,
            {"dice_value": self.dice_value},
            self.current_player
        ))
        
        return self.dice_value
    
    def get_valid_moves(self, player_color: PlayerColor) -> List[Tuple[Piece, int]]:
        """Get all valid moves for the current player"""
        if self.current_player != player_color or self.game_state != GameState.MOVING_PIECE:
            return []
        
        player = self.players[player_color]
        valid_moves = []
        
        # Check if player can move any piece
        for piece in player.pieces:
            new_position = self._calculate_new_position(piece, self.dice_value)
            if self._is_valid_move(piece, new_position):
                valid_moves.append((piece, new_position))
        
        return valid_moves
    
    def move_piece(self, player_color: PlayerColor, piece_id: int) -> bool:
        """Move a specific piece for the current player"""
        if self.current_player != player_color or self.game_state != GameState.MOVING_PIECE:
            return False
        
        player = self.players[player_color]
        if piece_id < 0 or piece_id >= 4:
            return False
        
        piece = player.pieces[piece_id]
        new_position = self._calculate_new_position(piece, self.dice_value)
        
        if not self._is_valid_move(piece, new_position):
            self._emit_event(GameEvent(
                EventType.INVALID_MOVE,
                {"piece_id": piece_id, "dice_value": self.dice_value},
                player_color
            ))
            return False
        
        # Execute the move
        old_position = piece.position
        piece.position = new_position
        
        # Check if piece reached final home
        if self._is_in_final_home(piece):
            piece.is_home = True
            player.home_count += 1
            
            self._emit_event(GameEvent(
                EventType.PIECE_HOME,
                {"piece_id": piece_id, "player_color": player_color.value},
                player_color
            ))
        
        # Check for captures
        captured_piece = self._check_capture(piece, new_position)
        if captured_piece:
            captured_piece.reset()
            self._emit_event(GameEvent(
                EventType.PIECE_CAPTURED,
                {"captured_piece": str(captured_piece), "capturing_piece": str(piece)},
                player_color
            ))
        
        # Update piece safety
        piece.is_safe = new_position in self.safe_positions
        
        self._emit_event(GameEvent(
            EventType.PIECE_MOVED,
            {
                "piece_id": piece_id,
                "old_position": old_position,
                "new_position": new_position,
                "dice_value": self.dice_value
            },
            player_color
        ))
        
        # Check for game over
        if player.has_won():
            self._end_game(player_color)
            return True
        
        # Move to next player
        self._next_turn()
        return True
    
    def _calculate_new_position(self, piece: Piece, dice_value: int) -> int:
        """Calculate new position for a piece after moving"""
        if piece.is_home:
            return piece.position
        
        if piece.position == -1:  # Piece in home area
            if dice_value == 6:
                player = self.players[piece.player_color]
                return player.start_position
            return -1
        
        # Calculate new position on main board
        new_pos = piece.position + dice_value
        
        # Check if piece should enter home stretch
        if self._should_enter_home_stretch(piece, new_pos):
            home_stretch_pos = new_pos - self.board_size
            player = self.players[piece.player_color]
            return player.home_position + home_stretch_pos
        
        # Wrap around the board
        if new_pos >= self.board_size:
            new_pos -= self.board_size
        
        return new_pos
    
    def _should_enter_home_stretch(self, piece: Piece, new_position: int) -> bool:
        """Check if piece should enter home stretch"""
        if new_position < self.board_size:
            return False
        
        # Check if piece has completed a full circle
        player = self.players[piece.player_color]
        start_pos = player.start_position
        if piece.position < start_pos and new_position >= start_pos:
            return False
        
        return True
    
    def _is_in_final_home(self, piece: Piece) -> bool:
        """Check if piece is in final home position"""
        player = self.players[piece.player_color]
        if piece.position < player.home_position:
            return False
        
        home_stretch = self.home_stretch_positions[piece.player_color]
        return piece.position in home_stretch
    
    def _is_valid_move(self, piece: Piece, new_position: int) -> bool:
        """Check if a move is valid"""
        # Can't move if piece is already home
        if piece.is_home:
            return False
        
        # If piece is in home area, need 6 to move out
        if piece.position == -1:
            return self.dice_value == 6
        
        # Check if new position is occupied by own piece
        player = self.players[piece.player_color]
        for other_piece in player.pieces:
            if other_piece != piece and other_piece.position == new_position and not other_piece.is_home:
                return False
        
        return True
    
    def _check_capture(self, moving_piece: Piece, position: int) -> Optional[Piece]:
        """Check if a piece captures another piece"""
        if position in self.safe_positions:
            return None
        
        for player in self.players.values():
            for piece in player.pieces:
                if (piece != moving_piece and 
                    piece.position == position and 
                    not piece.is_home and 
                    piece.player_color != moving_piece.player_color):
                    return piece
        
        return None
    
    def _next_turn(self):
        """Move to the next player's turn"""
        player_order = [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]
        if self.current_player is None:
            return
        current_index = player_order.index(self.current_player)
        next_index = (current_index + 1) % 4
        
        # Skip players who have won
        while next_index != current_index:
            next_player = player_order[next_index]
            if next_player in self.players and not self.players[next_player].has_won():
                break
            next_index = (next_index + 1) % 4
        
        self.current_player = player_order[next_index]
        self.game_state = GameState.ROLLING_DICE
        
        self._emit_event(GameEvent(
            EventType.PLAYER_TURN_CHANGED,
            {"player_color": self.current_player.value},
            self.current_player
        ))
    
    def _end_game(self, winner: PlayerColor):
        """End the game with a winner"""
        self.game_state = GameState.GAME_OVER
        
        self._emit_event(GameEvent(
            EventType.GAME_OVER,
            {"winner": winner.value},
            winner
        ))
    
    def get_game_state(self) -> Dict:
        """Get current game state for UI consumption"""
        return {
            "game_state": self.game_state.value,
            "current_player": self.current_player.value if self.current_player else None,
            "dice_value": self.dice_value,
            "players": {
                color.value: {
                    "home_count": player.home_count,
                    "has_won": player.has_won(),
                    "pieces": [
                        {
                            "piece_id": piece.piece_id,
                            "position": piece.position,
                            "is_home": piece.is_home,
                            "is_safe": piece.is_safe
                        }
                        for piece in player.pieces
                    ]
                }
                for color, player in self.players.items()
            }
        }
    
    def reset_game(self):
        """Reset the game to initial state"""
        for player in self.players.values():
            for piece in player.pieces:
                piece.reset()
            player.home_count = 0
        
        self.current_player = None
        self.game_state = GameState.WAITING_FOR_PLAYERS
        self.dice_value = 0
        
        if len(self.players) == 4:
            self._start_game()