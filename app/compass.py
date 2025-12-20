from typing import Dict
from sqlalchemy.orm import Session
from datetime import datetime
from .models import MarketState


# =========================
# 1. ESTADO INTERNO (desde DB)
# =========================

def compute_compass_state(db: Session, market_id: str) -> Dict:
    """
    Obtiene el último estado del mercado desde la DB
    y lo normaliza al formato Compass.
    """

    state = (
        db.query(MarketState)
        .filter(MarketState.market_id == market_id)
        .order_by(MarketState.timestamp.desc())
        .first()
    )

    if not state:
        return None

    return {
        "state": state.regime,          # CALM | WATCH | UNSTABLE | ALERT
        "confidence": state.confidence,
        "metrics": {
            "risk": state.risk,
            "exposure": state.exposure
        },
        "phase": state.regime,           # por ahora igual, luego se refina
        "alerts": state.regime in ["UNSTABLE", "ALERT"],
        "updated_at": state.timestamp.isoformat()
    }


# =========================
# 2. FILTRO POR TIER
# =========================

def build_compass_response(
    db: Session,
    market_id: str,
    tier: str
) -> Dict:

    data = compute_compass_state(db, market_id)

    if not data:
        return {"message": "No data yet"}

    if tier == "free":
        return {
            "state": data["state"],
            "updated_at": data["updated_at"],
            "delayed": True
        }

    if tier == "pro":
        return {
            "state": data["state"],
            "confidence": data["confidence"],
            "metrics": data["metrics"],
            "updated_at": data["updated_at"]
        }

    if tier == "premium":
        return {
            "state": data["state"],
            "confidence": data["confidence"],
            "metrics": data["metrics"],
            "phase": data["phase"],
            "alerts": data["alerts"],
            "updated_at": data["updated_at"]
        }

    return {"error": "invalid tier"}

import json
from pathlib import Path

TIERS = json.loads(
    Path("app/tiers.json").read_text()
)

def build_compass_response(state, tier: str):
    config = TIERS.get(tier, TIERS["free"])

    data = {}

    for field in config["fields"]:
        data[field] = getattr(state, field)

    data["tier"] = tier
    data["delayed"] = config["delay_seconds"] > 0

    return data

