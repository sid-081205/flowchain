import sys
import os

# Ensure we can import from spoonos_components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../spoonos_components')))

try:
    from spoon_ai.tools.base import BaseTool
    from pydantic import Field, PrivateAttr
    from neo3 import vm, blockchain, contracts, storage, settings
    from neo3.network import payload
    from neo3.core import types
    from neo3.wallet import Wallet
    HAS_NEO_MAMBA = True
except ImportError as e:
    print(f"[Warning] neo-mamba not installed or build failed ({e}). Running in MOCK mode.")
    # Fallback/Mock classes
    HAS_NEO_MAMBA = False
    class Wallet: pass

class NeoWalletTool(BaseTool):
    name: str = "neo_wallet_tool"
    description: str = "Interacts with Neo N3 blockchain (Get Balance, Send GAS)"
    parameters: dict = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The command to execute.",
                "enum": ["balance", "transfer"]
            },
            "to_address": {
                "type": "string",
                "description": "Recipient address (required for transfer)"
            },
            "amount": {
                "type": "number",
                "description": "Amount of GAS to send (required for transfer)"
            }
        },
        "required": ["command"]
    }
    
    # Private attributes
    _rpc_url: str = PrivateAttr()
    _is_mock: bool = PrivateAttr(default=True)

    def __init__(self, rpc_url: str, private_key_wif: str):
        super().__init__()
        self._rpc_url = rpc_url
        self._is_mock = not HAS_NEO_MAMBA
        
        if self._is_mock:
            print("[NeoWalletTool] ⚠️  MOCK MODE ACTIVE. No real blockchain connection.")
        elif private_key_wif:
            print(f"[NeoWalletTool] Initialized with WIF (Length: {len(private_key_wif)})")
        else:
            print("[NeoWalletTool] No WIF provided.")

    async def execute(self, command: str, to_address: str = None, amount: float = 0, **kwargs):
        """
        Main entry point.
        """
        if self._is_mock:
            return self._mock_execute(command, to_address, amount)

        if command == "balance":
            return await self.get_balance()
        if command == "transfer":
            if not to_address or not amount:
                return "Error: Missing to_address or amount for transfer."
            return await self.transfer(to_address, amount)
            
        return f"Unknown command: {command}"
    
    def _mock_execute(self, command: str, to_address: str = None, amount: float = 0):
        if command == "balance":
            return {"NEO": 100, "GAS": 520.5, "NOTE": "MOCK_DATA"}
        if command == "transfer":
             return f"MOCK_TRANSFER: Sent {amount} GAS to {to_address}. TXID: 0xmock12345"
        return f"Unknown mock command: {command}"

    async def get_balance(self):
        # Placeholder for actual RPC call using neo-mamba or logic
        # For the demo skeleton with missing dependencies, we return a mock success
        return {"NEO": 100, "GAS": 500}
    
    async def transfer(self, to_address: str, amount: float):
        # Logic to construct transaction using Neo-Mamba
        # This will fail efficiently if no dependencies, but we are guarded by _is_mock
        return f"Actual transfer logic not implemented yet. (Address: {to_address}, Amount: {amount})"
