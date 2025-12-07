# FlowChain Neo Wallet Integration

## Overview

FlowChain now includes comprehensive Neo N3 blockchain wallet integration, allowing you to manage NEO and GAS assets securely through an AI agent interface. The system supports both Turnkey HSM signing (recommended for production) and local private key signing.

## Features

### 🔐 Secure Wallet Operations
- **Turnkey Integration**: Enterprise-grade HSM signing
- **Local Signing**: Direct private key support for development
- **Mock Wallet**: Safe testing without real funds

### 💰 Asset Management
- Check NEO and GAS balances in real-time
- Send NEO/GAS to other addresses
- Estimate transaction fees
- View transaction history

### 🤖 AI Agent Integration
- Natural language wallet operations
- Contextual portfolio summaries
- Market-aware transaction guidance
- Security-first approach

## Quick Setup

### 1. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
# Edit .env with your actual API keys and wallet information
```

### 2. Required Dependencies

Ensure you have the necessary dependencies installed:

```bash
# Install Neo blockchain dependencies
pip install neo3-python

# Install SpoonOS SDK and AI components
pip install spoon-ai
pip install python-dotenv
```

### 3. API Keys Required

- **Gemini API Key**: Get from [AI Studio](https://aistudio.google.com/app/apikey)
- **Neo Testnet Funds**: Get NEO/GAS from [NeoWish Faucet](https://neowish.ngd.network/)
- **Turnkey Account** (optional): Sign up at [Turnkey.com](https://turnkey.com)

## Usage Examples

### Basic Wallet Operations

```python
from src.neo_wallet_agent import FlowChainNeoIntegration

# Initialize the integration
integration = FlowChainNeoIntegration()
await integration.initialize()

# Get portfolio summary
portfolio = await integration.get_portfolio_summary()
print(portfolio)

# Execute wallet commands
response = await integration.execute_neo_command("What is my NEO balance?")
```

### Natural Language Interface

The agent responds to natural language queries:

- "What is my current NEO balance?"
- "Show me my wallet status"
- "Send 10 GAS to NAddress123..."
- "Estimate the cost of a transfer"
- "What assets do I hold?"

### Running the Main Agent

```bash
# Start FlowChain with Neo integration
python src/main.py
```

### Testing the Integration

```bash
# Run comprehensive tests
python test_neo_integration.py
```

## Security Features

### 🔒 Turnkey HSM Integration
- Private keys never exposed to application
- Enterprise-grade security
- Audit trail for all transactions
- Multi-signature support

### 🛡️ Local Wallet Security
- WIF private keys stored in environment variables
- Secure transaction signing
- Network isolation support

### ⚠️ Mock Wallet for Development
- Safe testing without real funds
- Simulated blockchain operations
- Development and demo environments

## Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `NEO_WIF` | Neo private key (WIF format) | Optional* |
| `TURNKEY_API_KEY` | Turnkey API key | Optional* |
| `TURNKEY_SIGN_WITH` | Turnkey wallet ID | Optional* |
| `NEO_RPC_URL` | Neo RPC endpoint | No (defaults to testnet) |
| `USE_TURNKEY_SIGNING` | Use Turnkey for signing | No (default: true) |
| `USE_MOCK_WALLET` | Use mock wallet | No (default: false) |

*Either NEO_WIF or Turnkey credentials required for real operations

### Network Configuration

```bash
# Testnet (default)
NEO_RPC_URL=https://testnet1.neo.coz.io:443
NEO_NETWORK=testnet

# Mainnet (production)
NEO_RPC_URL=https://mainnet1.neo.coz.io:443
NEO_NETWORK=mainnet
```

## Agent Integration

The Neo wallet agent integrates seamlessly with the main FlowChain agent:

```python
class FlowChainAgent(ToolCallAgent):
    # Neo wallet integration enabled
    # Responds to wallet queries naturally
    # Provides real-time portfolio data
    # Guides users through secure transactions
```

## Example Interactions

```
👤 User: Hello FlowChain
🤖 FlowChain: Greetings. Neo wallet systems online. How are you today?

👤 User: Show me my portfolio
🤖 FlowChain: 🏦 **Neo Wallet Status**
             💰 NEO: 100
             ⛽ GAS: 520.5
             🔗 Network: testnet
             🔐 Security: Turnkey

👤 User: Send 10 GAS to NAddress123
🤖 FlowChain: I'll help you send 10 GAS. Let me verify your balance first...
             ✅ Sufficient balance confirmed.
             🔐 Initiating secure transaction via Turnkey...
             ✅ Transaction completed: 0xabc123...
```

## Troubleshooting

### Common Issues

1. **"No wallet credentials found"**
   - Ensure either NEO_WIF or Turnkey credentials are set
   - Check .env file formatting

2. **"Connection failed"**
   - Verify NEO_RPC_URL is accessible
   - Check network connectivity

3. **"Insufficient balance"**
   - Get testnet funds from NeoWish faucet
   - Verify wallet address has assets

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run your operations
```

## Advanced Features

### Custom Transaction Types
- NEP-17 token transfers
- Smart contract invocations  
- Multi-signature transactions
- Batch operations

### Market Integration
- Real-time price data
- Portfolio valuation
- Market-aware recommendations
- Risk assessment

### Voice Interface
- Natural speech input
- Hands-free trading
- Audio confirmations
- Multi-language support

## Contributing

To contribute to the Neo wallet integration:

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit a pull request

## License

This project is part of FlowChain and follows the same licensing terms.

---

**Need Help?** Check the troubleshooting section or create an issue in the repository.
