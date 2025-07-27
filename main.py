import argparse
import os
from datetime import datetime
from utils.data import get_historical_data
from utils.vol import calculate_realized_vol
import pandas as pd

HORIZONS = {'1Y': 252, '2Y': 504, '5Y': 1260, '10Y': 2520}

def analyze_ticker(ticker, plot=False):
    try:
        print(f"\n[DEBUG] Fetching {ticker} data...")
        prices = get_historical_data(ticker, years=10)
        if prices is None:
            raise ValueError("No price data returned")
            
        print(f"[DEBUG] Data range: {prices.index[0].date()} to {prices.index[-1].date()}")

        # In analyze_ticker() function, before results = {}
        print(f"\n[DEBUG] Price data sample (last 5 days):")
        print(prices.tail())
        print(f"\n[DEBUG] Data length: {len(prices)} days")
        
        results = {}
        for name, days in HORIZONS.items():
            if len(prices) >= days:
                results[name] = calculate_realized_vol(prices[-days:])
        
        vol_df = pd.DataFrame.from_dict(results, orient='index', columns=['Volatility'])
        
        if plot:
            from utils.viz import plot_volatility
            plot_volatility(prices, ticker)
            
        return vol_df.dropna()
        
    except Exception as e:
        print(f"[ERROR] Analysis failed: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('tickers', nargs='+')
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    
    os.makedirs("outputs", exist_ok=True)
    
    for ticker in args.tickers:
        result = analyze_ticker(ticker, args.plot)
        if result is not None:
            print(f"\n{ticker} Volatility:\n{result.to_markdown(floatfmt='.2%')}")

if __name__ == "__main__":
    main()