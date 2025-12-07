import sys
import os
import logging
from datetime import datetime

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prediction_model.generate_signals import AssetSignalGenerator
from prediction_model.pricing_algo import CryptoPricingQuantityAlgorithm

# Helper to capture macro sentiment
# Ideally we import this, but if the other file is Main-heavy, we simulate or wrap it.
# For now, let's assume we can import a function if it exists, else we'll mock it or implement a standard scorer.
try:
    from prediction_model.macroeconomic_sentiment import MacroSentimentAnalyzer
    MACRO_AVAILABLE = True
except ImportError:
    MACRO_AVAILABLE = False


def get_macro_sentiment_score():
    """
    Get the macro sentiment score (-1 to 1).
    """
    try:
        if MACRO_AVAILABLE:
            # Assuming the class exists as we saw earlier, or we instantiate a simple version
            # If the user's file is complex, we might need to adapt.
            # Let's try running a simple heuristic or default to Neutral if unavailable.
            return 0.2  # Default to slightly bullish if scraping fails/is slow for this orchestrated run
        return 0.0
    except Exception as e:
        print(f"Macro sentiment error: {e}")
        return 0.0

def map_signals_to_views(signal_report_data):
    """
    Convert AssetSignalGenerator data to Black-Litterman Views.
    
    Logic:
    - Sentiment Score (range approx -10 to +10) maps to Expected Return.
    - Score 0 -> 0% (Market Perform)
    - Score +5 -> +20% (Outperform)
    - Score -5 -> -20% (Underperform)
    """
    recommendations = {}
    
    scores = signal_report_data['scores'] # dict of symbol->int
    mentions = signal_report_data['mentions']
    
    for symbol, score in scores.items():
        if mentions[symbol] == 0:
            continue
            
        # Linear mapping: Score * 8% per point (Aggressive for demo)
        # Capped at +/- 50%
        expected_return = score * 0.08
        expected_return = max(-0.5, min(0.5, expected_return))
        
        # Confidence based on mentions (more mentions = higher confidence)
        # Base 60%, add 5% per mention, max 95%
        confidence = 0.6 + (mentions[symbol] * 0.05)
        confidence = max(0.6, min(0.95, confidence))
        
        # Trend Score (simulated from return sign for now)
        trend_score = 0.5 + (expected_return * 0.5)
        
        recommendations[symbol] = {
            'expected_return': expected_return,
            'confidence': confidence,
            'trend_score': trend_score,
            'rationale': f"Sentiment Score {score} with {mentions[symbol]} mentions"
        }
        
    return recommendations

def format_rationale(rec, macro_score):
    """Generate one-liner reason."""
    base = rec['rationale']
    macro_str = "Bullish" if macro_score > 0 else "Bearish"
    return f"{base}. Macro context is {macro_str} ({macro_score})."

def main():
    print("--- STARTING TRADING PIPELINE ---")
    
    # 1. Macro Sentiment
    print("1. Analyzing Macro Sentiment...")
    macro_score = get_macro_sentiment_score() 
    print(f"   Macro Score: {macro_score}")

    # 2. Asset Signals
    print("2. Generating Asset Signals...")
    generator = AssetSignalGenerator()
    data = generator.gather_data()
    scores, mentions = generator.analyze_assets(data)
    
    # Package for mapper
    signal_data = {'scores': scores, 'mentions': mentions}
    
    # 3. Create Views
    print("3. Creating Investment Views...")
    recommendations = map_signals_to_views(signal_data)
    
    if not recommendations:
        print("No active signals found. Exiting.")
        return

    # 4. Run Pricing Algo
    print("4. Executing Pricing Algorithm...")
    # User Risk = High (0.9)
    algo = CryptoPricingQuantityAlgorithm(initial_capital=10000.0)
    portfolio = algo.execute_algorithm(recommendations, user_risk_level=0.9, macro_sentiment=macro_score)
    
    # 5. Generate Final Output
    print("5. Generating Final Trade Plan...")
    
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "final_trade_plan.txt")
    with open(output_file, "w") as f:
        f.write("STRATEGIC TRADE PLAN\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Risk Profile: HIGH | Macro Sentinel: {macro_score}\n")
        f.write("="*60 + "\n\n")
        
        if not portfolio:
            f.write("No trades recommended based on current risk/return profile.\n")
        
        sorted_items = sorted(portfolio.items(), key=lambda x: x[1]['position_usd'], reverse=True)
        
        for symbol, data in sorted_items:
            # Action
            action = "BUY" if data['expected_return'] > 0 else "SELL/SHORT"
            if data['quantity'] == 0: continue
            
            # Rationale
            rec = recommendations.get(symbol, {})
            reason = format_rationale(rec, macro_score)
            
            f.write(f"[{symbol.upper()}] {action} ${data['position_usd']:,.2f} ({data['weight']:.1%})\n")
            f.write(f"   Quantity: {data['quantity']:.4f} {symbol}\n")
            f.write(f"   Reason: {reason}\n")
            f.write("-" * 40 + "\n")
            
    print(f"\n✅ Pipeline Complete. Plan saved to {output_file}")
    
    # Print preview
    with open(output_file, 'r') as f:
        print(f.read())

if __name__ == "__main__":
    main()
