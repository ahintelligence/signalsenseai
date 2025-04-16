from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from app.predict import get_prediction
from app.history import get_price_history

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
def predict(ticker: str):
    return get_prediction(ticker)

@app.get("/history/{ticker}")
def history(ticker: str, range: str = Query("1mo", enum=["1mo", "3mo", "6mo", "ytd", "1y"])):
    return get_price_history(ticker, range)


