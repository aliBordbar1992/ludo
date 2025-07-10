"""
CLI Example for Ludo Game

This demonstrates how to use the core Ludo game logic with a simple command-line interface.
"""

from ludo_game import LudoGame, PlayerColor, GameState, EventType
import random


class CLIGame:
    """Simple CLI interface for the Ludo game"""
    
    def __init__(self):
        self.game = LudoGame()
        self.game.add_event_listener(self._handle_event)
        self._setup_players()
    
    def _setup_players(self):
        """Add all four players to the game"""
        colors = [PlayerColor.RED, PlayerColor.GREEN, PlayerColor.YELLOW, PlayerColor.BLUE]
        for color in colors:
            self.game.add_player(color)
    
    def _handle_event(self, event):
        """Handle game events"""
        if event.event_type == EventType.GAME_STARTED:
            print(f"\n🎮 Game started! Players: {', '.join(event.data['players'])}")
        
        elif event.event_type == EventType.DICE_ROLLED:
            print(f"🎲 {event.player_color.value.capitalize()} rolled a {event.data['dice_value']}")
        
        elif event.event_type == EventType.PIECE_MOVED:
            data = event.data
            print(f"♟️  {event.player_color.value.capitalize()} moved piece {data['piece_id']} "
                  f"from position {data['old_position']} to {data['new_position']}")
        
        elif event.event_type == EventType.PLAYER_TURN_CHANGED:
            print(f"👤 {event.data['player_color'].capitalize()}'s turn")
        
        elif event.event_type == EventType.PIECE_CAPTURED:
            print(f"💥 {event.data['captured_piece']} was captured by {event.data['capturing_piece']}")
        
        elif event.event_type == EventType.PIECE_HOME:
            print(f"🏠 {event.data['player_color'].capitalize()} piece {event.data['piece_id']} reached home!")
        
        elif event.event_type == EventType.GAME_OVER:
            print(f"🏆 {event.data['winner'].capitalize()} wins the game!")
        
        elif event.event_type == EventType.INVALID_MOVE:
            print(f"❌ Invalid move attempted")
    
    def _display_board(self):
        """Display the current game state"""
        state = self.game.get_game_state()
        print("\n" + "="*50)
        print("LUDO BOARD")
        print("="*50)
        
        for color_name, player_data in state['players'].items():
            print(f"\n{color_name.upper()}:")
            print(f"  Home pieces: {player_data['home_count']}")
            print(f"  Has won: {player_data['has_won']}")
            
            for piece in player_data['pieces']:
                status = "🏠 HOME" if piece['is_home'] else f"Position {piece['position']}"
                safe = " (SAFE)" if piece['is_safe'] else ""
                print(f"    Piece {piece['piece_id']}: {status}{safe}")
        
        print(f"\nCurrent player: {state['current_player']}")
        print(f"Game state: {state['game_state']}")
        if state['dice_value'] > 0:
            print(f"Last dice roll: {state['dice_value']}")
        print("="*50)
    
    def _get_valid_moves(self, player_color):
        """Get and display valid moves for a player"""
        valid_moves = self.game.get_valid_moves(player_color)
        if not valid_moves:
            print("No valid moves available.")
            return []
        
        print("Valid moves:")
        for i, (piece, new_position) in enumerate(valid_moves):
            status = "HOME" if piece.is_home else f"Position {piece.position}"
            print(f"  {i+1}. Move piece {piece.piece_id} ({status}) to position {new_position}")
        
        return valid_moves
    
    def _auto_play_turn(self, player_color):
        """Automatically play a turn for a player"""
        if self.game.game_state == GameState.ROLLING_DICE:
            dice = self.game.roll_dice()
            print(f"\n🎲 {player_color.value.capitalize()} rolled: {dice}")
        
        if self.game.game_state == GameState.MOVING_PIECE:
            valid_moves = self.game.get_valid_moves(player_color)
            
            if valid_moves:
                # Choose a random valid move
                piece, new_position = random.choice(valid_moves)
                success = self.game.move_piece(player_color, piece.piece_id)
                if success:
                    print(f"♟️  {player_color.value.capitalize()} moved piece {piece.piece_id}")
                else:
                    print(f"❌ {player_color.value.capitalize()} failed to move piece {piece.piece_id}")
            else:
                print(f"😴 {player_color.value.capitalize()} has no valid moves, skipping turn")
                # Force next turn
                self.game._next_turn()
    
    def play_game(self, auto_play=True, max_turns=100):
        """Play the game"""
        print("🎮 Starting Ludo Game!")
        print("Press Enter to continue or 'q' to quit")
        
        turn_count = 0
        
        while (self.game.game_state != GameState.GAME_OVER and 
               turn_count < max_turns):
            
            if not auto_play:
                input_val = input("\nPress Enter for next turn or 'q' to quit: ")
                if input_val.lower() == 'q':
                    break
            
            if self.game.current_player:
                self._auto_play_turn(self.game.current_player)
                turn_count += 1
            
            if not auto_play:
                self._display_board()
        
        if self.game.game_state == GameState.GAME_OVER:
            print("\n🎉 Game finished!")
        else:
            print(f"\n⏰ Game stopped after {turn_count} turns")


def main():
    """Main function to run the CLI game"""
    print("Welcome to Ludo!")
    print("1. Auto-play (fast)")
    print("2. Manual step-by-step")
    
    choice = input("Choose mode (1 or 2): ").strip()
    
    game = CLIGame()
    
    if choice == "1":
        game.play_game(auto_play=True)
    elif choice == "2":
        game.play_game(auto_play=False)
    else:
        print("Invalid choice, using auto-play mode")
        game.play_game(auto_play=True)


if __name__ == "__main__":
    main()