# Project Context: FlowChain

## 1. Project Identity: "FlowChain"
**FlowChain** is a voice-native, autonomous "Guardian Agent" for the Neo N3 Blockchain, secured by SpoonOS Trusted Execution Environments (TEE).

**Current Development Focus**:
The primary goal is to establish the **SpoonOS Agent Core**. This serves as the secure "Brain" that will eventually coordinate with Voice and Prediction nodes.

## 2. Core Architecture (Production Vision)

The system follows a Hub-and-Spoke model secured by dual TEEs.

### A. The Brain (SpoonOS Agent) **[Active Dev]**
- **Runtime**: Python 3.10+ (SpoonOS SDK).
- **Responsibility**: Security, Transaction construction, and Policy enforcement.
- **Infrastructure**: SpoonOS TEE ensures Private Keys are never exposed.

### B. The Voice (ElevenLabs Node) **[Future Integration]**
- **Role**: Handles WebSocket audio streams (Stt/TtS).
- **Context**: Will eventually feed intents to the Brain via API/Socket.

### C. The Quant (Prediction Engine) **[Future Integration]**
- **Role**: Calculates "Vibe Scores" and LMSR probabilities.
- **Context**: Will provide signals to the Brain for automated trading.

### D. The Hands (Turnkey & Neo) **[Active Dev]**
- **Signing**: Turnkey API holds the Neo Private Key.
- **Execution**: `neo-mamba` executes swaps or interacts with Smart Contracts on Neo N3.

## 3. Implementation Plan (SpoonOS Core)

### Phase 1: The Secure Skeleton
- [x] Initialize `src/main.py` with `spoon-ai-sdk` (Basic).
- [ ] **[Refactor]** Clean `src/main.py` to remove any voice placeholders.
- [ ] **[Config]** Ensure `src/config.py` is clean and focused on Neo/Spoon credentials.

### Phase 2: Wallet Connectivity
- [ ] **Tool Setup**: Configure `NeoWalletTool` in `src/main.py`.
- [ ] **Testnet Check**: Implement a startup routine that prints the Agent's address and GAS balance.
- [ ] **Transaction Test**: Execute a self-transfer or simple invocation to verify TEE signing.

## 4. Security Rules
- **Private Keys**: NEVER printed to console. Managed via `spoon_toolkits.web3`.
- **Policy**: All transactions must be validated by the Agent's internal policy logic (even before Voice confirmation is added).
