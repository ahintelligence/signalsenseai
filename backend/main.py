from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from app.predict import get_prediction
from app.history import get_price_history
from routes.summary import router as summary_router 
import yfinance as yf
from fastapi import HTTPException


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

@app.get("/latest-price/{ticker}")
def get_latest_price(ticker: str):
    try:
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
            "close": round(latest["Close"], 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")



app.include_router(summary_router)