from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services.data_provider import get_stock_data
from app.core.optimizer import run_optimization
from app.core.features import generate_features
from app.services.trainer import load_model
from app.core.version import API_VERSION, MODEL_VERSION
import numpy as np
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


# === Schemas ===
class PredictionRequest(BaseModel):
    ticker: str


class BatchPredictionRequest(BaseModel):
    tickers: list[str]


@router.get("/status")
def status():
    return {"status": "LATTICE online", "trust": "Stable", "version": API_VERSION}


@router.get("/version")
def version():
    return {
        "api_version": API_VERSION,
        "model_version": MODEL_VERSION,
        "core_module": CORE_MODULE
    }


# === Prediction: GET (Shortcut) ===
@router.get("/predict/{ticker}")
def get_prediction(ticker: str):
    try:
        df = get_stock_data(ticker)
        X, _ = generate_features(df, ticker=ticker)
        model = load_model(ticker)

        preds = model.predict(X)
        probas = model.predict_proba(X)[:, 1]
        latest_signal = preds[-1]
        confidence = float(np.round(probas[-1] * 100, 2))
        directive = "BUY" if latest_signal == 1 else "HOLD"

        return {
            "ticker": ticker.upper(),
            "directive": directive,
            "signal": int(latest_signal),
            "trust_index": f"{confidence}%",
            "confidence_raw": float(probas[-1]),
            "explanation": "N/A"
        }

    except Exception as e:
        logger.error(f"[!] Failed GET prediction for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed for {ticker}")


# === Prediction: POST ===
@router.post("/predict")
def predict(request: PredictionRequest):
    return get_prediction(request.ticker)


# === Batch Prediction ===
@router.post("/predict/batch")
def batch_predict(request: BatchPredictionRequest):
    results = {}
    for ticker in request.tickers:
        try:
            prediction = get_prediction(ticker)
            results[ticker.upper()] = prediction
        except Exception as e:
            results[ticker.upper()] = {"error": str(e)}
    return results


# === History ===
@router.get("/predict/history")
def predict_history(ticker: str, limit: int = Query(10, ge=1, le=100)):
    try:
        df = get_stock_data(ticker)
        X, _ = generate_features(df, ticker=ticker)
        model = load_model(ticker)

        preds = model.predict(X)
        probas = model.predict_proba(X)[:, 1]
        dates = df.index[-len(preds):]

        history = [
            {
                "timestamp": str(dates[i]),
                "signal": int(preds[i]),
                "trust_index": f"{round(probas[i] * 100, 2)}%"
            }
            for i in range(-limit, 0)
        ]

        return {
            "ticker": ticker.upper(),
            "count": len(history),
            "history": history[::-1]
        }

    except Exception as e:
        logger.error(f"[!] History error for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predict/{ticker}")
def get_latest_prediction(ticker: str):
    try:
        df = get_stock_data(ticker)
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")

        model = load_model(ticker)
        X, _ = generate_features(df, ticker=ticker)

        preds = model.predict(X)
        probas = model.predict_proba(X)[:, 1]

        latest_date = df.index[-1]
        latest_prediction = int(preds[-1])
        latest_confidence = round(float(probas[-1] * 100), 2)

        return JSONResponse({
            "ticker": ticker.upper(),
            "date": str(latest_date),
            "signal": latest_prediction,
            "confidence": latest_confidence
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[!] Prediction error for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# === Train / Retrain ===
@router.post("/train")
def train(request: PredictionRequest):
    try:
        run_optimization(ticker=request.ticker, n_trials=50)
        return {"status": "Model trained successfully"}
    except Exception as e:
        logger.error(f"[!] Training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrain")
def retrain(request: PredictionRequest):
    try:
        run_optimization(ticker=request.ticker, n_trials=100)
        return {"status": "Model retrained with deeper optimization"}
    except Exception as e:
        logger.error(f"[!] Retraining error: {e}")
        raise HTTPException(status_code=500, detail=str(e))




