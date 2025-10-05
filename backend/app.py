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

game_result = {
    'state': None
}


@app.route('/v1/api/game/reset', methods=['POST'])
def reset_game():
    global grid, moves, game_result

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
    winner = check_winner(x, y, z, player_id)
    draw = False

    if winner is None:
        draw = check_draw(grid)
        if draw:
            state = State.DRAW
            game_result['state'] = State.DRAW
    else:
        state = winner
        game_result['state'] = winner

    response = {
        'coordinates': {'x': x, 'y': z, 'z': y},
        'state': state
    }
    return jsonify(response), 201


def check_winner(x, y, z, player_id):
    elements = [0, 1, -1]
    directions = list(itertools.product(elements, repeat=3))[1:]

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
            return player_id

    return None


def check_draw(grid):
    return not np.any(grid == 0)


def get_valid_moves():
    zero_indices = np.argwhere(grid == 0)

    return [
        {'x': int(idx[0]), 'y': int(idx[2]), 'z': int(idx[1])}
        for idx in zero_indices
    ]


if __name__ == '__main__':
    print("Starting Three.js Backend Server...")

    app.run(debug=True, host='0.0.0.0', port=5000)
