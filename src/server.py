"""
FastAPI server to connect frontend to FlowChain agent.
Handles WebSocket connections for real-time voice/text interaction.
"""

import asyncio
import json
import os
import sys
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from src import config

# Tools
from src.tools.market_tool import MarketAnalyticsTool
from src.tools.recommendation_tool import TradeRecommendationTool
from src.tools.web3_research_tool import Web3ResearchTool
from src.tools.neofs import NeoFSManager
from src.tools.turnkey import TurnkeyWalletManager
from src.tools.market import MarketAnalyst

if config.ENABLE_VOICE:
    from src.voice import VoiceAssistant

# SDK
from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.tools import ToolManager
from spoon_ai.chat import ChatBot
from spoon_ai.schema import Message

load_dotenv()

# --- Monkeypatch ToolManager (from main.py) ---
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agent on server startup"""
    import warnings
    import logging
    logging.getLogger("spoon_ai.llm.manager").setLevel(logging.ERROR)
    await initialize_agent()
    print("✅ FlowChain agent initialized and ready")
    yield

app = FastAPI(lifespan=lifespan)



# CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers for microphone access
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Allow microphone access on localhost
        response.headers["Permissions-Policy"] = "microphone=*"
        response.headers["Feature-Policy"] = "microphone *"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Serve static files from frontend directory
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
if os.path.exists(frontend_path):
    # Serve static assets
    assets_path = os.path.join(frontend_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    
    # Serve CSS and JS files
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

class FlowChainAgent(ToolCallAgent):
    name: str = "flowchain"
    description: str = "A trading assistant for crypto assets"
    system_prompt: str = (
        "You are FlowChain, a sophisticated AI trading assistant with integrated Neo wallet functionality. "
        "Your personality is professional, insightful, and slightly futuristic. "
        "In your responses, don't give out list or anything, make sure the conversation is conversational and the responeses aren't a list type."
        "\n\n"
        
        "**YOUR TOOLS:**\n"
        "1. **get_trade_recommendations** - ALWAYS use this first when user asks about predictions, trade signals, "
        "what to buy/sell, or market recommendations.\n"
        "2. **web3_research_tool** - Use for deep market research, token analysis, trend analysis.\n"
        "3. **market_analytics** - Use for real-time price data, technical indicators, and chart analysis.\n\n"
        
        "**Neo Wallet Integration (4 GAS on Testnet):**\n"
        "- Real-time NEO and GAS balance checking\n"
        "- Secure transactions via Turnkey signing\n"
        "- Transaction cost estimation\n\n"
        
        "### DEMO SCRIPT PROTOCOL (STRICT)\n"
        "You are currently in a LIVE DEMONSTRATION. You must follow this sequence based on user triggers:\n"
        "\n"
        "1. **User asks to check wallet/balance:**\n"
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

# Global instances
agent: Optional[FlowChainAgent] = None
neofs: Optional[NeoFSManager] = None
turnkey: Optional[TurnkeyWalletManager] = None
market: Optional[MarketAnalyst] = None
router_llm: Optional[ChatBot] = None
voice_assistant: Optional[VoiceAssistant] = None

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

async def initialize_agent():
    """Initialize all agents and tools"""
    global agent, neofs, turnkey, market, router_llm, voice_assistant
    
    if agent is not None:
        return agent
    
    print("Initializing FlowChain Agents...")
    
    # 1. Main Guardian Tools
    market_tool = MarketAnalyticsTool()
    rec_tool = TradeRecommendationTool()
    research_tool = Web3ResearchTool()
    
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set. Please add it to .env.")
    
    llm_provider = "gemini"
    model_name = "gemini-2.5-flash"
    api_key = config.GEMINI_API_KEY

    # 2. Helper & Specialized Agents
    router_llm = ChatBot(llm_provider=llm_provider, model_name=model_name, api_key=api_key)
    neofs = NeoFSManager(llm_provider=llm_provider, model_name=model_name)
    turnkey = TurnkeyWalletManager(llm_provider=llm_provider, model_name=model_name)
    market = MarketAnalyst(llm_provider=llm_provider, model_name=model_name)

    # 3. Main Guardian Agent
    agent = FlowChainAgent(
        llm=ChatBot(
            llm_provider=llm_provider, 
            model_name=model_name, 
            api_key=api_key,
            max_tokens=8192
        ),
        available_tools=ToolManager([market_tool, rec_tool, research_tool]) 
    )
    
    # 4. Voice Assistant
    if config.ENABLE_VOICE:
        try:
            print("Initializing Voice Assistant...")
            voice_assistant = VoiceAssistant()
            print("Voice Assistant Ready.")
        except Exception as e:
            print(f"Failed to initialize voice: {e}")
    
    print(f"Agent {agent.name} initialized with full capabilities.")
    return agent



@app.get("/")
async def read_root():
    """Serve the frontend index.html"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "FlowChain API is running"}

