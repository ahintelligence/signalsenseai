import os
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from ta import add_all_ta_features
from app.data import get_stock_data

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def generate_features(df):
    df = add_all_ta_features(
        df, open="Open", high="High", low="Low", close="Close", volume="Volume", fillna=True
    )

    # Create return-based target
    df['Target'] = (df['Close'].shift(-3) > df['Close']).astype(int)
    df = df.dropna()

    feature_cols = [col for col in df.columns if col not in ['Target', 'Date']]
    return df[feature_cols], df['Target']

def train_model(ticker: str):
    df = get_stock_data(ticker)
    if df is None or df.empty:
        raise ValueError(f"No stock data found for {ticker}")

    X, y = generate_features(df)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    model = XGBClassifier(n_estimators=200, max_depth=5, learning_rate=0.05, use_label_encoder=False, eval_metric='logloss')
    model.fit(X_train, y_train)

    # Save model and scaler
    joblib.dump(model, os.path.join(MODEL_DIR, f"{ticker}_model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, f"{ticker}_scaler.pkl"))

    print(f"[✓] Trained and saved model + scaler for {ticker}")
    return model

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python train.py <TICKER>")
    else:
        train_model(sys.argv[1])


