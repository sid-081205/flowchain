// ==================== STATE MANAGEMENT ====================
const AppState = {
    READY: 'ready',
    LISTENING: 'listening'
};

let currentState = AppState.READY;

// ==================== DOM ELEMENTS ====================
const voiceButton = document.getElementById('voiceButton');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = statusIndicator.querySelector('.status-text');
const buttonText = voiceButton.querySelector('.button-text');
const canvas = document.getElementById('particleCanvas');
const ctx = canvas.getContext('2d');

// ==================== PARTICLE SYSTEM ====================
class Particle {
    constructor() {
        this.reset();
        this.y = Math.random() * canvas.height;
        this.opacity = Math.random() * 0.5 + 0.2;
    }

    reset() {
        this.x = Math.random() * canvas.width;
        this.y = -10;
        this.speed = Math.random() * 0.5 + 0.2;
        this.size = Math.random() * 2 + 1;
        this.opacity = Math.random() * 0.5 + 0.2;
    }

    update() {
        this.y += this.speed;

        if (this.y > canvas.height) {
            this.reset();
        }
    }

    draw() {
        ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Initialize particles
let particles = [];
const particleCount = 100;

function initParticles() {
    particles = [];
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
}

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    initParticles();
}

function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(particle => {
        particle.update();
        particle.draw();
    });

    requestAnimationFrame(animateParticles);
}

// ==================== STATE MANAGEMENT ====================
function setState(newState) {
    // Remove all state classes
    voiceButton.classList.remove('listening');
    statusIndicator.classList.remove('listening');

    currentState = newState;

    switch (newState) {
        case AppState.READY:
            buttonText.textContent = 'start conversation';
            statusText.textContent = 'ready';
            break;

        case AppState.LISTENING:
            voiceButton.classList.add('listening');
            statusIndicator.classList.add('listening');
            buttonText.textContent = 'listening...';
            statusText.textContent = 'listening';
            break;
    }
}

// ==================== VOICE BUTTON HANDLER ====================
voiceButton.addEventListener('click', () => {
    if (currentState === AppState.READY) {
        // Start listening
        setState(AppState.LISTENING);

        // TODO: Integrate with your backend here
        // Example: startVoiceRecording();

    } else if (currentState === AppState.LISTENING) {
        // Stop listening and return to ready
        setState(AppState.READY);

        // TODO: Integrate with your backend here
        // Example: stopVoiceRecording();
    }
});

// ==================== KEYBOARD ACCESSIBILITY ====================
voiceButton.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        voiceButton.click();
    }
});

// ==================== INITIALIZATION ====================
window.addEventListener('resize', resizeCanvas);
window.addEventListener('load', () => {
    resizeCanvas();
    animateParticles();
});

// ==================== BACKEND INTEGRATION HELPERS ====================
// Uncomment and modify these functions to integrate with your backend

/*
async function startVoiceRecording() {
    try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Initialize your voice recording logic here
        // Example: Send audio stream to your backend
        
        console.log('Voice recording started');
    } catch (error) {
        console.error('Error accessing microphone:', error);
        setState(AppState.READY);
        alert('Unable to access microphone. Please check your permissions.');
    }
}

function stopVoiceRecording() {
    // Stop recording and send to backend for processing
    console.log('Voice recording stopped');
}

function cancelProcessing() {
    // Cancel any ongoing processing
    console.log('Processing cancelled');
}

// Example WebSocket connection for real-time communication
function connectToBackend() {
    const ws = new WebSocket('ws://your-backend-url');
    
    ws.onopen = () => {
        console.log('Connected to backend');
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        // Handle backend responses
        console.log('Received from backend:', data);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
        console.log('Disconnected from backend');
    };
    
    return ws;
}
*/
