// ==================== CONFIGURATION ====================
const CONFIG = {
    PARTICLE_COUNT: 50,
    PARTICLE_link_DISTANCE: 150,
    PARTICLE_SPEED: 0.5,
    RECONNECT_DELAY: 3000,
    SPEECH_LANG: 'en-US'
};

const AppState = {
    READY: 'ready',
    LISTENING: 'listening',
    PROCESSING: 'processing',
    SPEAKING: 'speaking'
};

let currentState = AppState.READY;

// ==================== DOM ELEMENTS ====================
const voiceButton = document.getElementById('voiceButton');
const statusIndicator = document.getElementById('statusIndicator');
// Safe selectors
const statusText = statusIndicator ? statusIndicator.querySelector('.status-text') : null;
const buttonText = voiceButton ? voiceButton.querySelector('.button-text') : null;
const canvas = document.getElementById('particleCanvas');
const ctx = canvas ? canvas.getContext('2d') : null;

// ==================== STATE MANAGEMENT ====================
function setState(newState) {
    // Check if UI elements exist before trying to update them
    if (!voiceButton || !statusIndicator || !buttonText || !statusText) return;

    // Remove all state classes
    voiceButton.classList.remove('listening', 'processing', 'speaking');
    statusIndicator.classList.remove('listening', 'processing', 'speaking');

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

        case AppState.PROCESSING:
            voiceButton.classList.add('processing');
            statusIndicator.classList.add('processing');
            buttonText.textContent = 'processing...';
            statusText.textContent = 'processing';
            break;

        case AppState.SPEAKING:
            voiceButton.classList.add('speaking');
            statusIndicator.classList.add('speaking');
            buttonText.textContent = 'speaking...';
            statusText.textContent = 'agent speaking';
            break;
    }
}

// ==================== PARTICLE SYSTEM ====================
let particles = [];
let animationId;

class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.vx = (Math.random() - 0.5) * CONFIG.PARTICLE_SPEED;
        this.vy = (Math.random() - 0.5) * CONFIG.PARTICLE_SPEED;
        this.size = Math.random() * 2 + 1;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;

        if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
        if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
    }

    draw() {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

function initParticles() {
    if (!canvas) return;
    resizeCanvas();
    particles = [];
    for (let i = 0; i < CONFIG.PARTICLE_COUNT; i++) {
        particles.push(new Particle());
    }
}

function animateParticles() {
    if (!ctx || !canvas) return; // FIX: Added safety check
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(p => {
        p.update();
        p.draw();

        // Connect particles
        particles.forEach(p2 => {
            const dx = p.x - p2.x;
            const dy = p.y - p2.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < CONFIG.PARTICLE_link_DISTANCE) {
                ctx.beginPath();
                ctx.strokeStyle = `rgba(255, 255, 255, ${0.1 * (1 - distance / CONFIG.PARTICLE_link_DISTANCE)})`;
                ctx.lineWidth = 1;
                ctx.moveTo(p.x, p.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();
            }
        });
    });

    animationId = requestAnimationFrame(animateParticles);
}

function resizeCanvas() {
    if (!canvas) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

// ==================== WEBSOCKET & AUDIO ====================
let websocket = null;

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws`;

    console.log(`Connecting to WebSocket at ${wsUrl}`);
    websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
        console.log('WebSocket Connected');
        setState(AppState.READY);
    };

    websocket.onmessage = (event) => {
        handleBackendMessage(JSON.parse(event.data));
    };

    websocket.onerror = (error) => {
        console.error('WebSocket Error:', error);
        if (statusText) statusText.textContent = 'connection error'; // FIX: Safe access
    };

    websocket.onclose = () => {
        console.log('WebSocket Disconnected');
        if (statusText) statusText.textContent = 'disconnected'; // FIX: Safe access
        setTimeout(connectWebSocket, CONFIG.RECONNECT_DELAY);
    };
}

function handleBackendMessage(data) {
    if (data.type === 'response') {
        if (data.message) {
            console.log('Agent:', data.message);
            if (!data.audio) {
                speakResponse(data.message);
            }
        }
        setState(AppState.READY);
    } else if (data.type === 'audio') {
        playAudio(data.audio);
    } else if (data.type === 'status') {
        if (data.status === 'processing') setState(AppState.PROCESSING);
    } else if (data.type === 'error') {
        alert(data.message);
        setState(AppState.READY);
    }
}

function playAudio(base64Audio) {
    setState(AppState.SPEAKING);
    // Be careful with the base64 prefix
    const audio = new Audio("data:audio/mp3;base64," + base64Audio);
    audio.play();
    audio.onended = () => setState(AppState.READY);
}

function speakResponse(text) {
    if ('speechSynthesis' in window) {
        speechSynthesis.cancel(); // Stop any current speech
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.onstart = () => setState(AppState.SPEAKING);
        utterance.onend = () => setState(AppState.READY);
        speechSynthesis.speak(utterance);
    }
}

// ==================== SPEECH RECOGNITION ====================
let recognition;

function initSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = CONFIG.SPEECH_LANG;

        recognition.onstart = () => setState(AppState.LISTENING);

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            console.log('User:', transcript);

            if (websocket && websocket.readyState === WebSocket.OPEN) {
                websocket.send(JSON.stringify({
                    type: 'text',
                    content: transcript
                }));
                setState(AppState.PROCESSING);
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech Recognition Error:', event.error);
            setState(AppState.READY);
        };

        recognition.onend = () => {
            // Only reset if we didn't transition to processing
            if (currentState === AppState.LISTENING) {
                setState(AppState.READY);
            }
        };
    } else {
        alert('Speech recognition not supported in this browser.');
    }
}

// ==================== EVENT LISTENERS ====================
if (voiceButton) {
    voiceButton.addEventListener('click', () => {
        if (currentState === AppState.READY) {
            if (recognition) recognition.start();
        } else if (currentState === AppState.SPEAKING) {
            speechSynthesis.cancel();
            setState(AppState.READY);
        }
    });
}

window.addEventListener('resize', () => {
    resizeCanvas();
    // Re-init particles on substantial resize if needed, or just let them be
});

window.addEventListener('load', () => {
    initParticles();
    animateParticles();
    connectWebSocket();
    initSpeechRecognition();
});
