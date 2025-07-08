import pandas as pd
import yfinance as yf
from typing import List

def fetch_daily_prices(tickers: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetches daily adjusted closing prices for a list of tickers from Yahoo Finance.
    """
    try:
        price_data = yf.download(tickers, start=start_date, end=end_date, progress=False)['Adj Close']
        price_data.ffill(inplace=True)
        price_data.bfill(inplace=True)
        if price_data.isnull().values.any():
            raise ValueError("Data fetching resulted in NaN values after cleaning.")
        if isinstance(price_data, pd.Series): # Handle case of single ticker
            return price_data.to_frame(name=tickers[0])
        return price_data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()
