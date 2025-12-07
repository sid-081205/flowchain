"""
Neo Wallet Agent Integration for FlowChain
Integrates Neo N3 blockchain wallet functionality with the FlowChain agent system
"""

import os
import asyncio
import json
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Neo asset script hashes (mainnet/testnet)
NEO_SCRIPT_HASH = "0xef4073a0f2b305a38ec4050e4d3d28bc40ea63f5"
GAS_SCRIPT_HASH = "0xd2a4cff31913016155e38e474a2c06d08be276cf"

# Get config values directly from environment
NEO_WIF = os.getenv("NEO_WIF")
NEO_ADDRESS = os.getenv("NEO_ADDRESS", "")
NEO_RPC_URL = os.getenv("NEO_RPC_URL", "https://testnet1.neo.coz.io:443")
TURNKEY_SIGN_WITH = os.getenv("TURNKEY_SIGN_WITH")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def get_neo_balance_direct(address=None, rpc_url=None):
    """Get Neo wallet balance using direct RPC call"""
    if address is None:
        address = NEO_ADDRESS
    if rpc_url is None:
        rpc_url = NEO_RPC_URL
        
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getnep17balances",
        "params": [address]
    }
    
    try:
        response = requests.post(rpc_url, json=payload, timeout=10)
        data = response.json()
        
        balances = {"NEO": 0, "GAS": 0.0}
        
        if "result" in data and "balance" in data["result"]:
            for item in data["result"]["balance"]:
                asset_hash = item.get("assethash", "")
                amount = int(item.get("amount", "0"))
                
                if asset_hash == NEO_SCRIPT_HASH:
                    balances["NEO"] = amount
                elif asset_hash == GAS_SCRIPT_HASH:
                    balances["GAS"] = amount / 100000000
        
        return balances
    except Exception as e:
        return {"error": str(e), "NEO": 0, "GAS": 0}


class FlowChainNeoIntegration:
    """Integration class to connect Neo wallet with FlowChain agent"""
    
    def __init__(self):
        self.address = NEO_ADDRESS
        self.rpc_url = NEO_RPC_URL
        self.has_private_key = bool(NEO_WIF)
        self._initialized = False
        self._cached_balance = None
    
    async def initialize(self, use_turnkey=False):
        """Initialize the Neo wallet integration"""
        try:
            print("🚀 Initializing FlowChain Neo Wallet Integration...")
            print(f"📍 Wallet Address: {self.address}")
            print(f"🔗 RPC Endpoint: {self.rpc_url}")
            
            balance = get_neo_balance_direct(self.address, self.rpc_url)
            
            self._cached_balance = balance
            self._initialized = True
            print(f"✅ Neo wallet connected successfully!")
            print(f"💰 Balance: {balance.get('GAS', 0)} GAS, {balance.get('NEO', 0)} NEO")
            return True
                
        except Exception as e:
            print(f"❌ Neo integration failed: {e}")
            return False
    
    async def get_wallet_status(self):
        """Get comprehensive wallet status"""
        try:
            balance = get_neo_balance_direct(self.address, self.rpc_url)
            self._cached_balance = balance
            
            return {
                "status": "connected",
                "address": self.address,
                "balance": balance,
                "has_private_key": self.has_private_key,
                "network": "testnet" if "testnet" in self.rpc_url else "mainnet",
                "rpc_url": self.rpc_url
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "address": self.address}
    
    async def get_portfolio_summary(self):
        """Get formatted portfolio summary"""
        if not self._initialized:
            await self.initialize()
        
        try:
            status = await self.get_wallet_status()
            
            if status["status"] == "connected":
                balance = status["balance"]
                neo_balance = balance.get('NEO', 0)
                gas_balance = balance.get('GAS', 0)
                
                summary = "🏦 **Neo Wallet Status**\n"
                summary += f"📍 Address: {self.address[:8]}...{self.address[-6:]}\n"
                summary += f"💰 NEO: {neo_balance}\n"
                summary += f"⛽ GAS: {gas_balance:.8f}\n"
                summary += f"🔗 Network: {status.get('network', 'testnet')}\n"
                summary += f"🔐 Private Key: {'✅ Loaded' if self.has_private_key else '❌ Not loaded'}"
                return summary
            else:
                return f"❌ Neo wallet error: {status.get('error', 'Unknown error')}"
                
        except Exception as e:
            return f"❌ Error accessing Neo wallet: {e}"
    
    async def get_balance(self):
        """Get current wallet balance"""
        return get_neo_balance_direct(self.address, self.rpc_url)
    
    async def execute_neo_command(self, command):
        """Execute a Neo wallet command"""
        if not self._initialized:
            await self.initialize()
        
        command_lower = command.lower()
        
        if any(word in command_lower for word in ["balance", "holdings", "how much", "wallet", "portfolio", "status"]):
            return await self.get_portfolio_summary()
        
        if "neo" in command_lower and any(word in command_lower for word in ["balance", "how much", "have"]):
            balance = await self.get_balance()
            return f"💰 You have {balance.get('NEO', 0)} NEO"
        
        if "gas" in command_lower and any(word in command_lower for word in ["balance", "how much", "have"]):
            balance = await self.get_balance()
            return f"⛽ You have {balance.get('GAS', 0):.8f} GAS"
        
        if any(word in command_lower for word in ["address", "wallet address", "my address"]):
            return f"📍 Your Neo wallet address is: {self.address}"
        
        balance = await self.get_balance()
        return f"🏦 Neo Wallet Status:\n💰 NEO: {balance.get('NEO', 0)}\n⛽ GAS: {balance.get('GAS', 0):.8f}\n📍 Address: {self.address}"


# Global instance
neo_integration = FlowChainNeoIntegration()


async def initialize_neo_wallet(use_turnkey=False):
    """Initialize Neo wallet integration"""
    return await neo_integration.initialize(use_turnkey)


async def get_neo_portfolio():
    """Get Neo portfolio summary"""
    return await neo_integration.get_portfolio_summary()


async def get_neo_balance():
    """Get Neo wallet balance"""
    return await neo_integration.get_balance()


async def execute_neo_operation(command):
    """Execute Neo operation"""
    return await neo_integration.execute_neo_command(command)


async def demo_neo_wallet():
    """Demo Neo wallet functionality"""
    print("🎯 FlowChain Neo Wallet Demo")
    print("=" * 50)
    
    success = await neo_integration.initialize()
    
    if success:
        print("\n📊 Portfolio Summary:")
        summary = await neo_integration.get_portfolio_summary()
        print(summary)
        
        print("\n💬 Testing Commands:")
        test_commands = [
            "What is my NEO balance?",
            "How much GAS do I have?",
            "Show me my wallet address",
        ]
        
        for cmd in test_commands:
            print(f"\n👤 User: {cmd}")
            response = await neo_integration.execute_neo_command(cmd)
            print(f"🤖 Agent: {response}")
    
    print("\n✅ Demo completed!")


if __name__ == "__main__":
    asyncio.run(demo_neo_wallet())
