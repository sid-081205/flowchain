#!/usr/bin/env python3
"""
Test script for FlowChain Neo Wallet Integration
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.neo_wallet_agent import FlowChainNeoIntegration, demo_neo_wallet

async def test_neo_integration():
    """Test the Neo wallet integration"""
    print("🧪 Testing FlowChain Neo Wallet Integration")
    print("=" * 60)
    
    try:
        # Test 1: Initialize integration
        print("\n[Test 1] Initializing Neo Integration...")
        integration = FlowChainNeoIntegration()
        success = await integration.initialize()
        
        if success:
            print("✅ Integration initialized successfully")
        else:
            print("❌ Integration initialization failed")
            return
        
        # Test 2: Portfolio summary
        print("\n[Test 2] Getting portfolio summary...")
        portfolio = await integration.get_portfolio_summary()
        print(f"Portfolio data:\n{portfolio}")
        
        # Test 3: Wallet commands
        print("\n[Test 3] Testing wallet commands...")
        test_commands = [
            "What is my NEO balance?",
            "Show wallet status",
            "What assets do I currently hold?",
        ]
        
        for cmd in test_commands:
            print(f"\n👤 Command: {cmd}")
            response = await integration.execute_neo_command(cmd)
            print(f"🤖 Response: {response}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

async def run_full_demo():
    """Run the full Neo wallet demo"""
    print("\n🎯 Running Full Demo...")
    await demo_neo_wallet()

if __name__ == "__main__":
    print("FlowChain Neo Wallet Test Suite")
    print("Choose an option:")
    print("1. Run integration tests")
    print("2. Run full demo")
    print("3. Run both")
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            asyncio.run(test_neo_integration())
        elif choice == "2":
            asyncio.run(run_full_demo())
        elif choice == "3":
            asyncio.run(test_neo_integration())
            asyncio.run(run_full_demo())
        else:
            print("Invalid choice")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed: {e}")
