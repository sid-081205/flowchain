import asyncio
import os
import sys
import json

# Add project root to sys.path to allow running as script
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

# SDK Imports
from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.tools import ToolManager
from spoon_ai.chat import ChatBot
from spoon_ai.schema import Message

# Project Imports
from src import config
from src.neo_wallet_agent import neo_integration, initialize_neo_wallet, get_neo_portfolio

from src.tools.market_tool import MarketAnalyticsTool
from src.tools.recommendation_tool import TradeRecommendationTool
from src.tools.web3_research_tool import Web3ResearchTool
from src.tools.neofs import NeoFSManager
from src.tools.turnkey import TurnkeyWalletManager
from src.tools.market import MarketAnalyst

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
    description: str = "A trading assistant for crypto assets with Neo wallet integration"
    system_prompt: str = (
        "You are **FlowChain**, a personal AI crypto wallet assistant. "
        "Your goal is to grow the user's capital by using the prediction model to give suggestions on when to buy and sell, "
        "maximizing returns or cutting losses.\n\n"
        
        "**PERSONALITY & TONE**\n"
        "- **Conversational & Direct**: Speak like a helpful personal assistant. Be straight to the point but use full sentences.\n"
        "- **No Jargon**: Avoid futuristic phrases like 'Systems Online'. Just say 'I'm ready' or 'Here is the data'.\n\n"

        "**CORE CAPABILITIES & TOOLS**\n"
        "1.  **get_trade_recommendations**: USE THIS FIRST for any question about trading, predictions, or strategy. "
        "It reads the latest trade plan from the prediction model. Explain the rationale (sentiment/macro) before giving the signal.\n"
        "2.  **web3_research_tool**: Use for deep-dive analysis on specific tokens or market trends.\n"
        "3.  **Neo Wallet**: You can check balances and sign transactions via Turnkey.\n\n"

        "**OPERATIONAL PROTOCOLS**\n"
        "- **On Execution**: If you execute a trade or transaction, explicitly REITERATE the action you took. Example: 'I have bought you 0.08 BTC.'\n"
        "- **Voice Behavior**: Keep responses speakable. If there is an error (e.g., wallet connection failed), explicitly VOICE the error out to the user.\n"
        "- **Safety**: Always verify funds before recommending execution.\n"
    )
    max_steps: int = 10

async def get_intent_router(llm: ChatBot, query: str) -> str:
    """Classifies the intent of the user query."""
    system_prompt = """
    You are a query router. Classify the user's request into one of these categories:
    - 'neofs': Storage, uploading, downloading, files.
    - 'turnkey': Wallet creation, signing, keys, security, batch operations.
    - 'market': Price analysis, charts, trends, buy/sell advice.
    - 'general': Everything else (chat, specific NEO operations if not covered above).
    
    Respond with ONLY the category name in JSON format: {"category": "..."}
    """
    try:
        response = await llm.chat([
            Message(role="system", content=system_prompt),
            Message(role="user", content=query)
        ])
        data = json.loads(response.content.strip())
        return data.get("category", "general")
    except:
        return "general"

async def main():
    print("Initializing FlowChain Guardian Agent with Neo Wallet...")

    # 1. Initialize Neo Wallet Integration
    print("🔗 Connecting to Neo N3 blockchain...")
    neo_success = await initialize_neo_wallet()
    
    if neo_success:
        print("✅ Neo wallet integration successful!")
        # Get initial portfolio status
        portfolio = await get_neo_portfolio()
        print(f"📊 Portfolio Status:\n{portfolio}")
    else:
        print("⚠️ Neo wallet integration failed - continuing with limited functionality")

    # 2. Setup Tools
    market_tool = MarketAnalyticsTool()
    rec_tool = TradeRecommendationTool()
    research_tool = Web3ResearchTool()

    # 3. Create Agent
    if not config.GEMINI_API_KEY:
         print("[ERROR] GEMINI_API_KEY not set. Please add it to .env.")
         return

    llm_provider = "gemini"
    model_name = "gemini-2.5-flash"
    api_key = config.GEMINI_API_KEY

    # Helper for routing
    router_llm = ChatBot(llm_provider=llm_provider, model_name=model_name, api_key=api_key)

    # Specialized Agents
    neofs_mgr = NeoFSManager(llm_provider=llm_provider, model_name=model_name)
    turnkey_mgr = TurnkeyWalletManager(llm_provider=llm_provider, model_name=model_name)
    # market_mgr = MarketAnalyst(llm_provider=llm_provider, model_name=model_name) # Assuming this tool exists or was removed. 
    # Based on previous file reads, MarketAnalyst was imported. If it's valid, keep it. 
    # But wait, did I verify MarketAnalyst? It was in imports. Let's keep it consistent with previous main.py
    market_mgr = MarketAnalyst(llm_provider=llm_provider, model_name=model_name)

    guardian = FlowChainAgent(
        llm=ChatBot(
            llm_provider=llm_provider, 
            model_name=model_name, 
            api_key=api_key,
            max_tokens=8192
        ),
        available_tools=ToolManager([market_tool, rec_tool, research_tool]) 
    )

    print(f"🤖 Agent {guardian.name} initialized with Neo wallet integration and SpoonOS tools.")

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

    await interactive_loop(guardian, neofs_mgr, turnkey_mgr, market_mgr, router_llm, voice_assistant)

async def interactive_loop(guardian, neofs, turnkey, market, router_llm, voice=None):
    """Interaction loop with routing."""
    print("\n💬 FlowChain CLI Ready. Type 'exit' to quit.")
    if voice:
        print("🎤 Voice Mode Enabled. Speak to interact.")
    print("------------------------------------------------")
    
    while True:
        try:
            user_msg = ""
            if voice:
                user_msg = voice.listen()
                if not user_msg: continue
                if user_msg.lower() in ["exit", "quit", "stop", "goodbye"]:
                     print("Exiting...")
                     break
            else:
                print("You: ", end="", flush=True)
                user_msg = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not user_msg: break
            
            user_msg = user_msg.strip()
            if user_msg.lower() in ["exit", "quit"]: break
            if not user_msg: continue

            print(f"You said: {user_msg}") # Feedback in CLI

            # Routing
            print("...Thinking...")
            category = await get_intent_router(router_llm, user_msg)
            print(f"[Debug] Intent detected: {category}")
            
            response = ""
            try:
                if category == "neofs":
                    response = await neofs.run(user_msg)
                elif category == "turnkey":
                    response = await turnkey.run(user_msg)
                elif category == "market":
                    if "eth" in user_msg.lower(): token = "ETH"
                    elif "btc" in user_msg.lower(): token = "BTC"
                    elif "neo" in user_msg.lower(): token = "NEO"
                    else: token = "BTC"
                    response = await market.analyze_token(token)
                else:
                    response = await guardian.run(user_msg)

                print(f"FlowChain: {response}")
                
                if voice:
                    # Simple mood detection
                    response_lower = response.lower()
                    mood = "neutral"
                    if any(w in response_lower for w in ["profit", "gain", "excellent", "secure", "good", "great"]):
                        mood = "happy"
                    elif any(w in response_lower for w in ["loss", "drop", "critical", "alert", "warning", "regret", "shit", "error", "failed"]):
                        mood = "serious"
                    voice.speak(response, mood=mood)
                    
            except Exception as e:
                print(f"FlowChain [Error]: {e}")
                error_msg = f"I'm sorry, I encountered an error executing that request: {str(e)}"
                if voice: voice.speak(error_msg)

        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nShutting down...")
            break

if __name__ == "__main__":
    asyncio.run(main())
