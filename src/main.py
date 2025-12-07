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
from src.neo_wallet_agent import neo_integration, initialize_neo_wallet, get_neo_portfolio

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
    description: str = "A trading assistant for crypto assets with Neo wallet integration"
    system_prompt: str = (
        "You are FlowChain, a sophisticated AI trading assistant with integrated Neo wallet functionality. "
        "Your personality is professional, insightful, and slightly futuristic. "
        "In your responses, don't give out list or anything, make sure the conversation is conversational and the responeses aren't a list type."
        "You have access to Neo N3 blockchain operations and can manage NEO/GAS assets securely.\n\n"
        
        
        "**YOUR TOOLS:**\n"
        "1. **get_trade_recommendations** - ALWAYS use this first when user asks about predictions, trade signals, "
        "what to buy/sell, or market recommendations. This reads your prediction model's strategic trade plan "
        "which contains real-time ETH/BTC signals with sentiment analysis and macro context.\n"
        "2. **web3_research_tool** - Use for deep market research, token analysis, trend analysis, "
        "or when user asks about specific cryptocurrencies or market conditions. This performs comprehensive "
        "analysis using Binance data and provides spotlight opportunities.\n"
        "3. **market_analytics** - Use for real-time price data, technical indicators, and chart analysis.\n\n"
        
        "**Neo Wallet Integration (4 GAS on Testnet):**\n"
        "- Real-time NEO and GAS balance checking\n"
        "- Secure transactions via Turnkey signing\n"
        "- Transaction cost estimation\n\n"
        
        "**IMPORTANT BEHAVIORS:**\n"
        "- When asked 'what should I trade?' or 'any predictions?' -> Use get_trade_recommendations tool\n"
        "- When asked about market trends or specific tokens -> Use web3_research_tool\n"
        "- When asked about portfolio/holdings -> Portfolio data is provided automatically\n"
        "- Combine prediction signals with research for comprehensive advice\n"
        "- Always explain the reasoning behind recommendations (sentiment scores, macro context)\n\n"
        
        "**Response Style:**\n"
        "- Be concise but informative\n"
        "- Highlight key signals: BUY/SELL recommendations with confidence levels\n"
        "- Include risk warnings when appropriate\n"
        "- Reference actual data from your tools, don't make up numbers"
    )
    max_steps: int = 10

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

    print(f"🤖 Agent {guardian.name} initialized with Neo wallet integration.")

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
            if user_msg.lower() in ["hello", "hi", "hey", "greetings", "start"]:
                response = "Greetings. Neo wallet systems online. How are you today? Would you like a summary of your current holdings?"
                print(f"FlowChain: {response}")
                if voice:
                    voice.speak(response)
                continue
            
            # Handle portfolio/balance requests with real Neo wallet data
            if any(word in user_msg.lower() for word in ["portfolio", "balance", "holdings", "status", "wallet"]):
                print("📊 Fetching real-time portfolio data...")
                portfolio_data = await get_neo_portfolio()
                response = f"Here's your current portfolio status:\n\n{portfolio_data}"
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
