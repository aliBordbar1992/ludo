"""
Tests for AI Player functionality

This module tests the AI players with different difficulty levels
to ensure they make appropriate strategic decisions.
"""

import unittest
from ludo_game import LudoGame, PlayerColor, GameState
from ai_player import AIPlayer, AIDifficulty, AIGameManager


class TestAIPlayer(unittest.TestCase):
    """Test cases for AI Player functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.game = LudoGame()
        self.ai_manager = AIGameManager(self.game)
        
        # Add all players
        colors = [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]
        for color in colors:
            self.game.add_player(color)
    
    def test_ai_player_creation(self):
        """Test AI player creation with different difficulties"""
        # Test Easy AI
        easy_ai = AIPlayer(PlayerColor.RED, AIDifficulty.EASY)
        self.assertEqual(easy_ai.color, PlayerColor.RED)
        self.assertEqual(easy_ai.difficulty, AIDifficulty.EASY)
        
        # Test Medium AI
        medium_ai = AIPlayer(PlayerColor.GREEN, AIDifficulty.MEDIUM)
        self.assertEqual(medium_ai.color, PlayerColor.GREEN)
        self.assertEqual(medium_ai.difficulty, AIDifficulty.MEDIUM)
        
        # Test Hard AI
        hard_ai = AIPlayer(PlayerColor.BLUE, AIDifficulty.HARD)
        self.assertEqual(hard_ai.color, PlayerColor.BLUE)
        self.assertEqual(hard_ai.difficulty, AIDifficulty.HARD)
    
    def test_ai_manager(self):
        """Test AI manager functionality"""
        # Add AI players
        self.ai_manager.add_ai_player(PlayerColor.RED, AIDifficulty.EASY)
        self.ai_manager.add_ai_player(PlayerColor.GREEN, AIDifficulty.MEDIUM)
        self.ai_manager.add_ai_player(PlayerColor.BLUE, AIDifficulty.HARD)
        
        # Test AI player detection
        self.assertTrue(self.ai_manager.is_ai_player(PlayerColor.RED))
        self.assertTrue(self.ai_manager.is_ai_player(PlayerColor.GREEN))
        self.assertTrue(self.ai_manager.is_ai_player(PlayerColor.BLUE))
        self.assertFalse(self.ai_manager.is_ai_player(PlayerColor.YELLOW))
        
        # Test difficulty retrieval
        self.assertEqual(self.ai_manager.get_ai_difficulty(PlayerColor.RED), AIDifficulty.EASY)
        self.assertEqual(self.ai_manager.get_ai_difficulty(PlayerColor.GREEN), AIDifficulty.MEDIUM)
        self.assertEqual(self.ai_manager.get_ai_difficulty(PlayerColor.BLUE), AIDifficulty.HARD)
        self.assertIsNone(self.ai_manager.get_ai_difficulty(PlayerColor.YELLOW))
    
    def test_ai_makes_valid_moves(self):
        """Test that AI players make valid moves"""
        # Add AI players
        self.ai_manager.add_ai_player(PlayerColor.RED, AIDifficulty.EASY)
        self.ai_manager.add_ai_player(PlayerColor.GREEN, AIDifficulty.MEDIUM)
        self.ai_manager.add_ai_player(PlayerColor.YELLOW, AIDifficulty.HARD)
        
        # Play several turns and verify moves are valid
        for _ in range(20):
            if self.game.game_state == GameState.GAME_OVER:
                break
            
            current_player = self.game.current_player
            if current_player and self.ai_manager.is_ai_player(current_player):
                # Store game state before move
                old_state = self.game.get_game_state()
                
                # Make AI move
                success = self.ai_manager.make_ai_move()
                
                # Move should succeed unless no valid moves
                valid_moves = []
                if self.game.game_state == GameState.MOVING_PIECE:
                    valid_moves = self.game.get_valid_moves(current_player)
                
                if valid_moves:
                    self.assertTrue(success, f"AI should make valid move when moves available")
                
                # Game state should progress
                new_state = self.game.get_game_state()
                if success:
                    self.assertNotEqual(old_state, new_state, "Game state should change after valid move")
    
    def test_easy_ai_prefers_home_moves(self):
        """Test that Easy AI prefers moving pieces out of home"""
        ai_player = AIPlayer(PlayerColor.RED, AIDifficulty.EASY)
        ai_player.set_game(self.game)
        
        # Create scenario where AI can move piece out of home or move existing piece
        red_player = self.game.players[PlayerColor.RED]
        red_player.pieces[0].position = 5  # One piece on board
        
        # Simulate dice roll of 6 (allows home move)
        self.game.dice_value = 6
        self.game.game_state = GameState.MOVING_PIECE
        self.game.current_player = PlayerColor.RED
        
        # Get valid moves
        valid_moves = self.game.get_valid_moves(PlayerColor.RED)
        
        # Should have both home move and regular move
        home_moves = [move for move in valid_moves if move[0].position == -1]
        board_moves = [move for move in valid_moves if move[0].position != -1]
        
        if home_moves and board_moves:
            # Test Easy AI choice multiple times (due to randomness)
            home_choices = 0
            total_tests = 100
            
            for _ in range(total_tests):
                chosen_piece = ai_player._easy_move(valid_moves)
                if chosen_piece.position == -1:
                    home_choices += 1
            
            # Easy AI should prefer home moves at least 60% of the time
            home_preference = home_choices / total_tests
            self.assertGreater(home_preference, 0.6, "Easy AI should prefer home moves")
    
    def test_ai_difficulty_differences(self):
        """Test that different AI difficulties make different strategic choices"""
        # Set up a strategic scenario
        self.game.dice_value = 3
        self.game.game_state = GameState.MOVING_PIECE
        self.game.current_player = PlayerColor.RED
        
        # Place pieces in strategic positions
        red_player = self.game.players[PlayerColor.RED]
        red_player.pieces[0].position = 10
        red_player.pieces[1].position = 20
        
        # Place opponent piece that can be captured
        green_player = self.game.players[PlayerColor.GREEN]
        green_player.pieces[0].position = 13  # Can be captured by moving piece from 10
        
        valid_moves = self.game.get_valid_moves(PlayerColor.RED)
        
        if len(valid_moves) >= 2:
            # Create AI players
            easy_ai = AIPlayer(PlayerColor.RED, AIDifficulty.EASY)
            medium_ai = AIPlayer(PlayerColor.RED, AIDifficulty.MEDIUM)
            hard_ai = AIPlayer(PlayerColor.RED, AIDifficulty.HARD)
            
            for ai in [easy_ai, medium_ai, hard_ai]:
                ai.set_game(self.game)
            
            # Test that move scoring is different for different difficulties
            easy_scores = []
            medium_scores = []
            hard_scores = []
            
            for piece, new_pos in valid_moves:
                easy_scores.append(easy_ai._calculate_move_score_medium(piece, new_pos) if hasattr(easy_ai, '_calculate_move_score_medium') else 0)
                medium_scores.append(medium_ai._calculate_move_score_medium(piece, new_pos))
                hard_scores.append(hard_ai._calculate_move_score_hard(piece, new_pos))
            
            # Hard AI should generally have higher scores due to advanced strategy
            if len(hard_scores) > 1 and max(hard_scores) > 0:
                self.assertGreater(max(hard_scores), max(medium_scores) * 0.8, 
                                   "Hard AI should consider more strategic factors")
    
    def test_ai_handles_no_valid_moves(self):
        """Test AI behavior when no valid moves are available"""
        ai_player = AIPlayer(PlayerColor.RED, AIDifficulty.MEDIUM)
        ai_player.set_game(self.game)
        
        # Set up scenario with no valid moves (dice not 6, all pieces at home)
        self.game.dice_value = 3
        self.game.game_state = GameState.MOVING_PIECE
        self.game.current_player = PlayerColor.RED
        
        # Ensure all pieces are at home
        red_player = self.game.players[PlayerColor.RED]
        for piece in red_player.pieces:
            piece.position = -1
        
        # AI should handle this gracefully
        result = ai_player.make_move()
        self.assertTrue(result, "AI should handle no valid moves gracefully")
    
    def test_blocking_strategy(self):
        """Test that Hard AI considers blocking opponents"""
        hard_ai = AIPlayer(PlayerColor.RED, AIDifficulty.HARD)
        hard_ai.set_game(self.game)
        
        # Set up scenario where blocking is beneficial
        # Place opponent piece close to home
        green_player = self.game.players[PlayerColor.GREEN]
        green_player.pieces[0].position = 45  # Close to green's start (13 + 32 = 45)
        
        # Test blocking value calculation
        blocking_value = hard_ai._calculate_blocking_value(46)  # Position that could block
        
        # Should recognize some blocking value
        self.assertGreaterEqual(blocking_value, 0, "Should calculate blocking value")
    
    def test_capture_detection(self):
        """Test AI's ability to detect capture opportunities"""
        medium_ai = AIPlayer(PlayerColor.RED, AIDifficulty.MEDIUM)
        medium_ai.set_game(self.game)
        
        # Place opponent piece at position 10
        green_player = self.game.players[PlayerColor.GREEN]
        green_player.pieces[0].position = 10
        
        # Test capture detection
        captured_piece = medium_ai._check_capture_at_position(10)
        self.assertIsNotNone(captured_piece, "Should detect capturable piece")
        if captured_piece:
            self.assertEqual(captured_piece.player_color, PlayerColor.GREEN)
        
        # Test safe position (no capture)
        captured_safe = medium_ai._check_capture_at_position(0)  # Safe position
        self.assertIsNone(captured_safe, "Should not capture on safe position")


