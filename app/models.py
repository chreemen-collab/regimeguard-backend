from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class MarketState(Base):
    __tablename__ = "market_state"

    id = Column(Integer, primary_key=True, index=True)
    market_id = Column(String, index=True)
    regime = Column(String)
    risk = Column(String)
    exposure = Column(String)
    confidence = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
