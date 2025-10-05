# API endpoints for the game state

from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import itertools
from state import State
from game_funcs import game_data
from mcts import MCTS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication
mcts = None

game_result = {
    'state': None,
    'num_games': 0,
    'player1_score': 0,
    'player2_score': 0
}

@app.route('/v1/api/game/<string:result>/reset', methods=['POST'])
def reset_game(result):
    global game_data, game_result

    if result == 'player1' or result == 'player2':
        game_result[result + '_score'] += 1

    if result != 'none' and result != 'reset':
        game_result['num_games'] += 1

    game_data.grid = np.zeros((4, 4, 5), dtype=int)
    game_data.moves = []

    return jsonify(game_result), 200

@app.route('/v1/api/game/is_move_valid', methods=['POST'])
def is_move_valid():
    global game_data, game_result

    if not request.is_json:
        return jsonify({'error': 'Request is not json!'}), 400

    body = request.get_json()
    if not body or 'coordinates_2d' not in body:
        return jsonify({'error': 'Missing coordinates_2d in request body'}), 400

    coordinates_2d = body.get('coordinates_2d')
    x = int(coordinates_2d[0])
    y = int(coordinates_2d[1])

    if x is None or y is None:
        return jsonify({'error': 'Missing x or y coordinate'}), 400

    if not (0 <= x < 4 and 0 <= y < 4):
        return jsonify({
            'coordinates': {'x': -1, 'y': -1, 'z': -1},
            'state': State.INVALID_MOVE
        }), 201

    # checks if column is full 
    column = game_data.grid[x, y, :]
    empty_positions = np.where(column == 0)[0]
    if len(empty_positions) == 0:
        response = {
            'coordinates': {'x': -1, 'y': -1, 'z': -1},
            'state': State.INVALID_MOVE
        }
        return jsonify(response), 201

    z = int(empty_positions[0])

    response = {
        'coordinates': {'x': x, 'y': z, 'z': y},
        'state': State.CONTINUE
    }
    return jsonify(response), 201

@app.route('/v1/api/ai/<int:player_id>/moves', methods=['POST'])
def ai_move(player_id):
    global game_data, game_result, mcts

    if player_id != 1 and player_id != 2:
        return jsonify({'error': 'Invalid player_id'}), 400

    if not request.is_json:
        return jsonify({'error': 'Request is not json!'}), 400

    move = mcts.best_move(game_data.grid, player=player_id, game=game_data)
    x = int(move['x'])
    y = int(move['y'])
    z = int(move['z'])

    game_data.grid[x, y, z] = player_id

    move = {
        'player_id': player_id,
        'turn': game_data.turn,
        'coordinates': [x, y, z]
    }
    game_data.moves.append(move)
    game_data.turn += 1

    state = State.CONTINUE
    move_result = game_data.get_result(x, y, z, player_id)

    if move_result == 0.5: #draw
        state = State.DRAW
        game_result['state'] = State.DRAW
    elif move_result == 1 or move_result == 0: 
        # someone won and someone lost, we only care *IF* someone won
        state = player_id
        game_result['state'] = player_id 
    # else: #loss 
    #     state = get_opponent(player_id)
    #     game_result['state'] = get_opponent(player_id)

    response = {
        'coordinates': {'x': x, 'y': z, 'z': y},
        'state': state
    }
    return jsonify(response), 201

@app.route('/v1/api/players/<int:player_id>/moves', methods=['POST'])
def record_player_move(player_id):
    global game_data, game_result

    if player_id != 1 and player_id != 2:
        return jsonify({'error': 'Invalid player_id'}), 400

    if not request.is_json:
        return jsonify({'error': 'Request is not json!'}), 400

    body = request.get_json()
    if not body or 'coordinates_2d' not in body:
        return jsonify({'error': 'Missing coordinates_2d in request body'}), 400

    coordinates_2d = body.get('coordinates_2d')
    x = int(coordinates_2d[0])
    y = int(coordinates_2d[1])

    if x is None or y is None:
        return jsonify({'error': 'Missing x or y coordinate'}), 400

    column = game_data.grid[x, y, :]
    empty_positions = np.where(column == 0)[0]
    
    if len(empty_positions) == 0:
        return jsonify({
        'coordinates': {'x': -1, 'y': -1, 'z': -1},
        'state': State.INVALID_MOVE
    }), 201
    
    z = int(empty_positions[0])
    game_data.grid[x, y, z] = player_id

    move = {
        'player_id': player_id,
        'turn': game_data.turn,
        'coordinates': [x, y, z]
    }
    game_data.moves.append(move)
    game_data.turn += 1

    state = State.CONTINUE
    move_result = game_data.get_result(x, y, z, player_id)

    if move_result == 0.5: #draw
        state = State.DRAW
        game_result['state'] = State.DRAW
    elif move_result == 1 or move_result == 0: 
        # someone won and someone lost, we only care *IF* someone won
        state = player_id
        game_result['state'] = player_id 
    # else: #loss 
    #     state = get_opponent(player_id)
    #     game_result['state'] = get_opponent(player_id)

    response = {
        'coordinates': {'x': x, 'y': z, 'z': y},
        'state': state
    }
    return jsonify(response), 201

@app.route('/v1/api/ai/difficulty/<string:difficulty>', methods=['POST'])
def ai_difficulty(difficulty):
    global game_data, game_result, mcts

    if difficulty != 'easy' and difficulty != 'medium' and difficulty != 'hard':
        return jsonify({'error': 'Invalid difficulty'}), 400

    if not request.is_json:
        return jsonify({'error': 'Request is not json!'}), 400

    difficulty_simulations = 1000
    difficulty_exploration = 0.7 if difficulty == 'hard' else 0.6 if difficulty == 'medium' else 0.5

    if mcts is None:
        mcts = MCTS(simulations=difficulty_simulations, exploration_constant=difficulty_exploration)
    else:
        mcts.simulations = difficulty_simulations
        mcts.exploration_constant = difficulty_exploration

    return jsonify({'success': 'Difficulty set to ' + difficulty}), 201

if __name__ == '__main__':
    print("Starting Three.js Backend Server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
