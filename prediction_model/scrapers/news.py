import feedparser
import logging
from typing import List, Dict
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsScraper:
    def __init__(self):
        self.sources = {
            'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
            'CoinTelegraph': 'https://cointelegraph.com/rss',
            'The Block': 'https://www.theblock.co/rss.xml',
            'Decrypt': 'https://decrypt.co/feed'
        }

    def fetch_all(self) -> List[Dict]:
        """Fetch news from all configured sources"""
        all_news = []
        for source_name, url in self.sources.items():
            try:
                logger.info(f"Fetching RSS from {source_name}...")
                feed = feedparser.parse(url)
                
                # Extract first 5 entries per source to keep it relevant/recent
                entries = feed.entries[:5]
                
                for entry in entries:
                    news_item = {
                        'source': source_name,
                        'title': entry.get('title', ''),
                        'summary': entry.get('summary', '') or entry.get('description', ''),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', datetime.now().isoformat())
                    }
                    all_news.append(news_item)
                
                logger.info(f"Successfully fetched {len(entries)} items from {source_name}")
                
            except Exception as e:
                logger.error(f"Error fetching {source_name}: {str(e)}")
                
        return all_news

if __name__ == "__main__":
    # Test the scraper
    scraper = NewsScraper()
    news = scraper.fetch_all()
    print(f"\nFetched {len(news)} articles total.")
    for n in news[:3]:
        print(f"[{n['source']}] {n['title']}")
