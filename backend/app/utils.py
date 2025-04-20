import numpy as np
import pandas as pd
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import AverageTrueRange, BollingerBands



def safe_serialize(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    elif isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: safe_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [safe_serialize(v) for v in obj]
    else:
        return obj

def generate_features(df: pd.DataFrame):
    df = df.copy()

    # Basic return & target
    df['Return'] = df['Close'].pct_change()
    df['Target'] = (df['Close'].shift(-3) > df['Close']).astype(int)

    # Prepare a flat Close series
    close = pd.Series(df['Close'].values.ravel(), index=df.index)

    # Standard indicators
    df['RSI'] = RSIIndicator(close=close).rsi()
    df['MACD'] = MACD(close=close).macd_diff()
    df['SMA_20'] = SMAIndicator(close=close, window=20).sma_indicator()
    df['EMA_10'] = EMAIndicator(close=close, window=10).ema_indicator()
    df['EMA_50'] = EMAIndicator(close=close, window=50).ema_indicator()

    # Volatility features with fallback
    try:
        atr = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14)
        df['atr14'] = atr.average_true_range()

        bb = BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_mid']   = bb.bollinger_mavg()
        df['bb_lower'] = bb.bollinger_lband()

        # Volatility regime flag
        df['vol_regime'] = (df['atr14'] > df['atr14'].rolling(50).median()).astype(int)
    except Exception:
        # Fallback if data too short or ta library errors
        df['atr14']      = pd.NA
        df['bb_upper']   = pd.NA
        df['bb_mid']     = pd.NA
        df['bb_lower']   = pd.NA
        df['vol_regime'] = pd.NA

    # Drop NaNs resulting from rolling or failures
    df = df.dropna()

    # Final feature list
    features = [
        'Open', 'High', 'Low', 'Close', 'Volume',
        'Return', 'RSI', 'MACD', 'SMA_20', 'EMA_10', 'EMA_50',
        'atr14', 'bb_upper', 'bb_mid', 'bb_lower', 'vol_regime'
    ]

    return df[features], df['Target']
