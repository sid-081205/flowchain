// ==================== STATE MANAGEMENT ====================
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
const statusText = statusIndicator.querySelector('.status-text');
const buttonText = voiceButton.querySelector('.button-text');
const canvas = document.getElementById('particleCanvas');
const ctx = canvas.getContext('2d');

// ==================== BACKEND CONNECTION ====================
let websocket = null;
let recognition = null;
let isListening = false;

// WebSocket connection
function connectWebSocket() {
    // Determine WebSocket URL based on current host
    // If served from the same server, use the same host/port
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host; // This includes port if present
    const wsUrl = `${protocol}//${host}/ws`;
    
    console.log('Connecting to:', wsUrl);
    
    websocket = new WebSocket(wsUrl);
    
    websocket.onopen = () => {
        console.log('✅ Connected to FlowChain backend');
        setState(AppState.READY);
        statusText.textContent = 'ready';
    };
    
    websocket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handleBackendMessage(data);
        } catch (e) {
            console.error('Error parsing message:', e);
        }
    };
    
    websocket.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setState(AppState.READY);
        statusText.textContent = 'connection error';
        // Try to reconnect
        setTimeout(() => {
            console.log('Attempting to reconnect...');
            connectWebSocket();
        }, 3000);
    };
    
    websocket.onclose = (event) => {
        console.log('🔌 Disconnected from backend. Code:', event.code, 'Reason:', event.reason);
        setState(AppState.READY);
        statusText.textContent = 'disconnected';
        // Attempt to reconnect after 3 seconds
        setTimeout(() => {
            console.log('🔄 Attempting to reconnect...');
            connectWebSocket();
        }, 3000);
    };
    
    return websocket;
}

// Handle messages from backend
function handleBackendMessage(data) {
    switch (data.type) {
        case 'status':
            statusText.textContent = data.status || 'ready';
            if (data.status === 'processing') {
                setState(AppState.PROCESSING);
            }
            break;
            
        case 'response':
            // Display the response (you can add a chat UI here)
            console.log('FlowChain:', data.message);
            if (data.message) {
                // Use browser's speech synthesis to speak the response
                speakResponse(data.message);
            } else {
                // If no message, go back to ready
                setState(AppState.READY);
            }
            break;
            
        case 'error':
            console.error('Error:', data.message);
            alert('Error: ' + data.message);
            setState(AppState.READY);
            break;
            
        case 'pong':
            // Heartbeat response
            break;
    }
}

// Speech synthesis for responses
function speakResponse(text) {
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        utterance.volume = 0.8;
        
        // Set speaking state when speech starts
        utterance.onstart = () => {
            console.log('Agent is speaking...');
            setState(AppState.SPEAKING);
        };
        
        // Return to ready when speech ends
        utterance.onend = () => {
            console.log('Agent finished speaking');
            setState(AppState.READY);
        };
        
        // Handle errors
        utterance.onerror = (event) => {
            console.error('Speech synthesis error:', event.error);
            setState(AppState.READY);
        };
        
        speechSynthesis.speak(utterance);
    } else {
        // If speech synthesis not available, just show the message and return to ready
        console.log('Speech synthesis not available');
        setState(AppState.READY);
    }
}

// Request microphone permission proactively
async function requestMicrophonePermission() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // Immediately stop the stream - we just needed permission
        stream.getTracks().forEach(track => track.stop());
        console.log('✅ Microphone permission granted');
        return true;
    } catch (error) {
        console.error('❌ Microphone permission denied:', error);
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            alert('Microphone access is required for voice interaction.\n\nPlease:\n1. Click the lock/info icon in your browser\'s address bar\n2. Allow microphone access\n3. Refresh the page');
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
            alert('No microphone found. Please connect a microphone and refresh the page.');
        } else {
            alert('Error accessing microphone: ' + error.message);
        }
        return false;
    }
}

