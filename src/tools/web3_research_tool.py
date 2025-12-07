import sys
import os
import asyncio
from spoon_ai.tools.base import BaseTool

# Add project root to sys.path to allow importing from spoonos_components
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import DeclarativeCryptoAnalysis deeply to avoid import errors during init if dependencies are missing
try:
    from spoonos_components.crypto_analysis import DeclarativeCryptoAnalysis
except ImportError:
    DeclarativeCryptoAnalysis = None

class Web3ResearchTool(BaseTool):
    name: str = "web3_research_tool"
    description: str = "Performs deep web3 market research and token analysis using Binance data and LLM insights. Use this when asked about market trends, specific token analysis, or general crypto research."
    
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Optional specific topic or token to focus on (currently performs broad market analysis)."
            }
        },
        "required": []
    }

    async def execute(self, query: str = ""):
        """
        Executes the DeclarativeCryptoAnalysis pipeline.
        """
        if DeclarativeCryptoAnalysis is None:
            return "Error: Could not import spoonos_components.crypto_analysis. Please check your installation."
        
        try:
            print(f"[Web3ResearchTool] Starting analysis for query: {query}...")
            analyzer = DeclarativeCryptoAnalysis()
            result = await analyzer.run(query=query)
            
            summary = result.get("final_summary", "No summary generated.")
            market_overview = result.get("market_overview", {})
            
            # Format the output for the agent
            output = f"**Market Research Report**\n\n{summary}\n"
            if market_overview.get("best_bet"):
                bet = market_overview["best_bet"]
                output += f"\n**Spotlight Opportunity**: {bet.get('token')} - {bet.get('analysis', {}).get('bet_title')}"
                
            return output
        except Exception as e:
            return f"Error executing web3 research: {str(e)}"
