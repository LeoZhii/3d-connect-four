# Three.js + Python Flask Application

A simple 3D web application built with Three.js frontend and Python Flask backend.

## Features

- 🎮 Interactive 3D scene with multiple object types (cube, sphere, cone, cylinder)
- 🎨 Real-time object manipulation (position, color, wireframe mode)
- 🌐 RESTful API backend for object management
- 🖱️ Mouse controls for camera movement (orbit, pan, zoom)
- 📊 Real-time FPS and camera position display
- 🎯 Dynamic lighting with shadows

## Project Structure

```
pd/
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main HTML file
│   └── js/
│       └── app.js          # Three.js application logic
├── package.json            # Node.js project file
└── README.md               # This file
```

## Setup Instructions

### 1. Backend Setup (Python)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py
```

The backend will start on `http://localhost:5000`

### 2. Frontend Setup

Simply open the `frontend/index.html` file in your web browser, or serve it using a local web server:

```bash
# Using Python's built-in server
cd frontend
python -m http.server 8000

# Or using Node.js http-server (if installed)
npx http-server -p 8000
```

Then open `http://localhost:8000` in your browser.

## API Endpoints

The Flask backend provides the following REST API endpoints:

- `GET /api/objects` - Get all 3D objects
- `GET /api/objects/<id>` - Get specific object by ID
- `POST /api/objects` - Create new object
- `PUT /api/objects/<id>` - Update existing object
- `DELETE /api/objects/<id>` - Delete object
- `GET /api/health` - Health check

### Example API Usage

```javascript
// Get all objects
fetch('http://localhost:5000/api/objects')
  .then(response => response.json())
  .then(data => console.log(data));

// Create new object
fetch('http://localhost:5000/api/objects', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    type: 'cube',
    position: { x: 0, y: 0, z: 0 },
    color: '#ff6b6b'
  })
});
```

## Controls

### Mouse Controls
- **Left Click + Drag**: Rotate camera around scene
- **Right Click + Drag**: Pan camera
- **Mouse Wheel**: Zoom in/out

### UI Controls
- **Object Type**: Select shape type (cube, sphere, cone, cylinder)
- **Color Picker**: Choose object color
- **Position Sliders**: Set X, Y, Z coordinates
- **Add Object**: Create new object with current settings
- **Clear Scene**: Remove all objects
- **Toggle Wireframe**: Switch between solid and wireframe rendering

## Technologies Used

### Frontend
- **Three.js**: 3D graphics library
- **HTML5/CSS3**: Structure and styling
- **Vanilla JavaScript**: Application logic

### Backend
- **Python 3**: Programming language
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing

## Development

### Adding New Features

1. **Backend**: Add new endpoints in `backend/app.py`
2. **Frontend**: Extend the `ThreeJSApp` class in `frontend/js/app.js`
3. **UI**: Modify `frontend/index.html` for new controls

### Customization

- **Lighting**: Modify `setupLighting()` method
- **Materials**: Change material properties in `createObject()`
- **Animation**: Add custom animations in the `animate()` loop
- **API**: Extend the Flask API with new endpoints

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure Flask-CORS is installed and configured
2. **Objects Not Loading**: Check if backend is running on port 5000
3. **Performance Issues**: Reduce object count or simplify geometry
4. **Browser Compatibility**: Ensure WebGL support is enabled

### Browser Requirements

- Modern browser with WebGL support
- JavaScript enabled
- Recommended: Chrome, Firefox, Safari, Edge (latest versions)

## License

MIT License - feel free to use and modify as needed!

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

Enjoy building amazing 3D applications! 🚀
