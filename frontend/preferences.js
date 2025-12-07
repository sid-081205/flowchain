// ==================== WALLET CONNECTION ==================== const connectWalletBtn = document.getElementById('connectWallet');
const disconnectWalletBtn = document.getElementById('disconnectWallet');
const walletStatus = document.getElementById('walletStatus');
const walletInfo = document.getElementById('walletInfo');
const walletAddress = document.getElementById('walletAddress');
const walletBalance = document.getElementById('walletBalance');
const statusDot = document.querySelector('.status-dot');
const statusLabel = document.querySelector('.status-label');

// Connect wallet handler
if (connectWalletBtn) {
    connectWalletBtn.addEventListener('click', async () => {
        // Change button to loading state
        connectWalletBtn.textContent = 'connecting to neuwallet...';
        connectWalletBtn.style.opacity = '0.7';

        // Simulate NeuWallet connection
        setTimeout(() => {
            // Update UI to connected state
            statusDot.classList.remove('disconnected');
            statusLabel.textContent = 'neuwallet connected';
            statusLabel.style.color = 'var(--color-success)';

            // Show wallet info
            walletInfo.classList.remove('hidden');

            // Simulate wallet data
            walletAddress.textContent = 'neu...8x92';
            walletBalance.textContent = '$24,592.84';

            // Hide connect button
            connectWalletBtn.style.display = 'none';
        }, 1500);
    });
}

// Disconnect wallet handler
if (disconnectWalletBtn) {
    disconnectWalletBtn.addEventListener('click', () => {
        // Reset to disconnected state
        statusDot.classList.add('disconnected');
        statusLabel.textContent = 'not connected';

        // Hide wallet info
        walletInfo.classList.add('hidden');

        // Show connect button
        connectWalletBtn.style.display = 'inline-block';
    });
}

// ==================== RISK SLIDER ====================
const riskSlider = document.getElementById('riskSlider');
const riskValue = document.getElementById('riskValue');
const riskDescription = document.getElementById('riskDescription');

const riskLevels = {
    1: {
        label: 'very conservative',
        description: 'minimal risk with focus on capital preservation and stable, low-volatility assets.'
    },
    2: {
        label: 'conservative',
        description: 'low risk approach prioritizing safety with modest growth potential.'
    },
    3: {
        label: 'moderate',
        description: 'balanced approach with moderate risk-reward ratio for steady growth.'
    },
    4: {
        label: 'aggressive',
        description: 'higher risk tolerance seeking substantial returns with increased volatility.'
    },
    5: {
        label: 'very aggressive',
        description: 'maximum risk appetite for potentially high returns, accepting significant volatility.'
    }
};

if (riskSlider) {
    riskSlider.addEventListener('input', (e) => {
        const level = parseInt(e.target.value);
        const risk = riskLevels[level];

        riskValue.textContent = risk.label;
        riskDescription.textContent = risk.description;

        // Update slider color based on risk level
        const percentage = ((level - 1) / 4) * 100;
        const color = `hsl(${220 - (percentage * 0.6)}, 80%, 60%)`;
        e.target.style.background = `linear-gradient(to right, ${color} 0%, ${color} ${percentage}%, rgba(255, 255, 255, 0.1) ${percentage}%, rgba(255, 255, 255, 0.1) 100%)`;
    });

    // Initialize slider
    riskSlider.dispatchEvent(new Event('input'));
}

// ==================== SAVE PREFERENCES ====================
// Initialize on DOM ready
function initSavePreferences() {
    const saveButton = document.querySelector('.save-button') || document.querySelector('button.save-button');
    const passkeyInput = document.getElementById('passkeyInput');

// Load saved passkey status on page load
if (passkeyInput) {
    const savedPasskey = localStorage.getItem('flowchain_passkey');
    if (savedPasskey) {
        // Passkey is saved, show it in password (dotted) form
        passkeyInput.type = 'password';
        passkeyInput.value = savedPasskey;
        passkeyInput.placeholder = 'passkey saved (enter new to change)';
    } else {
        // No passkey saved yet, show default in visible text form
        passkeyInput.type = 'text';
        passkeyInput.value = 'hacker';
    }

    // When user focuses on the field to edit, switch to text type so they can see what they're typing
    passkeyInput.addEventListener('focus', () => {
        if (passkeyInput.type === 'password') {
            passkeyInput.type = 'text';
        }
    });
}

if (saveButton) {
    console.log('Save button found, attaching click handler');
    saveButton.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Save button clicked!');
        
        // Collect all toggle states
        const toggles = document.querySelectorAll('.toggle input[type="checkbox"]');
        
        const preferences = {
            riskLevel: riskSlider ? parseInt(riskSlider.value) : 3,
            sources: [],
            passkey: passkeyInput ? passkeyInput.value : ''
        };

        toggles.forEach((toggle, index) => {
            const sourceItem = toggle.closest('.source-item');
            const sourceName = sourceItem.querySelector('.source-name').textContent;
            const sourceType = sourceItem.querySelector('.source-type').textContent;

            if (toggle.checked) {
                preferences.sources.push({
                    name: sourceName,
                    type: sourceType
                });
            }
        });

        // Save passkey to localStorage if provided
        if (passkeyInput && passkeyInput.value.trim() !== '') {
            const passkeyValue = passkeyInput.value;
            localStorage.setItem('flowchain_passkey', passkeyValue);
            
            // Blur the field first
            passkeyInput.blur();
            
            // Change to password type so it shows in dotted form
            const currentValue = passkeyInput.value;
            passkeyInput.type = 'password';
            // Restore the value after type change
            setTimeout(() => {
                passkeyInput.value = currentValue;
                passkeyInput.placeholder = 'passkey saved (enter new to change)';
            }, 50);
        }

        // TODO: Save preferences to backend
        console.log('Saving preferences:', preferences);

        // Show success feedback on button
        const originalText = saveButton.textContent;
        saveButton.textContent = 'saved!';
        saveButton.style.background = 'var(--color-success)';

        setTimeout(() => {
            saveButton.textContent = originalText;
            saveButton.style.background = 'var(--color-accent)';
        }, 2000);

        // Show toast notification - create it if it doesn't exist
        let toast = document.getElementById('toast');
        if (!toast) {
            // Create toast if it doesn't exist
            toast = document.createElement('div');
            toast.id = 'toast';
            toast.className = 'toast';
            toast.innerHTML = '<span class="toast-message">preferences saved</span>';
            document.body.appendChild(toast);
        }
        
        // Show the toast
        toast.classList.remove('hidden');
        toast.style.display = 'flex';
        toast.style.opacity = '1';
        toast.style.visibility = 'visible';
        toast.style.zIndex = '10000';
        
        console.log('Toast should be visible now');
        
        // Hide after 2.5 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                toast.classList.add('hidden');
                toast.style.display = 'none';
            }, 300);
        }, 2500);
    });
} else {
    console.error('Save button not found!');
}
}

// Run initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSavePreferences);
} else {
    initSavePreferences();
}

// ==================== TOGGLE ANIMATIONS ====================
// Add smooth animation when toggles are clicked
const toggleInputs = document.querySelectorAll('.toggle input[type="checkbox"]');

toggleInputs.forEach(input => {
    input.addEventListener('change', (e) => {
        const slider = e.target.nextElementSibling;

        // Add a subtle pulse animation
        slider.style.transform = 'scale(1.05)';
        setTimeout(() => {
            slider.style.transform = 'scale(1)';
        }, 150);
    });
});
