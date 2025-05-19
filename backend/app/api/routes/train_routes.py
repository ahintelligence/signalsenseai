from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.services.trainer import train_model, retrain_model
from app.services.predictor import require_token
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/train/{ticker}")
def train(ticker: str, _=Depends(require_token)):
    """Train a new model with default trial count."""
    try:
        train_model(ticker=ticker, n_trials=50)
        return JSONResponse({"status": f"Model trained for {ticker.upper()}"})
    except Exception as e:
        logger.error(f"[!] Train error for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Training failed")


@router.post("/retrain/{ticker}")
def retrain(ticker: str, _=Depends(require_token)):
    """Retrain a model with deeper search."""
    try:
        retrain_model(ticker=ticker, n_trials=100)
        return JSONResponse({"status": f"Model retrained (deep) for {ticker.upper()}"})
    except Exception as e:
        logger.error(f"[!] Retrain error for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Retraining failed")
