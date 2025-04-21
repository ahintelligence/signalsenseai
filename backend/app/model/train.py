import os
import json
import joblib
import logging
import pandas as pd
from datetime import datetime
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from app.data import get_stock_data
from app.model.features import generate_features
from app.model.evaluate import evaluate_model

# Setup logger
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Model storage path
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def train_model(
    ticker: str,
    n_estimators: int = 200,
    max_depth: int = 6,
    learning_rate: float = 0.05,
    test_size: float = 0.2,
    save_metadata: bool = True,
    return_metrics: bool = False
):
    logger.info(f"▶ Starting training for {ticker}")

    # Get stock data
    df = get_stock_data(ticker)
    if df is None or df.empty:
        raise ValueError(f"No stock data available for '{ticker}'")
    logger.info(f"✓ Loaded {len(df)} rows of data for {ticker}")

    # Generate features and targets
    X, y = generate_features(df)
    if X.empty or y.empty:
        raise ValueError(f"Not enough feature data to train for {ticker}")
    logger.info(f"✓ Generated {X.shape[1]} features from {X.shape[0]} samples")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    logger.info(f"✓ Split data into {len(X_train)} train / {len(X_test)} test rows")

    # Define and train model
    model = XGBClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        eval_metric="logloss",
        use_label_encoder=False
    )
    model.fit(X_train, y_train)
    logger.info("✓ Model training complete")

    # Evaluate model
    metrics = evaluate_model(model, X_test, y_test, ticker)

    # Save model
    model_path = os.path.join(MODEL_DIR, f"{ticker}_model.pkl")
    joblib.dump(model, model_path)
    logger.info(f"✓ Model saved to {model_path}")

    # Save metadata
    if save_metadata:
        meta = {
            "ticker": ticker,
            "timestamp": datetime.utcnow().isoformat(),
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "test_size": test_size,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "metrics": metrics
        }
        meta_path = model_path.replace(".pkl", ".meta.json")
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)
        logger.info(f"✓ Metadata saved to {meta_path}")

    return (model, metrics) if return_metrics else model


def load_model(ticker: str):
    """Load model from disk, or train if missing."""
    path = os.path.join(MODEL_DIR, f"{ticker}_model.pkl")
    if not os.path.exists(path):
        logger.warning(f"No existing model found for {ticker}, training a new one...")
        return train_model(ticker)
    logger.info(f"✓ Loaded model from {path}")
    return joblib.load(path)

def compare_models(tickers: list[str]):
    from app.model.evaluate import evaluate_model
    import os

    results = {}

    for ticker in tickers:
        path = os.path.join(MODEL_DIR, f"{ticker}_model.pkl")
        if not os.path.exists(path):
            continue
        model = joblib.load(path)
        df = get_stock_data(ticker)
        if df is None or df.empty:
            continue
        X, y = generate_features(df)
        _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        results[ticker] = evaluate_model(model, X_test, y_test, ticker)

    return results



# ───────────────────────────────────────────────────────────────
# CLI ENTRY
# ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train a model for a specific stock ticker.")
    parser.add_argument("ticker", type=str, help="Stock ticker symbol (e.g., AAPL)")
    parser.add_argument("--estimators", type=int, default=200, help="Number of trees (default: 200)")
    parser.add_argument("--depth", type=int, default=6, help="Tree max depth (default: 6)")
    parser.add_argument("--lr", type=float, default=0.05, help="Learning rate (default: 0.05)")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set size (default: 0.2)")
    parser.add_argument("--metrics", action="store_true", help="Return evaluation metrics after training")

    args = parser.parse_args()

    train_model(
        ticker=args.ticker,
        n_estimators=args.estimators,
        max_depth=args.depth,
        learning_rate=args.lr,
        test_size=args.test_size,
        return_metrics=args.metrics
    )





