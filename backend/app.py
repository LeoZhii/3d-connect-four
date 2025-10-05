from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import itertools
from state import State

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

grid = np.zeros((4, 4, 5), dtype=int)
turn = 1
moves = []
terminal = False #is the game over

game_result = {
    'state': None,
    'num_games': 0,
    'player1_score': 0,
    'player2_score': 0
}

@app.route('/v1/api/game/<string:result>/reset', methods=['POST'])
def reset_game(result):
    global grid, moves, game_result

    if result == 'player1' or result == 'player2':
        game_result[result + '_score'] += 1

    if result != 'none' and result != 'reset':
        game_result['num_games'] += 1

    grid = np.zeros((4, 4, 5), dtype=int)
    moves = []

    return jsonify(game_result), 200


@app.route('/v1/api/players/<int:player_id>/moves', methods=['POST'])
def record_player_move(player_id):
    global turn, grid, moves, game_result

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

    if not (0 <= x < 4 and 0 <= y < 4):
        return jsonify({
            'coordinates': {'x': -1, 'y': -1, 'z': -1},
            'state': State.INVALID_MOVE
        }), 201

    column = grid[x, y, :]
    empty_positions = np.where(column == 0)[0]
    if len(empty_positions) == 0:
        response = {
            'coordinates': {'x': -1, 'y': -1, 'z': -1},
            'state': State.INVALID_MOVE
        }
        return jsonify(response), 200

    z = int(empty_positions[0])
    grid[x, y, z] = player_id

    move = {
        'player_id': player_id,
        'turn': turn,
        'coordinates': [x, y, z]
    }
    moves.append(move)
    turn += 1

    state = State.CONTINUE
    winner = get_result(x, y, z, player_id)

    if winner == 0.5: #draw
        state = State.DRAW
        game_result['state'] = State.DRAW
    elif winner == 1: #win
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

# returns 1 for win, 0.5 for draw in perspective of the player
def get_result(x, y, z, player_id):
    elements = [0, 1, -1]
    directions = list(itertools.product(elements, repeat=3))[1:]

    # check for draw
    if not np.any(grid==0):
        terminal = True
        return 0.5

    for dx, dy, dz in directions:
        count = 1

        for i in range(1, 4):
            nx, ny, nz = x + dx*i, y + dy*i, z + dz*i
            if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 5:
                if grid[nx, ny, nz] == player_id:
                    count += 1
                else:
                    break
            else:
                break

        for i in range(1, 4):
            nx, ny, nz = x - dx*i, y - dy*i, z - dz*i
            if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 5:
                if grid[nx, ny, nz] == player_id:
                    count += 1
                else:
                    break
            else:
                break

        if count >= 4:
            terminal = True 
            return 1 #win 

    return None 


def is_terminal(grid):
    return terminal 

def get_opponent(current_player):
    return 1 if current_player == 2 else 2


def get_valid_moves(grid):
    zero_indices = np.argwhere(grid == 0)

    return [
        {'x': int(idx[0]), 'y': int(idx[2]), 'z': int(idx[1])}
        for idx in zero_indices
    ]


if __name__ == '__main__':
    print("Starting Three.js Backend Server...")

    app.run(debug=True, host='0.0.0.0', port=5000)
