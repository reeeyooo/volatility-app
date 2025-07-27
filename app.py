import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("MARKETSTACK_API_KEY")

# Title
st.title("Realized Volatility Calculator (Marketstack)")

# Sidebar: Ticker Input
st.sidebar.header("Parameters")
ticker = st.sidebar.text_input("Enter stock ticker (e.g., AAPL):", "AAPL")

# Date range selector
end_date = datetime.now().strftime("%Y-%m-%d")
start_date = st.sidebar.date_input(
    "Start date:",
    datetime.now() - timedelta(days=365)
).strftime("%Y-%m-%d")

# Parameters
annualize = st.sidebar.checkbox("Annualize volatility", value=True)
rolling_window = st.sidebar.slider("Rolling window (days)", 1, 252, 30)

def fetch_marketstack_data(ticker, start_date, end_date):
    """Fetch EOD data from Marketstack API."""
    base_url = "http://api.marketstack.com/v1/eod"
    url = f"{base_url}?access_key={API_KEY}&symbols={ticker}&date_from={start_date}&date_to={end_date}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "data" in data:
            df = pd.DataFrame(data["data"])
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
            return df.sort_index()
    st.error(f"Failed to fetch data. Check your API key or ticker symbol. Error: {response.text}")
    return None

if ticker:
    try:
        with st.spinner(f"Fetching data for {ticker}..."):
            data = fetch_marketstack_data(ticker, start_date, end_date)
        
        if data is not None:
            st.sidebar.subheader("Data Preview")
            st.sidebar.write(data.head())

            # Calculate daily returns
            close_prices = data["close"]
            returns = np.log(close_prices / close_prices.shift(1)).dropna()

            # Realized volatility (annualized if selected)
            def realized_volatility(returns, window=1, annualized=False):
                rv = returns.rolling(window).apply(lambda x: np.sqrt(np.sum(x**2)))
                if annualized:
                    rv *= np.sqrt(252)  # Annualize for daily data
                return rv
            
            rv = realized_volatility(returns, window=rolling_window, annualized=annualize)

            # Plotting
            st.subheader(f"Results for {ticker}")
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
            st.write(rv_df.dropna())
            st.download_button(
                label="Download as CSV",
                data=rv_df.to_csv().encode('utf-8'),
                file_name=f"{ticker}_realized_volatility.csv"
            )

    except Exception as e:
        st.error(f"Error: {str(e)}")
else:
    st.info("Please enter a stock ticker (e.g., AAPL, MSFT).")