// Three.js Application
class Connect4App {
    static STATE = Object.freeze({
        INVALID_MOVE: -1,
        CONTINUE: 0,
        PLAYER_1_WIN: 1,
        PLAYER_2_WIN: 2,
        DRAW: 3
      });

    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.objects = [];
        this.wireframeMode = false;
        this.animationId = null;
        this.fps = 60;
        this.frameCount = 0;
        this.lastTime = 0;
        this.playerOneTurn = true;
        this.player1Score = 0;
        this.player2Score = 0;
        this.gamesPlayed = 0;
        this.inSession = false;
        this.gameMode = 'pvp';
        this.gameDifficulty = 'easy';

        this.init();
        this.setupEventListeners();
        // this.loadObjectsFromAPI();
    }
    
    init() {
        // Hide loading message
        document.getElementById('loading').style.display = 'none';
        
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x222222);
        
        // Create camera
        this.camera = new THREE.PerspectiveCamera(
            75, 
            window.innerWidth / window.innerHeight, 
            0.1, 
            1000
        );
        this.camera.position.set(0, 2, 10);
        
        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        
        // Add renderer to container
        const container = document.getElementById('canvas-container');
        container.appendChild(this.renderer.domElement);
        
        // Add orbit controls
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        
        // Add lighting
        this.setupLighting();
        
        // Add ground plane
        this.addGroundPlane();
        
        // Start animation loop
        this.animate();

        // Add interactive grid lines
        this.addInteractiveGrid();
        this.setupMouseInteraction()

        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
        
        console.log('Three.js scene initialized successfully!');
    }
    
    setupLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
        this.scene.add(ambientLight);
        
        // Directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 50;
        directionalLight.shadow.camera.left = -10;
        directionalLight.shadow.camera.right = 10;
        directionalLight.shadow.camera.top = 10;
        directionalLight.shadow.camera.bottom = -10;
        this.scene.add(directionalLight);
        
        // Point light
        const pointLight = new THREE.PointLight(0xff6b6b, 0.5, 100);
        pointLight.position.set(-5, 5, 5);
        this.scene.add(pointLight);
        
        // Another point light
        const pointLight2 = new THREE.PointLight(0x4ecdc4, 0.5, 100);
        pointLight2.position.set(5, 5, -5);
        this.scene.add(pointLight2);
    }

    addGroundPlane() {
        const geometry = new THREE.PlaneGeometry(10, 10); // width x height
        const material = new THREE.MeshLambertMaterial({
            color: 0x333333,
            transparent: true,
            opacity: 0.8
        });
        const plane = new THREE.Mesh(geometry, material);
        plane.rotation.x = -Math.PI / 2; // lay flat
        plane.position.set(2, -0.5, 2);  // center at (2, -0.5, 2)
        plane.receiveShadow = false;
        this.scene.add(plane);
    }

    createObject(position, color, animateGravity = false) {
        let geometry = new THREE.SphereGeometry(0.5, 32, 32);
        const material = new THREE.MeshPhongMaterial({
            color: color,
            shininess: 100
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(position.x, animateGravity ? 10 : position.y, position.z);
        mesh.castShadow = false;
        mesh.receiveShadow = false;

        // Animation properties
        mesh.userData = {
            id: Date.now(),
            type: 'sphere',
            originalColor: color,
            rotationSpeed: {
                x: (Math.random() - 0.5) * 0.02,
                y: (Math.random() - 0.5) * 0.02,
                z: (Math.random() - 0.5) * 0.02
            },
            animateGravity: animateGravity,
            targetY: position.y,
            velocityY: 0
        };

        this.scene.add(mesh);
        this.objects.push(mesh);
        this.updateObjectCount();

        return mesh;
    }

    async playerMove(x, z) {
        const color = (app.playerOneTurn) ? '#FF0000' : '#FFFF00';
    
        // const coordinates = document.getElementById('coordinates').value.split(',');
        // const position = { x: coordinates[0], y: coordinates[1] };
        
        const playerId = (this.playerOneTurn) ? 1 : 2;

        try {
            const response = await fetch(`http://localhost:5000/v1/api/players/${playerId}/moves`, {
                method: 'POST', // Specify the method
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    // "coordinates_2d": [position.x, position.y]
                    "coordinates_2d": [x, z]
                }),
            });
    
            if (!response.ok) {
                // The server returns an object like: {'error': 'Missing x or y coordinate'}
                const errorMessage = result.error || 'Unknown server error.';
                console.error(`HTTP Error ${response.status}: ${errorMessage}`);
                // Throw an error to be caught by the outer catch block
                throw new Error(`Move failed: ${errorMessage}`);
            }

            const response_json = await response.json();
            const updated_coordinates = response_json.coordinates;
            const state = response_json.state;
            
            console.log(`State: ${state}`);
            console.log(`Callling createObject with coordinates: ${x}, ${z}`);
            console.log(`Calling createObject with updated coordinates: ${updated_coordinates.x}, ${updated_coordinates.y}, ${updated_coordinates.z}`);
            
            updated_coordinates.x *= 1.5;
            updated_coordinates.y *= 1.5;
            updated_coordinates.z *= 1.5;
            
            switch (state) {
                case Connect4App.STATE.INVALID_MOVE: {
                    this.displayPopup({
                        message: '❌ Invalid Move!',
                        color: '#ff4444'
                    });
                    break;
                }
                 case Connect4App.STATE.PLAYER_1_WIN: {
                     this.createObject(updated_coordinates, color, true);
                     this.playerOneTurn = !this.playerOneTurn;

                     this.displayPopup({
                         message: '🎉 Player 1 Wins!',
                         color: '#4CAF50'
                     });

                     restartGame('player1');

                     break;
                 }
                 case Connect4App.STATE.PLAYER_2_WIN: {
                     this.createObject(updated_coordinates, color, true);
                     this.playerOneTurn = !this.playerOneTurn;

                     this.displayPopup({
                         message: '🎉 Player 2 Wins!',
                         color: '#4CAF50'
                     });

                     restartGame('player2');

                     break;
                 }
                 case Connect4App.STATE.DRAW: {
                     this.createObject(updated_coordinates, color, true);
                     this.playerOneTurn = !this.playerOneTurn;

                     this.displayPopup({
                         message: '🤝 Draw!',
                         color: '#4CAF50'
                     });

                     restartGame('draw');

                     break;
                 }
                case Connect4App.STATE.CONTINUE: {
                    this.createObject(updated_coordinates, color, true);
                    this.playerOneTurn = !this.playerOneTurn;
                }
            }
                        
        } catch (error) {
            // 5. Handle network errors (e.g., server unreachable) or errors thrown above
            console.error('An error occurred during the fetch operation:', error.message);
            throw error; // Re-throw the error for the caller to handle
        }
        
    }

    displayPopup(popup_content) {
        const popup = document.createElement('div');
        popup.id = 'invalid-move-popup';
        popup.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: ${popup_content.color};
            color: white;
            padding: 20px;
            border-radius: 8px;
            font-family: Arial, sans-serif;
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        popup.innerHTML = popup_content.message;
        document.body.appendChild(popup);
        
        // Fade in
        setTimeout(() => {
            popup.style.opacity = '1';
        }, 10);
        
        // Auto-hide after 2 seconds
        setTimeout(() => {
            popup.style.opacity = '0';
            setTimeout(() => {
                if (popup.parentNode) {
                    popup.parentNode.removeChild(popup);
                }
            }, 300);
        }, 500);
    }

    // Add interactive gridlines
    addInteractiveGrid() {
        const rows = 4, cols = 4, depth = 5;
        const spacing = 1.5;
        this.gridCells = []; // store each column for interaction

        const baseMaterial = new THREE.MeshBasicMaterial({
            color: 0x555555,
            wireframe: true,
            transparent: true,
            opacity: 0.5
        });

        this.highlightMaterial = new THREE.MeshBasicMaterial({
            color: 0xffff00,
            wireframe: true,
            transparent: true,
            opacity: 0.7
        });

        this.highlightMesh = null; // currently glowing column

        this.gridGroup = new THREE.Group();

        for (let x = 0; x < rows; x++) {
            for (let z = 0; z < cols; z++) {
                const geometry = new THREE.BoxGeometry(spacing, depth * spacing, spacing);
                const mesh = new THREE.Mesh(geometry, baseMaterial.clone());
                mesh.position.set(x * spacing, (depth * spacing)/2 - 0.5, z * spacing); // centered vertically
                this.gridGroup.add(mesh);
                this.gridCells.push({x, z, mesh});
            }
        }

        this.scene.add(this.gridGroup);
    }

    // Raycaster for selecting the grid
    setupMouseInteraction() {
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();

        window.addEventListener('mousemove', (event) => {
            this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
            this.updateColumnHighlight();
        });

        window.addEventListener('click', (event) => {
            // Ignore clicks on UI elements
            if (event.target.closest('#ui-panel') || 
                event.target.closest('#scoreboard') || 
                event.target.closest('#main-menu') ||
                event.target.closest('#center-controls') ||
                event.target.closest('#info-panel')) {
                return;
            }

            if (this.highlightedColumn && this.inSession) {

                const cellData = this.gridCells.find(c => c.mesh === this.highlightedColumn);

                if (cellData) {
                    console.log(`Clicked column at matrix position: (${cellData.x}, ${cellData.z})`);
                }
                this.playerMove(this.highlightedColumn.x, this.highlightedColumn.z).then(() => {
                    // updateButtons();
                })
                .catch(error => {
                    console.error("Error occurred while making player move:", error);
                });
            }
        });
    }

    updateColumnHighlight() {
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.gridCells.map(c => c.mesh));
        if (intersects.length > 0) {
            const selectedMesh = intersects[0].object;
            const cell = this.gridCells.find(c => c.mesh === selectedMesh);
            if (cell !== this.highlightedColumn) {
                this.highlightedColumn = cell;
                if (!this.highlightMesh) {
                    const color = app.playerOneTurn ? '#ff0000' : '#ffff00';
                    this.highlightMaterial.color.set(color);

                    this.highlightMesh = new THREE.Mesh(selectedMesh.geometry.clone(), this.highlightMaterial);
                    this.scene.add(this.highlightMesh);
                }
                this.highlightMesh.position.copy(selectedMesh.position);
            }
        } else {
            this.highlightedColumn = null;
            if (this.highlightMesh) {
                this.scene.remove(this.highlightMesh);
                this.highlightMesh = null;
            }
        }
    }

    setupEventListeners() {
        
        // Initialize scoreboard
        this.updateScoreboard();
        
        // Make scoreboard draggable (with small delay to ensure DOM is ready)
        setTimeout(() => {
            this.setupDraggableScoreboard();
        }, 100);
                
    }
    
  

    setupDraggableScoreboard() {
        const scoreboard = document.getElementById('scoreboard');
        let isDragging = false;
        let currentX;
        let currentY;
        let initialX;
        let initialY;
        
        // Initialize position from CSS
        const rect = scoreboard.getBoundingClientRect();
        let xOffset = rect.left;
        let yOffset = rect.top;

        const dragStart = (e) => {
            if (e.target.classList.contains('drag-handle') || e.target === scoreboard) {
                initialX = e.clientX - xOffset;
                initialY = e.clientY - yOffset;

                if (e.target === scoreboard || e.target.classList.contains('drag-handle')) {
                    isDragging = true;
                    scoreboard.classList.add('dragging');
                    e.preventDefault();
                }
            }
        };

        const drag = (e) => {
            if (isDragging) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;

                xOffset = currentX;
                yOffset = currentY;

                scoreboard.style.left = xOffset + 'px';
                scoreboard.style.top = yOffset + 'px';
            }
        };

        const dragEnd = (e) => {
            if (isDragging) {
                initialX = currentX;
                initialY = currentY;
                isDragging = false;
                scoreboard.classList.remove('dragging');
            }
        };

        const dragStartTouch = (e) => {
            if (e.target.classList.contains('drag-handle') || e.target === scoreboard) {
                initialX = e.touches[0].clientX - xOffset;
                initialY = e.touches[0].clientY - yOffset;

                if (e.target === scoreboard || e.target.classList.contains('drag-handle')) {
                    isDragging = true;
                    scoreboard.classList.add('dragging');
                    e.preventDefault();
                }
            }
        };

        const dragTouch = (e) => {
            if (isDragging) {
                e.preventDefault();
                currentX = e.touches[0].clientX - initialX;
                currentY = e.touches[0].clientY - initialY;

                xOffset = currentX;
                yOffset = currentY;

                scoreboard.style.left = xOffset + 'px';
                scoreboard.style.top = yOffset + 'px';
            }
        };

        const dragEndTouch = (e) => {
            if (isDragging) {
                initialX = currentX;
                initialY = currentY;
                isDragging = false;
                scoreboard.classList.remove('dragging');
            }
        };

        scoreboard.addEventListener('mousedown', dragStart);
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', dragEnd);

        // Touch support for mobile
        scoreboard.addEventListener('touchstart', dragStartTouch);
        document.addEventListener('touchmove', dragTouch);
        document.addEventListener('touchend', dragEndTouch);
    }

    updateScoreboard() {
        document.getElementById('player1Score').textContent = this.player1Score;
        document.getElementById('player2Score').textContent = this.player2Score;
        document.getElementById('currentPlayer').textContent = this.playerOneTurn ? 'Player 1' : 'Player 2';
        document.getElementById('gamesPlayed').textContent = this.gamesPlayed;
    }
    
    updatePositionPreview(value, axis) {
        // This could show a preview of where the object will be placed
        console.log(`${axis}: ${value}`);
    }
    
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        
        // Update controls
        this.controls.update();
        
        // Calculate FPS
        this.calculateFPS();
        
        // Update UI
        this.updateUI();

        // Gravity Falls
        this.objects.forEach(obj => {
            if (obj.userData.animateGravity) {
                // Simple gravity effect
                obj.userData.velocityY -= 0.02; // gravity acceleration
                obj.position.y += obj.userData.velocityY;

                // Stop at target
                if (obj.position.y <= obj.userData.targetY) {
                    obj.position.y = obj.userData.targetY;
                    obj.userData.animateGravity = false;
                    obj.userData.velocityY = 0;
                }
            }
        });


        // Render
        this.renderer.render(this.scene, this.camera);
    }
    
    calculateFPS() {
        this.frameCount++;
        const currentTime = performance.now();
        
        if (currentTime - this.lastTime >= 1000) {
            this.fps = Math.round((this.frameCount * 1000) / (currentTime - this.lastTime));
            this.frameCount = 0;
            this.lastTime = currentTime;
        }
    }
    
    updateUI() {
        document.getElementById('fps').textContent = this.fps;
        document.getElementById('cameraPos').textContent = 
            `${this.camera.position.x.toFixed(1)},${this.camera.position.y.toFixed(1)},${this.camera.position.z.toFixed(1)}`;
    }
    
    updateObjectCount() {
        document.getElementById('objectCount').textContent = this.objects.length;
    }
    
    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
    
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        // Clean up Three.js objects
        this.objects.forEach(obj => {
            this.scene.remove(obj);
            if (obj.geometry) obj.geometry.dispose();
            if (obj.material) obj.material.dispose();
        });
        
        this.objects = [];
        
        if (this.renderer) {
            this.renderer.dispose();
        }
    }
}

