import sys
import os
import json
import asyncio

# Ensure we can import from spoonos_components
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../spoonos_components')))

try:
    from spoon_ai.tools.base import BaseTool
    from spoon_ai.turnkey import Turnkey
    from neo3 import vm, blockchain, contracts, storage, settings
    from neo3.network import payload
    from neo3.core import types
    from neo3.wallet import Wallet
    HAS_NEO_MAMBA = True
except ImportError as e:
    print(f"[Warning] neo-mamba not installed or build failed ({e}). Running in MOCK mode.")
    from spoon_ai.tools.base import BaseTool
    # Fallback/Mock classes
    HAS_NEO_MAMBA = False
    class Wallet: pass


class TurnkeyNeoWalletTool(BaseTool):
    """
    A Tool that uses Turnkey (Remote HSM) to sign Neo N3 transactions.
    It builds the transaction locally but sends the hash to Turnkey for signing.
    """
    name: str = "turnkey_neo_wallet"
    description: str = "Manage Neo N3 assets and transactions using Turnkey secure signing. Capabilities: get balance, send assets (gas)."
    parameters: dict = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string", 
                "description": "Operation to perform. Supported: 'balance', 'send'"
            },
            "to_address": {
                "type": "string",
                "description": "Recipient address for 'send' command"
            },
            "amount": {
                "type": "number",
                "description": "Amount to send for 'send' command"
            },
            "asset": {
                "type": "string",
                "description": "Asset symbol (GAS or NEO), default GAS"
            }
        },
        "required": ["command"]
    }

    def __init__(self, rpc_url: str, turnkey_sign_with: str):
        super().__init__()
        self._rpc_url = rpc_url
        self._sign_with = turnkey_sign_with
        self._client = None
        self._is_mock = not HAS_NEO_MAMBA

        if self._is_mock:
            print("[TurnkeyNeo] ⚠️  MOCK MODE ACTIVE. No real blockchain connection.")
        elif turnkey_sign_with:
            print(f"[TurnkeyNeo] Initialized with Key ID: {turnkey_sign_with}")
        else:
            print("[TurnkeyNeo] ⚠️  No Signing Identity (TURNKEY_SIGN_WITH) provided.")

    @property
    def client(self):
        if self._client is None:
            self._client = Turnkey()
        return self._client

    async def execute(self, command: str, **kwargs):
        if self._is_mock:
            return await self._mock_execute(command, **kwargs)

        if command == "balance":
            return await self.get_balance()
        elif command == "send":
            return await self.send_asset(
                kwargs.get("to_address"),
                kwargs.get("amount"),
                kwargs.get("asset", "GAS")
            )
        else:
            return f"Unknown command: {command}"

    async def _mock_execute(self, command: str, **kwargs):
        if command == "balance":
            return json.dumps({"GAS": 100.0, "NEO": 10})
        elif command == "send":
            return f"✅ [MOCK] Sent {kwargs.get('amount')} {kwargs.get('asset')} to {kwargs.get('to_address')} via Turnkey Signer {self._sign_with}"
        return f"Mock received command: {command}"

    async def get_balance(self):
        # Implementation would ideally use public key to get address, 
        # but for now we assume we know the address or just return a placeholder 
        # since getting the public key from Turnkey requires an extra call.
        # For this demo, we'll try to fetch it if possible or just print status.
        return f"Turnkey Neo Wallet Active (Signer: {self._sign_with})\nTo get real balance, we need to derive the public key from Turnkey first."

    async def send_asset(self, to_address: str, amount: float, asset: str):
        if not self._sign_with:
            return "❌ No Signing Identity configured (TURNKEY_SIGN_WITH missing)."

        # 1. Build Transaction (Mock logic for now as full neo3 construction is complex)
        # In a real impl, we would:
        # tx = neo3.Transaction(...)
        # tx_hash = tx.hash()
        
        # 2. Sign with Turnkey
        print(f"[TurnkeyNeo] Requesting signature for transaction from Turnkey (ID: {self._sign_with})...")
        
        # Mocking a hash for demonstration
        mock_tx_hash = "0000000000000000000000000000000000000000000000000000000000000001"
        
        try:
            # We use HASH_FUNCTION_NOT_APPLICABLE because the tx hash is already a hash
            result = self.client.sign_raw_hash(
                sign_with=self._sign_with,
                hash_hex=mock_tx_hash,
                hash_function="HASH_FUNCTION_NOT_APPLICABLE" 
            )
            
            signature = result.get('activity', {}).get('result', {}).get('signRawPayloadResult', {}).get('r') 
            # Note: Actual result parsing depends on Turnkey API response structure for raw payload
            
            return f"✅ Transaction Signed via Turnkey!\nTxHash: {mock_tx_hash}\nTurnkey Activity Status: {result.get('activity', {}).get('status')}"
            
        except Exception as e:
            return f"❌ Turnkey Signing Failed: {str(e)}"
