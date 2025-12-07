import logging
from datetime import datetime
from scrapers.news import NewsScraper
from scrapers.social import RedditScraper, TwitterScraper

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SignalGenerator:
    def __init__(self):
        # Initialize scrapers
        self.news_scraper = NewsScraper()
        self.reddit_scraper = RedditScraper()
        self.twitter_scraper = TwitterScraper()

        # Simple Keyword Dictionary
        self.bullish_keywords = ['surge', 'rally', 'bull', 'high', 'record', 'gain', 'adoption', 'approve', 'etf', 'buy']
        self.bearish_keywords = ['crash', 'drop', 'bear', 'low', 'ban', 'hack', 'fraud', 'sell', 'risk', 'fail']

    def gather_data(self):
        """Aggregate data from all sources"""
        logging.info("Starting data collection...")
        
        data = {
            'news': self.news_scraper.fetch_all(),
            'reddit': self.reddit_scraper.fetch(),
            'twitter': self.twitter_scraper.fetch_all()
        }
        
        logging.info(f"Collected {len(data['news'])} news items, {len(data['reddit'])} reddit posts, {len(data['twitter'])} tweets")
        return data

    def analyze_sentiment(self, text):
        """Simple keyword-based sentiment analysis"""
        text = text.lower()
        bull_score = sum(1 for k in self.bullish_keywords if k in text)
        bear_score = sum(1 for k in self.bearish_keywords if k in text)
        
        if bull_score > bear_score:
            return "BULLISH"
        elif bear_score > bull_score:
            return "BEARISH"
        else:
            return "NEUTRAL"

    def generate_report(self):
        """Generate text report with heuristic trade ideas"""
        raw_data = self.gather_data()
        
        report = []
        report.append(f"CRYPTO MARKET SIGNAL REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60 + "\n")

        # 1. NEWS ANALYSIS
        report.append("--- MARKET NEWS ANALYSIS ---")
        for item in raw_data['news']:
            sentiment = self.analyze_sentiment(item['title'] + " " + item['summary'])
            signal = "WATCH"
            if sentiment == "BULLISH": signal = "CONSIDER LONG"
            if sentiment == "BEARISH": signal = "CONSIDER SHORT"
            
            report.append(f"[{item['source']}] {item['title']}")
            report.append(f"   Sentiment: {sentiment} -> Action: {signal}")
            report.append("-" * 40)
        report.append("\n")

        # 2. SOCIAL ANALYSIS
        report.append("--- SOCIAL SENTIMENT (REDDIT/TWITTER) ---")
        social_items = raw_data['reddit'] + raw_data['twitter']
        for item in social_items:
            title = item.get('title', item.get('summary', ''))
            sentiment = self.analyze_sentiment(title)
            
            report.append(f"[{item.get('source', 'Social')}] {title[:100]}...")
            report.append(f"   Sentiment: {sentiment}")
        report.append("\n")

        # 3. AGGREGATED TRADE IDEAS
        report.append("--- AGGREGATED TRADE IDEAS (HEURISTIC) ---")
        
        # Simple Logic: Count total Bullish vs Bearish signals
        all_texts = [n['title'] for n in raw_data['news']] + \
                    [r['title'] for r in raw_data['reddit']] + \
                    [t.get('summary', '') for t in raw_data['twitter']]
        
        total_text = " ".join(all_texts).lower()
        bull_count = sum(1 for k in self.bullish_keywords if k in total_text)
        bear_count = sum(1 for k in self.bearish_keywords if k in total_text)
        
        market_sentiment = "NEUTRAL"
        if bull_count > bear_count: market_sentiment = "BULLISH"
        if bear_count > bull_count: market_sentiment = "BEARISH"
        
        report.append(f"Overall Market Sentiment: {market_sentiment}")
        report.append(f"Bullish Keywords: {bull_count} | Bearish Keywords: {bear_count}")
        
        if market_sentiment == "BULLISH":
            report.append("\n>> TRADE IDEA: LONG BETA ASSETS (ETH, SOL)")
            report.append("   Rationale: Positive news flow outweighs negative keywords.")
            report.append("   Strategy: Look for dips in strong uptrends.")
        elif market_sentiment == "BEARISH":
            report.append("\n>> TRADE IDEA: SHORT/HEDGE (BTC, ETH)")
            report.append("   Rationale: Negative sentiment dominates headlines.")
            report.append("   Strategy: Sell rallies into resistance.")
        else:
            report.append("\n>> TRADE IDEA: RANGE TRADE / WAIT")
            report.append("   Rationale: Conflicting signals in market data.")
        
        return "\n".join(report)

    def save_report(self, report_text):
        """Save report to file"""
        output_file = "trade_signals_report.txt"
        with open(output_file, "w") as f:
            f.write(report_text)
        logging.info(f"Report saved to {output_file}")
        print(report_text)

if __name__ == "__main__":
    try:
        generator = SignalGenerator()
        report = generator.generate_report()
        generator.save_report(report)
    except Exception as e:
        logging.error(f"Generation failed: {str(e)}")
