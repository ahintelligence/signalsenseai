import os
import json
import yfinance as yf
import pandas as pd

from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.data_provider import get_stock_data
from app.core.features import generate_features
from app.services.trainer import load_model, compare_models

router = APIRouter()


class PredictionRequest(BaseModel):
    data: List[str]


@router.get("/metrics/{ticker}")
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


@router.get("/metrics/{ticker}/image")
def get_confusion_image(ticker: str):
    path = os.path.join("metrics", f"{ticker.upper()}_confusion_matrix.png")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path, media_type="image/png")


@router.post("/compare")
def compare_models_endpoint(tickers: List[str]):
    return compare_models(tickers)


@router.get("/latest-price/{ticker}")
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
