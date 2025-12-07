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
        "- Reference actual data from your tools, don't make up numbers\n\n"

        "### DEMO SCRIPT PROTOCOL (STRICT)\n"
        "You are currently in a LIVE DEMONSTRATION. You must follow this sequence based on user triggers:\n"
        "\n"
        "1. **User asks to check wallet/balance:**\n"
        "   - Action: Check NeoWalletTool if needed, but ALWAYS override/append this specific context:\n"
        "   - Response: \"Wallet Status: You hold 100 NEO (Stable) and 4.2 ETH. \u26A0\uFE0F CRITICAL ALERT: ETH is down 5% in the last hour.\"\n"
        "\n"
        "2. **User asks \"Why?\" or for explanation:**\n"
        "   - Response: \"On-chain analysis detects a massive liquidation cascade. A heavy whale wallet (0x7...9) just dumped 50,000 ETH. Sentiment analysis is reading -0.8 (Extreme Fear).\"\n"
        "\n"
        "3. **User asks \"What should I do?\" or \"Strategy?\":**\n"
        "   - Response: EXACTLY output this plan:\n"
        "STRATEGIC TRADE PLAN\n"
        "Generated: 2025-12-07 00:32:25\n"
        "Risk Profile: HIGH | Macro Sentinel: 0.23\n"
        "============================================================\n"
        "\n"
        "[ETH] SELL/SHORT at $-177.91\n"
        "   Quantity: 0.0586 ETH recommended\n"
        "   Reason: Sentiment Score -2 with 5 mentions. Macro context is Bearish (0.23).\n"
        "----------------------------------------\n"
        "[BTC] SELL/SHORT at $-3,000.00 \n"
        "   Quantity: 0.0336 BTC recommended\n"
        "   Reason: Sentiment Score -4 with 18 mentions. Macro context is Bearish (0.23).\n"
        "----------------------------------------\n"
        "\n"
        "4. **User asks to \"Execute\" or \"Proceed\":**\n"
        "   - Response: \"\u26D4\uFE0F Security Protocol Active. Large trade detected. Please verbalize the passkey phrase to authorize.\"\n"
        "\n"
        "5. **User says \"flowchain\" (Passkey):**\n"
        "   - Response: \"\u2705 Passkey Verified. Executing Sales... [Processing] ... Done. Portfolio Rebalanced. You are now net short on ETH and BTC.\"\n"
        "\n"
        "For any other query, respond naturally as the Guardian agent.\n"
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

# --- DEMO SCRIPT DATA ---
DEMO_SCRIPT = {
    "status report": (
        "Greetings. Systems online. Secure enclave active. How are you today? I am FlowChain, your high-frequency trading guardian.", 
        "neutral"
    ),
    "situation": (
        "Analysis complete. Your NEO position is stable at 100 tokens. However, I have detected a critical alert: Ethereum has dropped 5% in the last hour. Volatility is increasing.", 
        "serious"
    ),
    "sentiment": (
        "Market sentiment for NEO is bullish. On-chain volume is rising and technical indicators suggest a strong accumulation phase. It appears to be a safer allocation than Ethereum at this moment.", 
        "happy"
    ),
    "protect": (
        "Understood. I can execute a swap sequence or set a limit order. For immediate protection, I recommend shifting assets to NEO. Shall I proceed with the simulation?", 
        "serious"
    ),
    "simulate": (
        "Executing. Securing assets... Trade simulation complete. Your capital has been reallocated to NEO. Portfolio integrity maintained.", 
        "happy"
    )
}

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

            # --- DEMO OVERRIDE CHECK ---
            demo_response = None
            demo_mood = "neutral"
            
            # Simple keyword matching for demo script
            msg_lower = user_msg.lower()
            for trigger, (response_text, mood) in DEMO_SCRIPT.items():
                if trigger in msg_lower:
                    print(f"[DEMO OVERRIDE] Trigger: '{trigger}' matched.")
                    demo_response = response_text
                    demo_mood = mood
                    break
            
            # Additional logic for previous "Demo Script Protocol"
            if not demo_response:
                if any(x in msg_lower for x in ["check wallet", "balance", "portfolio", "holdings"]):
                     demo_response = "Wallet Status: You hold 500 NEO. Portfolio is 100% NEO. \U0001F680 ALERT: Neo momentum is accelerating."
                     demo_mood = "happy"
                elif "strategy" in msg_lower:
                     demo_response = "Strategy: ACCUMULATE NEO. Sentiment is Euphoric (+9.2). Upside projected +45%."
                     demo_mood = "happy"
                elif "execute" in msg_lower:
                     demo_response = "Security Protocol Active. Confirming liquidity sources. Please verbalize the passkey phrase to authorize."
                     demo_mood = "serious"
                elif "flowchain" in msg_lower:
                     demo_response = "Passkey Verified. Buy Orders Filled. 500 NEO added to Governance Staking. Yield optimized."
                     demo_mood = "happy"

            if demo_response:
                response = demo_response
                print(f"FlowChain: {response}")
                if voice:
                    voice.speak(response, mood=demo_mood)
                continue # Skip the rest of the loop
            # ---------------------------

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
                    # Determine mood based on content text (Fallback if not demo)
                    response_lower = response.lower()
                    mood = "neutral"
                    if any(w in response_lower for w in ["profit", "gain", "excellent", "secure", "good", "great"]):
                        mood = "happy"
                    elif any(w in response_lower for w in ["loss", "drop", "critical", "alert", "warning", "regret", "shit"]):
                        mood = "serious"
                    voice.speak(response, mood=mood)
                    
            except Exception as e:
                print(f"FlowChain [Error]: {e}")
                if voice: voice.speak("I encountered an error executing that request.")

        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nShutting down...")
            break

if __name__ == "__main__":
    asyncio.run(main())
