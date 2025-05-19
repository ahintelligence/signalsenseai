import os
import numpy as np
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.data_provider import get_stock_data
from app.services.trainer import load_model
from app.core.features import generate_features
from app.services.explainer_service import explain_signal  # renamed from app.explain
import logging

bearer = HTTPBearer()
SECRET_TOKEN = os.getenv("API_SECRET_TOKEN", "YOUR_SECRET_TOKEN")
logger = logging.getLogger(__name__)


def require_token(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    if creds.credentials != SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True


def generate_prediction(ticker: str) -> dict:
    df = get_stock_data(ticker)
    if df is None or df.empty:
        raise ValueError(f"No data for '{ticker.upper()}'")

    X, _ = generate_features(df, ticker=ticker)
    if X.empty:
        raise ValueError("Not enough data to compute features")

    model = load_model(ticker)
    row = X.iloc[[-1]].values

    pred = model.predict(row)[0]
    proba = model.predict_proba(row)[0][int(pred)]
    confidence = round(float(proba) * 100, 2)
    directive = "BUY" if pred else "HOLD"

    try:
        explanation = explain_signal(X)
    except Exception as e:
        logger.warning(f"[!] Explanation failed: {e}")
        explanation = "No explanation available."

    return {
        "ticker": ticker.upper(),
        "directive": directive,
        "signal": int(pred),
        "confidence_raw": float(proba),
        "trust_index": f"{confidence}%",
        "explanation": explanation,
        "message": f"Signal Confidence: {confidence}%. No override."
    }


def generate_batch_prediction(tickers: list[str]) -> dict:
    results = {}
    for ticker in tickers:
        try:
            results[ticker.upper()] = generate_prediction(ticker)
        except Exception as e:
            logger.error(f"[!] Batch prediction error for {ticker}: {e}")
            results[ticker.upper()] = {"error": str(e)}
    return results




