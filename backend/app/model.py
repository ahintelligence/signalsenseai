import os
import joblib
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from app.data import get_stock_data

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def compute_true_range(df: pd.DataFrame) -> pd.Series:
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
    return (100 - (100 / (1 + rs))).round(2)


def generate_features(df: pd.DataFrame):
    df = df.copy()

    # 1) Target: 3-day forward move
    df["Return"] = df["Close"].pct_change()
    df["Target"] = (df["Close"].shift(-3) > df["Close"]).astype(int)

    # 2) RSI (14)
    df["RSI"] = compute_rsi(df["Close"], window=14)

    # 3) MACD diff: EMA12 - EMA26, minus its own 9-day EMA
    ema_fast = df["Close"].ewm(span=12, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=26, adjust=False).mean()
    macd_line = (ema_fast - ema_slow).round(4)
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    df["MACD"] = (macd_line - signal_line).round(4)

    # 4) Moving averages
    df["SMA_20"] = df["Close"].rolling(window=20).mean().round(4)
    df["EMA_10"] = df["Close"].ewm(span=10, adjust=False).mean().round(4)
    df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean().round(4)

    # 5) ATR (14)
    df["atr14"] = compute_true_range(df).rolling(window=14).mean().round(4)

    # 6) Bollinger Bands (20, 2σ)
    roll_mean = df["Close"].rolling(window=20).mean()
    roll_std = df["Close"].rolling(window=20).std()
    df["bb_mid"] = roll_mean.round(4)
    df["bb_upper"] = (roll_mean + 2 * roll_std).round(4)
    df["bb_lower"] = (roll_mean - 2 * roll_std).round(4)

    # 7) Volatility regime
    df["vol_regime"] = (
        df["atr14"] > df["atr14"].rolling(window=50).median()
    ).astype(int)

    # 8) Drop NaNs from any rolling indicator
    df = df.dropna()

    features = [
        "Open", "High", "Low", "Close", "Volume",
        "Return", "RSI", "MACD", "SMA_20", "EMA_10", "EMA_50",
        "atr14", "bb_upper", "bb_mid", "bb_lower", "vol_regime"
    ]
    return df[features], df["Target"]


def train_model(ticker: str):
    df = get_stock_data(ticker)
    if df is None or df.empty:
        raise ValueError(f"No stock data found for {ticker}")

    X, y = generate_features(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = XGBClassifier(
        n_estimators=100,
        use_label_encoder=False,
        eval_metric="logloss"
    )
    model.fit(X_train, y_train)

    model_path = os.path.join(MODEL_DIR, f"{ticker}_model.pkl")
    joblib.dump(model, model_path)
    print(f"[✓] Trained and saved model for {ticker} at {model_path}")
    return model


def load_model(ticker: str):
    model_path = os.path.join(MODEL_DIR, f"{ticker}_model.pkl")
    if not os.path.exists(model_path):
        return train_model(ticker)
    return joblib.load(model_path)









