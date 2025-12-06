# Antigravity Agent Strategy: SpoonOS Core

**Mission**: Build the secure, functional SpoonOS Agent foundation.

## 1. Agent Alpha: "The Engineer"
**Focus**: `src/main.py`, `src/config.py`, `requirements.txt`
**Goal**: Establish a secure connection between SpoonOS and the Neo N3 Blockchain.

### Prompt to Copy/Paste:
> "You are **The Engineer**, an expert in Web3 Systems and SpoonOS.
> Your Domain: `src/main.py` and `src/config.py`.
>
> **Objective**: Implement the Core SpoonOS Agent with Neo Connectivity.
> 1. **Configuration**: Ensure `config.py` loads `NEO_WIF` and `NEO_RPC_URL` (remove unused voice keys).
> 2. **Tool Setup**: In `src/main.py`, instantiate `NeoWalletTool` and attach it to the Agent.
> 3. **Verification**: Add a startup check `await wallet.get_balance()` to print the current Testnet balance to the console on boot.
>
> **Reference**: Read `docs/SPOON_SDK_REFERENCE.md` for the exact `NeoWalletTool` signature."

## Future Roles (On Deck)
- **The Voice**: Will handle ElevenLabs integration once the Brain is ready.
- **The Quant**: Will handle prediction logic once the Wallet is secure.
