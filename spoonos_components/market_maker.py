import asyncio
import logging
from typing import Dict, Any, Optional

# Import our components
from spoonos_components.crypto_analysis import DeclarativeCryptoAnalysis
from spoonos_components.wallet_agent import FlowchainWalletAgent

logger = logging.getLogger(__name__)

class MarketMaker:
    """
    Orchestrates the creation of Prediction Markets based on Crypto Analysis.
    """
    def __init__(self):
        self.analyst = DeclarativeCryptoAnalysis()
        self.wallet = FlowchainWalletAgent()

    async def run_market_creation_cycle(self, query: str = "") -> Dict[str, Any]:
        print(f"🔄 [MarketMaker] Starting cycle with query: '{query}'")
        
        # Step 1: Analyze Market
        print("📊 [MarketMaker] Running Crypto Analysis...")
        analysis_result = await self.analyst.run(query)
        market_overview = analysis_result.get("market_overview", {})
        final_summary = analysis_result.get("final_summary", "")
        
        best_bet = market_overview.get("best_bet")
        if not best_bet:
            return {
                "status": "skipped",
                "reason": "No high-confidence opportunities found.",
                "analysis_summary": final_summary
            }
        
        bet_title = best_bet.get("analysis", {}).get("bet_title", "Unknown Bet")
        score = best_bet.get("analysis", {}).get("score", 0.5)
        token = best_bet.get("token", "UNKNOWN")
        
        print(f"🎯 [MarketMaker] Identified Opportunity: {bet_title} (Confidence: {score})")
        
        # Step 2: Propose Market Creation
        # We need to sign this proposal to verify "Flowchain AI" is the creator
        print(f"✍️ [MarketMaker] Signing proposal for '{bet_title}'...")
        
        # We use the wallet agent to sign. 
        # In a real app, this would build a transaction to a Factory Contract.
        signature = await self.wallet.sign_bet_proposal(
            title=bet_title,
            outcome="binary_yes_no",
            odds=score
        )
        
        print(f"✅ [MarketMaker] Proposal Signed! Signature: {str(signature)[:30]}...")
        
        return {
            "status": "created",
            "market": {
                "title": bet_title,
                "asset": token,
                "initial_probability": score,
                "creator_signature": signature
            },
            "analysis_summary": final_summary
        }

if __name__ == "__main__":
    async def main():
        mm = MarketMaker()
        res = await mm.run_market_creation_cycle()
        print("\n\n=== CYCLE RESULT ===")
        print(res)
    
    asyncio.run(main())
