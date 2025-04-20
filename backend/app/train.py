import os
import joblib
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import AverageTrueRange, BollingerBands
from app.data import get_stock_data
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from app.utils import generate_features


MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)



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

    # Predict and evaluate
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    logger.info(f"[✓] Accuracy:  {accuracy:.2%}")
    logger.info(f"[✓] Precision: {precision:.2%}")
    logger.info(f"[✓] Recall:    {recall:.2%}")
    logger.info(f"[✓] F1 Score:  {f1:.2%}")
    logger.info(f"[✓] Classification Report:\n{classification_report(y_test, y_pred)}")

    # Save model
    path = os.path.join(MODEL_DIR, f"{ticker}_model.pkl")
    joblib.dump(model, path)
    logger.info(f"[✓] Saved model ➞ {path}")

    return model

def load_model(ticker: str):
    model_path = os.path.join(MODEL_DIR, f"{ticker}_model.pkl")
    if not os.path.exists(model_path):
        return train_model(ticker)
    return joblib.load(model_path)



