# FlowChain Project Slide Deck Content

## 1. SpoonOS Usage Overview

**Leveraging the SpoonOS Agent Framework**
We utilized the SpoonOS core architecture to build a specialized DeFi Guardian. Instead of starting from scratch, we adapted key components from the `spoonos_components` library:

*   **Reference Architecture**: We used **`spoonos_components/turnkey_demo_reference.py`** as our architectural blueprint. This file provided the pattern for a secure, tool-calling agent that delegates critical operations to specialized sub-agents.
*   **Agent Foundation**: We adapted **`spoonos_components/wallet_agent.py`** to build our functionality. We utilized its `ToolCallAgent` structure and monkey-patched the `ToolManager` to support our custom, high-frequency trading tools alongside standard SpoonAI SDK tools.
*   **Core Integration**: We built directly on top of `spoon_ai.agents.toolcall` and `spoon_ai.tools`, extending the `BaseTool` class to create our custom `NeoWalletTool` and `TurnkeyNeoWalletTool`.

---

## 2. Turnkey Implementation

**Secure, Non-Custodial Signing**
We implemented a custom Turnkey integration that brings institutional-grade security to the Neo ecosystem, modeled after the patterns in `turnkey_demo_reference.py`.

*   **Custom Neo Integration**: While SpoonOS provides native EVM tools, we created a bespoke **`TurnkeyNeoWalletTool`**.
*   **Remote HSM Workflow**: 
    1.  **Construction**: The agent constructs a raw Neo N3 transaction payload locally.
    2.  **Hashing**: We compute the transaction hash strictly within the application logic.
    3.  **Signing**: We use the Turnkey API (`sign_raw_hash`) to sign this hash inside a secure enclave.
    4.  **Result**: The private key *never* allows the application to see it. It remains isolated in the hardware security module (HSM), preventing leakage even if the application layer is compromised.

---

## 3. Neo Blockchain Layer Implementation

**Native Neo N3 & NeoFS Integration**
We engineered a dedicated Neo layer ("The Green Layer") that acts as the backbone for FlowChain's operations.

*   **Direct State Interaction**: We integrated the **`neo-mamba` SDK**  to allow the agent to read real-time blockchain state (balances, gas prices, block height) directly from the Neo N3 network, rather than relying on cached indexers.
*   **Decentralized Storage (NeoFS)**: We implemented a **`NeoFSManager`** agent. This allows FlowChain to treat decentralized storage as a native file system—automatically uploading sensitive trade logs and backup data to NeoFS containers for immutable, censorship-resistant preservation.
*   **Bullish Neo Logic**: The agent uses on-chain data analysis to dynamically recommend **NEO** accumulation strategies, detecting volatility in other chains (like ETH) and executing swaps into the Neo ecosystem for capital preservation.