// Initialize Web Speech API
function initSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = () => {
            console.log('🎤 Speech recognition started');
            isListening = true;
            setState(AppState.LISTENING);
        };
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            console.log('💬 You said:', transcript);
            
            // Send to backend
            if (websocket && websocket.readyState === WebSocket.OPEN) {
                console.log('📤 Sending message to backend:', transcript);
                websocket.send(JSON.stringify({
                    type: 'text',
                    content: transcript
                }));
                setState(AppState.PROCESSING);
            } else {
                console.error('❌ WebSocket not connected. Current state:', websocket ? websocket.readyState : 'null');
                alert('Not connected to server. Please refresh the page.');
                setState(AppState.READY);
            }
            
            isListening = false;
        };
        
        recognition.onerror = (event) => {
            console.error('❌ Speech recognition error:', event.error);
            isListening = false;
            setState(AppState.READY);
            
            if (event.error === 'no-speech') {
                statusText.textContent = 'no speech detected';
                setTimeout(() => {
                    if (currentState === AppState.READY) {
                        statusText.textContent = 'ready';
                    }
                }, 2000);
            } else if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
                statusText.textContent = 'microphone denied';
                alert('Microphone access denied.\n\nTo enable:\n1. Click the lock/info icon (🔒) in your browser\'s address bar\n2. Find "Microphone" and set it to "Allow"\n3. Refresh this page');
            } else if (event.error === 'aborted') {
                console.log('Speech recognition aborted (user stopped)');
            } else {
                statusText.textContent = 'recognition error';
                console.error('Speech recognition error details:', event);
            }
        };
        
        recognition.onend = () => {
            console.log('🔇 Speech recognition ended');
            isListening = false;
            if (currentState === AppState.LISTENING) {
                setState(AppState.READY);
            }
        };
    } else {
        console.warn('⚠️ Speech recognition not supported in this browser');
        alert('Your browser does not support speech recognition.\n\nPlease use:\n• Google Chrome (recommended)\n• Microsoft Edge\n• Safari (macOS/iOS)\n\nFirefox does not support the Web Speech API.');
    }
}

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
            statusText.textContent = 'speaking';
            break;
    }
}

// ==================== VOICE BUTTON HANDLER ====================
voiceButton.addEventListener('click', async () => {
    if (currentState === AppState.READY) {
        // Start listening
        if (!websocket || websocket.readyState !== WebSocket.OPEN) {
            alert('Not connected to backend. Please wait for connection...');
            connectWebSocket();
            return;
        }
        
        // Request microphone permission if not already granted
        const hasPermission = await requestMicrophonePermission();
        if (!hasPermission) {
            return;
        }
        
        if (recognition && !isListening) {
            try {
                recognition.start();
            } catch (e) {
                console.error('Error starting recognition:', e);
                // If already started, stop and restart
                if (recognition) {
                    recognition.stop();
                    setTimeout(() => {
                        try {
                            recognition.start();
                        } catch (err) {
                            console.error('Failed to restart recognition:', err);
                            setState(AppState.READY);
                        }
                    }, 100);
                }
            }
        } else if (!recognition) {
            alert('Speech recognition not available. Please use a supported browser (Chrome, Edge, or Safari).');
        }

    } else if (currentState === AppState.LISTENING) {
        // Stop listening
        if (recognition && isListening) {
            recognition.stop();
        }
        setState(AppState.READY);
    } else if (currentState === AppState.PROCESSING) {
        // Can't interrupt processing
        console.log('Processing in progress, please wait...');
    } else if (currentState === AppState.SPEAKING) {
        // Stop speaking and return to ready
        if ('speechSynthesis' in window) {
            speechSynthesis.cancel();
        }
        setState(AppState.READY);
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
window.addEventListener('load', async () => {
    resizeCanvas();
    animateParticles();
    
    // Initialize speech recognition
    initSpeechRecognition();
    
    // Connect to backend
    connectWebSocket();
    
    // Show helpful message about microphone access
    console.log('💡 Tip: When you click the button, your browser will ask for microphone permission.');
    console.log('   Make sure to click "Allow" to enable voice interaction.');
});
