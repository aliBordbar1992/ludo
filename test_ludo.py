"""
Tests for Ludo Game Logic

This module contains comprehensive tests for the Ludo game implementation.
"""

import unittest
from unittest.mock import Mock
from ludo_game import (
    LudoGame, PlayerColor, GameState, EventType, 
    Player, Piece, GameEvent
)


class TestLudoGame(unittest.TestCase):
    """Test cases for the Ludo game"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.game = LudoGame()
        self.event_listener = Mock()
        self.game.add_event_listener(self.event_listener)
    
    def test_add_players(self):
        """Test adding players to the game"""
        # Add all four players
        self.assertTrue(self.game.add_player(PlayerColor.RED))
        self.assertTrue(self.game.add_player(PlayerColor.GREEN))
        self.assertTrue(self.game.add_player(PlayerColor.YELLOW))
        self.assertTrue(self.game.add_player(PlayerColor.BLUE))
        
        # Try to add duplicate player
        self.assertFalse(self.game.add_player(PlayerColor.RED))
        
        # Check that game started
        self.assertEqual(self.game.game_state, GameState.ROLLING_DICE)
        self.assertEqual(self.game.current_player, PlayerColor.RED)
    
    def test_remove_players(self):
        """Test removing players from the game"""
        self.game.add_player(PlayerColor.RED)
        self.game.add_player(PlayerColor.GREEN)
        
        self.assertTrue(self.game.remove_player(PlayerColor.RED))
        self.assertFalse(self.game.remove_player(PlayerColor.RED))  # Already removed
        self.assertFalse(self.game.remove_player(PlayerColor.BLUE))  # Never added
    
    def test_dice_roll(self):
        """Test dice rolling functionality"""
        # Set up game
        for color in [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]:
            self.game.add_player(color)
        
        # Test dice roll
        dice_value = self.game.roll_dice()
        self.assertGreaterEqual(dice_value, 1)
        self.assertLessEqual(dice_value, 6)
        self.assertEqual(self.game.game_state, GameState.MOVING_PIECE)
        self.assertEqual(self.game.dice_value, dice_value)
    
    def test_piece_movement(self):
        """Test piece movement logic"""
        # Set up game
        for color in [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]:
            self.game.add_player(color)
        
        # Roll a 6 to get a piece out
        self.game.roll_dice()
        if self.game.dice_value == 6:
            # Move piece 0 out
            success = self.game.move_piece(PlayerColor.RED, 0)
            self.assertTrue(success)
            
            # Check piece position
            red_player = self.game.players[PlayerColor.RED]
            piece = red_player.pieces[0]
            self.assertEqual(piece.position, 0)
    
    def test_invalid_moves(self):
        """Test invalid move detection"""
        # Set up game
        for color in [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]:
            self.game.add_player(color)
        
        # Try to move when it's not your turn
        self.assertFalse(self.game.move_piece(PlayerColor.GREEN, 0))
        
        # Try to move invalid piece ID
        self.game.roll_dice()
        self.assertFalse(self.game.move_piece(PlayerColor.RED, 10))  # Invalid piece ID
    
    def test_piece_capture(self):
        """Test piece capture mechanics"""
        # Set up game
        for color in [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]:
            self.game.add_player(color)
        
        # Get pieces to position 1 (not safe)
        self.game.roll_dice()
        if self.game.dice_value == 6:
            self.game.move_piece(PlayerColor.RED, 0)  # Red piece to position 0
        
        # Move green piece to capture red piece
        self.game.roll_dice()
        if self.game.dice_value == 1:
            self.game.move_piece(PlayerColor.GREEN, 0)  # Green piece to position 1
            
            # Check that red piece was captured (reset to -1)
            red_piece = self.game.players[PlayerColor.RED].pieces[0]
            self.assertEqual(red_piece.position, -1)
    
    def test_safe_positions(self):
        """Test safe position mechanics"""
        # Set up game
        for color in [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]:
            self.game.add_player(color)
        
        # Get pieces to safe positions
        self.game.roll_dice()
        if self.game.dice_value == 6:
            self.game.move_piece(PlayerColor.RED, 0)  # Red piece to position 0 (safe)
        
        # Try to capture piece on safe position
        self.game.roll_dice()
        if self.game.dice_value == 6:
            self.game.move_piece(PlayerColor.GREEN, 0)  # Green piece to position 0
            
            # Red piece should still be there (safe position)
            red_piece = self.game.players[PlayerColor.RED].pieces[0]
            self.assertEqual(red_piece.position, 0)
    
    def test_home_stretch(self):
        """Test home stretch mechanics"""
        # Set up game
        for color in [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]:
            self.game.add_player(color)
        
        # Manually set piece to near home stretch
        red_player = self.game.players[PlayerColor.RED]
        piece = red_player.pieces[0]
        piece.position = 49  # Just before home stretch
        
        # Roll dice to enter home stretch
        self.game.roll_dice()
        if self.game.dice_value == 1:
            self.game.move_piece(PlayerColor.RED, 0)
            
            # Check if piece entered home stretch
            self.assertGreaterEqual(piece.position, 50)
    
    def test_winning_condition(self):
        """Test winning condition"""
        # Set up game
        for color in [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]:
            self.game.add_player(color)
        
        # Manually set all red pieces to home
        red_player = self.game.players[PlayerColor.RED]
        for piece in red_player.pieces:
            piece.position = 55  # Final home position
            piece.is_home = True
        
        red_player.home_count = 4
        
        # Check winning condition
        self.assertTrue(red_player.has_won())
    
    def test_valid_moves(self):
        """Test valid move calculation"""
        # Set up game
        for color in [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]:
            self.game.add_player(color)
        
        # Roll dice
        self.game.roll_dice()
        
        # Get valid moves
        valid_moves = self.game.get_valid_moves(PlayerColor.RED)
        
        # If dice is 6, should be able to move pieces from home
        if self.game.dice_value == 6:
            self.assertGreater(len(valid_moves), 0)
    
    def test_event_system(self):
        """Test event system"""
        # Set up game
        for color in [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]:
            self.game.add_player(color)
        
        # Check that game started event was emitted
        self.event_listener.assert_called()
        call_args = self.event_listener.call_args_list
        game_started_calls = [call for call in call_args 
                            if call[0][0].event_type == EventType.GAME_STARTED]
        self.assertGreater(len(game_started_calls), 0)
    
    def test_game_state_serialization(self):
        """Test game state serialization"""
        # Set up game
        for color in [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]:
            self.game.add_player(color)
        
        # Get game state
        state = self.game.get_game_state()
        
        # Check required fields
        self.assertIn('game_state', state)
        self.assertIn('current_player', state)
        self.assertIn('dice_value', state)
        self.assertIn('players', state)
        
        # Check player data structure
        for player_data in state['players'].values():
            self.assertIn('home_count', player_data)
            self.assertIn('has_won', player_data)
            self.assertIn('pieces', player_data)
            
            for piece_data in player_data['pieces']:
                self.assertIn('piece_id', piece_data)
                self.assertIn('position', piece_data)
                self.assertIn('is_home', piece_data)
                self.assertIn('is_safe', piece_data)
    
    def test_reset_game(self):
        """Test game reset functionality"""
        # Set up game and make some moves
        for color in [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]:
            self.game.add_player(color)
        
        self.game.roll_dice()
        if self.game.dice_value == 6:
            self.game.move_piece(PlayerColor.RED, 0)
        
        # Reset game
        self.game.reset_game()
        
        # Check that all pieces are reset
        for player in self.game.players.values():
            for piece in player.pieces:
                self.assertEqual(piece.position, -1)
                self.assertFalse(piece.is_home)
                self.assertFalse(piece.is_safe)
            self.assertEqual(player.home_count, 0)


class TestPlayer(unittest.TestCase):
    """Test cases for Player class"""
    
    def test_player_creation(self):
        """Test player creation"""
        player = Player(PlayerColor.RED)
        
        self.assertEqual(player.color, PlayerColor.RED)
        self.assertEqual(len(player.pieces), 4)
        self.assertEqual(player.home_count, 0)
        self.assertEqual(player.start_position, 0)
        self.assertEqual(player.home_position, 50)
    
    def test_piece_queries(self):
        """Test piece query methods"""
        player = Player(PlayerColor.RED)
        
        # Initially all pieces should be in home
        self.assertEqual(len(player.get_pieces_in_home()), 4)
        self.assertEqual(len(player.get_pieces_on_board()), 0)
        self.assertEqual(len(player.get_pieces_in_final_home()), 0)
        
        # Move a piece out
        player.pieces[0].position = 0
        self.assertEqual(len(player.get_pieces_in_home()), 3)
        self.assertEqual(len(player.get_pieces_on_board()), 1)
    
    def test_winning_condition(self):
        """Test winning condition check"""
        player = Player(PlayerColor.RED)
        
        # Initially not won
        self.assertFalse(player.has_won())
        
        # Set all pieces to home
        for piece in player.pieces:
            piece.is_home = True
        
        self.assertTrue(player.has_won())


class TestPiece(unittest.TestCase):
    """Test cases for Piece class"""
    
    def test_piece_creation(self):
        """Test piece creation"""
        piece = Piece(PlayerColor.RED, 0)
        
        self.assertEqual(piece.player_color, PlayerColor.RED)
        self.assertEqual(piece.piece_id, 0)
        self.assertEqual(piece.position, -1)
        self.assertFalse(piece.is_home)
        self.assertFalse(piece.is_safe)
    
    def test_piece_reset(self):
        """Test piece reset"""
        piece = Piece(PlayerColor.RED, 0)
        piece.position = 10
        piece.is_home = True
        piece.is_safe = True
        
        piece.reset()
        
        self.assertEqual(piece.position, -1)
        self.assertFalse(piece.is_home)
        self.assertFalse(piece.is_safe)


if __name__ == '__main__':
    unittest.main()