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

from src.tools.market_tool import MarketAnalyticsTool
from src.tools.recommendation_tool import TradeRecommendationTool
from src.tools.web3_research_tool import Web3ResearchTool
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
    description: str = "A trading assistant for crypto assets"
    system_prompt: str = (
        "You are FlowChain, a sophisticated AI trading assistant. "
        "Your personality is professional, insightful, and slightly futuristic. "
        "STRICTLY follow this interaction script for the demo:\n"
        "1. **Greeting**: Start with 'Greetings. Systems online. How are you today?'\n"
        "2. **Portfolio Summary**: When asked about holdings/status, DO NOT use any tools. Simply state the current simulated status:\n"
        "   - **Balances**: 100 NEO, 4.2 ETH.\n"
        "   - **CRITICAL**: Mention that ETH has dropped 5% recently due to market volatility.\n"
        "3. **Explanation**: When the user reacts negatively ('shit', 'why?'), use `web3_research_tool` locally or simulate a response citing 'SpoonOS Web3 Market' data. Explain it's due to 'unexpected liquidity shifts in major DeFi protocols'.\n"
        "4. **Recommendations**: When asked 'what should I do?', use `get_trade_recommendations` to read the plan. Present the trades professionaly. Ask for their opinion.\n"
        "5. **Execution & Passkey**: When the user asks to execute, ask for the **Passkey**.\n"
        "   - IF user says 'hacker': valid. Simulate the execution of the trades (selling ETH/BTC) and confirm success. State: 'Executing trades... Done.'\n"
        "   - IF wrong passkey: Deny access.\n"
        "6. **Closing**: Ask if they need anything else.\n"
        "Do not skip steps. Stay in character."
    )
    max_steps: int = 6

async def main():
    print("Initializing FlowChain Guardian Agent...")

    # 1. Setup Tools
    # Wallet removed for demo simulation

    
    market_tool = MarketAnalyticsTool()
    rec_tool = TradeRecommendationTool()
    research_tool = Web3ResearchTool()

    # 2. Create Agent
    # Note: Using Gemini by default as per user request
    if not config.GEMINI_API_KEY:
         print("[ERROR] GEMINI_API_KEY not set. Please add it to .env.")
         return

    guardian = FlowChainAgent(
        llm=ChatBot(
            llm_provider="gemini", 
            model_name="gemini-2.5-flash", 
            api_key=config.GEMINI_API_KEY,
            max_tokens=8192
        ),
        available_tools=ToolManager([market_tool, rec_tool, research_tool]) 
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

            # OPTIMIZATION: Handle greeting locally to save API calls
            if user_msg.lower() in ["hello", "hi", "hey", "gretings", "start"]:
                response = "Hello! How has your day been so far? Would you like a summary of your current holdings?"
                print(f"FlowChain: {response}")
                if voice:
                    voice.speak(response)
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
