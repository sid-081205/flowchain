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
const saveButton = document.querySelector('.save-button');

if (saveButton) {
    saveButton.addEventListener('click', () => {
        // Collect all toggle states
        const toggles = document.querySelectorAll('.toggle input[type="checkbox"]');
        const preferences = {
            riskLevel: riskSlider ? parseInt(riskSlider.value) : 3,
            sources: []
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

        // TODO: Save preferences to backend
        console.log('Saving preferences:', preferences);

        // Show success feedback
        const originalText = saveButton.textContent;
        saveButton.textContent = 'saved!';
        saveButton.style.background = 'var(--color-success)';

        setTimeout(() => {
            saveButton.textContent = originalText;
            saveButton.style.background = 'var(--color-accent)';
        }, 2000);
    });
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
