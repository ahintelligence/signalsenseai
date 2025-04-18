from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/api/summary")
def get_summary():
    return JSONResponse({
        "assets": ["TSLA", "AAPL", "ETH", "USDJPY"],
        "volatility_clusters": True,
        "active_signals": 3,
        "last_update": "2.3s ago"
    })
