import os
import logging
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from ta.volume import MFIIndicator
from app.data import get_stock_data
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import json
import csv
from pathlib import Path
from hyperopt import fmin, tpe, hp, Trials, STATUS_OK
from sklearn.ensemble import StackingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import lightgbm as lgb
import mlflow
import mlflow.sklearn
from app.sentiment import get_news_sentiment_series, get_social_sentiment_series
from pandas.api.types import is_datetime64_any_dtype as is_datetime



mlflow.set_tracking_uri("http://127.0.0.1:5000")

# ──────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Setup directories and logger
METRICS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "metrics"))
os.makedirs(METRICS_DIR, exist_ok=True)
MODEL_DIR   = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
def cross_validate_model(model, X, y):
    scores = cross_val_score(model, X, y, cv=5)
    logger.info(f"Cross‑validated scores: {scores}")
    logger.info(f"Mean accuracy: {scores.mean():.2%}")

def train_stacked_model(X_train, y_train):
    base_learners = [
        ('xgb', XGBClassifier(use_label_encoder=False, eval_metric='logloss')),
        ('rf', RandomForestClassifier()),
        ('lgb', lgb.LGBMClassifier())
    ]
    stacking_model = StackingClassifier(
        estimators=base_learners,
        final_estimator=LogisticRegression()
    )
    stacking_model.fit(X_train, y_train)
    return stacking_model

# -----------------------------------------------------------------------------
def compute_true_range(df: pd.DataFrame) -> pd.Series:
    high, low, close = df["High"], df["Low"], df["Close"]
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low  - prev_close).abs()
    return pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

def compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta    = series.diff()
    gain     = delta.clip(lower=0)
    loss     = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs       = avg_gain / avg_loss
    return (100 - (100 / (1 + rs))).round(4)

def compute_smoothed_macd(df: pd.DataFrame) -> pd.Series:
    ema_fast   = df["Close"].ewm(span=12, adjust=False).mean()
    ema_slow   = df["Close"].ewm(span=26, adjust=False).mean()
    macd       = ema_fast - ema_slow
    signal_line= macd.ewm(span=9, adjust=False).mean()
    return (macd - signal_line).round(4)

def compute_rsi_momentum(df: pd.DataFrame, window: int = 14) -> pd.Series:
    rsi = compute_rsi(df["Close"], window)
    return rsi.diff().round(4)

# -----------------------------------------------------------------------------
def generate_features(df: pd.DataFrame, rsi_window: int = 14, mfi_window: int = 14):
    df = df.copy(deep=True)

    # Validate core structure
    required = ["Open", "High", "Low", "Close", "Volume"]
    if not all(col in df.columns for col in required):
        raise ValueError("Missing required OHLCV columns")

    # Target & indicators
    df["RETURN"]        = df["Close"].pct_change()
    df["TARGET"]        = (df["Close"].shift(-3) > df["Close"]).astype(int)
    df["RSI"]           = compute_rsi(df["Close"], rsi_window)
    df["MACD"]          = compute_smoothed_macd(df)
    df["RSI_MOMENTUM"]  = compute_rsi_momentum(df, rsi_window)
    df["SMA_20"]        = df["Close"].rolling(20).mean().round(4)
    df["EMA_10"]        = df["Close"].ewm(span=10).mean().round(4)
    df["EMA_50"]        = df["Close"].ewm(span=50).mean().round(4)
    df["ATR14"]         = compute_true_range(df).rolling(14).mean().round(4)

    mid = df["Close"].rolling(20).mean()
    std = df["Close"].rolling(20).std()
    df["BB_MID"]   = mid.round(4)
    df["BB_UPPER"] = (mid + 2 * std).round(4)
    df["BB_LOWER"] = (mid - 2 * std).round(4)
    df["VOL_REGIME"] = (df["ATR14"] > df["ATR14"].rolling(50).median()).astype(int)

    direction = np.sign(df["Close"].diff().fillna(0))
    df["OBV"] = (direction * df["Volume"]).cumsum().round(4)

    tp = (df["High"] + df["Low"] + df["Close"]) / 3.0
    mf = tp * df["Volume"]
    pos_mf = mf.where(tp > tp.shift(1), 0.0)
    neg_mf = mf.where(tp < tp.shift(1), 0.0)
    mf_ratio = pos_mf.rolling(mfi_window).sum() / neg_mf.rolling(mfi_window).sum()
    df["MFI"] = (100 - 100 / (1 + mf_ratio)).round(4)

    # Prepare reindexing keys
    if not is_datetime(df.index):
        df.index = pd.to_datetime(df.index)
    date_index = pd.to_datetime(df.index.date)

    # SOCIAL
    social_sent = get_social_sentiment_series("AAPL", days=7)
    if social_sent.empty:
        logger.warning("No social sentiment — using zeros")
        df["SOCIAL_SENTIMENT"] = 0.0
    else:
        s = social_sent.reindex(date_index).ffill().bfill().values
        df["SOCIAL_SENTIMENT"] = s

    # NEWS
    news_sent = get_news_sentiment_series("AAPL", days=7)
    if news_sent.empty:
        logger.warning("No news sentiment — using zeros")
        df["NEWS_SENTIMENT"] = 0.0
    else:
        s = news_sent.reindex(date_index).ffill().bfill().values
        df["NEWS_SENTIMENT"] = s

    # Drop garbage
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    if len(df) < 10:
        logger.warning("After feature + sentiment engineering, not enough rows left.")

    features = [
        "Open", "High", "Low", "Close", "Volume", "RETURN", "RSI", "MACD",
        "SMA_20", "EMA_10", "EMA_50", "ATR14", "BB_UPPER", "BB_MID", "BB_LOWER",
        "VOL_REGIME", "OBV", "MFI", "NEWS_SENTIMENT", "SOCIAL_SENTIMENT"
    ]
    return df[features], df["TARGET"]



