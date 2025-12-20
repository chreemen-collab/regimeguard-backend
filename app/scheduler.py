from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import MarketState
from .engine import run_engine
from .config import MARKETS, ENGINE_UPDATE_MINUTES

scheduler = BackgroundScheduler()

def update_markets():
    db: Session = SessionLocal()
    try:
        for market_id in MARKETS:
            state = run_engine(market_id)
            record = MarketState(**state)
            db.add(record)
        db.commit()
        print("Markets updated")
    finally:
        db.close()

def start_scheduler():
    update_markets()  # <-- corre una vez al arrancar
    scheduler.add_job(
        update_markets,
        "interval",
        minutes=ENGINE_UPDATE_MINUTES
    )
    scheduler.start()

