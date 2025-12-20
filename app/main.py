from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .models import MarketState
from .scheduler import start_scheduler
from .config import MARKETS

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RegimeGuard API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    start_scheduler()

@app.get("/markets")
def list_markets():
    return MARKETS

@app.get("/market/{market_id}")
def get_market_state(market_id: str, db: Session = Depends(get_db)):
    if market_id not in MARKETS:
        raise HTTPException(status_code=404, detail="Market not found")

    state = (
        db.query(MarketState)
        .filter(MarketState.market_id == market_id)
        .order_by(MarketState.timestamp.desc())
        .first()
    )

    if not state:
        return {"message": "No data yet"}

    return {
        "market": market_id,
        "regime": state.regime,
        "risk": state.risk,
        "exposure": state.exposure,
        "confidence": state.confidence,
        "updated_at": state.timestamp
    }

@app.get("/healthz")
def healthcheck():
    return {
        "status": "ok",
        "service": "RegimeGuard",
        "version": "0.1.0"
    }

@app.get("/")
def root():
    return {
        "name": "RegimeGuard API",
        "status": "online",
        "docs": "/docs",
        "health": "/healthz"
    }

@app.get("/")
def root():
    return {
        "name": "RegimeGuard API",
        "status": "online",
        "version": "0.1.0",
        "endpoints": {
            "health": "/healthz",
            "markets": "/markets",
            "market_state": "/market/{market_id}",
            "docs": "/docs"
        }
    }