// Global functions for UI controls
let app;

async function restartGame(result) {
    app.inSession = false;

    if (result === 'reset') {
        app.displayPopup({
            message: '⏳ Restarting Game...',
            color: '#FFD580'
        });
    }

    if (result != 'none' && result != 'reset') {
        await sleep(2000); 
    }

    app.objects.forEach(obj => {
        app.scene.remove(obj);
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) obj.material.dispose();
    });
    app.objects = [];
    app.updateObjectCount();

    try {
        const response = await fetch(`http://localhost:5000/v1/api/game/${result}/reset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            // The server returns an object like: {'error': 'Missing x or y coordinate'}
            const errorMessage = result.error || 'Unknown server error.';
            console.error(`HTTP Error ${response.status}: ${errorMessage}`);
            // Throw an error to be caught by the outer catch block
            throw new Error(`Move failed: ${errorMessage}`);
        }
        const response_json = await response.json();    

        app.gamesPlayed = response_json.num_games;
        app.player1Score = response_json.player1_score;
        app.player2Score = response_json.player2_score;
        app.updateScoreboard();

        app.playerOneTurn = true;
        app.inSession = true;
        // updateButtons();

    } catch (error) {
        // 5. Handle network errors (e.g., server unreachable) or errors thrown above
        console.error('An error occurred during the fetch operation:', error.message);
        throw error; // Re-throw the error for the caller to handle
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

function toggleWireframe() {
    app.wireframeMode = !app.wireframeMode;
    app.objects.forEach(obj => {
        obj.material.wireframe = app.wireframeMode;
    });
}

function updateButtons() {
    if (app.playerOneTurn) {
        document.getElementById('playerOneButton').style.opacity = '1';
        document.getElementById('playerTwoButton').style.opacity = '0.5';
    } else {
        document.getElementById('playerOneButton').style.opacity = '0.5';
        document.getElementById('playerTwoButton').style.opacity = '1'; 
    }
}

// Main Menu Functions
function startGame() {
    document.getElementById('main-menu').classList.add('hidden');
    document.getElementById('loading').style.display = 'block';
    
    setTimeout(() => {
        document.getElementById('loading').style.display = 'none';
    }, 1000);

    restartGame('none');
}

function returnToMainMenu() {
    document.getElementById('main-menu').classList.remove('hidden');
    // Reset game state
    if (app) {
        restartGame('reset');
    }
}

function  setupGameModeToggle() {
    const gameModeSelect = document.getElementById('game-mode-select');
    const difficultySelect = document.getElementById('difficulty-select');
    
    // Function to toggle difficulty select based on game mode
    function toggleDifficultySelect() {
        if (gameModeSelect.value === 'pvp') {
            difficultySelect.disabled = true;
            difficultySelect.style.opacity = '0.5';
            difficultySelect.style.cursor = 'not-allowed';

        } else {
            difficultySelect.disabled = false;
            difficultySelect.style.opacity = '1';
            difficultySelect.style.cursor = 'pointer';
        }
    }
    
    // Set initial state
    toggleDifficultySelect();
    
    // Add event listener for changes
    gameModeSelect.addEventListener('change', toggleDifficultySelect);
}

function showPanelModal(panel_modal) {
    const modal = document.getElementById(panel_modal);
    modal.style.display = 'block';
    
    // Close when clicking outside the modal content
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            closePanelModal(panel_modal);
        }
    });
}

function closePanelModal(modal) {
    document.getElementById(modal).style.display = 'none';
}

function applySettings() {
    const gameMode = document.getElementById('game-mode-select').value;
    const gameDifficulty = document.getElementById('difficulty-select').value;
    
    app.gameMode = gameMode;
    app.gameDifficulty = gameDifficulty;
    
    closePanelModal("settings-modal");
}

// Initialize the application when the page loads
window.addEventListener('DOMContentLoaded', () => {
    
    app = new Connect4App();
    const buttons = document.querySelectorAll('.playerButton');

    setupGameModeToggle();

    // updateButtons();
    restartGame('none');

});

// Clean up when page unloads
window.addEventListener('beforeunload', () => {
    if (app) {
        app.destroy();
    }
});

