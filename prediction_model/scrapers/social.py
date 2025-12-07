import os
import requests
import logging
from typing import List, Dict
from datetime import datetime
import time

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Tavily import
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedditScraper:
    def __init__(self):
        self.url = "https://www.reddit.com/r/CryptoCurrency/hot.json?limit=10"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}

    def fetch(self) -> List[Dict]:
        """Fetch hot posts from r/CryptoCurrency"""
        posts = []
        try:
            logging.info("Fetching Reddit data...")
            response = requests.get(self.url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                for child in data['data']['children']:
                    post = child['data']
                    if not post.get('stickied'): # Skip pinned posts
                        posts.append({
                            'source': 'Reddit (r/CC)',
                            'title': post.get('title'),
                            'summary': post.get('selftext', '')[:300] + "...", # Truncate long text
                            'score': post.get('score'),
                            'url': f"https://reddit.com{post.get('permalink')}",
                            'published': datetime.fromtimestamp(post.get('created_utc', 0)).isoformat()
                        })
                logging.info(f"Fetched {len(posts)} Reddit posts")
            else:
                logging.error(f"Reddit API Error: {response.status_code}")
        except Exception as e:
            logging.error(f"Error fetching Reddit: {str(e)}")
        return posts

class TwitterScraper:
    def __init__(self):
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        
    def fetch_selenium(self, query="$BTC crypto") -> List[Dict]:
        """Attempt to fetch tweets using Selenium (Brittle)"""
        tweets = []
        driver = None
        try:
            logging.info("Attempting Twitter scrape via Selenium...")
            chrome_options = Options()
            chrome_options.add_argument("--headless") # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Search URL
            encoded_query = requests.utils.quote(query)
            url = f"https://twitter.com/search?q={encoded_query}&src=typed_query&f=live"
            
            driver.get(url)
            time.sleep(5) # Wait for load
            
            # Simple extractor for tweet text (selectors change often)
            articles = driver.find_elements(By.TAG_NAME, "article")
            for article in articles[:5]:
                try:
                    text = article.text
                    if text:
                        tweets.append({
                            'source': 'Twitter (Selenium)',
                            'title': f"Tweet about {query}",
                            'summary': text.replace('\n', ' ')[:200],
                            'url': 'https://twitter.com', # Hard to get specific link without complex logic
                            'published': datetime.now().isoformat()
                        })
                except:
                    continue
                    
            logging.info(f"Selenium fetched {len(tweets)} tweets")
            
        except Exception as e:
            logging.warning(f"Selenium scrape failed: {str(e)}")
        finally:
            if driver:
                driver.quit()
        return tweets

    def fetch_tavily(self, query="latest cryptocurrency news and tweets") -> List[Dict]:
        """Fetch social context using Tavily API (Reliable Fallback)"""
        results = []
        if not self.tavily_api_key:
            logging.error("No Tavily API key found")
            return results

        try:
            logging.info("Fetching social context via Tavily...")
            client = TavilyClient(api_key=self.tavily_api_key)
            response = client.search(query, search_depth="advanced", max_results=5)
            
            for res in response.get('results', []):
                results.append({
                    'source': 'Social/News (Tavily)',
                    'title': res.get('title'),
                    'summary': res.get('content'),
                    'url': res.get('url'),
                    'published': datetime.now().isoformat()
                })
            logging.info(f"Tavily fetched {len(results)} items")
        except Exception as e:
            logging.error(f"Tavily error: {str(e)}")
            
        return results

    def fetch_all(self) -> List[Dict]:
        # Try Selenium first, fallback to Tavily
        tweets = self.fetch_selenium()
        if not tweets:
            logging.info("Fallback to Tavily...")
            tweets = self.fetch_tavily()
        return tweets

if __name__ == "__main__":
    # Test Reddit
    r_scraper = RedditScraper()
    print("\n--- Reddit Posts ---")
    posts = r_scraper.fetch()
    for p in posts[:2]:
        print(f"- {p['title']}")

    # Test Twitter
    t_scraper = TwitterScraper()
    print("\n--- Twitter/Social Data ---")
    tweets = t_scraper.fetch_all()
    for t in tweets[:2]:
        print(f"- {t['summary'][:100]}...")
