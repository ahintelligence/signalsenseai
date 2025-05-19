import yfinance as yf
import pandas as pd
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def get_stock_data(ticker: str, start: str = "2020-01-01", end: str = None, interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical stock data using yfinance.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., "AAPL").
        start (str): Start date for historical data.
        end (str): End date for historical data.
        interval (str): Data granularity (e.g., "1d", "1wk").

    Returns:
        pd.DataFrame: Cleaned OHLCV data.
    """
    try:
        logger.info(f"Fetching data for {ticker} from {start} to {end} with interval {interval}")
        df = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=True)

        if df.empty:
            raise ValueError("Downloaded data is empty")

        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df = df[~df.index.duplicated(keep='first')]
        df.dropna(inplace=True)

        logger.info(f"✓ Retrieved {len(df)} rows for {ticker}")
        return df

    except Exception as e:
        logger.error(f"[!] Failed to fetch stock data for {ticker}: {e}")
        raise HTTPException(status_code=404, detail=f"No stock data found for '{ticker.upper()}'")


