import yfinance as yf
from fastapi import HTTPException

def get_stock_data(ticker: str):
    try:
        df = yf.download(ticker, period="6mo", interval="1d")
        if df.empty:
            raise ValueError("No stock data found")
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        raise HTTPException(status_code=404, detail=f"No stock data found for {ticker}")
