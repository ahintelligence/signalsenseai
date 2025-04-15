import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from app.data import get_stock_data

def generate_features(df):
    df['Return'] = df['Close'].pct_change()
    df['Target'] = df['Close'].shift(-3) > df['Close']
    df['RSI'] = compute_rsi(df['Close'])
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
    df = df.dropna()
    features = ['Open', 'High', 'Low', 'Close', 'Volume', 'Return', 'RSI', 'SMA_50', 'MACD']
    return df[features], df['Target']

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def train_model(ticker: str):
    df = get_stock_data(ticker)
    X, y = generate_features(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    import os
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(model_dir, f"{ticker}_model.pkl"))
    return model

def load_model(ticker: str):
    import os
    model_path = os.path.join(os.path.dirname(__file__), "models", f"{ticker}_model.pkl")
    if not os.path.exists(model_path):
        return train_model(ticker)
    return joblib.load(model_path)
