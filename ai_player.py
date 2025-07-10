"""
AI Player for Ludo Game

This module provides AI players with three difficulty levels:
- Easy: Random moves with basic rules
- Medium: Strategic moves with piece prioritization
- Hard: Advanced strategy with opponent blocking and optimal play
"""

from enum import Enum
from typing import List, Tuple, Optional, Dict
import random
from ludo_game import LudoGame, PlayerColor, Piece, GameState


class AIDifficulty(Enum):
    """AI difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class AIPlayer:
    """AI player that can make strategic moves in Ludo game"""
    
    def __init__(self, color: PlayerColor, difficulty: AIDifficulty):
        self.color = color
        self.difficulty = difficulty
        self.game: Optional[LudoGame] = None
    
    def set_game(self, game: LudoGame):
        """Set the game instance for the AI player"""
        self.game = game
    
    def make_move(self) -> bool:
        """Make a move based on AI difficulty level"""
        if not self.game or self.game.current_player != self.color:
            return False
        
        # Roll dice if needed
        if self.game.game_state == GameState.ROLLING_DICE:
            self.game.roll_dice()
        
        # Make move if possible
        if self.game.game_state == GameState.MOVING_PIECE:
            valid_moves = self.game.get_valid_moves(self.color)
            
            if not valid_moves:
                # No valid moves, skip turn
                self.game._next_turn()
                return True
            
            # Choose move based on difficulty
            chosen_piece = self._choose_move(valid_moves)
            if chosen_piece:
                return self.game.move_piece(self.color, chosen_piece.piece_id)
        
        return False
    
    def _choose_move(self, valid_moves: List[Tuple[Piece, int]]) -> Optional[Piece]:
        """Choose which piece to move based on difficulty level"""
        if not valid_moves:
            return None
        
        if self.difficulty == AIDifficulty.EASY:
            return self._easy_move(valid_moves)
        elif self.difficulty == AIDifficulty.MEDIUM:
            return self._medium_move(valid_moves)
        else:  # HARD
            return self._hard_move(valid_moves)
    
    def _easy_move(self, valid_moves: List[Tuple[Piece, int]]) -> Piece:
        """Easy AI: Random move with basic preferences"""
        # Prefer moving pieces out of home if possible
        home_moves = [(piece, pos) for piece, pos in valid_moves if piece.position == -1]
        if home_moves and random.random() < 0.7:  # 70% chance to prefer home moves
            return random.choice(home_moves)[0]
        
        # Otherwise random move
        return random.choice(valid_moves)[0]
    
    def _medium_move(self, valid_moves: List[Tuple[Piece, int]]) -> Piece:
        """Medium AI: Strategic moves with piece prioritization"""
        move_scores = []
        
        for piece, new_position in valid_moves:
            score = self._calculate_move_score_medium(piece, new_position)
            move_scores.append((piece, score))
        
        # Sort by score (highest first) and add some randomness
        move_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Choose from top 3 moves with weighted randomness
        top_moves = move_scores[:min(3, len(move_scores))]
        weights = [3, 2, 1][:len(top_moves)]
        
        chosen_piece = random.choices(
            [piece for piece, _ in top_moves],
            weights=weights
        )[0]
        
        return chosen_piece
    
    def _hard_move(self, valid_moves: List[Tuple[Piece, int]]) -> Piece:
        """Hard AI: Advanced strategy with opponent analysis"""
        move_scores = []
        
        for piece, new_position in valid_moves:
            score = self._calculate_move_score_hard(piece, new_position)
            move_scores.append((piece, score))
        
        # Sort by score and choose the best move
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return move_scores[0][0]
    
    def _calculate_move_score_medium(self, piece: Piece, new_position: int) -> float:
        """Calculate move score for medium difficulty"""
        if not self.game:
            return 0.0
            
        score = 0.0
        
        # Priority 1: Move pieces out of home (high priority)
        if piece.position == -1:
            score += 50
        
        # Priority 2: Get pieces closer to home stretch
        if piece.position >= 0:
            player = self.game.players[self.color]
            distance_to_home = self._calculate_distance_to_home_stretch(piece, new_position)
            score += (52 - distance_to_home) * 2  # Closer to home = higher score
        
        # Priority 3: Avoid being captured
        if self._is_vulnerable_position(new_position):
            score -= 30
        
        # Priority 4: Enter home stretch
        if self._is_entering_home_stretch(piece, new_position):
            score += 40
        
        # Priority 5: Capture opponents
        captured_piece = self._check_capture_at_position(new_position)
        if captured_piece:
            score += 25
        
        return score
    
    def _calculate_move_score_hard(self, piece: Piece, new_position: int) -> float:
        """Calculate move score for hard difficulty"""
        if not self.game:
            return 0.0
            
        score = self._calculate_move_score_medium(piece, new_position)
        
        # Advanced strategies for hard AI
        
        # Priority 1: Block opponents aggressively
        blocking_value = self._calculate_blocking_value(new_position)
        score += blocking_value * 15
        
        # Priority 2: Protect pieces strategically
        if new_position in self.game.safe_positions:
            score += 20
        
        # Priority 3: Form protective groups
        group_bonus = self._calculate_group_bonus(new_position)
        score += group_bonus * 10
        
        # Priority 4: Prevent opponent captures
        prevention_bonus = self._calculate_capture_prevention(piece, new_position)
        score += prevention_bonus * 25
        
        # Priority 5: Optimal home stretch timing
        if self._is_entering_home_stretch(piece, new_position):
            timing_bonus = self._calculate_home_stretch_timing(piece)
            score += timing_bonus * 20
        
        # Priority 6: Aggressive capture when safe
        if self._check_capture_at_position(new_position):
            safety_multiplier = 2.0 if new_position in self.game.safe_positions else 1.0
            score += 30 * safety_multiplier
        
        return score
    
    def _calculate_distance_to_home_stretch(self, piece: Piece, position: int) -> int:
        """Calculate distance from position to home stretch entry"""
        if not self.game or piece.is_home or position == -1:
            return 0
        
        player = self.game.players[self.color]
        start_pos = player.start_position
        
        # Distance calculation considering board wrap-around
        if position >= start_pos:
            return self.game.board_size - position + start_pos
        else:
            return start_pos - position
    
    def _is_vulnerable_position(self, position: int) -> bool:
        """Check if position is vulnerable to capture"""
        if not self.game or position in self.game.safe_positions or position == -1:
            return False
        
        # Check if any opponent can capture at this position
        for color, player in self.game.players.items():
            if color == self.color:
                continue
            
            for piece in player.pieces:
                if piece.position == -1 or piece.is_home:
                    continue
                
                # Check if opponent can reach this position with dice 1-6
                for dice in range(1, 7):
                    opponent_new_pos = self.game._calculate_new_position(piece, dice)
                    if opponent_new_pos == position:
                        return True
        
        return False
    
    def _is_entering_home_stretch(self, piece: Piece, new_position: int) -> bool:
        """Check if move enters home stretch"""
        if not self.game:
            return False
        player = self.game.players[self.color]
        home_stretch = self.game.home_stretch_positions[self.color]
        return new_position in home_stretch and piece.position < player.home_position
    
    def _check_capture_at_position(self, position: int) -> Optional[Piece]:
        """Check if moving to position would capture an opponent"""
        if not self.game or position in self.game.safe_positions:
            return None
        
        for color, player in self.game.players.items():
            if color == self.color:
                continue
            
            for piece in player.pieces:
                if piece.position == position and not piece.is_home:
                    return piece
        
        return None
    
    def _calculate_blocking_value(self, position: int) -> float:
        """Calculate how valuable it is to block opponents at this position"""
        if not self.game:
            return 0.0
            
        blocking_value = 0.0
        
        for color, player in self.game.players.items():
            if color == self.color:
                continue
            
            for piece in player.pieces:
                if piece.position == -1 or piece.is_home:
                    continue
                
                # Check if this position blocks opponent's optimal path
                distance_to_position = abs(piece.position - position) % self.game.board_size
                if distance_to_position <= 6:  # Within one dice roll
                    # Higher value for blocking pieces closer to home
                    piece_progress = self._get_piece_progress(piece)
                    blocking_value += (piece_progress / 100) * (7 - distance_to_position)
        
        return blocking_value
    
    def _calculate_group_bonus(self, position: int) -> float:
        """Calculate bonus for forming protective groups"""
        if not self.game:
            return 0.0
            
        group_bonus = 0.0
        my_pieces_nearby = 0
        
        for piece in self.game.players[self.color].pieces:
            if piece.position == -1 or piece.is_home:
                continue
            
            distance = abs(piece.position - position) % self.game.board_size
            if distance <= 3:  # Within 3 positions
                my_pieces_nearby += 1
        
        # Bonus for having pieces nearby (safety in numbers)
        if my_pieces_nearby > 0:
            group_bonus = my_pieces_nearby * 0.5
        
        return group_bonus
    
    def _calculate_capture_prevention(self, piece: Piece, new_position: int) -> float:
        """Calculate bonus for preventing opponent captures"""
        if not self.game:
            return 0.0
            
        prevention_value = 0.0
        
        # Check if this move saves other pieces from capture
        for my_piece in self.game.players[self.color].pieces:
            if my_piece == piece or my_piece.position == -1 or my_piece.is_home:
                continue
            
            # Check if opponents can currently capture this piece
            current_threats = self._count_threats_to_piece(my_piece)
            
            # Simulate move and check threats after
            old_position = piece.position
            piece.position = new_position
            new_threats = self._count_threats_to_piece(my_piece)
            piece.position = old_position  # Restore
            
            if new_threats < current_threats:
                prevention_value += (current_threats - new_threats) * 10
        
        return prevention_value
    
    def _calculate_home_stretch_timing(self, piece: Piece) -> float:
        """Calculate optimal timing for entering home stretch"""
        if not self.game:
            return 0.5
            
        # Consider if other pieces need to be moved first
        player = self.game.players[self.color]
        pieces_behind = 0
        
        for other_piece in player.pieces:
            if other_piece.position == -1:  # Still in home area
                pieces_behind += 1
        
        # Prefer entering home stretch when most pieces are on board
        if pieces_behind <= 1:
            return 1.0
        else:
            return 0.5  # Lower priority if many pieces still at home
    
    def _get_piece_progress(self, piece: Piece) -> float:
        """Get piece progress as percentage (0-100)"""
        if not self.game:
            return 0.0
            
        if piece.position == -1:
            return 0.0
        if piece.is_home:
            return 100.0
        
        player = self.game.players[piece.player_color]
        start_pos = player.start_position
        
        # Calculate progress around the board
        if piece.position >= start_pos:
            progress = piece.position - start_pos
        else:
            progress = self.game.board_size - start_pos + piece.position
        
        return (progress / self.game.board_size) * 100
    
    def _count_threats_to_piece(self, piece: Piece) -> int:
        """Count how many opponents can capture this piece"""
        if not self.game or piece.position in self.game.safe_positions or piece.position == -1 or piece.is_home:
            return 0
        
        threats = 0
        for color, player in self.game.players.items():
            if color == self.color:
                continue
            
            for opponent_piece in player.pieces:
                if opponent_piece.position == -1 or opponent_piece.is_home:
                    continue
                
                # Check if opponent can reach this piece with any dice roll
                for dice in range(1, 7):
                    new_pos = self.game._calculate_new_position(opponent_piece, dice)
                    if new_pos == piece.position:
                        threats += 1
                        break  # Count each opponent piece only once
        
        return threats


class AIGameManager:
    """Manages AI players in a Ludo game"""
    
    def __init__(self, game: LudoGame):
        self.game = game
        self.ai_players: Dict[PlayerColor, AIPlayer] = {}
    
    def add_ai_player(self, color: PlayerColor, difficulty: AIDifficulty):
        """Add an AI player with specified difficulty"""
        ai_player = AIPlayer(color, difficulty)
        ai_player.set_game(self.game)
        self.ai_players[color] = ai_player
        return ai_player
    
    def is_ai_player(self, color: PlayerColor) -> bool:
        """Check if a player is controlled by AI"""
        return color in self.ai_players
    
    def make_ai_move(self) -> bool:
        """Make a move for the current player if they are AI"""
        current_player = self.game.current_player
        if current_player and current_player in self.ai_players:
            return self.ai_players[current_player].make_move()
        return False
    
    def get_ai_difficulty(self, color: PlayerColor) -> Optional[AIDifficulty]:
        """Get the difficulty level of an AI player"""
        if color in self.ai_players:
            return self.ai_players[color].difficulty
        return None