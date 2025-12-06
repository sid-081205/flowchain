from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypedDict
import aiohttp

# Configure logging
logger = logging.getLogger(__name__)

from spoon_ai.llm.manager import get_llm_manager
from spoon_ai.schema import Message
# Fallback for MCP tools if graph API is missing (we use manual tool execution or simplified agents)
# In SDK 0.2.1, we might not have 'MCPToolSpec' registry easily accessible without Agents.
# We will simulate the Tavily tool call if possible or just use a placeholder if the tool class isn't standard.
# Actually, we can use the 'Tools' from spoon-ai-sdk if we have them. 

# Import optional toolkits
try:
    from spoon_toolkits.crypto.crypto_powerdata.tools import CryptoPowerDataCEXTool
except ImportError:
    CryptoPowerDataCEXTool = None

try:
    # Try to import Tavily if available in toolkits, otherwise we might need a custom tool
    from spoon_ai.tools import BaseTool
except ImportError:
    BaseTool = object

class DeclarativeCryptoAnalysis:
    def __init__(self) -> None:
        self.llm = get_llm_manager()
        self.powerdata_tool = CryptoPowerDataCEXTool() if CryptoPowerDataCEXTool else None
        # We don't have the Graph API's 'register_mcp_tool', so we skip Tavily mostly or mock it
        self.tavily_search_tool = None 
        # Check environment for Tavily key
        if os.getenv("TAVILY_API_KEY"):
            # If we had a TavilyTool class we would init it here. 
            # For now, we'll skip news or use a simple HTTP fetch if strictly needed.
            pass

    async def _fetch_binance_market_data(self) -> Dict[str, Any]:
        """Fetch real Binance market data"""
        async with aiohttp.ClientSession() as session:
            url = "https://api.binance.com/api/v3/ticker/24hr"
            async with session.get(url) as response:
                if response.status != 200:
                    return {"error": f"Binance API failed: {response.status}"}
                binance_data = await response.json()

        stablecoins = {'USDCUSDT', 'FDUSDUSDT', 'TUSDUSDT', 'BUSDUSDT', 'DAIUSDT', 'USDPUSDT', 'FRAXUSDT', 'LUSDUSDT', 'SUSDUSDT', 'USTCUSDT', 'USDDUSDT', 'GUSDUSDT', 'PAXGUSDT', 'USTUSDT'}

        usdt_pairs = []
        for item in binance_data:
            if isinstance(item, dict) and item.get('symbol', '').endswith('USDT'):
                symbol = item.get('symbol', '')
                if symbol not in stablecoins and all(key in item for key in ['symbol', 'priceChangePercent', 'volume', 'lastPrice']):
                    usdt_pairs.append({
                        'symbol': symbol,
                        'priceChangePercent': float(item['priceChangePercent']),
                        'volume': float(item['volume']),
                        'lastPrice': float(item['lastPrice']),
                        'count': int(item.get('count', 0)),
                        'quoteVolume': float(item.get('quoteVolume', 0))
                    })

        # Top 5 by volume
        top_pairs = sorted(usdt_pairs, key=lambda x: x['quoteVolume'], reverse=True)[:5]
        return {"top_pairs": top_pairs}

    async def _analyze_single_token(self, token: str, price: float, change: float) -> Dict[str, Any]:
        """Analyze a single token"""
        try:
            # 1. Fetch Kline Data
            kline_result = {"daily_data": "N/A (PowerData missing)"}
            if self.powerdata_tool:
                try:
                    symbol = f"{token}/USDT"
                    indicators_config = {"rsi": [{"timeperiod": 14}], "ema": [{"timeperiod": 12}, {"timeperiod": 26}]}
                    daily_result = await self.powerdata_tool.execute(
                        exchange="binance",
                        symbol=symbol,
                        timeframe="1d",
                        limit=50,
                        indicators_config=json.dumps(indicators_config),
                        use_enhanced=True,
                    )
                    # Handle tool output format (might be string or object)
                    kline_result = {"daily_data": str(daily_result)[:1000]} 
                except Exception as e:
                    kline_result = {"error": str(e)}

            # 2. LLM Analysis
            prompt = f"""Analyze {token} for a Prediction Market.
Price: ${price}, 24h Change: {change}%
Tech Data: {kline_result}

Provide:
1. Short sentiment summary.
2. A probability score (0.0 to 1.0) for price INCREASE over next 24h.
3. Suggest a "Bet" title (e.g. "{token} > $X by tomorrow").
Output JSON: {{ "sentiment": "...", "score": 0.X, "bet_title": "..." }}
"""
            llm_response = await self.llm.chat([Message(role="user", content=prompt)])
            try:
                content = llm_response.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].strip()
                
                analysis_json = json.loads(content)
            except:
                analysis_json = {"sentiment": llm_response.content[:100], "score": 0.5, "bet_title": "Analysis failed"}

            return {
                "token": token,
                "analysis": analysis_json,
                "price": price,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as exc:
            return {"token": token, "error": str(exc)}

    async def run(self, query: str = "") -> Dict[str, Any]:
        """Run the analysis pipeline"""
        # Step 1: Binance Data
        binance_res = await self._fetch_binance_market_data()
        if "error" in binance_res:
            return {"error": binance_res["error"]}
        
        top_pairs = binance_res.get("top_pairs", [])
        
        # Step 2: Parallel Analysis
        tasks = []
        for pair in top_pairs:
            token = pair["symbol"].replace("USDT", "")
            price = float(pair["lastPrice"])
            change = float(pair["priceChangePercent"])
            tasks.append(self._analyze_single_token(token, price, change))
        
        results = await asyncio.gather(*tasks)
        
        # Step 3: Aggregation
        token_reports = {r["token"]: r for r in results if "token" in r}
        
        summary = f"Analyzed {len(token_reports)} tokens.\n"
        best_bet = None
        best_score_dist = 0.0
        
        for t, r in token_reports.items():
            if "error" in r: continue
            analysis = r.get("analysis", {})
            score = analysis.get("score", 0.5)
            bet_title = analysis.get("bet_title", "N/A")
            summary += f"- {t}: {bet_title} (Prob: {score})\n"
            
            dist = abs(score - 0.5)
            if dist > best_score_dist:
                best_score_dist = dist
                best_bet = r

        return {
            "final_summary": summary,
            "market_overview": {"best_bet": best_bet},
            "token_reports": token_reports
        }

if __name__ == "__main__":
    async def main():
        print("Running Simple Crypto Analysis...")
        demo = DeclarativeCryptoAnalysis()
        res = await demo.run()
        print(res.get("final_summary"))
    asyncio.run(main())
