from fastapi import APIRouter, HTTPException
import yfinance as yf

router = APIRouter()

@router.get("/latest-price/{ticker}")
def get_latest_price(ticker: str):
    """
    Fetch the most recent price data for a given ticker symbol.
    """
    stock = yf.Ticker(ticker.upper())
    df = stock.history(period="1d", interval="1m")

    if df.empty:
        raise HTTPException(status_code=404, detail="No data available for this ticker.")

    latest = df.iloc[-1]

    return {
        "ticker": ticker.upper(),
        "date": latest.name.isoformat(),
        "open": round(latest["Open"], 2),
        "high": round(latest["High"], 2),
        "low": round(latest["Low"], 2),
        "close": round(latest["Close"], 2),
        "volume": int(latest["Volume"]),
    }

