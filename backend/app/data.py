import yfinance as yf
import pandas as pd

def get_stock_data(ticker: str, period="6mo"):
    df = yf.download(ticker, period=period)
    df = df.dropna()
    return df
