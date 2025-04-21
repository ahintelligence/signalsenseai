import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.model.train import load_model
from app.data import get_stock_data
from app.model.features import generate_features
from app.explain import explain_signal

# Set up router and auth
router = APIRouter()
bearer = HTTPBearer()
SECRET_TOKEN = os.getenv("API_SECRET_TOKEN", "YOUR_SECRET_TOKEN")


def require_token(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    """Validate access token from the client."""
    if creds.credentials != SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True


def predict_signal(ticker: str) -> dict:
    """Core prediction logic separated from routing."""
    df = get_stock_data(ticker)
    if df is None or df.empty:
        raise ValueError(f"No data for '{ticker.upper()}'")

    X, _ = generate_features(df)
    if X.empty:
        raise ValueError("Not enough data to compute features")

    model = load_model(ticker)
    row = X.iloc[[-1]].values

    pred = model.predict(row)[0]
    proba = model.predict_proba(row)[0][int(pred)]
    confidence = round(float(proba) * 100, 2)

    try:
        explanation = explain_signal(X)
    except Exception:
        explanation = "No explanation available."

    return {
        "ticker": ticker.upper(),
        "signal": "Buy" if pred else "Hold/Sell",
        "confidence": confidence,
        "explanation": explanation,
    }


@router.get("/predict/{ticker}")
def get_prediction(ticker: str, _=Depends(require_token)):
    """API endpoint to get signal prediction for a stock."""
    try:
        result = predict_signal(ticker)
        return JSONResponse(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



