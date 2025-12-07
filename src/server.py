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

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from src import config
from src.tools.market_tool import MarketAnalyticsTool
from src.tools.recommendation_tool import TradeRecommendationTool
from src.tools.web3_research_tool import Web3ResearchTool
from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.tools import ToolManager
from spoon_ai.chat import ChatBot

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

app = FastAPI()

# CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "You are FlowChain, a sophisticated AI trading assistant. "
        "Your personality is professional, insightful, and slightly futuristic. "
        "STRICTLY follow this interaction script for the demo:\n"
        "1. **Greeting**: Start with 'Greetings. Systems online. How are you today?'\n"
        "2. **Portfolio Summary**: When asked about holdings/status, DO NOT use any tools. Simply state the current status:\n"
        "   - **Balances**: 100 NEO, 4.2 ETH.\n"
        "   - **CRITICAL**: Mention that ETH has dropped 5% recently due to market volatility.\n"
        "3. **Explanation**: When the user reacts negatively ('shit', 'why?'), use `web3_research_tool` to fetch data citing 'SpoonOS Web3 Market' data. Explain it's due to 'unexpected liquidity shifts in major DeFi protocols'.\n"
        "4. **Recommendations**: When asked 'what should I do?', use `get_trade_recommendations` to read the plan. Present the trades professionaly. Ask for their opinion.\n"
        "5. **Execution & Passkey**: When the user asks to execute, ask for the **Passkey**.\n"
        "   - IF user says 'hacker': valid. Execute the trades (selling ETH/BTC) and confirm success. State: 'Executing trades... Done.'\n"
        "   - IF wrong passkey: Deny access.\n"
        "6. **Closing**: Ask if they need anything else.\n"
        "Do not skip steps. Stay in character."
    )
    max_steps: int = 6

# Global agent instance
agent: Optional[FlowChainAgent] = None

async def initialize_agent():
    """Initialize the FlowChain agent"""
    global agent
    
    if agent is not None:
        return agent
    
    print("Initializing FlowChain Guardian Agent...")
    
    # Setup Tools
    market_tool = MarketAnalyticsTool()
    rec_tool = TradeRecommendationTool()
    research_tool = Web3ResearchTool()
    
    # Create Agent
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set. Please add it to .env.")
    
    agent = FlowChainAgent(
        llm=ChatBot(
            llm_provider="gemini", 
            model_name="gemini-2.5-flash", 
            api_key=config.GEMINI_API_KEY,
            max_tokens=8192
        ),
        available_tools=ToolManager([market_tool, rec_tool, research_tool]) 
    )
    
    print(f"Agent {agent.name} initialized.")
    return agent

@app.on_event("startup")
async def startup_event():
    """Initialize agent on server startup"""
    # Suppress unnecessary warnings during startup
    import warnings
    import logging
    
    # Filter out LLM manager cleanup warnings
    logging.getLogger("spoon_ai.llm.manager").setLevel(logging.ERROR)
    
    await initialize_agent()
    print("✅ FlowChain agent initialized and ready")

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
    # Handle CSS and JS files
    if path.endswith('.css') or path.endswith('.js'):
        file_path = os.path.join(frontend_path, path)
        if os.path.exists(file_path):
            return FileResponse(file_path)
    
    # Handle HTML files
    if path.endswith('.html') or path == "":
        file_path = os.path.join(frontend_path, path if path else "index.html")
        if os.path.exists(file_path):
            return FileResponse(file_path)
    
    # Default to index.html for SPA routing
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"error": "File not found"}

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
                # If not JSON, treat as plain text
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
                
                # Process with agent
                try:
                    print(f"🤖 Processing with agent...")
                    response = await agent.run(content)
                    print(f"✅ Agent response: {response[:100]}..." if len(response) > 100 else f"✅ Agent response: {response}")
                    
                    # Send response
                    await websocket.send_json({
                        "type": "response",
                        "message": response,
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

