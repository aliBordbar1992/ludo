"""
Web API Example for Ludo Game

This demonstrates how to use the core Ludo game logic with a web API.
"""

from flask import Flask, jsonify, request
from ludo_game import LudoGame, PlayerColor, GameState, EventType
import json

app = Flask(__name__)

# Global game instance (in production, you'd use a proper session management)
game = LudoGame()

# Store game events for the web interface
game_events = []

def handle_game_event(event):
    """Store game events for the web interface"""
    game_events.append({
        'event_type': event.event_type.value,
        'data': event.data,
        'player_color': event.player_color.value if event.player_color else None
    })

# Add event listener to the game
game.add_event_listener(handle_game_event)

@app.route('/api/game/status', methods=['GET'])
def get_game_status():
    """Get current game status"""
    return jsonify(game.get_game_state())

@app.route('/api/game/players', methods=['POST'])
def add_player():
    """Add a player to the game"""
    data = request.get_json()
    color_name = data.get('color', '').upper()
    
    try:
        color = PlayerColor[color_name]
        success = game.add_player(color)
        return jsonify({
            'success': success,
            'message': f'Player {color_name} added successfully' if success else f'Player {color_name} already exists'
        })
    except KeyError:
        return jsonify({
            'success': False,
            'message': f'Invalid color: {color_name}. Valid colors: {[c.name for c in PlayerColor]}'
        }), 400

@app.route('/api/game/roll-dice', methods=['POST'])
def roll_dice():
    """Roll the dice for the current player"""
    if game.game_state != GameState.ROLLING_DICE:
        return jsonify({
            'success': False,
            'message': 'Cannot roll dice at this time'
        }), 400
    
    dice_value = game.roll_dice()
    return jsonify({
        'success': True,
        'dice_value': dice_value,
        'current_player': game.current_player.value if game.current_player else None
    })

@app.route('/api/game/valid-moves', methods=['GET'])
def get_valid_moves():
    """Get valid moves for the current player"""
    if not game.current_player:
        return jsonify({'valid_moves': []})
    
    valid_moves = game.get_valid_moves(game.current_player)
    moves_data = []
    
    for piece, new_position in valid_moves:
        moves_data.append({
            'piece_id': piece.piece_id,
            'current_position': piece.position,
            'new_position': new_position,
            'is_home': piece.is_home
        })
    
    return jsonify({
        'current_player': game.current_player.value,
        'valid_moves': moves_data
    })

@app.route('/api/game/move-piece', methods=['POST'])
def move_piece():
    """Move a piece for the current player"""
    data = request.get_json()
    piece_id = data.get('piece_id')
    
    if piece_id is None:
        return jsonify({
            'success': False,
            'message': 'piece_id is required'
        }), 400
    
    if not game.current_player:
        return jsonify({
            'success': False,
            'message': 'No current player'
        }), 400
    
    success = game.move_piece(game.current_player, piece_id)
    
    return jsonify({
        'success': success,
        'message': 'Piece moved successfully' if success else 'Invalid move',
        'game_state': game.game_state.value,
        'current_player': game.current_player.value if game.current_player else None
    })

@app.route('/api/game/events', methods=['GET'])
def get_events():
    """Get recent game events"""
    return jsonify({
        'events': game_events[-50:]  # Return last 50 events
    })

@app.route('/api/game/reset', methods=['POST'])
def reset_game():
    """Reset the game to initial state"""
    game.reset_game()
    game_events.clear()
    return jsonify({
        'success': True,
        'message': 'Game reset successfully'
    })

@app.route('/api/game/auto-play', methods=['POST'])
def auto_play():
    """Automatically play a turn for the current player"""
    if not game.current_player:
        return jsonify({
            'success': False,
            'message': 'No current player'
        }), 400
    
    # Roll dice if needed
    if game.game_state == GameState.ROLLING_DICE:
        game.roll_dice()
    
    # Get valid moves
    valid_moves = game.get_valid_moves(game.current_player)
    
    if valid_moves:
        # Choose first valid move
        piece, new_position = valid_moves[0]
        success = game.move_piece(game.current_player, piece.piece_id)
        return jsonify({
            'success': True,
            'action': 'moved_piece',
            'piece_id': piece.piece_id,
            'new_position': new_position
        })
    else:
        # No valid moves, skip turn
        game._next_turn()
        return jsonify({
            'success': True,
            'action': 'skipped_turn',
            'message': 'No valid moves available'
        })

