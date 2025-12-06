# FlowChain Specification

## 1. References & Sources
- **Tools**:
    - **SpoonOS**: The Trusted Execution Environment (TEE) and Agent Framework.
    - **Turnkey**: Non-custodial, Policy-based Key Management System.
    - **Neo N3**: The target blockchain for transaction execution.

## 2. SpoonOS Integration Strategy
SpoonOS serves as the secure orchestration layer for FlowChain. It provides the following key capabilities:

### A. The Agent Framework (`spoon_ai.agents`)
- **Role**: The "Brain" of the application.
- **Component**: `ToolCallAgent`
- **Function**: Uses an LLM (Gemini/OpenAI) to reason about user intents (e.g., "Check my balance") and map them to specific Tool executions.
- **Security**: Runs within a TEE to ensure the Agent's reasoning and prompt context cannot be tampered with.

### B. Standardized Tool Interface (`spoon_ai.tools`)
- **Role**: The "Hands" of the application.
- **Component**: `BaseTool` (Abstract Base Class)
- **Function**: Provides a standard way for the Agent to interact with the world. FlowChain implements custom tools like `NeoWalletTool` and `TurnkeyNeoWalletTool` that inherit from this base class, ensuring compatibility with the Agent's planning loop.

### C. Secure Signing Infrastructure (`spoon_ai.turnkey`)
- **Role**: The "Vault".
- **Component**: `Turnkey` Client (Customized)
- **Function**:
    1.  **Isolation**: The Agent *never* holds the private key.
    2.  **Transaction Building**: The Agent builds a raw Neo N3 transaction hash locally.
    3.  **Remote Signing**: The Agent uses the `Turnkey` client to send *only the hash* to Turnkey's secure endpoint.
    4.  **Policy Enforcement**: Turnkey verifies the request against allowed policies (e.g., spending limits) before returning a cryptographic signature.
    5.  **Broadcasting**: The Agent re-assembles the signed transaction and broadcasts it to the Neo network.

## 3. Implementation Details
### Core Components Map
| Component | Source Path | Role |
| :--- | :--- | :--- |
| **Agent Core** | `src/main.py` | Initialization/Bootstrapping |
| **Tool Manager** | `spoon_ai.tools.tool_manager` | Tool Registration & Execution |
| **Neo Logic** | `src/tools/neo_tool.py` | Local/Mock Wallet Operations |
| **Secure Logic** | `src/tools/turnkey_neo_tool.py` | Turnkey-Integrated Signing |
| **Turnkey Client** | `spoonos_components/spoon_ai/turnkey/client.py` | API Wrapper (Enhanced with `sign_raw_hash`) |

### Transaction Flow
1.  **Intent**: User says "Send 10 GAS".
2.  **Planning**: `ToolCallAgent` selects `TurnkeyNeoWalletTool`.
3.  **Construction**: Tool creates a Neo Transaction Object.
4.  **Hashing**: Tool generates `Transaction.hash()`.
5.  **Signing**: `Turnkey.sign_raw_hash(hash)` is called.
6.  **Execution**: Signed transaction is relayed via RPC to Neo N3 Node.

## 4. Development Log
### Decisions Made
- **Turnkey Integration**: Shifted from direct WIF management to Turnkey for production-grade security.
- **Mock Mode**: Implemented robust fallback logic ("Graceful Degradation") to allow development without full dependencies (`neo-mamba`).
