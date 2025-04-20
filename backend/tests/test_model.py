import pandas as pd
from app.model import generate_features

def make_dummy_df():
    dates = pd.date_range("2022-01-01", periods=30, freq="D")
    data = {
        "Open": range(30),
        "High": [x + 1 for x in range(30)],
        "Low": range(30),
        "Close": [x + 1 for x in range(30)],
        "Volume": [100] * 30,
    }
    df = pd.DataFrame(data, index=dates)
    return df

def test_generate_features_columns():
    df = make_dummy_df()
    X, y = generate_features(df)


    expected_cols = ("RSI", "MACD", "SMA_20", "ATR14", "BB_UPPER", "VOL_REGIME")
    for col in expected_cols:
        assert col in X.columns


    assert len(X) == len(y) > 0
