import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from pathlib import Path

# --- Configuration ---
# Load API key (tries .env first, then Streamlit secrets)
load_dotenv()
API_KEY = os.getenv("MARKETSTACK_API_KEY") or st.secrets.get("MARKETSTACK_API_KEY")

# --- Streamlit App ---
st.title("📈 Realized Volatility Calculator (Marketstack)")

# Sidebar inputs
ticker = st.sidebar.text_input("Enter stock ticker (e.g., AAPL):", "AAPL")
start_date = st.sidebar.date_input("Start date:", datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input("End date:", datetime.now())
annualize = st.sidebar.checkbox("Annualize volatility", value=True)
rolling_window = st.sidebar.slider("Rolling window (days)", 1, 252, 30)

def fetch_marketstack_data(ticker, start_date, end_date):
    """Fetch EOD data from Marketstack API."""
    if not API_KEY:
        st.error("API key not found! Check your .env or Streamlit secrets.")
        return None
    
    base_url = "http://api.marketstack.com/v1/eod"
    url = f"{base_url}?access_key={API_KEY}&symbols={ticker}&date_from={start_date}&date_to={end_date}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                df = pd.DataFrame(data["data"])
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
                return df.sort_index()
        st.error(f"API Error: {response.text}")
    except Exception as e:
        st.error(f"Connection failed: {str(e)}")
    return None

if ticker:
    try:
        with st.spinner(f"Fetching data for {ticker}..."):
            data = fetch_marketstack_data(
                ticker,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
        
        if data is not None:
            # Calculate returns
            close_prices = data["close"]
            returns = np.log(close_prices / close_prices.shift(1)).dropna()

            # Realized volatility calculation
            def realized_volatility(returns, window=1, annualized=False):
                rv = returns.rolling(window).apply(lambda x: np.sqrt(np.sum(x**2)))
                return rv * np.sqrt(252) if annualized else rv
            
            rv = realized_volatility(returns, window=rolling_window, annualized=annualize)

            # Plotting
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            ax1.plot(close_prices, label='Close Price')
            ax1.set_title(f"{ticker} Price")
            ax1.legend()
            
            ax2.plot(rv, label='Realized Volatility', color='red')
            ax2.set_title(f"Rolling {rolling_window}-Day Realized Volatility")
            ax2.legend()
            
            st.pyplot(fig)

            # Download results
            st.subheader("Export Results")
            rv_df = pd.DataFrame({"Realized_Volatility": rv})
            st.download_button(
                label="Download as CSV",
                data=rv_df.to_csv().encode('utf-8'),
                file_name=f"{ticker}_realized_volatility.csv"
            )

    except Exception as e:
        st.error(f"Error: {str(e)}")
else:
    st.info("Please enter a stock ticker (e.g., AAPL, MSFT).")