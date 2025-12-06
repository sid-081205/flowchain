import asyncio
import os
import sys

# Ensure src can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src import config
from src.tools.neo_tool import NeoWalletTool

async def verify():
    print("--- Verifying Neo Wallet Setup ---")
    
    # Reload config to pick up any new env vars if set freshly
    # (Though typically script restart is needed)
    
    if not config.NEO_WIF:
        print("ERROR: NEO_WIF not found in environment variables.")
        print("Please create a .env file and add your Private Key (WIF).")
        return

    print(f"RPC URL: {config.NEO_RPC_URL}")
    
    try:
        # Note: The tool implementation details are inferred. 
        # config.NEO_WIF is the value, but NeoWalletTool might expect the env var NAME or the VALUE.
        # src/main.py uses private_key_env="NEO_WIF", implying it looks up the env var by name.
        if "NEO_WIF" not in os.environ:
             # Just in case config loaded it but it's not in os.environ for the tool (unlikely if load_dotenv used)
             pass

        wallet = NeoWalletTool(
            rpc_url=config.NEO_RPC_URL,
            private_key_wif=config.NEO_WIF
        )
        
        print("Connecting to network...")
        balance = await wallet.get_balance()
        print(f"✅ Success! Connection established.")
        print(f"💰 Balance: {balance} GAS")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print("Check your WIF key, RPC URL, and internet connection.")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify())
