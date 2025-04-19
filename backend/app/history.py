import yfinance as yf
import pandas as pd
import ta
from fastapi.responses import JSONResponse
import traceback

# Supported yfinance period strings:
VALID_PERIODS = {"1d", "5d", "1mo", "3mo", "6mo", "ytd", "1y", "2y", "5y", "10y", "max"}

def get_price_history(ticker: str, range: str = "1mo"):
    # 1) Validate the range param
    if range not in VALID_PERIODS:
        return JSONResponse(
            status_code=400,
            content={
                "error": f"Invalid range '{range}'. Must be one of {', '.join(sorted(VALID_PERIODS))}"
            }
        )

    try:
        # 2) Fetch data
        df = yf.download(
            tickers=ticker,
            period=range,
            interval="1d",
            auto_adjust=False,
            progress=False
        )

        # 3) Handle no-data
        if df.empty:
            return JSONResponse(
                status_code=404,
                content={"error": f"No data found for {ticker} in period '{range}'"}
            )

                # 4) Normalize columns (flatten potential multi-index and standardize names)
        df = df.reset_index()
        df.columns = [
            (col if isinstance(col, str) else col[0]).lower().replace(" ", "_")
            for col in df.columns
        ]

        # 5) Ensure required fields
        required = ["date", "open", "high", "low", "close"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            return JSONResponse(
                status_code=500,
                content={"error": f"Missing required columns: {', '.join(missing)}"}
            )

        # 6) Format and clean data
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        df = df.dropna(subset=["open", "high", "low", "close"]).copy()

        # 7) Compute moving averages
        df["sma20"] = df["close"].rolling(window=20).mean().round(2)
        df["ema9"] = df["close"].ewm(span=9, adjust=False).mean().round(2)
        df["ema20"] = df["close"].ewm(span=20, adjust=False).mean().round(2)
        df["ema50"] = df["close"].ewm(span=50, adjust=False).mean().round(2)
        df["ema100"] = df["close"].ewm(span=100, adjust=False).mean().round(2)
        df["ema200"] = df["close"].ewm(span=200, adjust=False).mean().round(2)

        # 8) Compute RSI (14-period)
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df["rsi"] = (100 - (100 / (1 + rs))).round(2)

        # 9. ATR (14‑period)
        df["atr14"] = ta.volatility.average_true_range(
            df["high"], df["low"], df["close"], window=14
        ).round(2)

        # 10. Bollinger Bands (20‑period)
        bb = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
        df["bb_upper"] = bb.bollinger_hband().round(2)
        df["bb_mid"]   = bb.bollinger_mavg().round(2)
        df["bb_lower"] = bb.bollinger_lband().round(2)

        # 11. Regime flag: high volatility when ATR > rolling median
        df["vol_regime"] = (
            df["atr14"] > df["atr14"].rolling(50).median()
        ).astype(int)

        # 12) Backfill any NaNs from rolling/ewm
        df = df.fillna(method="bfill").copy()

        # 13) Serialize and respond
        history_records = df.to_dict(orient="records")
        return JSONResponse(
            content={
                "ticker": ticker.upper(),
                "range": range,
                "history": history_records
            }
        )

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Unexpected error: {str(e)}"}
        )


    