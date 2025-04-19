import os
import joblib
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from app.data import get_stock_data

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def generate_features(df: pd.DataFrame):
    df = df.copy()

    df['Return'] = df['Close'].pct_change()
    df['Target'] = df['Close'].shift(-3) > df['Close']

    # Ensure Close is a proper flat Series
    close = pd.Series(df['Close'].values.ravel(), index=df.index)

    # Technical indicators
    df['RSI'] = RSIIndicator(close=close).rsi()
    df['MACD'] = MACD(close=close).macd_diff()
    df['SMA_20'] = SMAIndicator(close=close, window=20).sma_indicator()
    df['EMA_10'] = EMAIndicator(close=close, window=10).ema_indicator()
    df['EMA_50'] = EMAIndicator(close=close, window=50).ema_indicator()

    df = df.dropna()

    features = [
        'Open', 'High', 'Low', 'Close', 'Volume',
        'Return', 'RSI', 'MACD', 'SMA_20', 'EMA_10', 'EMA_50'
    ]

    return df[features], df['Target']


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

