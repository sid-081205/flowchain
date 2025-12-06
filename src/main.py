import asyncio
import sys
import os
from dotenv import load_dotenv

# Ensure project root and spoonos_components are in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)


try:
    from spoon_ai.agents.toolcall import ToolCallAgent
    from spoon_ai.chat import ChatBot
    from spoon_ai.tools import ToolManager
    from spoon_ai.tools.base import BaseTool
except ImportError as e:
    print(f"CRITICAL: Could not import SpoonOS components. Error: {e}")
    sys.exit(1)

from src import config
from src.tools.neo_tool import NeoWalletTool

# --- Monkeypatch ToolManager (Fix for Pydantic/SDK mismatch) ---
original_init = ToolManager.__init__
def patched_init(self, tools=None):
    if tools is None or (isinstance(tools, dict) and 'name' in tools):
        self.tools = []
        self.tool_map = {}
        self.indexed = False
        return
    return original_init(self, tools)
ToolManager.__init__ = patched_init
# -------------------------------------------------------------

async def main():
    print("\n🚀 Initializing FlowChain Guardian (SpoonOS)...")

    # 1. Setup Identity
    print(f"   - LLM: OpenAI (gpt-4o)")
    chatbot = ChatBot(
        llm_provider="openai",
        model_name="gpt-4o",
        api_key=config.OPENAI_API_KEY
    )

    # 2. Define Tools
    print(f"   - Wallet: Neo N3 ({config.NEO_RPC_URL})")
    neo_tool = NeoWalletTool(
        rpc_url=config.NEO_RPC_URL,
        private_key_wif=config.NEO_WIF
    )
    
    # 3. Create Agent
    tool_manager = ToolManager([neo_tool])
    
    guardian = ToolCallAgent(
        agent_name="FlowChainCore",
        agent_description="Neo N3 Guardian Agent",
        llm=chatbot,
        available_tools=tool_manager,
        system_prompt=(
            "You are FlowChain, a secure crypto wallet guardian. "
            "You manage a Neo N3 wallet. "
            "You can check balances and execute transfers using the 'neo_wallet_tool'. "
            "Always be precise with financial data. "
            "If asked to transfer, confirm the details first."
        )
    )
    print(f"✅ Agent {guardian.name} ready.\n")

    # 4. Interactive Loop
    print("💬 Chat with FlowChain (type 'exit' to quit)")
    print("---------------------------------------------")
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit", "q"]:
                break
            
            if not user_input.strip():
                continue

            print("FlowChain:", end=" ", flush=True)
            response = await guardian.run(user_input)
            print(f"{response}\n")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
