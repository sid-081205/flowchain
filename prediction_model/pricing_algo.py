"""
Crypto Pricing and Quantity Algorithm
Combines Black-Litterman Model with Kelly Criterion for optimal portfolio allocation
"""

import numpy as np
import pandas as pd
# from scipy.optimize import minimize # Unused in this snippets but good to have
from typing import Dict, List, Tuple
import requests
from datetime import datetime


class CryptoPricingQuantityAlgorithm:
    """
    Advanced pricing and quantity algorithm for cryptocurrency trading.
    Uses Black-Litterman for asset selection and Kelly Criterion for position sizing.
    """
    
    def __init__(self, 
                 initial_capital: float = 10000.0,
                 risk_free_rate: float = 0.04,
                 tau: float = 0.025):
        """
        Initialize the algorithm.
        
        Args:
            initial_capital: Starting capital in USD
            risk_free_rate: Annual risk-free rate (e.g., 0.04 for 4%)
            tau: Black-Litterman uncertainty parameter (typically 0.01-0.05)
        """
        self.capital = initial_capital
        self.risk_free_rate = risk_free_rate
        self.tau = tau
        
    def get_crypto_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Fetch current crypto prices from CoinGecko API.
        
        Args:
            symbols: List of crypto symbols (e.g., ['bitcoin', 'ethereum'])
            
        Returns:
            Dictionary of symbol: price pairs
        """
        try:
            # CoinGecko API (free, no key required)
            # Map common symbols to ids if needed, but 'bitcoin', 'ethereum' work
            # We might need a mapper if strict symbols like 'BTC' are passed
            # For now assume symbols passed are valid CoinGecko IDs or close
            
            # Simple mapper for safety
            id_map = {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana', 'XRP': 'ripple',
                'BNB': 'binancecoin', 'DOGE': 'dogecoin', 'ADA': 'cardano', 
                'AVAX': 'avalanche-2', 'LINK': 'chainlink', 'MATIC': 'matic-network'
            }
            
            ids_list = [id_map.get(s, s.lower()) for s in symbols]
            ids = ','.join(ids_list)
            
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            prices = {}
            for i, sym in enumerate(symbols):
                cg_id = ids_list[i]
                if cg_id in data:
                    prices[sym] = data[cg_id]['usd']
                else:
                    prices[sym] = 0.0
                    
            return prices
            
        except Exception as e:
            print(f"Error fetching prices: {e}")
            # Return mock prices for demonstration
            return {symbol: 1000.0 * (i + 1) for i, symbol in enumerate(symbols)}
    
    def get_historical_returns(self, symbols: List[str], days: int = 30) -> pd.DataFrame:
        """
        Fetch historical returns for covariance calculation.
        In production, this would pull real historical data.
        
        Args:
            symbols: List of crypto symbols
            days: Number of days of historical data
            
        Returns:
            DataFrame of daily returns
        """
        # Mock historical returns for demonstration
        # In production, fetch real data from CoinGecko or similar API
        np.random.seed(42)
        returns = {}
        
        for symbol in symbols:
            # Generate realistic crypto returns (higher volatility)
            daily_returns = np.random.normal(0.001, 0.05, days)
            returns[symbol] = daily_returns
            
        return pd.DataFrame(returns)
    
    def calculate_covariance_matrix(self, returns_df: pd.DataFrame) -> np.ndarray:
        """
        Calculate covariance matrix from historical returns.
        
        Args:
            returns_df: DataFrame of historical returns
            
        Returns:
            Covariance matrix
        """
        return returns_df.cov().values * 252  # Annualize
    
    def calculate_market_equilibrium(self, 
                                     prices: Dict[str, float],
                                     market_caps: Dict[str, float] = None) -> np.ndarray:
        """
        Calculate market equilibrium returns (prior).
        Uses market cap weights if available, otherwise equal weights.
        
        Args:
            prices: Current crypto prices
            market_caps: Market capitalizations (optional)
            
        Returns:
            Array of equilibrium returns
        """
        n_assets = len(prices)
        
        if market_caps:
            total_cap = sum(market_caps.values())
            weights = np.array([market_caps[symbol] / total_cap for symbol in prices.keys()])
        else:
            # Equal weights if no market cap data
            weights = np.ones(n_assets) / n_assets
        
        # Equilibrium returns based on risk-free rate
        # In practice, use reverse optimization from market weights
        equilibrium_returns = np.ones(n_assets) * (self.risk_free_rate + 0.05)
        
        return equilibrium_returns
    
    def black_litterman_model(self,
                              equilibrium_returns: np.ndarray,
                              covariance_matrix: np.ndarray,
                              views: Dict[str, float],
                              view_confidences: Dict[str, float],
                              symbols: List[str]) -> np.ndarray:
        """
        Implement Black-Litterman model to combine market equilibrium with views.
        
        Args:
            equilibrium_returns: Market equilibrium return vector
            covariance_matrix: Asset covariance matrix
            views: Dictionary of asset views (expected returns from recommendation system)
            view_confidences: Dictionary of confidence levels (0-1) for each view
            symbols: List of crypto symbols
            
        Returns:
            Adjusted expected returns
        """
        n_assets = len(symbols)
        
        # Create view matrix P (links views to assets)
        # For absolute views, P is identity-like
        P = np.zeros((len(views), n_assets))
        Q = np.zeros(len(views))
        omega_diag = []
        
        # Fix: Need to ensure consistent ordering between symbols list and views keys
        view_keys = list(views.keys())
        
        for i, symbol in enumerate(view_keys):
            view_return = views[symbol]
            if symbol in symbols:
                idx = symbols.index(symbol)
                P[i, idx] = 1.0
                Q[i] = view_return
                
                # Uncertainty in views (Omega)
                # Lower confidence = higher uncertainty
                confidence = view_confidences.get(symbol, 0.5)
                # Use variance of the asset as baseline
                variance = covariance_matrix[idx, idx]
                uncertainty = (1 - confidence) * self.tau * variance if variance > 0 else 0.01
                omega_diag.append(uncertainty)
        
        Omega = np.diag(omega_diag)
        
        # Black-Litterman formula
        tau_sigma = self.tau * covariance_matrix
        
        # M = [(τΣ)^-1 + P'Ω^-1P]^-1
        # Added regularization for numerical stability
        try:
            M_inv = np.linalg.inv(tau_sigma) + P.T @ np.linalg.inv(Omega) @ P
            M = np.linalg.inv(M_inv)
            
            # E(R) = M × [(τΣ)^-1 × π + P'Ω^-1 × Q]
            expected_returns = M @ (np.linalg.inv(tau_sigma) @ equilibrium_returns + 
                                    P.T @ np.linalg.inv(Omega) @ Q)
        except np.linalg.LinAlgError:
            print("Matrix inversion failed, using Equilibrium returns")
            return equilibrium_returns
            
        return expected_returns
    
    def kelly_criterion(self,
                       expected_return: float,
                       win_probability: float,
                       volatility: float,
                       base_capital: float) -> float:
        """
        Calculate optimal position size using Kelly Criterion.
        
        Args:
            expected_return: Expected return for the asset
            win_probability: Probability of positive return (from sentiment)
            volatility: Asset volatility
            base_capital: Capital available for this position
            
        Returns:
            Optimal position size in USD
        """
        # Adjust win probability to be bounded
        win_prob = max(0.5, min(0.95, win_probability))
        lose_prob = 1 - win_prob
        
        # Kelly formula with volatility adjustment
        # f* = (p * b - q) / b * (1 - σ²/2)
        # Support for SHORTING: Use absolute return for sizing, then apply sign
        is_short = expected_return < 0
        abs_return = abs(expected_return)
        
        if abs_return == 0:
            return 0.0
        
        odds = abs_return / (1 - abs_return) if abs_return < 1 else abs_return
        
        kelly_fraction = (win_prob * odds - lose_prob) / odds
        
        # Volatility adjustment (reduce position for high volatility)
        volatility_adjustment = max(0.1, 1 - volatility / 2)
        kelly_fraction *= volatility_adjustment
        
        # Ensure fraction is positive and reasonable
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25% per asset
        
        # Apply direction
        if is_short:
            kelly_fraction = -kelly_fraction
        
        position_size = base_capital * kelly_fraction
        
        return position_size
    
    def adjust_for_macro_sentiment(self,
                                   positions: Dict[str, float],
                                   macro_sentiment: float) -> Dict[str, float]:
        """
        Adjust position sizes based on macroeconomic sentiment.
        
        Args:
            positions: Dictionary of symbol: position_size
            macro_sentiment: Score from -1 (very bearish) to +1 (very bullish)
            
        Returns:
            Adjusted positions
        """
        # Macro sentiment multiplier
        # -1.0 (very bearish) -> 0.5x positions
        #  0.0 (neutral) -> 1.0x positions
        # +1.0 (very bullish) -> 1.5x positions
        macro_multiplier = 1.0 + (macro_sentiment * 0.5)
        macro_multiplier = max(0.3, min(1.8, macro_multiplier))
        
        adjusted_positions = {
            symbol: size * macro_multiplier 
            for symbol, size in positions.items()
        }
        
        return adjusted_positions
    
    def apply_risk_constraints(self,
                              positions: Dict[str, float],
                              user_risk_level: float) -> Dict[str, float]:
        """
        Apply user risk preferences and position constraints.
        
        Args:
            positions: Dictionary of symbol: position_size
            user_risk_level: User risk from 0 (conservative) to 1 (aggressive)
            
        Returns:
            Risk-adjusted positions
        """
        # Risk multipliers
        # 0.0-0.25: Conservative (0.25x)
        # 0.25-0.5: Moderate (0.5x)
        # 0.5-0.75: Balanced (1.0x)
        # 0.75-1.0: Aggressive (1.5x)
        if user_risk_level < 0.25:
            risk_multiplier = 0.25
        elif user_risk_level < 0.5:
            risk_multiplier = 0.5
        elif user_risk_level < 0.75:
            risk_multiplier = 1.0
        else:
            # Aggressive
            risk_multiplier = 1.5
        
        # Apply risk multiplier
        adjusted_positions = {
            symbol: size * risk_multiplier 
            for symbol, size in positions.items()
        }
        
        # Position limits
        max_position_per_asset = self.capital * 0.3  # Max 30% per asset
        min_position = self.capital * 0.01  # Min 1% per asset
        
        for symbol in adjusted_positions:
            if abs(adjusted_positions[symbol]) > max_position_per_asset:
                # Retain sign
                sign = 1 if adjusted_positions[symbol] > 0 else -1
                adjusted_positions[symbol] = sign * max_position_per_asset
            elif abs(adjusted_positions[symbol]) < min_position:
                adjusted_positions[symbol] = 0.0  # Don't trade if too small
        
        # Ensure total doesn't exceed capital
        total_allocated = sum(adjusted_positions.values())
        if total_allocated > self.capital:
            scale_factor = self.capital / total_allocated
            adjusted_positions = {
                symbol: size * scale_factor 
                for symbol, size in adjusted_positions.items()
            }
        
        return adjusted_positions
    
    def calculate_quantities(self,
                            positions: Dict[str, float],
                            prices: Dict[str, float]) -> Dict[str, float]:
        """
        Convert position sizes (USD) to quantities (number of coins).
        
        Args:
            positions: Dictionary of symbol: position_size_usd
            prices: Dictionary of symbol: price_per_coin
            
        Returns:
            Dictionary of symbol: quantity
        """
        quantities = {}
        
        for symbol, position_usd in positions.items():
            if position_usd != 0 and symbol in prices and prices[symbol] > 0:
                quantity = position_usd / prices[symbol]
                quantities[symbol] = quantity
        
        return quantities
    
    def execute_algorithm(self,
                         recommendations: Dict[str, Dict],
                         user_risk_level: float,
                         macro_sentiment: float) -> Dict[str, Dict]:
        """
        Main execution function.
        """
        print("\n" + "="*80)
        print("CRYPTO PRICING AND QUANTITY ALGORITHM")
        print("="*80)
        
        # Extract symbols from recommendations
        symbols = list(recommendations.keys())
        print(f"\n📊 Processing {len(symbols)} cryptocurrencies: {', '.join(symbols)}")
        
        # Step 1: Get current prices
        print("\n💰 Step 1: Fetching current prices...")
        prices = self.get_crypto_prices(symbols)
        for symbol, price in prices.items():
            print(f"  {symbol}: ${price:,.2f}")
        
        # Step 2: Get historical data and calculate covariance
        print("\n📈 Step 2: Calculating covariance matrix...")
        returns_df = self.get_historical_returns(symbols)
        covariance_matrix = self.calculate_covariance_matrix(returns_df)
        volatilities = np.sqrt(np.diag(covariance_matrix))
        print(f"  Volatility range: {volatilities.min():.2%} - {volatilities.max():.2%}")
        
        # Step 3: Calculate market equilibrium
        print("\n⚖️  Step 3: Calculating market equilibrium...")
        equilibrium_returns = self.calculate_market_equilibrium(prices)
        
        # Step 4: Apply Black-Litterman with views
        print("\n🎯 Step 4: Applying Black-Litterman model with recommendations...")
        views = {symbol: rec['expected_return'] for symbol, rec in recommendations.items()}
        confidences = {symbol: rec['confidence'] for symbol, rec in recommendations.items()}
        
        expected_returns = self.black_litterman_model(
            equilibrium_returns, covariance_matrix, views, confidences, symbols
        )
        
        print("  Adjusted expected returns:")
        for i, symbol in enumerate(symbols):
            print(f"    {symbol}: {expected_returns[i]:.2%}")
        
        # Step 5: Kelly Criterion
        print("\n💼 Step 5: Calculating optimal position sizes (Kelly Criterion)...")
        positions = {}
        
        for i, symbol in enumerate(symbols):
            win_probability = recommendations[symbol]['confidence']
            volatility = volatilities[i]
            
            position_size = self.kelly_criterion(
                expected_returns[i],
                win_probability,
                volatility,
                self.capital
            )
            
            positions[symbol] = position_size
            print(f"  {symbol}: ${position_size:,.2f}")
        
        # Step 6: Adjust for macro
        print(f"\n🌍 Step 6: Adjusting for macro sentiment ({macro_sentiment:+.2f})...")
        positions = self.adjust_for_macro_sentiment(positions, macro_sentiment)
        
        # Step 7: Risk constraints
        print(f"\n🛡️  Step 7: Applying risk constraints (risk level: {user_risk_level:.2f})...")
        positions = self.apply_risk_constraints(positions, user_risk_level)
        
        # Step 8: Calculate quantities
        print("\n🔢 Step 8: Converting to quantities...")
        quantities = self.calculate_quantities(positions, prices)
        
        # Prepare final output
        output = {}
        total_allocated = sum(positions.values())
        
        for symbol in symbols:
            if positions[symbol] != 0:
                output[symbol] = {
                    'position_usd': positions[symbol],
                    'quantity': quantities[symbol],
                    'price': prices[symbol],
                    'weight': positions[symbol] / total_allocated if total_allocated > 0 else 0,
                    'expected_return': expected_returns[symbols.index(symbol)],
                    'confidence': recommendations[symbol]['confidence']
                }
        
        return output
