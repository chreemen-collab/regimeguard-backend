import random
from datetime import datetime

REGIMES = ["BASE", "MICRO", "HARD"]
RISKS = ["LOW", "MED", "HIGH", "EXTREME"]
EXPOSURES = ["OFF", "LOW", "MED"]
CONFIDENCE = ["HIGH", "MED", "LOW"]

def run_engine(market_id: str) -> dict:
    regime = random.choice(REGIMES)
    risk = random.choice(RISKS)

    if risk in ("HIGH", "EXTREME"):
        exposure = "LOW" if risk == "HIGH" else "OFF"
    else:
        exposure = "MED"

    confidence = random.choice(CONFIDENCE)

    return {
        "market_id": market_id,
        "regime": regime,
        "risk": risk,
        "exposure": exposure,
        "confidence": confidence,
        "timestamp": datetime.utcnow()
    }
