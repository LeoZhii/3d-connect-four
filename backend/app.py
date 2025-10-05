from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

grid = np.zeros((4, 4, 5), dtype=int)
turn = 1
moves = []


@app.route('/v1/api/players/<int:player_id>/moves', methods=['POST'])
def record_player_move(player_id):
    global turn, grid, moves

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
        return jsonify({'error': 'Coordinates out of bounds (must be 0-3)'}), 400

    column = grid[x, y, :]
    empty_positions = np.where(column == 0)[0]
    if len(empty_positions) == 0:
        return jsonify({'error': 'Column is full'}), 400

    z = int(empty_positions[0])
    grid[x, y, z] = player_id

    move = {
        'player_id': player_id,
        'turn': turn,
        'coordinates': [x, y, z]
    }
    moves.append(move)
    turn += 1

    # TODO: Check for winner

    response = {
        'coordinates': [x, y, z]
    }
    return jsonify(response), 201


if __name__ == '__main__':
    print("Starting Three.js Backend Server...")
    print("\nServer running at: http://localhost:5000")

    app.run(debug=True, host='0.0.0.0', port=5050)
