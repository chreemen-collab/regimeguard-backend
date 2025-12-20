import json
from pathlib import Path
from typing import Dict
from sqlalchemy.orm import Session
from .models import MarketState

TIERS = json.loads(
    Path("app/tiers.json").read_text()
)

def compute_compass_state(db: Session, market_id: str) -> Dict | None:
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
        "phase": state.regime,
        "alerts": state.regime in ["UNSTABLE", "ALERT"],
        "updated_at": state.timestamp.isoformat()
    }

def build_compass_response(
    db: Session,
    market_id: str,
    tier: str
) -> Dict:

    base = compute_compass_state(db, market_id)

    if not base:
        return {"message": "No data yet"}

    config = TIERS.get(tier, TIERS["free"])

    response = {
        "state": base["state"],
        "updated_at": base["updated_at"],
        "tier": tier
    }

    if "confidence" in config["fields"]:
        response["confidence"] = base["confidence"]

    if "metrics" in config["fields"]:
        response["metrics"] = base["metrics"]

    if "phase" in config["fields"]:
        response["phase"] = base["phase"]

    if "alerts" in config["fields"]:
        response["alerts"] = base["alerts"]

    response["delayed"] = config["delay_seconds"] > 0

    return response
