import yfinance as yf
import pandas as pd
from fastapi import HTTPException

def get_stock_data(ticker: str, start="2020-01-01", end=None, interval="1d"):
    try:
        df = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=True)
        if df.empty:
            raise ValueError("No stock data found")

        # Clean index and sort
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        df = df[["Open", "High", "Low", "Close", "Volume"]]  # enforce expected cols

        # Drop duplicates and empty values
        df = df[~df.index.duplicated(keep='first')]
        df.dropna(inplace=True)

        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        raise HTTPException(status_code=404, detail=f"No stock data found for {ticker}")

