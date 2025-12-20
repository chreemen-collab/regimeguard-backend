from datetime import datetime
from typing import Dict


# =========================
# 1. ESTADO INTERNO COMPLETO
# =========================

def compute_internal_state() -> Dict:
    """
    Este representa TODO lo que tu sistema sabe.
    Esto NO se expone completo nunca.
    """
    return {
        "state": "ALERT",              # CALM | WATCH | UNSTABLE | ALERT
        "confidence": 97,              # 0–100
        "metrics": {
            "volatility": 0.28,
            "liquidity": 0.71,
            "momentum": 0.85
        },
        "phase": "CONTRACTION",        # solo premium
        "alerts": True,                # solo premium
        "updated_at": datetime.utcnow().isoformat()
    }


# =========================
# 2. FILTRO POR TIER
# =========================

def build_compass_response(tier: str) -> Dict:
    data = compute_internal_state()

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

    # fallback de seguridad
    return {
        "error": "invalid tier"
    }
