import os
import logging
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from ta.volume import MFIIndicator
from app.data import get_stock_data

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def compute_true_range(df: pd.DataFrame) -> pd.Series:
    """Average True Range component (not annualized)."""
    high, low, close = df["High"], df["Low"], df["Close"]
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    return pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)


def compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return (100 - (100 / (1 + rs))).round(4)


def generate_features(df: pd.DataFrame, rsi_window: int = 14, mfi_window: int = 14):
    """Generates predictive features and binary targets from raw OHLCV data."""
    df = df.copy(deep=True)

    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    if not all(col in df.columns for col in required_cols):
        raise ValueError("Missing required OHLCV columns in input DataFrame")

    # Targets and Returns
    df["RETURN"] = df["Close"].pct_change()
    df["TARGET"] = (df["Close"].shift(-3) > df["Close"]).astype(int)

    # Technical Indicators
    df["RSI"] = compute_rsi(df["Close"], window=rsi_window)

    ema_fast = df["Close"].ewm(span=12, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=26, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    df["MACD"] = (macd_line - signal_line).round(4)

    df["SMA_20"] = df["Close"].rolling(20).mean().round(4)
    df["EMA_10"] = df["Close"].ewm(span=10, adjust=False).mean().round(4)
    df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean().round(4)

    df["ATR14"] = compute_true_range(df).rolling(14).mean().round(4)

    mid = df["Close"].rolling(20).mean()
    std = df["Close"].rolling(20).std()
    df["BB_MID"] = mid.round(4)
    df["BB_UPPER"] = (mid + 2 * std).round(4)
    df["BB_LOWER"] = (mid - 2 * std).round(4)

    df["VOL_REGIME"] = (df["ATR14"] > df["ATR14"].rolling(50).median()).astype(int)

    # On-Balance Volume
    direction = np.sign(df["Close"].diff().fillna(0))
    df["OBV"] = (direction * df["Volume"]).fillna(0).cumsum().round(4)

    # MFIIndicator — with flattened Series inputs
    mfi_raw = MFIIndicator(
        high=df["High"].squeeze(),
        low=df["Low"].squeeze(),
        close=df["Close"].squeeze(),
        volume=df["Volume"].squeeze(),
        window=mfi_window
    ).money_flow_index()

    if isinstance(mfi_raw, pd.DataFrame):
        mfi_raw = mfi_raw.squeeze()

    if not isinstance(mfi_raw, pd.Series):
        raise TypeError("MFIIndicator returned unexpected type")

    logger.debug(f"MFI shape: {mfi_raw.shape}, type: {type(mfi_raw)}")

    df["MFI"] = mfi_raw.round(4)

    # Clean up NaNs/Infs
    df = df.replace([np.inf, -np.inf], np.nan).dropna()

    features = [
        "Open", "High", "Low", "Close", "Volume",
        "RETURN", "RSI", "MACD", "SMA_20", "EMA_10", "EMA_50",
        "ATR14", "BB_UPPER", "BB_MID", "BB_LOWER", "VOL_REGIME",
        "OBV", "MFI"
    ]

    return df[features], df["TARGET"]


def train_model(ticker: str):
    """Train XGBoost model for a given ticker and save it."""
    df = get_stock_data(ticker)
    if df is None or df.empty:
        raise ValueError(f"No stock data for {ticker}")

    X, y = generate_features(df)

    if X.empty or y.empty:
        raise ValueError(f"Not enough feature data to train for {ticker}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    logger.info(f"Training on {len(X_train)} rows | Testing on {len(X_test)} rows")

    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        eval_metric="logloss",
        use_label_encoder=False
    )
    model.fit(X_train, y_train)

    acc = model.score(X_test, y_test)
    logger.info(f"[✓] Model accuracy: {acc:.2%}")

    path = os.path.join(MODEL_DIR, f"{ticker}_model.pkl")
    joblib.dump(model, path)
    logger.info(f"[✓] Saved model ➞ {path}")

    return model


def load_model(ticker: str):
    """Load a model from disk or train a new one."""
    path = os.path.join(MODEL_DIR, f"{ticker}_model.pkl")
    if not os.path.exists(path):
        logger.info(f"Model not found for {ticker}, training...")
        return train_model(ticker)
    return joblib.load(path)




