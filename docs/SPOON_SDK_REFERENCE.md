# SpoonOS SDK Reference

**Usage Warning**: This reference is derived from preliminary documentation. Agents must follow these signatures strictly to avoid `ImportError` or `AttributeError`.

## 1. Core Agent (`spoon_ai`)

### `Agent` Class
The main orchestrator running inside the TEE.

```python
from spoon_ai import Agent, LLM
from spoon_toolkits.web3 import NeoWalletTool

# Initialization
guardian = Agent(
    name="AgentName",              # str: Name of the agent
    llm=agent_identity,            # LLM: The identity/model instance
    tools=[wallet_tool],           # list: List of Tool objects
    system_prompt="Your prompt..." # str: The core directive
)

# Methods
await guardian.speak("Hello world")  # Synthesizes speech (if ElevenLabs integrated)
await guardian.run()                 # Starts the main loop (if not custom)
```

### `LLM` Class
Defines the cognitive backend.

```python
from spoon_ai import LLM

agent_identity = LLM(
    provider="openai",  # str: "openai", "anthropic", etc.
    model="gpt-4o"      # str: Specific model identifier
)
```

## 2. Toolkits (`spoon_toolkits`)

### `NeoWalletTool`
A tool for interacting with the Neo N3 blockchain via Turnkey/Mamba.

```python
from spoon_toolkits.web3 import NeoWalletTool

wallet = NeoWalletTool(
    rpc_url="https://testnet1.neo.coz.io:443", # str: Neo N3 RPC Node
    private_key_env="NEO_WIF"                  # str: NAME of the env var (not the key itself)
)

# Usage (via Agent capability or direct if exposed)
# typically the Agent uses this internally when LLM decides to "send transaction"
```

## 3. Directory Structure Expectations
Agents should assume the following project structure:

```
/
├── src/
│   ├── main.py          # Entry point
│   ├── config.py        # Env vars
│   ├── engine/          # [Quant] Prediction logic
│   └── voice/           # [Voice] IO logic
└── docs/
    └── SPOON_SDK_REFERENCE.md  # This file
```

## 4. Best Practices
- **Environment Variables**: Always load from `src/config.py`, never `os.getenv` directly in functional code if possible.
- **Async**: The runtime is heavily `asyncio` based. Always use `async/await`.
- **Latency**: Voice operations should be optimized for <200ms.
