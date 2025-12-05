import asyncio
import os
from spoon_ai import Agent, LLM
from spoon_toolkits.web3 import NeoWalletTool
from src import config

async def main():
    print("Initializing VoxAegis Guardian Agent...")

    # 1. Setup Identity
    # Using config.OPENAI_API_KEY implicitly or explicitly depending on SDK
    # Assuming SDK reads from env or we pass it if needed, but the pattern shows simplistic init.
    agent_identity = LLM(provider="openai", model="gpt-4o")

    # 2. Define Tools
    wallet = NeoWalletTool(
        rpc_url=config.NEO_RPC_URL,
        private_key_env="NEO_WIF" # SDK expects env var name, not value
    )

    # 3. Create Agent
    guardian = Agent(
        name="VoxAegis",
        llm=agent_identity,
        tools=[wallet],
        system_prompt="You are a high-frequency trading guardian. Protect assets at all costs. You are capable of executing on-chain transactions via the Neo blockchain."
    )

    print(f"Agent {guardian.name} initialized.")

    # 3.5 Verification: Check Balance
    try:
        balance = await wallet.get_balance()
        print(f"Current Neo Balance: {balance}")
    except Exception as e:
        print(f"Failed to fetch balance: {e}")
    
    # 4. Start Proactive Loop
    try:
        await monitor_loop(guardian)
    except KeyboardInterrupt:
        print("VoxAegis shutting down...")

async def monitor_loop(agent: Agent):
    """
    Main event loop for the guardian.
    """
    print("Starting monitor loop... (Press Ctrl+C to stop)")
    while True:
        # Placeholder for polling logic (Phase 4)
        # Placeholder for Voice I/O (Phase 2)
        
        # For Phase 1, just keep alive and print heartbeat
        # print("Heartbeat: Monitoring...")
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
