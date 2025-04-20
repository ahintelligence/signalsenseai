import numpy as np
import pandas as pd
from app.model import load_model, generate_features
from app.data import get_stock_data


def walk_forward_validation(df, model, window_size=30):
    train_size = window_size
    history = []
    
    for i in range(train_size, len(df)):
        train, test = df.iloc[i - train_size:i], df.iloc[i:i+1]
        X_train, y_train = train.drop('TARGET', axis=1), train['TARGET']
        X_test, y_test = test.drop('TARGET', axis=1), test['TARGET']
        
        model.fit(X_train, y_train)
        prediction = model.predict(X_test)
        history.append(prediction)
    
    return history

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
    if hasattr(preds, "to_numpy"):
        preds = preds.to_numpy()
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

    print(f"\n Final Portfolio Value: ${final_value:,.2f}")
    print(f" Return: {total_return:.2f}%")

    return {
        "ticker": ticker,
        "final_value": final_value,
        "return_pct": total_return,
        "history": history
    }





















