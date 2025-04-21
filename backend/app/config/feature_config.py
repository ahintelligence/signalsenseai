# app/config/feature_config.py

import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

def parse_bool(val, default=False):
    if isinstance(val, bool):
        return val
    if val is None:
        return default
    return str(val).strip().lower() in ["1", "true", "yes", "on"]

# Feature switches, read from environment or fallback to default
FEATURE_FLAGS = {
    "rsi":               parse_bool(os.getenv("FEATURE_RSI"), True),
    "rsi_momentum":      parse_bool(os.getenv("FEATURE_RSI_MOMENTUM"), True),
    "macd":              parse_bool(os.getenv("FEATURE_MACD"), True),
    "sma_20":            parse_bool(os.getenv("FEATURE_SMA_20"), True),
    "ema_10":            parse_bool(os.getenv("FEATURE_EMA_10"), True),
    "ema_50":            parse_bool(os.getenv("FEATURE_EMA_50"), True),
    "atr":               parse_bool(os.getenv("FEATURE_ATR"), True),
    "bollinger_bands":   parse_bool(os.getenv("FEATURE_BOLLINGER_BANDS"), True),
    "vol_regime":        parse_bool(os.getenv("FEATURE_VOL_REGIME"), True),
    "obv":               parse_bool(os.getenv("FEATURE_OBV"), True),
    "mfi":               parse_bool(os.getenv("FEATURE_MFI"), True),
    "news_sentiment":    parse_bool(os.getenv("FEATURE_NEWS_SENTIMENT"), True),
    "social_sentiment":  parse_bool(os.getenv("FEATURE_SOCIAL_SENTIMENT"), True),
}

# Parameter configs
RSI_WINDOW = int(os.getenv("RSI_WINDOW", 14))
MFI_WINDOW = int(os.getenv("MFI_WINDOW", 14))

