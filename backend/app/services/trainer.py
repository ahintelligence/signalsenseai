import os
import json
import joblib
import logging
import pandas as pd
from datetime import datetime
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
from app.services.data_provider import get_stock_data
from app.core.features import generate_features
from app.core.evaluate import evaluate_model


# Setup logger
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Model storage directory
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# ───────────────────────────────────────────────────────────────
# Shared Utilities
# ───────────────────────────────────────────────────────────────

def get_model_path(ticker: str, artifact_name: str = "model") -> str:
    """Construct standardized path to a saved model file."""
    return os.path.join(MODEL_DIR, f"{ticker}_{artifact_name}.pkl")


def save_model(model, ticker: str, artifact_name: str = "model") -> str:
    """Save the trained model to disk."""
    model_path = get_model_path(ticker, artifact_name)
    joblib.dump(model, model_path)
    return model_path


# ───────────────────────────────────────────────────────────────
# Core Training Logic
# ───────────────────────────────────────────────────────────────

def train_model(
    ticker: str,
    n_estimators: int = 200,
    max_depth: int = 6,
    learning_rate: float = 0.05,
    test_size: float = 0.2,
    artifact_name: str = "model",
    save_metadata: bool = True,
    return_metrics: bool = False
):
    logger.info(f"▶ Starting training for {ticker}")

    df = get_stock_data(ticker)
    if df is None or df.empty:
        raise ValueError(f"No stock data available for '{ticker}'")
    logger.info(f"✓ Loaded {len(df)} rows of data for {ticker}")

    X, y = generate_features(df)
    if X.empty or y.empty:
        raise ValueError(f"Not enough feature data to train for {ticker}")
    logger.info(f"✓ Generated {X.shape[1]} features from {X.shape[0]} samples")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    logger.info(f"✓ Split data into {len(X_train)} train / {len(X_test)} test rows")

    model = XGBClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        eval_metric="logloss",
        use_label_encoder=False
    )
    model.fit(X_train, y_train)
    logger.info("✓ Model training complete")

    metrics = evaluate_model(model, X_test, y_test, ticker)

    # Save model
    model_path = save_model(model, ticker, artifact_name)
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
    
def retrain_model(ticker: str, n_trials: int = 100):
    """Wrapper to retrain a model with extended trials."""
    from app.core.optimizer import run_optimization
    return run_optimization(ticker=ticker, n_trials=n_trials)


def load_model(ticker: str, artifact_name: str = "model"):
    """Load model from disk or fallback to training."""
    path = get_model_path(ticker, artifact_name)
    if not os.path.exists(path):
        logger.warning(f"No existing model found for {ticker}, training a new one...")
        return train_model(ticker)
    logger.info(f"✓ Loaded model from {path}")
    return joblib.load(path)


def evaluate_multiple_models(tickers: list[str]):
    """Evaluate multiple pre-trained models for comparison."""
    results = {}

    for ticker in tickers:
        path = get_model_path(ticker)
        if not os.path.exists(path):
            logger.warning(f"⨯ No model for {ticker}, skipping")
            continue

        model = joblib.load(path)
        df = get_stock_data(ticker)
        if df is None or df.empty:
            logger.warning(f"⨯ No data for {ticker}, skipping")
            continue

        X, y = generate_features(df)
        _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        results[ticker] = evaluate_model(model, X_test, y_test, ticker)

    return results

def compare_models(tickers: list) -> dict:
    results = {}

    for ticker in tickers:
        try:
            # Get historical data
            df = get_stock_data(ticker)
            if df is None or df.empty:
                results[ticker] = {"error": "No data found"}
                continue

            # Generate features
            X, y = generate_features(df)
            if X.empty or y.empty:
                results[ticker] = {"error": "Feature generation failed"}
                continue

            model = load_model(ticker)
            booster = model.get_booster()
            trained_features = booster.feature_names

            # Realign features
            rename_map = {}
            suffix = f" {ticker}"
            for fname in trained_features:
                if fname.endswith(suffix):
                    base = fname[:-len(suffix)]
                else:
                    base = fname.strip()
                rename_map[base] = fname
            X = X.rename(columns=rename_map)[trained_features]

            # Make predictions
            y_pred = model.predict(X)
            y_proba = model.predict_proba(X).max(axis=1)

            # Metrics
            accuracy = accuracy_score(y, y_pred)
            precision = precision_score(y, y_pred, zero_division=0)
            recall = recall_score(y, y_pred, zero_division=0)
            f1 = f1_score(y, y_pred, zero_division=0)

            results[ticker] = {
                "accuracy": round(accuracy, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4),
                "average_confidence": round(float(y_proba.mean()), 4),
                "sample_size": len(y)
            }

        except Exception as e:
            results[ticker] = {"error": str(e)}

    return results


# ───────────────────────────────────────────────────────────────
# CLI ENTRY (Optional)
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






