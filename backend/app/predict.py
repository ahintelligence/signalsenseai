from app.model import load_model, generate_features
from app.data import get_stock_data
from app.explain import explain_signal

def get_prediction(ticker: str):
    df = get_stock_data(ticker)
    X, _ = generate_features(df)
    model = load_model(ticker)
    latest = X.iloc[-1:].values
    prediction = model.predict(latest)[0]
    probability = model.predict_proba(latest)[0][int(prediction)]
    signal = "Buy" if prediction else "Hold/Sell"
    explanation = explain_signal(X)

    return {
        "ticker": ticker,
        "signal": signal,
        "confidence": round(probability * 100, 2),
        "explanation": explanation
    }
