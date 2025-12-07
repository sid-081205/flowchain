import logging
import requests
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class MarketScraper:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        # Mapping symbol -> CoinGecko ID
        self.asset_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'SOL': 'solana',
            'XRP': 'ripple',
            'BNB': 'binancecoin',
            'DOGE': 'dogecoin',
            'ADA': 'cardano',
            'AVAX': 'avalanche-2',
            'LINK': 'chainlink',
            'MATIC': 'matic-network'
        }

    def fetch_prices(self) -> Dict[str, Dict]:
        """Fetch current price and 24h change for tracked assets"""
        try:
            logging.info("Fetching market data from CoinGecko...")
            ids = ",".join(self.asset_map.values())
            url = f"{self.base_url}/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # print(f"DEBUG: {data}") 
                results = {}
                
                # Remap back to symbols
                for symbol, cg_id in self.asset_map.items():
                    if cg_id in data:
                        coin_data = data[cg_id]
                        results[symbol] = {
                            'price': coin_data.get('usd', 0),
                            'change_24h': coin_data.get('usd_24h_change', 0)
                        }
                
                logging.info(f"Fetched market data for {len(results)} assets")
                return results
            else:
                logging.error(f"CoinGecko API Error: {response.status_code}")
                return {}
                
        except Exception as e:
            logging.error(f"Error fetching market data: {str(e)}")
            return {}

if __name__ == "__main__":
    scraper = MarketScraper()
    data = scraper.fetch_prices()
    for symbol, info in data.items():
        print(f"{symbol}: ${info['price']} ({info['change_24h']:.2f}%)")
