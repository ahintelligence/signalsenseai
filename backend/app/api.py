# backend/app/api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.data import get_stock_data
from app.model.optimizer import run_optimization
from app.model.features import generate_features
from app.model.model_loader import load_model  # You’ll need to implement this
import pandas as pd
import numpy as np

app = FastAPI()


class PredictionRequest(BaseModel):
    ticker: str


@app.post("/predict")
def predict(request: PredictionRequest):
    try:
        df = get_stock_data(request.ticker)
        X, _ = generate_features(df, ticker=request.ticker)
        model = load_model(request.ticker)
        preds = model.predict(X)
        probas = model.predict_proba(X)[:, 1]

        latest_signal = preds[-1]
        confidence = float(np.round(probas[-1] * 100, 2))
        directive = "BUY" if latest_signal == 1 else "HOLD"

        return {
            "directive": directive,
            "trust_index": f"{confidence}%",
            "signal": int(latest_signal),
            "message": f"Signal Confidence: {confidence}%. No human override.",
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model not found for ticker.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/train")
def train(request: PredictionRequest):
    try:
        run_optimization(ticker=request.ticker, n_trials=50)
        return {"status": "Model trained successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

