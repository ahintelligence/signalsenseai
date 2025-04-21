import numpy as np
import pandas as pd
import logging
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from app.sentiment import get_news_sentiment_series, get_social_sentiment_series
from app.config.feature_config import FEATURE_FLAGS, RSI_WINDOW, MFI_WINDOW

logger = logging.getLogger(__name__)

def compute_rsi(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def compute_smoothed_macd(df):
    ema_fast = df["Close"].ewm(span=12, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=26, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd - signal

def compute_true_range(df):
    high, low, close = df["High"], df["Low"], df["Close"]
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1)
    return tr.max(axis=1)

def compute_rsi_momentum(df, window=14):
    rsi = compute_rsi(df["Close"], window)
    return rsi.diff()

def sanitize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sanitize column names to be compatible with LightGBM and Optuna (safe for JSON).
    """
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(map(str, col)).strip() for col in df.columns.values]
    df.columns = (
        pd.Index(df.columns)
        .astype(str)
        .str.replace(r"[^\w\d_]", "_", regex=True)  # keep only a-zA-Z0-9_
        .str.replace(r"__+", "_", regex=True)
        .str.strip("_")
    )
    return df

def generate_features(df, rsi_window=RSI_WINDOW, mfi_window=MFI_WINDOW, ticker="AAPL"):
    df = df.copy()

    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"Missing required columns: {required_cols}")

    # Target label
    df["RETURN"] = df["Close"].pct_change()
    df["TARGET"] = (df["Close"].shift(-3) > df["Close"]).astype(int)

    # Technical indicators
    if FEATURE_FLAGS["rsi"]:
        df["RSI"] = compute_rsi(df["Close"], rsi_window)

    if FEATURE_FLAGS["rsi_momentum"]:
        df["RSI_MOMENTUM"] = compute_rsi_momentum(df, rsi_window)

    if FEATURE_FLAGS["macd"]:
        df["MACD"] = compute_smoothed_macd(df)

    if FEATURE_FLAGS["sma_20"]:
        df["SMA_20"] = df["Close"].rolling(20).mean()

    if FEATURE_FLAGS["ema_10"]:
        df["EMA_10"] = df["Close"].ewm(span=10).mean()

    if FEATURE_FLAGS["ema_50"]:
        df["EMA_50"] = df["Close"].ewm(span=50).mean()

    if FEATURE_FLAGS["atr"]:
        df["ATR14"] = compute_true_range(df).rolling(14).mean()

    if FEATURE_FLAGS["bollinger_bands"]:
        mid = df["Close"].rolling(20).mean()
        std = df["Close"].rolling(20).std()
        df["BB_MID"] = mid
        df["BB_UPPER"] = mid + 2 * std
        df["BB_LOWER"] = mid - 2 * std

    if FEATURE_FLAGS["vol_regime"]:
        df["VOL_REGIME"] = (df["ATR14"] > df["ATR14"].rolling(50).median()).astype(int)

    if FEATURE_FLAGS["obv"]:
        direction = np.sign(df["Close"].diff().fillna(0))
        df["OBV"] = (direction * df["Volume"]).cumsum()

    if FEATURE_FLAGS["mfi"]:
        tp = (df["High"] + df["Low"] + df["Close"]) / 3
        mf = tp * df["Volume"]
        pos_mf = mf.where(tp > tp.shift(1), 0.0)
        neg_mf = mf.where(tp < tp.shift(1), 0.0)
        mf_ratio = pos_mf.rolling(mfi_window).sum() / neg_mf.rolling(mfi_window).sum()
        df["MFI"] = 100 - 100 / (1 + mf_ratio)

    # Ensure datetime index
    if not is_datetime(df.index):
        df.index = pd.to_datetime(df.index)

    if isinstance(df.index, pd.MultiIndex):
        df = df.sort_index()

    idx = pd.to_datetime(df.index.date)

    # Sentiment Features
    if FEATURE_FLAGS["social_sentiment"]:
        try:
            social = get_social_sentiment_series(ticker, days=7).reindex(idx).ffill().bfill()
            df["SOCIAL_SENTIMENT"] = social.values if not social.empty else 0.0
        except Exception as e:
            logger.warning(f"[!] Social sentiment failed: {e}")
            df["SOCIAL_SENTIMENT"] = 0.0

    if FEATURE_FLAGS["news_sentiment"]:
        try:
            news = get_news_sentiment_series(ticker, days=7).reindex(idx).ffill().bfill()
            df["NEWS_SENTIMENT"] = news.values if not news.empty else 0.0
        except Exception as e:
            logger.warning(f"[!] News sentiment failed: {e}")
            df["NEWS_SENTIMENT"] = 0.0

    # Final Cleanup
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    if len(df) < 10:
        logger.warning("[!] Feature generation resulted in very few usable rows.")

    # Use .pop() to extract and drop target cleanly
    target = df.pop("TARGET")

    # Sanitize columns for modeling
    df = sanitize_columns(df)

    print("[DEBUG] Target class distribution:\n", target.value_counts(normalize=True))

    return df, target