# -----------------------------------------------------------------------------
# Hyperopt objective (example)
def objective(params):
    ticker = "AAPL"
    df = get_stock_data(ticker)
    if df is None or df.empty:
        raise ValueError(f"No data for {ticker}")

    X, y = generate_features(df)
    if len(X) < 10:
        return {'loss': 1.0, 'status': STATUS_OK}

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = XGBClassifier(
        n_estimators=int(params['n_estimators']),
        max_depth=int(params['max_depth']),
        learning_rate=params['learning_rate'],
        eval_metric='logloss',
        use_label_encoder=False
    )
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    return {'loss': -acc, 'status': STATUS_OK}

_space = {
  'n_estimators': hp.choice('n_estimators', [100,200,300]),
  'max_depth':    hp.choice('max_depth',    [3,6,9]),
  'learning_rate':hp.uniform('learning_rate', 0.01,0.1),
}

# -----------------------------------------------------------------------------
def train_model(ticker: str):
    df = get_stock_data(ticker)
    if df is None or df.empty:
        raise ValueError(f"No data for {ticker}")

    X, y = generate_features(df)
    if len(X) < 10:
        raise ValueError(f"Not enough data to train for {ticker}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info(f"Training on {len(X_train)} rows; testing on {len(X_test)} rows")

    with mlflow.start_run():
        mlflow.log_param("n_estimators", 200)
        mlflow.log_param("max_depth", 6)
        mlflow.log_param("learning_rate", 0.05)

        model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            eval_metric="logloss",
            use_label_encoder=False
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        report = classification_report(
            y_test, y_pred, target_names=["Hold/Sell","Buy"], output_dict=True
        )
        json_path = os.path.join(METRICS_DIR, f"{ticker}_report.json")
        with open(json_path, "w") as f:
            json.dump(report, f, indent=4)
        mlflow.log_artifact(json_path)

        mlflow.log_metric("accuracy",  model.score(X_test, y_test))
        mlflow.log_metric("precision", report["Buy"]["precision"])
        mlflow.log_metric("recall",    report["Buy"]["recall"])
        mlflow.log_metric("f1_score",  report["Buy"]["f1-score"])

        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(6,4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=["Hold/Sell","Buy"],
                    yticklabels=["Hold/Sell","Buy"])
        plt.tight_layout()
        cm_path = os.path.join(METRICS_DIR, f"{ticker}_confusion_matrix.png")
        plt.savefig(cm_path); plt.close()
        mlflow.log_artifact(cm_path)

        model_path = os.path.join(MODEL_DIR, f"{ticker}_model.pkl")
        joblib.dump(model, model_path)
        mlflow.log_artifact(model_path)

    return model

def load_model(ticker: str):
    path = os.path.join(MODEL_DIR, f"{ticker}_model.pkl")
    if not os.path.exists(path):
        logger.info(f"No model for {ticker}, training fresh...")
        return train_model(ticker)
    return joblib.load(path)

def compare_models(tickers: list[str]) -> dict:
    results = {}
    for t in tickers:
        rpt = os.path.join(METRICS_DIR, f"{t}_report.json")
        if not os.path.exists(rpt):
            logger.warning(f"No metrics for {t}, skipping.")
            continue
        with open(rpt) as f:
            report = json.load(f)
        results[t] = {
            "accuracy": report["accuracy"],
            "precision": report["Buy"]["precision"],
            "recall":    report["Buy"]["recall"],
            "f1_score":  report["Buy"]["f1-score"],
        }

    # --- save comparison.json ---
    comp_json = os.path.join(METRICS_DIR, "comparison.json")
    with open(comp_json, "w") as f:
        json.dump(results, f, indent=4)
    logger.info(f"[✓] Saved comparison JSON to {comp_json}")

    # --- save comparison.csv ---
    comp_csv = os.path.join(METRICS_DIR, "comparison.csv")
    with open(comp_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Ticker", "Accuracy", "Precision", "Recall", "F1 Score"])
        for t, m in results.items():
            writer.writerow([t, m["accuracy"], m["precision"], m["recall"], m["f1_score"]])
    logger.info(f"[✓] Saved comparison CSV to {comp_csv}")

    # --- optional bar‐plot ---
    try:
        df = pd.DataFrame(results).T  # transpose so tickers are rows
        ax = df.plot(
            kind="bar",
            figsize=(10, 6),
            ylim=(0, 1),
            rot=0,
            title="Model Performance Comparison"
        )
        ax.set_ylabel("Score")
        plt.tight_layout()

        plot_path = os.path.join(METRICS_DIR, "comparison_plot.png")
        plt.savefig(plot_path)
        plt.close()
        logger.info(f"[✓] Saved comparison plot to {plot_path}")
    except Exception as e:
        logger.warning(f"[!] Could not create comparison plot: {e}")

        
    return results

# -----------------------------------------------------------------------------
if __name__ == "__main__":
    trials = Trials()
    best   = fmin(fn=objective, space=_space, algo=tpe.suggest, max_evals=50, trials=trials)
    print("Best hyperparameters:", best)