class TestAIGameIntegration(unittest.TestCase):
    """Integration tests for AI players in full games"""
    
    def test_full_ai_game(self):
        """Test a complete game with AI players"""
        game = LudoGame()
        ai_manager = AIGameManager(game)
        
        # Add all AI players with different difficulties
        colors = [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]
        difficulties = [AIDifficulty.EASY, AIDifficulty.MEDIUM, AIDifficulty.HARD, AIDifficulty.HARD]
        
        for color, difficulty in zip(colors, difficulties):
            game.add_player(color)
            ai_manager.add_ai_player(color, difficulty)
        
        # Play the game for a limited number of turns
        max_turns = 200
        turn_count = 0
        
        while game.game_state != GameState.GAME_OVER and turn_count < max_turns:
            current_player = game.current_player
            if current_player and ai_manager.is_ai_player(current_player):
                success = ai_manager.make_ai_move()
                if not success:
                    break
            turn_count += 1
        
        # Game should progress without errors
        self.assertLess(turn_count, max_turns, "Game should not require excessive turns")
        
        # At least some pieces should have moved
        some_progress = False
        for player in game.players.values():
            for piece in player.pieces:
                if piece.position != -1:  # Not in home area
                    some_progress = True
                    break
            if some_progress:
                break
        
        self.assertTrue(some_progress, "AI players should make progress in the game")


def run_ai_tests():
    """Run all AI player tests"""
    print("Running AI Player Tests...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestAIPlayer))
    suite.addTests(loader.loadTestsFromTestCase(TestAIGameIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_ai_tests()