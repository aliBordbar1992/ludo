"""
AI CLI Example for Ludo Game

This demonstrates how to use the AI players with different difficulty levels
in the Ludo game. Players can choose to play against AI opponents or watch
AI vs AI matches.
"""

from ludo_game import LudoGame, PlayerColor, GameState, EventType
from ai_player import AIPlayer, AIDifficulty, AIGameManager
import time
import random


class AILudoCLI:
    """CLI interface for Ludo game with AI players"""
    
    def __init__(self):
        self.game = LudoGame()
        self.ai_manager = AIGameManager(self.game)
        self.game.add_event_listener(self._handle_event)
        self.human_players = set()
        self.move_delay = 1.0  # Delay between AI moves for better visualization
    
    def _handle_event(self, event):
        """Handle game events"""
        if event.event_type == EventType.GAME_STARTED:
            print(f"\n🎮 Game started! Players: {', '.join(event.data['players'])}")
            self._show_player_types()
        
        elif event.event_type == EventType.DICE_ROLLED:
            dice = event.data['dice_value']
            player_type = "Human" if event.player_color in self.human_players else "AI"
            difficulty = ""
            if event.player_color not in self.human_players:
                ai_diff = self.ai_manager.get_ai_difficulty(event.player_color)
                difficulty = f" ({ai_diff.value.capitalize()})" if ai_diff else ""
            
            print(f"🎲 {event.player_color.value.capitalize()} {player_type}{difficulty} rolled a {dice}")
        
        elif event.event_type == EventType.PIECE_MOVED:
            data = event.data
            player_type = "Human" if event.player_color in self.human_players else "AI"
            print(f"♟️  {event.player_color.value.capitalize()} {player_type} moved piece {data['piece_id']} "
                  f"from position {data['old_position']} to {data['new_position']}")
        
        elif event.event_type == EventType.PLAYER_TURN_CHANGED:
            player_type = "Human" if event.data['player_color'] in [p.value for p in self.human_players] else "AI"
            print(f"👤 {event.data['player_color'].capitalize()} {player_type}'s turn")
        
        elif event.event_type == EventType.PIECE_CAPTURED:
            print(f"💥 {event.data['captured_piece']} was captured by {event.data['capturing_piece']}")
        
        elif event.event_type == EventType.PIECE_HOME:
            print(f"🏠 {event.data['player_color'].capitalize()} piece {event.data['piece_id']} reached home!")
        
        elif event.event_type == EventType.GAME_OVER:
            winner_color = PlayerColor(event.data['winner'])
            winner_type = "Human" if winner_color in self.human_players else "AI"
            difficulty = ""
            if winner_color not in self.human_players:
                ai_diff = self.ai_manager.get_ai_difficulty(winner_color)
                difficulty = f" ({ai_diff.value.capitalize()})" if ai_diff else ""
            
            print(f"🏆 {event.data['winner'].capitalize()} {winner_type}{difficulty} wins the game!")
        
        elif event.event_type == EventType.INVALID_MOVE:
            print(f"❌ Invalid move attempted")
    
    def _show_player_types(self):
        """Display player types and difficulties"""
        print("\nPlayer Setup:")
        for color in [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]:
            if color in self.human_players:
                print(f"  {color.value.capitalize()}: Human Player")
            else:
                difficulty = self.ai_manager.get_ai_difficulty(color)
                if difficulty:
                    print(f"  {color.value.capitalize()}: AI Player ({difficulty.value.capitalize()})")
                else:
                    print(f"  {color.value.capitalize()}: Not in game")
        print()
    
    def _display_board(self):
        """Display the current game state"""
        state = self.game.get_game_state()
        print("\n" + "="*60)
        print("LUDO BOARD")
        print("="*60)
        
        for color_name, player_data in state['players'].items():
            color = PlayerColor(color_name)
            player_type = "Human" if color in self.human_players else "AI"
            difficulty = ""
            if color not in self.human_players:
                ai_diff = self.ai_manager.get_ai_difficulty(color)
                difficulty = f" ({ai_diff.value.capitalize()})" if ai_diff else ""
            
            print(f"\n{color_name.upper()} {player_type}{difficulty}:")
            print(f"  Home pieces: {player_data['home_count']}/4")
            print(f"  Has won: {player_data['has_won']}")
            
            for piece in player_data['pieces']:
                status = "🏠 HOME" if piece['is_home'] else f"Position {piece['position']}"
                safe = " (SAFE)" if piece['is_safe'] else ""
                print(f"    Piece {piece['piece_id']}: {status}{safe}")
        
        print(f"\nCurrent player: {state['current_player']}")
        print(f"Game state: {state['game_state']}")
        if state['dice_value'] > 0:
            print(f"Last dice roll: {state['dice_value']}")
        print("="*60)
    
    def _get_human_move(self, player_color):
        """Get move from human player"""
        if self.game.game_state == GameState.ROLLING_DICE:
            input(f"\n{player_color.value.capitalize()}, press Enter to roll dice: ")
            dice = self.game.roll_dice()
            print(f"🎲 You rolled: {dice}")
        
        if self.game.game_state == GameState.MOVING_PIECE:
            valid_moves = self.game.get_valid_moves(player_color)
            
            if not valid_moves:
                print("No valid moves available. Turn skipped.")
                self.game._next_turn()
                return
            
            print("\nValid moves:")
            for i, (piece, new_position) in enumerate(valid_moves):
                status = "HOME AREA" if piece.position == -1 else f"Position {piece.position}"
                print(f"  {i+1}. Move piece {piece.piece_id} from {status} to position {new_position}")
            
            while True:
                try:
                    choice = input(f"\nChoose move (1-{len(valid_moves)}): ").strip()
                    if choice.lower() == 'q':
                        return
                    
                    move_idx = int(choice) - 1
                    if 0 <= move_idx < len(valid_moves):
                        piece, _ = valid_moves[move_idx]
                        success = self.game.move_piece(player_color, piece.piece_id)
                        if not success:
                            print("Move failed. Try again.")
                        else:
                            break
                    else:
                        print("Invalid choice. Try again.")
                except ValueError:
                    print("Please enter a number.")
    
    def setup_game(self):
        """Setup the game with player choices"""
        print("🎮 Welcome to Ludo with AI!")
        print("\nGame Setup:")
        print("1. Human vs 3 AI (Easy, Medium, Hard)")
        print("2. Human vs 3 AI (All Hard)")
        print("3. AI vs AI (watch different difficulties)")
        print("4. Custom setup")
        print("5. Quick demo (all AI, fast)")
        
        choice = input("\nChoose setup (1-5): ").strip()
        
        if choice == "1":
            self._setup_human_vs_mixed_ai()
        elif choice == "2":
            self._setup_human_vs_hard_ai()
        elif choice == "3":
            self._setup_ai_vs_ai()
        elif choice == "4":
            self._setup_custom()
        elif choice == "5":
            self._setup_quick_demo()
        else:
            print("Invalid choice, using default setup (Human vs 3 AI)")
            self._setup_human_vs_mixed_ai()
    
    def _setup_human_vs_mixed_ai(self):
        """Setup human vs AI with different difficulties"""
        colors = [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]
        difficulties = [None, AIDifficulty.EASY, AIDifficulty.MEDIUM, AIDifficulty.HARD]
        
        # Human is red, others are AI
        self.human_players.add(PlayerColor.RED)
        
        for i, color in enumerate(colors):
            self.game.add_player(color)
            if i > 0:  # AI players
                self.ai_manager.add_ai_player(color, difficulties[i])
        
        print(f"\nYou are playing as {PlayerColor.RED.value.capitalize()} (Human)")
        print("AI opponents:")
        print(f"  {PlayerColor.GREEN.value.capitalize()}: Easy AI")
        print(f"  {PlayerColor.YELLOW.value.capitalize()}: Medium AI")
        print(f"  {PlayerColor.BLUE.value.capitalize()}: Hard AI")
    
    def _setup_human_vs_hard_ai(self):
        """Setup human vs 3 hard AI"""
        colors = [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]
        
        # Human is red, others are hard AI
        self.human_players.add(PlayerColor.RED)
        
        for color in colors:
            self.game.add_player(color)
            if color != PlayerColor.RED:
                self.ai_manager.add_ai_player(color, AIDifficulty.HARD)
        
        print(f"\nYou are playing as {PlayerColor.RED.value.capitalize()} (Human)")
        print("All AI opponents are set to Hard difficulty. Good luck!")
    
    def _setup_ai_vs_ai(self):
        """Setup AI vs AI with different difficulties"""
        colors = [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]
        difficulties = [AIDifficulty.EASY, AIDifficulty.MEDIUM, AIDifficulty.HARD, AIDifficulty.HARD]
        names = ["Easy", "Medium", "Hard", "Hard"]
        
        for color, difficulty in zip(colors, difficulties):
            self.game.add_player(color)
            self.ai_manager.add_ai_player(color, difficulty)
        
        print("\nAI vs AI match:")
        for color, name in zip(colors, names):
            print(f"  {color.value.capitalize()}: {name} AI")
        
        self.move_delay = 0.5  # Faster for AI vs AI
    
    def _setup_custom(self):
        """Custom game setup"""
        colors = [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]
        
        for color in colors:
            print(f"\nSetup for {color.value.capitalize()}:")
            print("1. Human player")
            print("2. Easy AI")
            print("3. Medium AI") 
            print("4. Hard AI")
            print("5. Skip this player")
            
            choice = input("Choose (1-5): ").strip()
            
            if choice == "1":
                self.game.add_player(color)
                self.human_players.add(color)
            elif choice == "2":
                self.game.add_player(color)
                self.ai_manager.add_ai_player(color, AIDifficulty.EASY)
            elif choice == "3":
                self.game.add_player(color)
                self.ai_manager.add_ai_player(color, AIDifficulty.MEDIUM)
            elif choice == "4":
                self.game.add_player(color)
                self.ai_manager.add_ai_player(color, AIDifficulty.HARD)
            # Choice 5 or invalid: skip player
        
        if len(self.game.players) < 2:
            print("Need at least 2 players. Adding AI players...")
            remaining_colors = [c for c in colors if c not in self.game.players]
            for color in remaining_colors[:2]:
                self.game.add_player(color)
                self.ai_manager.add_ai_player(color, AIDifficulty.MEDIUM)
    
    def _setup_quick_demo(self):
        """Quick demo with all AI"""
        colors = [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]
        difficulties = [AIDifficulty.EASY, AIDifficulty.MEDIUM, AIDifficulty.HARD, AIDifficulty.HARD]
        
        for color, difficulty in zip(colors, difficulties):
            self.game.add_player(color)
            self.ai_manager.add_ai_player(color, difficulty)
        
        self.move_delay = 0.2  # Very fast for demo
        print("\nQuick demo: All AI players, accelerated gameplay")
    
    def play_game(self):
        """Play the game"""
        print("\n🎯 Game starting!")
        print("Controls: Press Enter to continue, 'q' to quit, 'b' to show board")
        
        turn_count = 0
        max_turns = 500  # Prevent infinite games
        
        while (self.game.game_state != GameState.GAME_OVER and 
               turn_count < max_turns):
            
            current_player = self.game.current_player
            if not current_player:
                break
            
            # Handle human player turn
            if current_player in self.human_players:
                self._get_human_move(current_player)
            
            # Handle AI player turn
            elif self.ai_manager.is_ai_player(current_player):
                if len(self.human_players) > 0:
                    # Show AI thinking when humans are playing
                    difficulty = self.ai_manager.get_ai_difficulty(current_player)
                    difficulty_str = difficulty.value.capitalize() if difficulty else "Unknown"
                    print(f"\n🤖 {current_player.value.capitalize()} AI ({difficulty_str}) is thinking...")
                    time.sleep(self.move_delay)
                
                success = self.ai_manager.make_ai_move()
                if not success:
                    print(f"AI move failed for {current_player.value}")
                    break
                
                # Add delay for better visualization
                if len(self.human_players) > 0:
                    time.sleep(self.move_delay * 0.5)
            
            turn_count += 1
            
            # Show board periodically for AI vs AI
            if len(self.human_players) == 0 and turn_count % 20 == 0:
                self._display_board()
                time.sleep(1)
        
        if self.game.game_state == GameState.GAME_OVER:
            print("\n🎉 Game finished!")
            self._display_board()
        else:
            print(f"\n⏰ Game stopped after {turn_count} turns")
    
    def run(self):
        """Run the complete game flow"""
        self.setup_game()
        
        if len(self.game.players) < 2:
            print("Not enough players to start the game.")
            return
        
        self.play_game()


def main():
    """Main function to run the AI Ludo game"""
    try:
        game = AILudoCLI()
        game.run()
    except KeyboardInterrupt:
        print("\n\n👋 Game interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")


if __name__ == "__main__":
    main()