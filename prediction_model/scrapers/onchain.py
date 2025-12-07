import logging
import os
import san
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class OnChainScraper:
    def __init__(self):
        self.api_key = os.getenv("SANTIMENT_API_KEY")
        if not self.api_key:
            logger.warning("SANTIMENT_API_KEY not found in environment. On-chain data will be skipped.")
        
        # Santiment uses 'slugs' which are largely similar to CoinGecko IDs but we verify
        self.slug_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'SOL': 'solana',
            'XRP': 'xrp', # Santiment uses 'xrp' usually, not 'ripple'
            'BNB': 'binance-coin',
            'DOGE': 'dogecoin',
            'ADA': 'cardano',
            'AVAX': 'avalanche',
            'LINK': 'chainlink',
            'MATIC': 'matic-network'
        }

    def fetch_metrics(self) -> Dict[str, Dict]:
        """Fetch daily active addresses, MVRV, and dev activity"""
        results = {}
        if not self.api_key:
            return results

        try:
            logging.info("Fetching on-chain data from Santiment...")
            
            # We want data for the last 1 day (or current state)
            # sanpy is dataframe based.
            
            # We'll fetch 30d MVRV (mvrv_usd_30d)
            # Daily Active Addresses (daily_active_addresses)
            # Dev activity (dev_activity)
            
            # Efficient way: loop for now as batching complex metrics can be tricky
            slugs = list(self.slug_map.values())
            
            # Sanity check connection/key implicitly on first call
            
            for symbol, slug in self.slug_map.items():
                metrics = {'mvrv_30d': 0, 'active_addresses': 0, 'dev_activity': 0}
                
                # 1. MVRV 30d
                try:
                    mvrv = san.get("mvrv_usd_30d", slug=slug, from_date="utc_now-1d", to_date="utc_now")
                    if not mvrv.empty: metrics['mvrv_30d'] = float(mvrv.iloc[-1, 0])
                except Exception:
                    pass # Likely restricted
                
                # 2. DAA
                try:
                    daa = san.get("daily_active_addresses", slug=slug, from_date="utc_now-1d", to_date="utc_now")
                    if not daa.empty: metrics['active_addresses'] = int(daa.iloc[-1, 0])
                except Exception:
                    pass

                # 3. Dev Activity (Usually free)
                try:
                    dev = san.get("dev_activity", slug=slug, from_date="utc_now-1d", to_date="utc_now")
                    if not dev.empty: metrics['dev_activity'] = int(dev.iloc[-1, 0])
                except Exception:
                    pass

                results[symbol] = metrics

            logging.info(f"Fetched on-chain data for {len(results)} assets")
            return results

        except Exception as e:
            logging.error(f"Santiment API Error: {str(e)}")
            return {}

if __name__ == "__main__":
    scraper = OnChainScraper()
    # Need to config API key for local run if not in env
    # san.ApiConfig.api_key = os.getenv("SANTIMENT_API_KEY") 
    data = scraper.fetch_metrics()
    for sym, metrics in data.items():
        print(f"[{sym}] MVRV: {metrics['mvrv_30d']:.2f}% | DAA: {metrics['active_addresses']} | Dev: {metrics['dev_activity']}")
