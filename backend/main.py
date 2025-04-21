from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.predict import router as predict_router
import yfinance as yf
import os
import json
import numpy as np
import pandas as pd

from typing import List

from app.predict import get_prediction
from app.history import get_price_history
from app.data import get_stock_data
from app.model import load_model, generate_features, compare_models
from routes.summary import router as summary_router

app = FastAPI()

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/predict/{ticker}")
def predict_ticker(ticker: str):
    return get_prediction(ticker)

@app.get("/history/{ticker}")
def history(ticker: str, range: str = Query("1mo", enum=["1mo", "3mo", "6mo", "ytd", "1y"])):
    return get_price_history(ticker, range)

@app.get("/latest-price/{ticker}")
def get_latest_price(ticker: str):
    stock = yf.Ticker(ticker.upper())
    df = stock.history(period="1d", interval="1m")

    if df.empty:
        raise HTTPException(status_code=404, detail="No data available for this ticker.")

    latest = df.iloc[-1]
    return {
        "date": latest.name.isoformat(),
        "open": round(latest["Open"], 2),
        "high": round(latest["High"], 2),
        "low": round(latest["Low"], 2),
        "close": round(latest["Close"], 2),
    }

@app.get("/metrics/{ticker}")
def get_metrics(ticker: str):
    base = "metrics"
    json_path = os.path.join(base, f"{ticker.upper()}_report.json")
    img_path = os.path.join(base, f"{ticker.upper()}_confusion_matrix.png")

    if not os.path.exists(json_path) or not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail="Metrics not found for this ticker")

    with open(json_path, "r") as f:
        report = json.load(f)

    return {
        "classification_report": report,
        "confusion_matrix_image": f"/metrics/{ticker}/image"
    }

@app.get("/metrics/{ticker}/image")
def get_confusion_image(ticker: str):
    path = os.path.join("metrics", f"{ticker.upper()}_confusion_matrix.png")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path, media_type="image/png")

@app.post("/compare")
def compare_models_endpoint(tickers: List[str]):
    return compare_models(tickers)

class PredictionRequest(BaseModel):
    data: List[str]  # adjust type if needed

@app.post("/predict")
async def predict_data(request: PredictionRequest):
    """
    Endpoint for making predictions using the trained model.
    Takes a list where the first element is the ticker symbol.
    """
    ticker = request.data[0].upper()
    df = get_stock_data(ticker)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="No stock data found for the provided ticker")

    # flatten MultiIndex if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        df.columns.name = None

    # generate features and align to model
    X, _ = generate_features(df)
    model = load_model(ticker)

    # ensure feature alignment
    booster = model.get_booster()
    trained_feat = booster.feature_names
    rename_map = {}
    suffix = f" {ticker}"
    for fname in trained_feat:
        if fname.endswith(suffix):
            base = fname[:-len(suffix)]
        else:
            base = fname.strip()
        rename_map[base] = fname
    X = X.rename(columns=rename_map)[trained_feat]

    # make prediction
    row = X.iloc[[-1]]
    pred = model.predict(row)[0]
    proba = model.predict_proba(row)[0][int(pred)]
    confidence = round(float(proba) * 100, 2)

    return {
        "ticker": ticker,
        "signal": "Buy" if pred == 1 else "Hold/Sell",
        "confidence": confidence
    }

# include any additional routers
app.include_router(summary_router)
app.include_router(predict_router)

