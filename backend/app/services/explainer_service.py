import logging
import pandas as pd

logger = logging.getLogger(__name__)

def explain_signal(df: pd.DataFrame) -> str:
    """
    Constructs a structured explanation from the latest technical indicators.

    Required indicators: RSI, SMA_20, MACD, Close.
    """
    try:
        latest = df.iloc[-1]

        rsi = latest.get('RSI')
        sma = latest.get('SMA_20')
        macd = latest.get('MACD')
        close = latest.get('Close')

        if pd.isna(rsi) or pd.isna(sma) or pd.isna(macd) or pd.isna(close):
            logger.warning("Incomplete data: explanation aborted.")
            return "Insufficient indicator data for explanation."

        logic_trace = []
        score = 0

        # RSI logic
        if rsi < 30:
            logic_trace.append(f"RSI={rsi:.1f} (oversold).")
            score += 1
        elif rsi > 70:
            logic_trace.append(f"RSI={rsi:.1f} (overbought).")
            score -= 1
        else:
            logic_trace.append(f"RSI={rsi:.1f} (neutral).")

        # SMA alignment
        if close > sma:
            logic_trace.append(f"Close={close:.2f} > SMA_20={sma:.2f} (bullish alignment).")
            score += 1
        else:
            logic_trace.append(f"Close={close:.2f} < SMA_20={sma:.2f} (bearish alignment).")
            score -= 1

        # MACD polarity
        if macd > 0:
            logic_trace.append(f"MACD={macd:.2f} (positive momentum).")
            score += 1
        else:
            logic_trace.append(f"MACD={macd:.2f} (negative momentum).")
            score -= 1

        # Classification logic
        if score >= 2:
            header = "Technical outlook: Bullish bias."
        elif score <= -2:
            header = "Technical outlook: Bearish bias."
        else:
            header = "Technical outlook: Indeterminate."

        return header + " " + " ".join(logic_trace)

    except Exception as e:
        logger.error(f"[Explainer] Failure: {e}")
        return "Explanation generation failed due to internal error."


# function for frontend charting
def get_stock_history(ticker):
    df = yf.download(ticker, period="6mo", interval="1d")
    df = df[['Close']].dropna()
    df.reset_index(inplace=True)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    return {"ticker": ticker, "history": df.to_dict(orient='records')}
