import matplotlib.pyplot as plt
from utils.vol import rolling_volatility
import os

def plot_volatility(prices, ticker):
    import matplotlib.pyplot as plt
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Price plot
    ax1.plot(prices)
    ax1.set_title(f"{ticker} Price History")
    ax1.grid(True)
    
    # Volatility plot
    rolling_vol = rolling_volatility(prices)
    ax2.plot(rolling_vol, color='purple')
    ax2.set_title("63-Day Rolling Volatility")
    ax2.grid(True)
    
    plt.tight_layout()
    return fig  # Return the figure instead of saving