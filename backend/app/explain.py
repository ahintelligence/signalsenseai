import yfinance as yf
import pandas as pd

def explain_signal(df):
    latest = df.iloc[-1]
    explanation_parts = []

    rsi = latest['RSI'].item() if hasattr(latest['RSI'], 'item') else latest['RSI']
    sma = latest['SMA_20'].item() if hasattr(latest['SMA_20'], 'item') else latest['SMA_20']
    macd = latest['MACD'].item() if hasattr(latest['MACD'], 'item') else latest['MACD']
    close = latest['Close'].item() if hasattr(latest['Close'], 'item') else latest['Close']

    score = 0

    if rsi < 30:
        explanation_parts.append(f"The RSI is {rsi:.1f}, indicating it's likely oversold.")
        score += 1
    elif rsi > 70:
        explanation_parts.append(f"The RSI is {rsi:.1f}, suggesting it's overbought.")
        score -= 1
    else:
        explanation_parts.append(f"The RSI is {rsi:.1f}, in a neutral range.")

    if close > sma:
        explanation_parts.append(f"Price is above the 20-day SMA ({sma:.2f}), indicating bullish momentum.")
        score += 1
    else:
        explanation_parts.append(f"Price is below the 20-day SMA ({sma:.2f}), indicating bearish momentum.")
        score -= 1


    if macd > 0:
        explanation_parts.append(f"MACD is positive ({macd:.2f}), confirming upward trend.")
        score += 1
    else:
        explanation_parts.append(f"MACD is negative ({macd:.2f}), confirming downward trend.")
        score -= 1

    if score >= 2:
        summary = "Overall, the indicators show a strong bullish signal."
    elif score <= -2:
        summary = "Overall, the indicators suggest a bearish trend."
    else:
        summary = "Overall, the signals are mixed."

    return summary + " " + " ".join(explanation_parts)

# function for frontend charting
def get_stock_history(ticker):
    df = yf.download(ticker, period="6mo", interval="1d")
    df = df[['Close']].dropna()
    df.reset_index(inplace=True)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    return {"ticker": ticker, "history": df.to_dict(orient='records')}
