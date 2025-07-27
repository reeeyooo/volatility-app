import numpy as np
import pandas as pd

def calculate_realized_vol(prices, window=252):
    """Handle Series with or without MultiIndex"""
    try:
        if isinstance(prices, pd.DataFrame):  # If MultiIndex slipped through
            prices = prices.iloc[:, 0] if prices.shape[1] == 1 else prices['Close']
            
        log_returns = np.log(prices / prices.shift(1)).dropna()
        return log_returns.std() * np.sqrt(window)
    except Exception as e:
        print(f"[VOL ERROR] {str(e)}")
        return np.nan

def rolling_volatility(prices, window=63):
    """Ensure proper rolling calculation"""
    try:
        log_returns = np.log(prices / prices.shift(1)).dropna()
        return log_returns.rolling(window).std() * np.sqrt(252)
    except Exception as e:
        print(f"[ROLLING VOL ERROR] {str(e)}")
        return pd.Series(index=prices.index, dtype=float)