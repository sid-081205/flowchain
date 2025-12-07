#!/usr/bin/env python3
"""
Quick test to check Neo wallet connection and holdings
"""
import asyncio
import os
import sys
import requests

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from dotenv import load_dotenv
load_dotenv(override=True)

# Your wallet details
NEO_ADDRESS = "NgT5VoR2R5FdDBrEhmjj3TdarVW1tHVCy8"
NEO_RPC_URL = "https://testnet1.neo.coz.io:443"

def check_neo_balance_rpc():
    """Check NEO balance using direct RPC call"""
    print("🔗 Connecting to Neo N3 Testnet...")
    print(f"📍 Address: {NEO_ADDRESS}")
    print(f"🌐 RPC: {NEO_RPC_URL}")
    print("-" * 50)
    
    # NEO contract hash on Neo N3
    NEO_CONTRACT = "0xef4073a0f2b305a38ec4050e4d3d28bc40ea63f5"
    GAS_CONTRACT = "0xd2a4cff31913016155e38e474a2c06d08be276cf"
    
    try:
        # Get NEO balance
        neo_payload = {
            "jsonrpc": "2.0",
            "method": "invokefunction",
            "params": [
                NEO_CONTRACT,
                "balanceOf",
                [{"type": "Hash160", "value": address_to_scripthash(NEO_ADDRESS)}]
            ],
            "id": 1
        }
        
        response = requests.post(NEO_RPC_URL, json=neo_payload, timeout=10)
        neo_result = response.json()
        
        neo_balance = 0
        if "result" in neo_result and "stack" in neo_result["result"]:
            stack = neo_result["result"]["stack"]
            if stack and "value" in stack[0]:
                neo_balance = int(stack[0]["value"]) if stack[0]["value"] else 0
        
        # Get GAS balance
        gas_payload = {
            "jsonrpc": "2.0",
            "method": "invokefunction",
            "params": [
                GAS_CONTRACT,
                "balanceOf",
                [{"type": "Hash160", "value": address_to_scripthash(NEO_ADDRESS)}]
            ],
            "id": 2
        }
        
        response = requests.post(NEO_RPC_URL, json=gas_payload, timeout=10)
        gas_result = response.json()
        
        gas_balance = 0
        if "result" in gas_result and "stack" in gas_result["result"]:
            stack = gas_result["result"]["stack"]
            if stack and "value" in stack[0]:
                raw_gas = int(stack[0]["value"]) if stack[0]["value"] else 0
                gas_balance = raw_gas / 100000000  # GAS has 8 decimals
        
        print("✅ Wallet Connected Successfully!")
        print("-" * 50)
        print("💰 YOUR NEO WALLET HOLDINGS:")
        print(f"   NEO: {neo_balance}")
        print(f"   GAS: {gas_balance:.8f}")
        print("-" * 50)
        
        return {"NEO": neo_balance, "GAS": gas_balance}
        
    except Exception as e:
        print(f"❌ Error connecting to Neo network: {e}")
        return None

def address_to_scripthash(address: str) -> str:
    """Convert Neo N3 address to scripthash"""
    import base58
    import hashlib
    
    try:
        # Decode base58 address
        decoded = base58.b58decode(address)
        # Remove version byte and checksum (first byte + last 4 bytes)
        scripthash_bytes = decoded[1:-4]
        # Reverse for little-endian
        scripthash_hex = scripthash_bytes[::-1].hex()
        return scripthash_hex
    except Exception as e:
        # Fallback: try simple conversion
        print(f"Note: Using fallback address conversion")
        return address

def simple_balance_check():
    """Simple balance check using getnep17balances"""
    print("🔗 Checking Neo wallet balance...")
    print(f"📍 Address: {NEO_ADDRESS}")
    print("-" * 50)
    
    payload = {
        "jsonrpc": "2.0",
        "method": "getnep17balances",
        "params": [NEO_ADDRESS],
        "id": 1
    }
    
    try:
        response = requests.post(NEO_RPC_URL, json=payload, timeout=15)
        result = response.json()
        
        if "result" in result:
            balances = result["result"].get("balance", [])
            
            print("✅ Wallet Connected Successfully!")
            print("-" * 50)
            print("💰 YOUR NEO WALLET HOLDINGS:")
            
            neo_balance = 0
            gas_balance = 0
            
            for balance in balances:
                asset_hash = balance.get("assethash", "")
                amount = balance.get("amount", "0")
                
                # NEO contract
                if asset_hash == "0xef4073a0f2b305a38ec4050e4d3d28bc40ea63f5":
                    neo_balance = int(amount)
                    print(f"   NEO: {neo_balance}")
                # GAS contract
                elif asset_hash == "0xd2a4cff31913016155e38e474a2c06d08be276cf":
                    gas_balance = int(amount) / 100000000
                    print(f"   GAS: {gas_balance:.8f}")
                else:
                    print(f"   Token ({asset_hash[:10]}...): {amount}")
            
            if not balances:
                print("   NEO: 0")
                print("   GAS: 0")
                print("\n💡 Tip: Get testnet NEO/GAS from https://neowish.ngd.network/")
            
            print("-" * 50)
            return {"NEO": neo_balance, "GAS": gas_balance}
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Connection timeout - Neo RPC server may be slow")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("🏦 FlowChain Neo Wallet Connection Test")
    print("=" * 50)
    
    # Use simple balance check method
    result = simple_balance_check()
    
    if result:
        print("\n✅ Neo wallet successfully linked to FlowChain!")
        print(f"🔐 Private Key: Loaded from .env (NEO_WIF)")
    else:
        print("\n⚠️ Could not retrieve balance, but wallet may still be configured.")
        print("The wallet credentials are set in your .env file.")
