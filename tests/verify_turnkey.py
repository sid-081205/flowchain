import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.turnkey_neo_tool import TurnkeyNeoWalletTool

async def main():
    print("🔐 Verifying Turnkey Neo Wallet Integration")
    print("=" * 50)
    
    # Check Env
    api_key = os.getenv("TURNKEY_API_KEY")
    sign_with = os.getenv("TURNKEY_SIGN_WITH")
    
    print(f"Environment Check:")
    print(f"TURNKEY_API_KEY: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"TURNKEY_SIGN_WITH: {'✅ Set' if sign_with else '⚠️  Missing (Mock mode will be limited)'}")
    
    # Initialize Tool
    print("\nInitializing Tool...")
    tool = TurnkeyNeoWalletTool(
        rpc_url="https://testnet1.neo.coz.io:443",
        turnkey_sign_with=sign_with or "mock-key-id"
    )
    
    # Test Balance
    print("\n[Test 1] Get Balance")
    balance = await tool.execute("balance")
    print(f"Result: {balance}")
    
    # Test Send (Simulation)
    print("\n[Test 2] Simulate Send Asset")
    send_result = await tool.execute(
        "send", 
        to_address="NbnjKGMBJzJ6j5PHeY5LDCNvsCnHLM7jS", 
        amount=10, 
        asset="GAS"
    )
    print(f"Result: {send_result}")

if __name__ == "__main__":
    asyncio.run(main())
