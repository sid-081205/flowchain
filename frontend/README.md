# FlowChain Frontend

A sleek, minimalist website for FlowChain - an AI-powered trading voice agent.

## Features

- **Sleek Black Design**: Modern, minimalist aesthetic with smooth gradients and animations
- **Voice Interaction Button**: Central interactive button with three states:
  - **Ready**: Default state, ready to start conversation
  - **Listening**: Active listening state with animated ripple effects
  - **Processing**: Processing state while AI responds
- **Particle Background**: Subtle animated particle system for visual depth
- **Fully Responsive**: Optimized for desktop, tablet, and mobile devices
- **Accessibility**: Keyboard navigation support and semantic HTML

## File Structure

```
frontend/
├── index.html          # Main HTML structure
├── styles.css          # Complete CSS design system
├── script.js           # Interactive JavaScript
└── assets/
    └── logo.png        # FlowChain logo
```

## Getting Started

### Option 1: Open Directly
Simply open `index.html` in your web browser.

### Option 2: Local Server (Recommended)
For the best experience, serve the files using a local server:

```bash
# Using Python 3
cd frontend
python3 -m http.server 8000

# Using Node.js (if you have http-server installed)
npx http-server frontend -p 8000
```

Then open `http://localhost:8000` in your browser.

## Backend Integration

The frontend is ready for backend integration. Key integration points in `script.js`:

1. **Voice Recording**: Uncomment and implement `startVoiceRecording()` function
2. **Stop Recording**: Uncomment and implement `stopVoiceRecording()` function
3. **WebSocket Connection**: Uncomment `connectToBackend()` for real-time communication

### Example Integration

```javascript
// In script.js, uncomment and modify:
async function startVoiceRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    // Send audio stream to your backend
}

// Connect to your backend WebSocket
const ws = new WebSocket('ws://your-backend-url');
```

## Customization

### Colors
Edit CSS variables in `styles.css`:

```css
:root {
    --color-bg: #0a0a0a;           /* Background color */
    --color-accent: #3b82f6;        /* Accent color for active states */
    --color-success: #10b981;       /* Success/ready indicator */
}
```

### Button Size
Modify in `styles.css`:

```css
.voice-button {
    width: 200px;  /* Change button width */
    height: 200px; /* Change button height */
}
```

### Particle Count
Adjust in `script.js`:

```javascript
const particleCount = 100; // Increase or decrease particles
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Design Philosophy

The design follows these principles:
- **Minimalism**: Clean, focused interface with single primary action
- **Premium Feel**: Smooth animations, subtle effects, and attention to detail
- **Accessibility**: Keyboard navigation and semantic HTML
- **Performance**: Optimized animations using CSS transforms and requestAnimationFrame

## Technologies Used

- **HTML5**: Semantic markup
- **CSS3**: Custom properties, animations, gradients, backdrop-filter
- **Vanilla JavaScript**: No dependencies, pure ES6+
- **Canvas API**: Particle animation system
- **Google Fonts**: Inter typeface

---

Built with ❤️ for FlowChain
