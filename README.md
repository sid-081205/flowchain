# FlowChain

**FlowChain** is a voice-native AI Financial Agent running on **SpoonOS**. It integrates a secure Neo N3 wallet with an intelligent agent to manage assets and execute transactions via voice or text commands.

## 🚀 Setup

### 1. Environment Build
Ensure you use the project's virtual environment to avoid dependency conflicts.

```bash
# Create virtual environment (if not exists)
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Copy the example environment file and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env` and add:
-   `OPENAI_API_KEY`: For the SpoonOS Agent logic.
-   `NEO_WIF`: Your Neo N3 Testnet Private Key (WIF format).

## 🧪 Running Tests

To verify your environment and wallet connection are working correctly, run the verification script.

**Using Virtual Environment (Recommended):**
```bash
./.venv/bin/python tests/verify_wallet.py
```

**If Activated:**
```bash
python3 tests/verify_wallet.py
```

-   **Success**: You will see your Wallet Address and Balance (or "Mock Mode" if libraries are missing).
-   **Failure**: Check your config or internet connection.

## 🤖 Running the Agent

Start the Core Guardian Agent to chat with your wallet:

```bash
./.venv/bin/python src/main.py
```

**Commands:**
-   "What is my balance?"
-   "Send [Amount] GAS to [Address]"
