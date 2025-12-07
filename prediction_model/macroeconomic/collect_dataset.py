"""
Collect cryptocurrency news articles using Tavily API for sentiment analysis training
"""

import os
import pandas as pd
from dotenv import load_dotenv
from tavily import TavilyClient
import random
import time

# Load environment variables
load_dotenv()

def fetch_crypto_articles(api_key, max_articles=1000):
    """Fetch diverse cryptocurrency news articles"""
    
    client = TavilyClient(api_key=api_key)
    
    # Diverse queries to get balanced dataset
    queries = [
        # Bullish/Positive queries
        "Bitcoin price surge rally all-time high",
        "Ethereum upgrade successful adoption",
        "Cryptocurrency institutional investment growth",
        "Crypto market bullish momentum positive",
        "Bitcoin ETF approval institutional adoption",
        "DeFi protocol growth innovation",
        "Blockchain technology breakthrough advancement",
        "Crypto regulation clarity positive development",
        "Major company Bitcoin adoption",
        "Cryptocurrency mainstream acceptance",
        
        # Bearish/Negative queries
        "Bitcoin crash decline bear market",
        "Cryptocurrency market crash plunge",
        "Crypto exchange hack security breach",
        "Regulatory crackdown cryptocurrency ban",
        "Bitcoin price fall below support",
        "Crypto market fear uncertainty doubt",
        "Cryptocurrency scam fraud investigation",
        "Market manipulation crypto concerns",
        "Bitcoin mining environmental concerns",
        "Crypto winter bear market downturn",
        
        # Neutral/Mixed queries
        "Cryptocurrency market analysis outlook",
        "Bitcoin price prediction forecast",
        "Crypto market volatility trading",
        "Blockchain technology development",
        "Central bank digital currency CBDC",
        "Cryptocurrency regulation policy",
        "Bitcoin halving impact analysis",
        "Crypto market trends indicators",
        "Institutional crypto investment strategy",
        "Cryptocurrency adoption statistics"
    ]
    
    all_articles = []
    articles_per_query = max_articles // len(queries)
    
    print(f"Fetching {max_articles} articles across {len(queries)} queries...")
    print("=" * 80)
    
    for i, query in enumerate(queries, 1):
        try:
            print(f"[{i}/{len(queries)}] Fetching: {query[:50]}...")
            response = client.search(query, max_results=articles_per_query)
            
            if 'results' in response:
                for result in response['results']:
                    article = {
                        'title': result.get('title', ''),
                        'content': result.get('content', ''),
                        'url': result.get('url', ''),
                        'query': query
                    }
                    all_articles.append(article)
                
                print(f"  ✓ Fetched {len(response['results'])} articles")
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ✗ Error with query: {e}")
            continue
    
    print("=" * 80)
    print(f"Total articles fetched: {len(all_articles)}")
    
    return all_articles

def label_sentiment(article):
    """
    Heuristic-based sentiment labeling
    Uses keyword matching to assign sentiment labels
    """
    text = f"{article['title']} {article['content']}".lower()
    query = article['query'].lower()
    
    # Positive keywords
    positive_keywords = [
        'surge', 'rally', 'bullish', 'gain', 'rise', 'growth', 'positive', 
        'breakthrough', 'success', 'adoption', 'approval', 'innovation',
        'momentum', 'optimistic', 'upgrade', 'expansion', 'increase',
        'record high', 'all-time high', 'institutional', 'mainstream'
    ]
    
    # Negative keywords
    negative_keywords = [
        'crash', 'plunge', 'bearish', 'decline', 'fall', 'drop', 'negative',
        'hack', 'breach', 'scam', 'fraud', 'ban', 'crackdown', 'fear',
        'uncertainty', 'doubt', 'concern', 'risk', 'threat', 'crisis',
        'collapse', 'manipulation', 'investigation', 'lawsuit'
    ]
    
    # Count keyword occurrences
    positive_count = sum(1 for keyword in positive_keywords if keyword in text)
    negative_count = sum(1 for keyword in negative_keywords if keyword in text)
    
    # Determine sentiment based on query context and keyword counts
    if 'bullish' in query or 'surge' in query or 'growth' in query or 'positive' in query:
        base_sentiment = 'Positive'
    elif 'bearish' in query or 'crash' in query or 'decline' in query or 'negative' in query:
        base_sentiment = 'Negative'
    else:
        base_sentiment = 'Neutral'
    
    # Adjust based on content
    if positive_count > negative_count + 2:
        return 'Positive'
    elif negative_count > positive_count + 2:
        return 'Negative'
    else:
        return base_sentiment

def create_dataset(articles):
    """Create labeled dataset from articles"""
    
    dataset = []
    
    for article in articles:
        # Combine title and content
        text = f"{article['title']} {article['content']}"
        
        # Skip very short articles
        if len(text.split()) < 10:
            continue
        
        # Label sentiment
        sentiment = label_sentiment(article)
        
        dataset.append({
            'text': text,
            'sentiment': sentiment,
            'url': article['url']
        })
    
    return pd.DataFrame(dataset)

def balance_dataset(df, target_per_class=None):
    """Balance the dataset by sentiment class"""
    
    sentiment_counts = df['sentiment'].value_counts()
    print("\nOriginal distribution:")
    print(sentiment_counts)
    
    if target_per_class is None:
        target_per_class = sentiment_counts.min()
    
    # Sample equal amounts from each class
    balanced_dfs = []
    for sentiment in df['sentiment'].unique():
        sentiment_df = df[df['sentiment'] == sentiment]
        if len(sentiment_df) > target_per_class:
            sentiment_df = sentiment_df.sample(n=target_per_class, random_state=42)
        balanced_dfs.append(sentiment_df)
    
    balanced_df = pd.concat(balanced_dfs, ignore_index=True)
    balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print("\nBalanced distribution:")
    print(balanced_df['sentiment'].value_counts())
    
    return balanced_df

def main():
    """Main execution function"""
    
    api_key = os.getenv('TAVILY_API_KEY')
    if not api_key:
        print("Error: TAVILY_API_KEY not found in .env file")
        return
    
    print("\n" + "=" * 80)
    print("CRYPTOCURRENCY SENTIMENT DATASET COLLECTION")
    print("=" * 80 + "\n")
    
    # Fetch articles
    articles = fetch_crypto_articles(api_key, max_articles=900)
    
    if not articles:
        print("\nNo articles fetched. Please check your API key.")
        return
    
    # Create dataset
    print("\nCreating labeled dataset...")
    df = create_dataset(articles)
    
    print(f"Created dataset with {len(df)} entries")
    
    # Balance dataset
    print("\nBalancing dataset...")
    df_balanced = balance_dataset(df)
    
    # Remove neutral class for binary classification
    df_binary = df_balanced[df_balanced['sentiment'].isin(['Positive', 'Negative'])].copy()
    
    print(f"\nFinal dataset size: {len(df_binary)} articles")
    print(f"Positive: {len(df_binary[df_binary['sentiment'] == 'Positive'])}")
    print(f"Negative: {len(df_binary[df_binary['sentiment'] == 'Negative'])}")
    
    # Save dataset
    output_file = 'crypto_sentiment_dataset.csv'
    df_binary.to_csv(output_file, index=False)
    print(f"\n✓ Dataset saved to '{output_file}'")
    
    # Display sample
    print("\nSample entries:")
    print("=" * 80)
    for i, row in df_binary.head(5).iterrows():
        print(f"\nSentiment: {row['sentiment']}")
        print(f"Text: {row['text'][:150]}...")
        print("-" * 80)
    
    return df_binary

if __name__ == "__main__":
    dataset = main()
