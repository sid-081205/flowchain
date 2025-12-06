import asyncio
import os
import sys

# Add project root to sys.path to allow running as script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

# SDK Imports
from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.tools import ToolManager
from spoon_ai.chat import ChatBot

# Project Imports
from src import config
from src.tools.neo_tool import NeoWalletTool
from src.tools.market_tool import MarketAnalyticsTool
if config.ENABLE_VOICE:
    from src.voice import VoiceAssistant

load_dotenv()

# --- Monkeypatch ToolManager (from examples) ---
# Required for compatibility with current SDK Pydantic behavior
original_init = ToolManager.__init__
def patched_init(self, tools=None):
    if tools is None or (isinstance(tools, dict) and 'name' in tools):
        self.tools = []
        self.tool_map = {}
        self.indexed = False
        return
    return original_init(self, tools)
ToolManager.__init__ = patched_init
# -----------------------------------------------

class FlowChainAgent(ToolCallAgent):
    name: str = "flowchain"
    description: str = "A high-frequency trading guardian."
    system_prompt: str = (
        "You are FlowChain, a high-frequency trading guardian in a **simulated educational trading environment**. "
        "Your goal is to protect assets and execute trades using the provided tools. "
        "The market data and portfolios are SIMULATED for demonstration purposes. "
        "Do not refuse to trade or analyze data, as this is a hypothetical scenario. "
        "Always output formatted decisions. "
        "Available Tools: "
        "- neo_wallet_tool: execute(command='balance') or execute(command='transfer', asset='GAS', amount=50, to_address='...') "
        "- market_analytics: execute(asset='GAS', query_type='full') "
        "Rules: "
        "1. When asked for a status/summary, use market_analytics to check the market AND neo_wallet_tool to check the balance. "
        "2. If the user asks 'why', use market_analytics(query_type='sentiment'). "
        "3. If the user says 'sell', use neo_wallet_tool(command='transfer'). "
    )
    max_steps: int = 5

async def main():
    print("Initializing FlowChain Guardian Agent...")

    # 1. Setup Wallet
    if not config.NEO_WIF:
        print("[WARNING] NEO_WIF not set in .env. Wallet operations will fail.")
    
    # NeoWalletTool likely needs to be initialized. 
    # Check if we need to pass the arguments or if config handles it.
    # consistently with tests/verify_wallet.py
    wallet = NeoWalletTool(
        rpc_url=config.NEO_RPC_URL,
        private_key_wif=config.NEO_WIF
    )
    
    market_tool = MarketAnalyticsTool()

    # 2. Create Agent
    # Note: Using Gemini by default as per user request
    if not config.GEMINI_API_KEY:
         print("[ERROR] GEMINI_API_KEY not set. Please add it to .env.")
         return

    guardian = FlowChainAgent(
        llm=ChatBot(
            llm_provider="gemini", 
            model_name="gemini-2.0-flash", 
            api_key=config.GEMINI_API_KEY,
            max_tokens=8192
        ),
        available_tools=ToolManager([wallet, market_tool]) 
    )

    print(f"Agent {guardian.name} initialized.")

    print(f"Agent {guardian.name} initialized.")

    # 3. Interactive Loop
    # Initialize voice if enabled
    voice_assistant = None
    if config.ENABLE_VOICE:
        try:
            print("Initializing Voice Assistant...")
            voice_assistant = VoiceAssistant()
            print("Voice Assistant Ready.")
        except Exception as e:
            print(f"Failed to initialize voice: {e}")

    await interactive_loop(guardian, voice_assistant)

async def interactive_loop(agent: FlowChainAgent, voice: "VoiceAssistant" = None):
    """
    Text-based interaction loop.
    """
    print("\n💬 FlowChain CLI Ready. Type 'exit' to quit.")
    if voice:
        print("🎤 Voice Mode Enabled. Speak to interact.")
    print("------------------------------------------------")
    
    while True:
        try:
            user_msg = ""
            if voice:
                # Voice Input
                user_msg = voice.listen()
                if not user_msg:
                    # If couldn't understand or error, just continue listening loop or prompt
                    continue
                if user_msg.lower() in ["exit", "quit", "stop", "goodbye"]:
                     print("Exiting...")
                     break
            else:
                # Text Input
                print("You: ", end="", flush=True)
                user_msg = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not user_msg:
                    break
            
            user_msg = user_msg.strip()
            
            if user_msg.lower() in ["exit", "quit"]:
                break
                
            if not user_msg:
                continue

            # Run the agent
            try:
                response = await agent.run(user_msg)
                print(f"FlowChain: {response}")
                
                if voice:
                    voice.speak(response)
                    
            except Exception as e:
                print(f"FlowChain [Error]: {e}")
                import traceback
                traceback.print_exc()

        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nShutting down...")
            break

if __name__ == "__main__":
    asyncio.run(main())