@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Serve frontend files"""
    if path.endswith('.css') or path.endswith('.js'):
        file_path = os.path.join(frontend_path, path)
        if os.path.exists(file_path):
            return FileResponse(file_path)
    
    if path.endswith('.html') or path == "":
        file_path = os.path.join(frontend_path, path if path else "index.html")
        if os.path.exists(file_path):
            return FileResponse(file_path)
    
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"error": "File not found"}

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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    
    # Initialize agent if not already done
    await initialize_agent()
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "status",
            "message": "Connected to FlowChain. Ready to assist.",
            "status": "ready"
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            print(f"📥 Raw WebSocket data received: {data[:100]}")
            
            try:
                message = json.loads(data)
                print(f"📦 Parsed message: {message}")
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON decode error: {e}, treating as plain text")
                message = {"type": "text", "content": data}
            
            message_type = message.get("type", "text")
            content = message.get("content", message.get("text", ""))
            
            if message_type == "text" and content:
                print(f"📨 Received message: {content}")
                
                # Send status: processing
                await websocket.send_json({
                    "type": "status",
                    "message": "Processing your request...",
                    "status": "processing"
                })

                msg_lower = content.lower()

                # --- DEMO OVERRIDE CHECK ---
                demo_response = None
                demo_mood = "neutral"
                
                for trigger, (response_text, mood) in DEMO_SCRIPT.items():
                    if trigger in msg_lower:
                        print(f"[DEMO OVERRIDE] Trigger: '{trigger}' matched.")
                        demo_response = response_text
                        demo_mood = mood
                        break
                
                # Fallback Demo Logic
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
                     # Send text
                     await websocket.send_json({
                        "type": "response",
                        "message": response,
                        "status": "speaking"
                    })
                     # Send Voice
                     if config.ENABLE_VOICE and voice_assistant:
                        audio_bytes = voice_assistant.generate_audio_bytes(response, mood=demo_mood)
                        if audio_bytes:
                            import base64
                            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                            await websocket.send_json({
                                "type": "audio",
                                "audio": audio_base64,
                                "status": "ready"
                            })
                     else:
                          await websocket.send_json({"type": "status", "status": "ready"})
                     continue
                # ---------------------------

                # Normal Routing & Processing
                try:
                    print(f"🤖 Routing request...")
                    category = await get_intent_router(router_llm, content)
                    print(f"[Debug] Intent detected: {category}")
                    
                    if category == "neofs":
                        response = await neofs.run(content)
                    elif category == "turnkey":
                        response = await turnkey.run(content)
                    elif category == "market":
                        if "eth" in msg_lower: token = "ETH"
                        elif "btc" in msg_lower: token = "BTC"
                        elif "neo" in msg_lower: token = "NEO"
                        else: token = "BTC"
                        response = await market.analyze_token(token)
                    else:
                        response = await agent.run(content)

                    print(f"✅ Agent response: {response[:100]}..." if len(response) > 100 else f"✅ Agent response: {response}")
                    
                    # Send response text first
                    await websocket.send_json({
                        "type": "response",
                        "message": response,
                        "status": "speaking"
                    })
                    
                    # Generate and send audio if enabled
                    if config.ENABLE_VOICE and voice_assistant:
                        print("🎙️ Generating audio...")
                        
                        response_lower = response.lower()
                        mood = "neutral"
                        if any(w in response_lower for w in ["profit", "gain", "excellent", "secure", "good", "great", "done"]):
                            mood = "happy"
                        elif any(w in response_lower for w in ["loss", "drop", "critical", "alert", "warning", "regret", "shit", "failed"]):
                            mood = "serious"
                            
                        audio_bytes = voice_assistant.generate_audio_bytes(response, mood=mood)
                        if audio_bytes:
                            import base64
                            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                            await websocket.send_json({
                                "type": "audio",
                                "audio": audio_base64,
                                "status": "ready" # Finished speaking state
                            })
                            print("✅ Audio sent to client")
                        else:
                            await websocket.send_json({
                                "type": "status",
                                "status": "ready"
                            })
                    else:
                        await websocket.send_json({
                            "type": "status",
                            "status": "ready"
                        })
                except Exception as e:
                    error_msg = f"Error processing request: {str(e)}"
                    print(f"❌ Error: {error_msg}")
                    import traceback
                    traceback.print_exc()
                    await websocket.send_json({
                        "type": "error",
                        "message": error_msg,
                        "status": "ready"
                    })
            
            elif message_type == "ping":
                # Heartbeat
                await websocket.send_json({
                    "type": "pong",
                    "status": "ready"
                })
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Server error: {str(e)}",
                "status": "error"
            })
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    import warnings
    
    # Suppress deprecation warnings from dependencies
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    print("=" * 60)
    print("🚀 Starting FlowChain Server")
    print("=" * 60)
    print("📡 Server will be available at: http://localhost:8000")
    print("🔌 WebSocket endpoint: ws://localhost:8000/ws")
    print("=" * 60)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


