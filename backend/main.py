from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.predict_routes import router as predict_router
from app.api.routes.train_routes import router as train_router
from app.api.routes.history_routes import router as history_router
from app.api.routes.analysis_routes import router as analysis_router
from app.api.routes.latest_price_routes import router as price_router
from routes.summary import router as summary_router  # optional placeholder

app = FastAPI(
    title="LATTICE API",
    description="Lattice AI — predictive analytics for stock signal generation",
    version="0.9.2",
)

# ────────────────────────────────
# CORS Setup (adjust for prod)
# ────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # update in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────────────────────
# Route Mounting
# ────────────────────────────────
app.include_router(predict_router, tags=["Prediction"])
app.include_router(train_router, tags=["Training"])
app.include_router(history_router, tags=["History"])
app.include_router(analysis_router, tags=["Analysis"])
app.include_router(summary_router, tags=["Summary"])
app.include_router(price_router, tags=["Price"])


