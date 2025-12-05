# FlowChain Specification

## 1. References & Sources
- **Tools**:
    - **SpoonOS**: TEE-based agent infrastructure on Neo N3.
    - **ElevenLabs**: WebSocket API for low-latency voice I/O.
    - **Turnkey**: Non-custodial key management.

## 2. Implementation Details
### Core Components
- **The Brain**: Python agent running in SpoonOS TEE.
- **The Hands**: Transaction execution via `neo-mamba` and `NeoWalletTool`.

### Current Status
- **Phase 1 (Skeleton)**: Complete.
- **Phase 2 (Wallet Integration)**: In Progress. Focus on connecting `NeoWalletTool`.

## 3. Development Log
### Decisions Made
- Removed "Prediction Market" scope (handled by teammate).
- Focus shifted to "AI Agent with Web3" track (Wallet Integration).
