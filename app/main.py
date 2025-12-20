from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .scheduler import start_scheduler
from .config import MARKETS
from .compass import build_compass_response

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

@app.get("/compass/status")
def get_compass_status(
    market_id: str,
    tier: str = "free",
    db: Session = Depends(get_db)
):
    if market_id not in MARKETS:
        raise HTTPException(status_code=404, detail="Market not found")

    return build_compass_response(db, market_id, tier)

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
        "endpoints": {
            "health": "/healthz",
            "markets": "/markets",
            "compass": "/compass/status",
            "docs": "/docs"
        }
    }

from datetime import datetime

@app.post("/debug/seed")
def seed_state(db: Session = Depends(get_db)):
    state = MarketState(
        market_id="BTC",
        regime="CALM",
        risk=0.2,
        exposure=0.3,
        confidence=0.85,
        timestamp=datetime.utcnow()
    )
    db.add(state)
    db.commit()
    return {"status": "seeded"}
