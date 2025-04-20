# backend/scripts/backtest.py

import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from app.data import get_stock_data
from app.model import generate_features

def walk_forward_backtest(
    ticker: str,
    train_window: int = None,
    test_window: int = 5,
    step: int = 5,
    cost_pct: float = 0.0005,
    hyperparams: dict = None
):
    """
    Walk‑forward backtest on `ticker`:
      • train on a sliding window of size `train_window`
      • test on the subsequent `test_window` days
      • advance the window by `step` each iteration
      • subtract `cost_pct` per trade
    """
    # 1) Load & feature‑engineer
    df = get_stock_data(ticker)
    if df is None or df.empty:
        print(f"No data for {ticker}, skipping")
        return

    X, y = generate_features(df)
    n = len(X)
    if n < 30:
        print(f"Not enough data ({n} rows) for {ticker}")
        return

    # 2) Determine train window
    default_tw = max(20, n // 4)
    train_window = train_window or default_tw
    if train_window + test_window > n:
        train_window = n - test_window - 1

    print(f"\nWalk‑forward for {ticker}: {n} rows, train={train_window}, test={test_window}, step={step}")

    prices = X["Close"].reset_index(drop=True)
    all_signals = []
    all_returns = []

    # 3) Slide the window
    for start in range(0, n - train_window - test_window + 1, step):
        end_train = start + train_window
        end_test  = end_train + test_window

        X_train, y_train = X.iloc[start:end_train], y.iloc[start:end_train]
        X_test,  _       = X.iloc[end_train:end_test], y.iloc[end_train:end_test]
        p0_series = prices.iloc[end_train:end_test]
        p1_series = prices.iloc[end_train + 1:end_test + 1]

        # skip if no class variation
        if y_train.nunique() < 2:
            continue

        # 4) Train
        params = hyperparams or {
            "n_estimators": 200,
            "max_depth": 5,
            "learning_rate": 0.05,
            "eval_metric": "logloss",
            "use_label_encoder": False,
        }
        model = XGBClassifier(**params)
        model.fit(X_train.values, y_train.values)

        # 5) Predict & simulate
        preds = model.predict(X_test.values).astype(int)
        for idx, pred in enumerate(preds):
            signal = "Buy" if pred else "Hold/Sell"
            all_signals.append(signal)

            p0 = p0_series.iloc[idx].item()
            p1 = p1_series.iloc[idx].item()
            rtn = (p1 - p0) / p0 - (cost_pct if pred else 0.0)
            all_returns.append(rtn)

    # 6) Results DataFrame
    df_res = pd.DataFrame({"signal": all_signals, "return": all_returns})
    if df_res.empty:
        print("No valid test steps run.")
        return

    win_rate = (df_res["return"] > 0).mean()
    avg_rtn  = df_res["return"].mean()
    cum_rtn  = (1 + df_res["return"]).prod() - 1

    print(f"  Iterations:         {len(df_res)}")
    print(f"  Win rate:           {win_rate:.2%}")
    print(f"  Avg per‑trade rtn:  {avg_rtn:.2%}")
    print(f"  Strategy cum rtn:   {cum_rtn:.2%}")

    # 7) Buy‑and‑hold baseline
    first_idx = train_window
    if first_idx < len(prices) - 1:
        entry_price = prices.iloc[first_idx].item()
        exit_price  = prices.iloc[-1].item()
        bh_rtn      = (exit_price - entry_price) / entry_price - cost_pct
        print(f"  Buy‑and‑Hold rtn:   {bh_rtn:.2%} (incl. cost)")

if __name__ == "__main__":
    # Optional hyperparameters to tweak
    hyperparams = {
        "n_estimators": 200,
        "max_depth": 5,
        "learning_rate": 0.05
    }

    for sym in ["AAPL", "GOOG", "TSLA"]:
        walk_forward_backtest(
            ticker=sym,
            train_window=None,    # auto ≈ 1/4 of data
            test_window=5,        # 5‑day hold
            step=5,               # retrain every 5 days
            cost_pct=0.0005,
            hyperparams=hyperparams
        )













