from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

VALID_PERIODS = {
    "1d", "5d", "1mo", "3mo", "6mo", "ytd", "1y", "2y", "5y", "10y", "max"
}

@router.get("/history/{ticker}")
def get_price_history(
    ticker: str,
    range: str = Query("1mo", description="Valid: 1d, 5d, 1mo, 3mo, ytd, 1y, max"),
):
    try:
        if range not in VALID_PERIODS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid range '{range}'. Choose from: {', '.join(sorted(VALID_PERIODS))}"
            )

        df = yf.download(
            tickers=ticker,
            period=range,
            interval="1d",
            auto_adjust=False,
            progress=False,
        )

        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data for {ticker}")

        df = df.reset_index()
        def normalize_col(col):
            if isinstance(col, tuple):
                col = col[0]
            return str(col).lower().replace(" ", "_")

        df.columns = [normalize_col(col) for col in df.columns]


        # Ensure required columns exist
        for col in ["date", "open", "high", "low", "close"]:
            if col not in df.columns:
                raise HTTPException(status_code=500, detail=f"Missing column: {col}")

        df["date"] = pd.to_datetime(df["date"])
        print(df[["date"]].head())
        df = df.dropna(subset=["open", "high", "low", "close"]).copy()

        # Indicators
        df["sma20"] = df["close"].rolling(window=20).mean().round(2)
        df["ema9"] = df["close"].ewm(span=9, adjust=False).mean().round(2)
        df["ema20"] = df["close"].ewm(span=20, adjust=False).mean().round(2)
        df["ema50"] = df["close"].ewm(span=50, adjust=False).mean().round(2)
        df["ema100"] = df["close"].ewm(span=100, adjust=False).mean().round(2)
        df["ema200"] = df["close"].ewm(span=200, adjust=False).mean().round(2)

        # RSI
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df["rsi"] = (100 - (100 / (1 + rs))).round(2)

        # ATR
        df["atr14"] = ta.volatility.average_true_range(
            df["high"], df["low"], df["close"], window=14
        ).round(2)

        # Bollinger Bands
        bb = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
        df["bb_upper"] = bb.bollinger_hband().round(2)
        df["bb_mid"] = bb.bollinger_mavg().round(2)
        df["bb_lower"] = bb.bollinger_lband().round(2)

        # Volatility Regime
        df["vol_regime"] = (df["atr14"] > df["atr14"].rolling(50).median()).astype(int)

        # Clean up NaNs from rolling calcs
        df = df.bfill().copy()

        # Final formatting
        history = []
        for index, row in df.iterrows():
            history.append({
                "time": int(row["date"].timestamp()), 
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "sma20": float(row["sma20"]),
                "ema9": float(row["ema9"]),
                "ema20": float(row["ema20"]),
                "ema50": float(row["ema50"]),
                "ema100": float(row["ema100"]),
                "ema200": float(row["ema200"]),
                "rsi": float(row["rsi"]),
                "atr14": float(row["atr14"]),
                "bb_upper": float(row["bb_upper"]),
                "bb_mid": float(row["bb_mid"]),
                "bb_lower": float(row["bb_lower"]),
                "vol_regime": int(row["vol_regime"]),
            })

        return JSONResponse({
            "ticker": ticker.upper(),
            "range": range,
            "count": len(history),
            "history": history
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[!] Chart history error for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")





