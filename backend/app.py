from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Sample 3D object data
sample_objects = [
    {
        "id": 1,
        "type": "cube",
        "position": {"x": 0, "y": 0, "z": 0},
        "rotation": {"x": 0, "y": 0, "z": 0},
        "scale": {"x": 1, "y": 1, "z": 1},
        "color": "#ff6b6b"
    },
    {
        "id": 2,
        "type": "sphere",
        "position": {"x": 3, "y": 0, "z": 0},
        "rotation": {"x": 0, "y": 0, "z": 0},
        "scale": {"x": 1, "y": 1, "z": 1},
        "color": "#4ecdc4"
    },
    {
        "id": 3,
        "type": "cone",
        "position": {"x": -3, "y": 0, "z": 0},
        "rotation": {"x": 0, "y": 0, "z": 0},
        "scale": {"x": 1, "y": 1, "z": 1},
        "color": "#45b7d1"
    }
]

@app.route('/api/objects', methods=['GET'])
def get_objects():
    """Get all 3D objects"""
    return jsonify(sample_objects)

@app.route('/api/objects/<int:object_id>', methods=['GET'])
def get_object(object_id):
    """Get a specific 3D object by ID"""
    obj = next((obj for obj in sample_objects if obj['id'] == object_id), None)
    if obj:
        return jsonify(obj)
    return jsonify({"error": "Object not found"}), 404

@app.route('/api/objects', methods=['POST'])
def create_object():
    """Create a new 3D object"""
    data = request.get_json()
    
    # Generate new ID
    new_id = max([obj['id'] for obj in sample_objects]) + 1 if sample_objects else 1
    
    new_object = {
        "id": new_id,
        "type": data.get('type', 'cube'),
        "position": data.get('position', {"x": 0, "y": 0, "z": 0}),
        "rotation": data.get('rotation', {"x": 0, "y": 0, "z": 0}),
        "scale": data.get('scale', {"x": 1, "y": 1, "z": 1}),
        "color": data.get('color', '#ffffff')
    }
    
    sample_objects.append(new_object)
    return jsonify(new_object), 201

@app.route('/api/objects/<int:object_id>', methods=['PUT'])
def update_object(object_id):
    """Update a 3D object"""
    obj = next((obj for obj in sample_objects if obj['id'] == object_id), None)
    if not obj:
        return jsonify({"error": "Object not found"}), 404
    
    data = request.get_json()
    
    # Update object properties
    if 'type' in data:
        obj['type'] = data['type']
    if 'position' in data:
        obj['position'].update(data['position'])
    if 'rotation' in data:
        obj['rotation'].update(data['rotation'])
    if 'scale' in data:
        obj['scale'].update(data['scale'])
    if 'color' in data:
        obj['color'] = data['color']
    
    return jsonify(obj)

@app.route('/api/objects/<int:object_id>', methods=['DELETE'])
def delete_object(object_id):
    """Delete a 3D object"""
    global sample_objects
    sample_objects = [obj for obj in sample_objects if obj['id'] != object_id]
    return jsonify({"message": "Object deleted successfully"})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Three.js Backend is running!"})

if __name__ == '__main__':
    print("Starting Three.js Backend Server...")
    print("API Endpoints:")
    print("  GET    /api/objects - Get all objects")
    print("  GET    /api/objects/<id> - Get specific object")
    print("  POST   /api/objects - Create new object")
    print("  PUT    /api/objects/<id> - Update object")
    print("  DELETE /api/objects/<id> - Delete object")
    print("  GET    /api/health - Health check")
    print("\nServer running at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
