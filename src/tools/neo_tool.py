import sys
import os
import random
import string

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

# Try to import config to check for forced mock mode
try:
    from src import config
except ImportError:
    # If running standalone or tests, config might not be reachable
    class MockConfig:
        USE_MOCK_WALLET = False
    config = MockConfig()

class NeoWalletTool(BaseTool):
    name: str = "neo_wallet_tool"
    description: str = "Interacts with Neo N3 blockchain (Get Balance, Send GAS). Supports mock mode for demos."
    
    # Define parameters schema
    parameters: dict = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Operation to perform. 'balance' checks funds, 'transfer' sends funds.",
                "enum": ["balance", "transfer"]
            },
            "asset": {
                "type": "string",
                "description": "Asset symbol (NEO or GAS). Required for transfer.",
                "enum": ["NEO", "GAS"]
            },
            "amount": {
                "type": "number",
                "description": "Amount to transfer. Required for transfer."
            },
            "to_address": {
                "type": "string",
                "description": "Recipient wallet address. Required for transfer."
            }
        },
        "required": ["command"]
    }
    
    # Private attributes
    _rpc_url: str = PrivateAttr()
    _is_mock: bool = PrivateAttr(default=False)
    _mock_balances: dict = PrivateAttr(default_factory=dict)

    def __init__(self, rpc_url: str, private_key_wif: str):
        super().__init__()
        self._rpc_url = rpc_url
        
        # Determine if we should use mock mode
        # 1. If neo-mamba is missing -> Mock
        # 2. If config.USE_MOCK_WALLET is True -> Mock
        self._is_mock = (not HAS_NEO_MAMBA) or getattr(config, 'USE_MOCK_WALLET', False)
        
        if self._is_mock:
            print("[NeoWalletTool] ⚠️  MOCK MODE ACTIVE. No real blockchain connection.")
            print("[NeoWalletTool] Using in-memory stateful mock wallet.")
            # Initialize Mock Balances from file or default
            try:
                import json
                with open("mock_wallet.json", "r") as f:
                    self._mock_balances = json.load(f)
            except Exception:
                self._mock_balances = {"NEO": 100, "GAS": 520.5, "ETH": 4.2}
        elif private_key_wif:
            print(f"[NeoWalletTool] Initialized with WIF (Length: {len(private_key_wif)})")
        else:
            print("[NeoWalletTool] No WIF provided.")

    async def execute(self, command: str, **kwargs):
        """
        Main entry point.
        """
        if self._is_mock:
            return self._mock_execute(command, **kwargs)

        if command == "balance":
            return await self.get_balance()
        elif command == "transfer":
            # Real implementation skeleton (not active for this demo task)
            return "Transfer not implemented for real wallet in this version."
            
        return f"Unknown command: {command}"
    
    def _mock_execute(self, command: str, **kwargs):
        if command == "balance":
            return self._mock_balances.copy()
        
        elif command == "transfer":
            asset = kwargs.get('asset')
            amount = kwargs.get('amount')
            to_addr = kwargs.get('to_address')
            
            if not asset or not amount or not to_addr:
                return "Error: Transfer requires 'asset', 'amount', and 'to_address'."
            
            if asset not in self._mock_balances:
                return f"Error: Unknown asset {asset}"
            
            if self._mock_balances[asset] < amount:
                return f"Error: Insufficient {asset} balance. Have {self._mock_balances[asset]}, need {amount}."
            
            # Perform transfer
            self._mock_balances[asset] -= amount
            
            # Generate fake TXID
            txid = "0x" + "".join(random.choices(string.hexdigits.lower(), k=64))
            
            return {
                "status": "success",
                "txid": txid,
                "message": f"Sent {amount} {asset} to {to_addr}",
                "new_balance": self._mock_balances
            }
            
        return f"Unknown mock command: {command}"

    async def get_balance(self):
        # Placeholder for actual RPC call using neo-mamba or logic
        # For the demo skeleton with missing dependencies, we return a mock success
        return {"NEO": 100, "GAS": 500}
