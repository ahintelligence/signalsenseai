import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from app.model import load_model, generate_features
from app.data import get_stock_data


def calculate_metrics(history: list[float]) -> dict:
    series = pd.Series(history)
    returns = series.pct_change().dropna()

    sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
    max_drawdown = ((series.cummax() - series) / series.cummax()).max() * 100
    volatility = returns.std() * np.sqrt(252)

    return {
        "sharpe_ratio": round(sharpe, 4),
        "max_drawdown_pct": round(max_drawdown, 2),
        "volatility": round(volatility, 4),
    }


def plot_history(history: list[float]):
    plt.figure(figsize=(10, 5))
    plt.plot(history, label="Portfolio Value")
    plt.title("Backtest Portfolio Value Over Time")
    plt.xlabel("Days")
    plt.ylabel("Portfolio Value ($)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def run_backtest(ticker: str, initial_cash: float = 10_000, verbose: bool = False):
    df = get_stock_data(ticker)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns.name = None

    X, y = generate_features(df)
    model = load_model(ticker)

    booster = model.get_booster()
    trained_features = booster.feature_names

    rename_map = {}
    suffix = f" {ticker}"
    for fname in trained_features:
        if fname.endswith(suffix):
            base = fname[:-len(suffix)]
        else:
            base = fname.strip()
        rename_map[base] = fname

    X_aligned = X.rename(columns=rename_map)
    X_aligned = X_aligned[trained_features]

    preds = model.predict(X_aligned)
    preds = np.array(preds).reshape(-1)

    close_prices = df["Close"]
    cash, position = initial_cash, 0
    history = []

    for i, signal in enumerate(preds):
        price = float(close_prices.iat[i])
        if signal == 1 and cash >= price:
            shares = cash // price
            cash -= shares * price
            position += shares
            if verbose:
                print(f"[BUY ] Day {i}: Bought {shares} @ {price:.2f}")
        elif signal == 0 and position > 0:
            cash += position * price
            if verbose:
                print(f"[SELL] Day {i}: Sold {position} @ {price:.2f}")
            position = 0
        history.append(cash + position * price)

    final_price = float(close_prices.iat[-1])
    final_value = cash + position * final_price
    total_return = ((final_value / initial_cash) - 1) * 100

    metrics = calculate_metrics(history)

    print(f"\n Final Portfolio Value: ${final_value:,.2f}")
    print(f" Return: {total_return:.2f}%")
    print(f" Sharpe Ratio: {metrics['sharpe_ratio']}")
    print(f" Max Drawdown: {metrics['max_drawdown_pct']}%")
    print(f" Volatility: {metrics['volatility']}")

    if verbose:
        plot_history(history)

    return {
        "ticker": ticker,
        "final_value": final_value,
        "return_pct": total_return,
        **metrics,
        "history": history
    }






















