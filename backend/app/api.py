# backend/app/api.py

from fastapi import FastAPI
from pydantic import BaseModel
from app.model import train_model, load_model, generate_features
from app.data import get_stock_data
import pandas as pd

app = FastAPI()

class PredictionRequest(BaseModel):
    ticker: str

@app.post("/predict")
def predict(request: PredictionRequest):
    df = get_stock_data(request.ticker)
    model = load_model(request.ticker)
    X, _ = generate_features(df)
    preds = model.predict(X)
    return {"predictions": preds.tolist()}

@app.post("/train")
def train(request: PredictionRequest):
    model = train_model(request.ticker)
    return {"status": "model trained successfully"}