@app.route('/')
def index():
    """Simple HTML interface for testing"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ludo Game API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .section { margin: 20px 0; padding: 10px; border: 1px solid #ccc; }
            button { margin: 5px; padding: 10px; }
            .status { background: #f0f0f0; padding: 10px; }
            .events { max-height: 300px; overflow-y: scroll; }
        </style>
    </head>
    <body>
        <h1>Ludo Game API</h1>
        
        <div class="section">
            <h2>Game Setup</h2>
            <button onclick="addPlayer('RED')">Add Red Player</button>
            <button onclick="addPlayer('GREEN')">Add Green Player</button>
            <button onclick="addPlayer('YELLOW')">Add Yellow Player</button>
            <button onclick="addPlayer('BLUE')">Add Blue Player</button>
            <button onclick="resetGame()">Reset Game</button>
        </div>
        
        <div class="section">
            <h2>Game Actions</h2>
            <button onclick="rollDice()">Roll Dice</button>
            <button onclick="getValidMoves()">Get Valid Moves</button>
            <button onclick="autoPlay()">Auto Play Turn</button>
        </div>
        
        <div class="section">
            <h2>Game Status</h2>
            <div id="status" class="status">Loading...</div>
            <button onclick="updateStatus()">Refresh Status</button>
        </div>
        
        <div class="section">
            <h2>Recent Events</h2>
            <div id="events" class="events">Loading...</div>
            <button onclick="updateEvents()">Refresh Events</button>
        </div>
        
        <script>
            async function addPlayer(color) {
                const response = await fetch('/api/game/players', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({color: color})
                });
                const result = await response.json();
                alert(result.message);
                updateStatus();
            }
            
            async function rollDice() {
                const response = await fetch('/api/game/roll-dice', {
                    method: 'POST'
                });
                const result = await response.json();
                if (result.success) {
                    alert(`Dice rolled: ${result.dice_value}`);
                } else {
                    alert(result.message);
                }
                updateStatus();
            }
            
            async function getValidMoves() {
                const response = await fetch('/api/game/valid-moves');
                const result = await response.json();
                console.log('Valid moves:', result);
                alert(`Found ${result.valid_moves.length} valid moves`);
                updateStatus();
            }
            
            async function autoPlay() {
                const response = await fetch('/api/game/auto-play', {
                    method: 'POST'
                });
                const result = await response.json();
                alert(result.message || result.action);
                updateStatus();
                updateEvents();
            }
            
            async function resetGame() {
                const response = await fetch('/api/game/reset', {
                    method: 'POST'
                });
                const result = await response.json();
                alert(result.message);
                updateStatus();
                updateEvents();
            }
            
            async function updateStatus() {
                const response = await fetch('/api/game/status');
                const status = await response.json();
                document.getElementById('status').innerHTML = 
                    '<pre>' + JSON.stringify(status, null, 2) + '</pre>';
            }
            
            async function updateEvents() {
                const response = await fetch('/api/game/events');
                const result = await response.json();
                document.getElementById('events').innerHTML = 
                    '<pre>' + JSON.stringify(result.events, null, 2) + '</pre>';
            }
            
            // Initial load
            updateStatus();
            updateEvents();
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("Starting Ludo Game Web API...")
    print("Open http://localhost:5000 in your browser")
    print("Or use the API endpoints directly:")
    print("  GET  /api/game/status")
    print("  POST /api/game/players")
    print("  POST /api/game/roll-dice")
    print("  GET  /api/game/valid-moves")
    print("  POST /api/game/move-piece")
    print("  GET  /api/game/events")
    print("  POST /api/game/reset")
    print("  POST /api/game/auto-play")
    
    app.run(debug=True, host='0.0.0.0', port=5000)