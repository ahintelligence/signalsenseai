from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.model import load_model, generate_features
from app.data import get_stock_data
from app.explain import explain_signal

# Simple bearer‑token guard
bearer = HTTPBearer()
def require_token(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    if creds.credentials != "YOUR_SECRET_TOKEN":
        raise HTTPException(401, "Invalid token")
    return True

def get_prediction(ticker: str, _=Depends(require_token)):
    # 1) Load data & features
    df = get_stock_data(ticker)
    if not df or df.empty:
        raise HTTPException(404, f"No data for '{ticker.upper()}'")
    X, _ = generate_features(df)
    if X.empty:
        raise HTTPException(400, "Not enough data to compute features")

    # 2) Predict
    model = load_model(ticker)
    row = X.iloc[[-1]].values
    pred = model.predict(row)[0]
    proba = model.predict_proba(row)[0][int(pred)]
    confidence = round(float(proba)*100, 2)

    # 3) Explain
    try:
        explanation = explain_signal(X)
    except Exception:
        explanation = "No explanation available."

    # 4) Return
    return JSONResponse({
        "ticker": ticker.upper(),
        "signal": "Buy" if pred else "Hold/Sell",
        "confidence": confidence,
        "explanation": explanation
    })








 



