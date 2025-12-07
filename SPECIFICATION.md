# FlowChain System Specification

## Overview
FlowChain is a sophisticated AI trading assistant integrating Voice interaction (ElevenLabs), Prediction Markets (SpoonOS/Binance), and Secure Wallet operations (Neo N3/Turnkey).

## Architecture
The application consists of four main functional components:

1.  **Voice Interface**: Real-time speech-to-text and text-to-speech using ElevenLabs and WebSockets.
2.  **Prediction Markets**: A data pipeline that analyzes market sentiment, generates signals, and produces a trade plan.
3.  **SpoonOS Integration**: Leverages `spoonos_components` for deep crypto analysis and research tools.
4.  **Neo3 & Turnkey Wallet**: Secure blockchain interaction for asset management (NEO/GAS) and transaction signing.

## Installation

### Prerequisites
- Python 3.10+
- `pip` and `virtualenv`

### Setup Steps
1.  Clone the repository.
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration
Create a `.env` file in the root directory (see `.env.example`).

### Required Environment Variables
| Variable | Description | Provider |
|----------|-------------|----------|
| `GEMINI_API_KEY` | AI Logic and Reasoning | Google AI Studio |
| `ELEVENLABS_API_KEY` | Voice Synthesis | ElevenLabs |
| `NEO_WIF` | Neo N3 Private Key (WIF) | Neo Blockchain |
| `TAVILY_API_KEY` | Web Search & Research | Tavily |

### Optional / Advanced
| Variable | Description |
|----------|-------------|
| `TURNKEY_API_KEY` | production-grade signing (optional) |
| `TURNKEY_SIGN_WITH` | Wallet ID for Turnkey |

## Application Functions

### 1. Running the System
Start the main application server:
```bash
python run_server.py
# Or directly:
# python src/server.py
```
Access the frontend at `http://localhost:8000`.

### 2. Voice Interaction
-   **ElevenLabs**: Utilizes `src/voice.py` and `src/server.py` WebSocket endpoints.
-   **Usage**: Click "Start Listening" on the frontend or speak if in Voice Mode. The agent listens for triggers like "check wallet", "strategy", or "execute".

### 3. Prediction Markets
The prediction engine runs as an independent pipeline to generate trade strategies.
**To generate a new trade plan:**
```bash
python prediction_model/run_pipeline.py
```
This generates `prediction_model/final_trade_plan.txt`, which the **TradeRecommendationTool** reads to provide advice.

### 4. SpoonOS Integration
-   **Location**: `spoonos_components/` and `src/tools/web3_research_tool.py`.
-   **Function**: The `DeclarativeCryptoAnalysis` class performs parallel analysis of top Binance pairs to identify opportunities.
-   **Usage**: Ask the agent "research market trends" or "analyze ETH".

### 5. Neo3 & Turnkey Configuration
-   **Location**: `src/neo_wallet_agent.py` and `src/tools/turnkey.py`.
-   **Function**: Manages Testnet assets.
-   **Testing**: Run `python test_neo_integration.py` to verify wallet connectivity and balance checks.

## directory Structure
-   `src/`: Core application logic (Server, Main Agent, Tools).
-   `frontend/`: Web interface assets.
-   `prediction_model/`: Signal generation pipeline.
-   `spoonos_components/`: specialized analysis modules.
-   `tests/`: Integration tests.
