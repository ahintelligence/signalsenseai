import os
import joblib
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import AverageTrueRange, BollingerBands
from app.data import get_stock_data

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def generate_features(df: pd.DataFrame):
    df = df.copy()

    # Basic return & target
    df['Return'] = df['Close'].pct_change()
    df['Target'] = (df['Close'].shift(-3) > df['Close']).astype(int)

    # Prepare a flat Close series
    close = pd.Series(df['Close'].values.ravel(), index=df.index)

    # Standard indicators
    df['RSI'] = RSIIndicator(close=close).rsi()
    df['MACD'] = MACD(close=close).macd_diff()
    df['SMA_20'] = SMAIndicator(close=close, window=20).sma_indicator()
    df['EMA_10'] = EMAIndicator(close=close, window=10).ema_indicator()
    df['EMA_50'] = EMAIndicator(close=close, window=50).ema_indicator()

    # Volatility features with fallback
    try:
        atr = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14)
        df['atr14'] = atr.average_true_range()

        bb = BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_mid']   = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()

        # Volatility regime flag
        df['vol_regime'] = (df['atr14'] > df['atr14'].rolling(50).median()).astype(int)
    except Exception:
        # Fallback if data too short or ta library errors
        df['atr14']      = pd.NA
        df['bb_upper']   = pd.NA
        df['bb_mid']     = pd.NA
        df['bb_lower']   = pd.NA
        df['vol_regime'] = pd.NA

    # Drop NaNs resulting from rolling or failures
    df = df.dropna()

    # Final feature list
    features = [
        'Open', 'High', 'Low', 'Close', 'Volume',
        'Return', 'RSI', 'MACD', 'SMA_20', 'EMA_10', 'EMA_50',
        'atr14', 'bb_upper', 'bb_mid', 'bb_lower', 'vol_regime'
    ]

    return df[features], df['Target']

def train_model(ticker: str):
    df = get_stock_data(ticker)
    if df is None or df.empty:
        raise ValueError(f"No stock data found for {ticker}")

    X, y = generate_features(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = XGBClassifier(
        n_estimators=100,
        use_label_encoder=False,
        eval_metric='logloss'
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



