import os
import asyncio
import json
from typing import Dict, Any, Optional

from spoon_ai.agents.toolcall import ToolCallAgent
from spoon_ai.tools import ToolManager
from spoon_ai.chat import ChatBot
from spoon_ai.schema import Message

try:
    from spoon_toolkits.crypto.crypto_powerdata.tools import CryptoPowerDataCEXTool
except ImportError:
    print("[WARNING] spoon_toolkits not found. Using Mock for Market Data.")
    class MockResult:
        def __init__(self, output, error=None):
            self.output = output
            self.error = error

    class CryptoPowerDataCEXTool:
        async def execute(self, **kwargs):
            # Return fake market data for demo purposes
            return MockResult(output="""
            [Mock Data]
            RSI: 45.2 (Neutral)
            EMA (20): 102.5
            EMA (50): 101.0
            MACD: Bullish Crossover
            Latest Close: 103.0
            """)

class MarketAnalyst:
    """Manager for Crypto Market Analysis using SpoonAI and PowerData."""
    
    def __init__(self, llm_provider="openrouter", model_name="openai/gpt-4o"):
        self.llm = ChatBot(llm_provider=llm_provider, model_name=model_name)
        self.powerdata_tool = CryptoPowerDataCEXTool()
        # We can add more tools here if needed, like the Tavily search if keys present

    async def analyze_token(self, token: str) -> str:
        """Perform a quick technical analysis on a token."""
        token = token.upper()
        symbol = f"{token}/USDT"
        
        try:
            # Fetch data (simplified from example)
            indicators_config = {
                "rsi": [{"timeperiod": 14}],
                "ema": [{"timeperiod": 20}, {"timeperiod": 50}],
                "macd": [{"fastperiod": 12, "slowperiod": 26, "signalperiod": 9}],
            }
            
            result = await self.powerdata_tool.execute(
                exchange="binance",
                symbol=symbol,
                timeframe="4h", # Good default
                limit=50,
                indicators_config=json.dumps(indicators_config),
                use_enhanced=True
            )
            
            if result.error:
                 return f"Could not fetch market data for {token}: {result.error}"

            # Summarize with LLM
            data_str = str(result.output)[:2000] # Truncate for prompt limits
            
            prompt = f"""
            You are a crypto analyst. Analyze the following 4h chart data for {token}.
            
            Data: {data_str}
            
            Provide a concise, spoken-word friendly summary:
            1. Current Trend
            2. Key Support/Resistance
            3. Actionable Signal (Buy/Sell/Wait)
            
            Keep it under 3 sentences suitable for reading out loud (TTS).
            """
            
            response = await self.llm.chat([Message(role="user", content=prompt)])
            return response.content.strip()
            
        except Exception as e:
            return f"Analysis failed: {str(e)}"
