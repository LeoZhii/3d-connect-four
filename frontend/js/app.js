// Three.js Application
class Connect4App {
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
        const geometry = new THREE.PlaneGeometry(20, 20);
        const material = new THREE.MeshLambertMaterial({ 
            color: 0x333333,
            transparent: true,
            opacity: 0.8
        });
        const plane = new THREE.Mesh(geometry, material);
        plane.rotation.x = -Math.PI / 2;
        plane.receiveShadow = true;
        this.scene.add(plane);
    }
    
    createObject(position, color) {
        let geometry = new THREE.SphereGeometry(0.5, 32, 32);

        
        const material = new THREE.MeshPhongMaterial({ 
            color: color,
            shininess: 100
        });
        
        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(position.x, position.y, position.z);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        
        // Add some animation properties
        mesh.userData = {
            id: Date.now(),
            type: 'sphere',
            originalColor: color,
            rotationSpeed: {
                x: (Math.random() - 0.5) * 0.02,
                y: (Math.random() - 0.5) * 0.02,
                z: (Math.random() - 0.5) * 0.02
            }
        };
        
        this.scene.add(mesh);
        this.objects.push(mesh);
        
        return mesh;
    }
    
    async loadObjectsFromAPI() {
        try {
            const response = await fetch('http://localhost:5000/api/objects');
            const objects = await response.json();
            
            objects.forEach(obj => {
                this.createObject(
                    obj.position,
                    obj.color
                );
            });
            
            this.updateObjectCount();
            console.log(`Loaded ${objects.length} objects from API`);
        } catch (error) {
            console.warn('Could not load objects from API:', error);
            // Create some default objects
            this.createObject('cube', { x: 0, y: 0, z: 0 }, '#ff6b6b');
            this.createObject('sphere', { x: 3, y: 0, z: 0 }, '#4ecdc4');
            this.createObject('cone', { x: -3, y: 0, z: 0 }, '#45b7d1');
            this.updateObjectCount();
        }
    }
    
    async addObjectToAPI(objectData) {
        try {
            const response = await fetch('http://localhost:5000/api/objects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(objectData)
            });
            
            if (response.ok) {
                const newObject = await response.json();
                console.log('Object added to API:', newObject);
            }
        } catch (error) {
            console.warn('Could not add object to API:', error);
        }
    }

    async playerMove() {
        const color = (app.playerOneTurn) ? '#FF0000' : '#FFFF00';
    
        const coordinates = document.getElementById('coordinates').value.split(',');
        const position = { x: coordinates[0], y: coordinates[1] };
        
        const playerId = (this.playerOneTurn) ? 1 : 2;

        try {
            const response = await fetch(`http://localhost:5000/v1/api/players/${playerId}/moves`, {
                method: 'POST', // Specify the method
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    "coordinates_2d": [position.x, position.y]
                }),
            });
    
            // 2. The server's response body will be JSON, parse it
            const updated_coordinates = await response.json();
    
            // 3. Handle non-successful HTTP status codes (e.g., 400, 500)
            if (!response.ok) {
                // The server returns an object like: {'error': 'Missing x or y coordinate'}
                const errorMessage = result.error || 'Unknown server error.';
                console.error(`HTTP Error ${response.status}: ${errorMessage}`);
                // Throw an error to be caught by the outer catch block
                throw new Error(`Move failed: ${errorMessage}`);
            }
    
            this.createObject(updated_coordinates, color);
    
        } catch (error) {
            // 5. Handle network errors (e.g., server unreachable) or errors thrown above
            console.error('An error occurred during the fetch operation:', error.message);
            throw error; // Re-throw the error for the caller to handle
        }
        
        // Create object in scene
        this.createObject(position, color);
        this.updateObjectCount();
        
        // Add to API
        // this.addObjectToAPI({
        //     type: 'sphere',
        //     position: position,
        //     color: color
        // });
    
        this.playerOneTurn = !this.playerOneTurn;
    }
    
    setupEventListeners() {
        // Position controls
        // ['posX', 'posY', 'posZ'].forEach(axis => {
        //     document.getElementById(axis).addEventListener('input', (e) => {
        //         this.updatePositionPreview(e.target.value, axis);
        //     });
        // });
        
        // Color control
        // document.getElementById('objectColor').addEventListener('change', (e) => {
        //     // Color preview could be added here
        // });

        document.getElementById('coordinates').addEventListener('input', (e) => {
            this.updatePositionPreview(e.target.value, 'coordinates');
        });
    }
    
    updatePositionPreview(value, axis) {
        // This could show a preview of where the object will be placed
        console.log(`${axis}: ${value}`);
    }
    
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        
        // Update controls
        this.controls.update();
        
        // Animate objects
        this.objects.forEach(obj => {
            if (obj.userData.rotationSpeed) {
                obj.rotation.x += obj.userData.rotationSpeed.x;
                obj.rotation.y += obj.userData.rotationSpeed.y;
                obj.rotation.z += obj.userData.rotationSpeed.z;
            }
        });
        
        // Calculate FPS
        this.calculateFPS();
        
        // Update UI
        this.updateUI();
        
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

function clearScene() {
    app.objects.forEach(obj => {
        app.scene.remove(obj);
        if (obj.geometry) obj.geometry.dispose();
        if (obj.material) obj.material.dispose();
    });
    app.objects = [];
    app.updateObjectCount();
}

function toggleWireframe() {
    app.wireframeMode = !app.wireframeMode;
    app.objects.forEach(obj => {
        obj.material.wireframe = app.wireframeMode;
    });
}

function updateButtons() {
    console.log(`Update button: Is player one turn: ${app.playerOneTurn}`);

    if (app.playerOneTurn) {
        document.getElementById('playerOneButton').style.opacity = '1';
        document.getElementById('playerTwoButton').style.opacity = '0.5';
    } else {
        document.getElementById('playerOneButton').style.opacity = '0.5';
        document.getElementById('playerTwoButton').style.opacity = '1'; 
    }
}

// Initialize the application when the page loads
window.addEventListener('DOMContentLoaded', () => {
    app = new Connect4App();
    const buttons = document.querySelectorAll('.playerButton');

    buttons.forEach(button => {
        button.addEventListener('click', (event) => {
            playerTurn = (app.playerOneTurn) ? "playerOne" : "playerTwo";
    
            if (event.target.value === playerTurn) {
                app.playerMove();
            }
            console.log(`Button clicked: ${event.target.textContent}`);
            updateButtons();
        });
    });

    updateButtons();

});

// Clean up when page unloads
window.addEventListener('beforeunload', () => {
    if (app) {
        app.destroy();
    }
});

