"""
Macroeconomic News Sentiment Analysis using LSTM Model
"""

import os
import re
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
from dotenv import load_dotenv
from tavily import TavilyClient
import nltk
from nltk.corpus import stopwords

# Download NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# Load environment variables
load_dotenv()

# Constants
MAX_SEQUENCE_LENGTH = 30
MODEL_PATH = 'crypto_sentiment_model.keras'
TOKENIZER_PATH = 'tokenizer.pkl'

# Preprocessing function (same as in notebook)
stop_words = stopwords.words('english')

def preprocess(text):
    """Clean and preprocess text"""
    text = re.sub(r'@\S+|https?:\S+|http?:\S|[^A-Za-z0-9 ]+', ' ', str(text).lower()).strip()
    tokens = [token for token in text.split() if token not in stop_words]
    return " ".join(tokens)

def load_model_and_tokenizer():
    """Load the trained model and tokenizer"""
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        with open(TOKENIZER_PATH, 'rb') as f:
            tokenizer = pickle.load(f)
        return model, tokenizer
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please run the macroeconomic.ipynb notebook first to train and save the model.")
        return None, None

def predict_sentiment(text, model, tokenizer):
    """Predict sentiment for a single text"""
    cleaned_text = preprocess(text)
    sequence = tokenizer.texts_to_sequences([cleaned_text])
    padded = pad_sequences(sequence, maxlen=MAX_SEQUENCE_LENGTH)
    score = model.predict(padded, verbose=0)[0][0]
    sentiment = 'Positive' if score > 0.5 else 'Negative'
    return {
        'text': text,
        'sentiment': sentiment,
        'score': float(score)
    }

def fetch_macro_news(max_results=20):
    """Fetch macroeconomic news affecting cryptocurrency"""
    api_key = os.getenv('TAVILY_API_KEY')
    if not api_key:
        print("Error: TAVILY_API_KEY not found in .env file")
        return []
    
    try:
        client = TavilyClient(api_key=api_key)
        
        queries = [
            "Federal Reserve interest rates cryptocurrency impact",
            "inflation cryptocurrency market",
            "economic recession crypto",
            "central bank policy bitcoin",
            "macroeconomic cryptocurrency"
        ]
        
        all_articles = []
        
        for query in queries:
            try:
                response = client.search(query, max_results=max_results//len(queries))
                
                if 'results' in response:
                    for result in response['results']:
                        article = {
                            'title': result.get('title', ''),
                            'content': result.get('content', ''),
                            'url': result.get('url', ''),
                            'full_text': f"{result.get('title', '')} {result.get('content', '')}"
                        }
                        all_articles.append(article)
                        
            except Exception as e:
                continue
        
        return all_articles
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def analyze_articles(articles, model, tokenizer):
    """Analyze sentiment for all articles"""
    results = []
    
    for article in articles:
        prediction = predict_sentiment(article['full_text'], model, tokenizer)
        results.append({
            'title': article['title'],
            'url': article['url'],
            'sentiment': prediction['sentiment'],
            'score': prediction['score']
        })
    
    return results

def calculate_final_score(results):
    """Calculate final sentiment score"""
    if not results:
        return 0.0
    
    scores = [r['score'] for r in results]
    return float(np.mean(scores))

def main():
    """Main execution function"""
    
    # Load model and tokenizer
    model, tokenizer = load_model_and_tokenizer()
    if model is None or tokenizer is None:
        return
    
    # Fetch news
    articles = fetch_macro_news(max_results=20)
    
    if not articles:
        print("No articles fetched.")
        return
    
    # Analyze sentiment
    results = analyze_articles(articles, model, tokenizer)
    
    # Calculate final score
    final_score = calculate_final_score(results)
    
    # Output results
    print("Articles Analyzed:")
    print("-" * 80)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   Sentiment: {result['sentiment']}")
        print(f"   Score: {result['score']:.4f}")
        print()
    
    print("-" * 80)
    print(f"Final Sentiment Score: {final_score:.4f}")
    print("-" * 80)
    
    return results, final_score

if __name__ == "__main__":
    results, final_score = main()
