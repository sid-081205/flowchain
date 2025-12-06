import sys
import os
import asyncio

# --- Path Setup ---
# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.tools.neo_tool import NeoWalletTool
from src import config

async def main():
    print("--- Verifying Mock Wallet ---")
    
    # Ensure Mock Mode is Active for test
    if not config.USE_MOCK_WALLET:
        print(f"[NOTE] USE_MOCK_WALLET is {config.USE_MOCK_WALLET}. Forcing ON for this test.")
        config.USE_MOCK_WALLET = True

    # 1. Initialize Tool
    wallet = NeoWalletTool(rpc_url="http://mock-rpc", private_key_wif="L3_mock_wif")
    
    # 2. Check Initial Balance
    print("\n[Test 1] Check Initial Balance")
    balance = await wallet.execute("balance")
    print(f"Balance: {balance}")
    
    assert "NEO" in balance
    assert "GAS" in balance
    initial_gas = balance["GAS"]
    print(f"Initial GAS: {initial_gas}")

    # 3. Perform Transfer
    transfer_amount = 10
    print(f"\n[Test 2] Transfer {transfer_amount} GAS")
    
    result = await wallet.execute(
        "transfer", 
        asset="GAS", 
        amount=transfer_amount, 
        to_address="N_recipient_address"
    )
    print(f"Transfer Result: {result}")
    
    # Validation
    if isinstance(result, str) and "Error" in result:
        print("❌ Transfer failed unexpectedly.")
        sys.exit(1)
        
    assert result["status"] == "success", "Transfer status should be success"
    assert "txid" in result, "Result should have txid"

    # 4. Verify State Update
    print("\n[Test 3] Verify Balance Deducted")
    new_balance = await wallet.execute("balance")
    print(f"New Balance: {new_balance}")
    
    expected_gas = initial_gas - transfer_amount
    assert new_balance["GAS"] == expected_gas, f"Expected {expected_gas} GAS, got {new_balance['GAS']}"
    
    print("\n✅ Mock Wallet Verification Passed!")

if __name__ == "__main__":
    asyncio.run(main())
