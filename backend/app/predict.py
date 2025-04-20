from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.model import load_model, generate_features
from app.data import get_stock_data
from app.explain import explain_signal

# Set up token-based auth
bearer = HTTPBearer()

def require_token(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    if creds.credentials != "YOUR_SECRET_TOKEN":
        raise HTTPException(status_code=401, detail="Invalid token")
    return True

def get_prediction(ticker: str, _=Depends(require_token)):
    # Fetch stock data
    df = get_stock_data(ticker)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"No data for '{ticker.upper()}'")

    # Generate features
    X, _ = generate_features(df)
    if X.empty:
        raise HTTPException(status_code=400, detail="Not enough data to compute features")

    # Load model
    model = load_model(ticker)

    # Get last row for prediction
    row = X.iloc[[-1]].values
    pred = model.predict(row)[0]
    proba = model.predict_proba(row)[0][int(pred)]
    confidence = round(float(proba) * 100, 2)

    # SHAP explanation
    try:
        explanation = explain_signal(X)
    except Exception:
        explanation = "No explanation available."

    # Response payload
    return JSONResponse({
        "ticker": ticker.upper(),
        "signal": "Buy" if pred else "Hold/Sell",
        "confidence": confidence,
        "explanation": explanation
    })


