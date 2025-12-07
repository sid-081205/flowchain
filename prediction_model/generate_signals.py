import logging
import re
from datetime import datetime
from collections import defaultdict
from scrapers.news import NewsScraper
from scrapers.social import RedditScraper, TwitterScraper
from scrapers.market import MarketScraper
from scrapers.onchain import OnChainScraper

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AssetSignalGenerator:
    def __init__(self):
        # Initialize scrapers
        self.news_scraper = NewsScraper()
        self.reddit_scraper = RedditScraper()
        self.twitter_scraper = TwitterScraper()
        self.market_scraper = MarketScraper()
        self.onchain_scraper = OnChainScraper()

        # Keyword Configuration
        self.bullish_keywords = ['surge', 'rally', 'bull', 'high', 'record', 'gain', 'adoption', 'approve', 'etf', 'buy', 'long', 'moon', 'breakout']
        self.bearish_keywords = ['crash', 'drop', 'bear', 'low', 'ban', 'hack', 'fraud', 'sell', 'short', 'risk', 'fail', 'dump', 'plummet']

        # Asset Mapping (Symbol -> List of keywords)
        self.assets = {
            'BTC': ['bitcoin', 'btc', 'satoshi'],
            'ETH': ['ethereum', 'ether', 'eth', 'vitalik'],
            'SOL': ['solana', 'sol'],
            'XRP': ['xrp', 'ripple'],
            'BNB': ['bnb', 'binance coin'],
            'DOGE': ['doge', 'dogecoin'],
            'ADA': ['cardano', 'ada'],
            'AVAX': ['avalanche', 'avax'],
            'LINK': ['chainlink', 'link'],
            'MATIC': ['polygon', 'matic']
        }

    def gather_data(self):
        """Aggregate data from all sources"""
        logging.info("Starting data collection...")
        
        data = {
            'news': self.news_scraper.fetch_all(),
            'reddit': self.reddit_scraper.fetch(),
            'twitter': self.twitter_scraper.fetch_all(),
            'market': self.market_scraper.fetch_prices(),
            'onchain': self.onchain_scraper.fetch_metrics()
        }
        
        logging.info(f"Collected data: {len(data['news'])} news, {len(data['reddit'])} reddit, {len(data['twitter'])} tweets, {len(data['onchain'])} onchain")
        return data

    def calculate_sentiment_score(self, text):
        """Calculate sentiment score for a piece of text"""
        text = text.lower()
        score = 0
        score += sum(1 for k in self.bullish_keywords if k in text)
        score -= sum(1 for k in self.bearish_keywords if k in text)
        return score

    def analyze_assets(self, data):
        """Analyze sentiment per asset"""
        asset_scores = defaultdict(int)
        asset_mentions = defaultdict(int)
        
        all_text_items = []
        
        # Combine all text sources
        for item in data['news']:
            all_text_items.append({'text': f"{item['title']} {item['summary']}", 'source': 'News'})
        for item in data['reddit']:
            all_text_items.append({'text': f"{item['title']} {item['summary']}", 'source': 'Reddit'})
        for item in data['twitter']:
            all_text_items.append({'text': item.get('summary', ''), 'source': 'Twitter'})

        # Process each text item
        for item in all_text_items:
            text = item['text'].lower()
            sentiment = self.calculate_sentiment_score(text)
            
            # Attribute sentiment to assets mentioned in the text
            for symbol, keywords in self.assets.items():
                if any(k in text for k in keywords):
                    asset_scores[symbol] += sentiment
                    asset_mentions[symbol] += 1
        
        return asset_scores, asset_mentions

    def generate_report(self):
        """Generate comprehensive trade report"""
        data = self.gather_data()
        scores, mentions = self.analyze_assets(data)
        market_data = data['market']
        onchain_data = data['onchain']
        
        report = []
        report.append(f"CRYPTO ASSET SIGNAL REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60 + "\n")

        report.append("--- ASSET ANALYSIS (SENTIMENT vs PRICE vs ON-CHAIN) ---")
        
        trade_recommendations = []

        for symbol in self.assets.keys():
            score = scores[symbol]
            mention_count = mentions[symbol]
            price_info = market_data.get(symbol, {'price': 0, 'change_24h': 0})
            chain_info = onchain_data.get(symbol, {'mvrv_30d': 0, 'active_addresses': 0})
            
            price_str = f"${price_info['price']}" if price_info['price'] > 0 else "N/A"
            trend = price_info['change_24h']
            
            # Logic for Signals
            signal = "NEUTRAL"
            rationale = "No strong signal."
            
            # --- ON-CHAIN LOGIC ---
            # MVRV > 15% -> High Risk (Bearish)
            # MVRV < -10% -> Undervalued (Bullish)
            onchain_signal = 0
            if chain_info['mvrv_30d'] > 15: onchain_signal = -2
            if chain_info['mvrv_30d'] < -10: onchain_signal = 2
            
            total_score = score + onchain_signal
            
            # Combined Logic
            # LONG: Positive Sentiment/OnChain + Trend > -2%
            if total_score >= 2 and trend > -2: 
                signal = "BULLISH (LONG)"
                rationale = f"Sentiment/OnChain Score (+{total_score}) support uptrend."
                trade_recommendations.append((symbol, "LONG", rationale))
            
            # SHORT: Negative Sentiment/OnChain + Trend < 2%
            elif total_score <= -2 and trend < 2:
                signal = "BEARISH (SHORT)"
                rationale = f"Sentiment/OnChain Score ({total_score}) indicate weakness."
                trade_recommendations.append((symbol, "SHORT", rationale))
            
            # Log detail if mentioned OR has significant on-chain data
            if mention_count > 0 or chain_info['active_addresses'] > 0:
                report.append(f"[{symbol}] Price: {price_str} ({trend:.2f}%)")
                report.append(f"   Mentions: {mention_count} | Sentiment Score: {score}")
                if chain_info['active_addresses'] > 0:
                    report.append(f"   On-Chain: MVRV {chain_info['mvrv_30d']:.1f}% | DAA {chain_info['active_addresses']}")
                report.append(f"   Signal: {signal}")
                report.append("-" * 30)

        report.append("\n")
        report.append("--- TOP TRADING OPPORTUNITIES ---")
        
        if not trade_recommendations:
            report.append("No high-convinction setpus detected based on current data.")
            report.append("Recommendation: WAIT / CASH")
        else:
            for symbol, direction, reasoning in trade_recommendations:
                report.append(f">> {direction} {symbol}")
                report.append(f"   Why: {reasoning}")
                report.append("")

        return "\n".join(report)

    def save_report(self, report_text):
        output_file = "asset_trade_signals.txt"
        with open(output_file, "w") as f:
            f.write(report_text)
        logging.info(f"Report saved to {output_file}")
        print(report_text)

if __name__ == "__main__":
    try:
        generator = AssetSignalGenerator()
        report = generator.generate_report()
        generator.save_report(report)
    except Exception as e:
        logging.error(f"Generation failed: {str(e)}")
