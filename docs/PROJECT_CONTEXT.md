# Project Context: FlowChain

## 1. Project Identity: "FlowChain"
**Tagline**: "The Oracle in Your Ear."

**FlowChain** is a voice-native AI Financial Agent running inside a SpoonOS Trusted Execution Environment (TEE). It protects your assets and allows for hands-free management via natural language.

**Scope Note**: "Prediction Market" features are handled by a teammate. This workspace focuses on **Core Wallet Infrastructure** and **SpoonOS Integration**.

**Hackathon Tracks**:
1.  **AI Agent with Web3**:
    *   **Goal**: Autonomous execution of swaps, bets, and portfolio rebalancing on Neo N3.
2.  **ElevenLabs Challenge**:
    *   **Goal**: A persistent audio companion that "pushes" intelligence to you.

## 2. Core Architecture

### A. The Brain (SpoonOS Agent)
- **Runtime**: Python 3.10+ (SpoonOS SDK).
- **Responsibility**: Security, Transaction construction, and Voice Intent processing.
- **Infrastructure**: SpoonOS TEE ensures Private Keys are never exposed.

### B. The Voice (ElevenLabs "Sentient IOS")
- **Input**: Streaming Audio -> WebSocket -> Intent.
- **Output**: Dynamic Persona (Analyst/Urgent modes).

### C. The Hands (Turnkey & Neo)
- **Signing**: Turnkey API holds the Neo Private Key.
- **Execution**: `neo-mamba` executes swaps or interacts with Smart Contracts on Neo N3.

## 3. Implementation Plan (Wallet Focus)

### Phase 1: Core Connectivity
- [ ] **Wallet Setup**: Configure `NeoWalletTool` with valid Testnet keys.
- [ ] **SpoonOS Check**: Verify the agent can successfully sign a "No-Op" or "Balance Check" transaction inside the TEE mock.

### Phase 2: Basic Skills
- [ ] **Balance Query**: User asks "How much GAS do I have?" -> Agent queries chain -> TTS response.
- [ ] **Simple Transfer**: User asks "Send 1 GAS to Alice" -> Agent constructs & signs tx.

## 4. Security Rules
- **Private Keys**: NEVER printed to console. Managed via `spoon_toolkits.web3`.
- **Confirmation**: All value-transfer transactions require explicit "YES" confirmation via voice.
