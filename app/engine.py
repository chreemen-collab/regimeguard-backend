"""
RegimeGuard Engine — powered by FDI-1 (Fracture Detection Integrator)
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

TICKER_MAP = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SPY": "SPY",
}

VOL_WINDOW = 30
TREND_WINDOW = 90
MOM_WINDOW = 30
FRACTURE_THRESHOLD = 0.6
COHERENCE_THRESHOLD = 0.5


def compute_metrics(prices: pd.Series) -> pd.DataFrame:
    r = prices.pct_change().fillna(0)
    volatility = r.rolling(VOL_WINDOW).std() * np.sqrt(252)
    trend = prices.pct_change(TREND_WINDOW)
    momentum = prices.pct_change(MOM_WINDOW)
    coherence = 1 - (
        r.rolling(VOL_WINDOW).std() /
        (r.rolling(2 * VOL_WINDOW).std() + 1e-9)
    )
    df = pd.DataFrame({"vol": volatility, "trend": trend, "mom": momentum, "coh": coherence}).fillna(0)
    for c in df.columns:
        m = df[c].abs().rolling(252).max()
        df[c] = np.where(m > 0, df[c] / m, 0)
        df[c] = np.clip(df[c], -1, 1)
    return df


def fracture_intensity(row) -> float:
    return float(np.clip(0.4 * row["trend"] + 0.4 * row["mom"] + 0.2 * row["coh"], 0, 1))


def map_regime(intensity: float, trend: float, vol: float):
    if vol > 0.7:
        risk = "EXTREME"
    elif vol > 0.4:
        risk = "HIGH"
    elif vol > 0.2:
        risk = "MED"
    else:
        risk = "LOW"

    if intensity > 0.65 and trend > 0.3:
        regime, exposure = "HARD", "MED"
        confidence = "HIGH" if intensity > 0.8 else "MED"
    elif intensity > 0.35 or trend > 0.1:
        regime, exposure, confidence = "MICRO", "LOW", "MED"
    else:
        regime = "BASE"
        exposure = "OFF" if risk in ("HIGH", "EXTREME") else "LOW"
        confidence = "HIGH" if vol < 0.2 else "MED"

    return regime, risk, exposure, confidence


def run_engine(market_id: str) -> dict:
    ticker = TICKER_MAP.get(market_id, market_id + "-USD")
    try:
        prices = yf.download(ticker, period="2y", progress=False)["Close"].dropna().squeeze()
        if len(prices) < 120:
            raise ValueError("Not enough data")
        metrics = compute_metrics(prices)
        last = metrics.iloc[-1]
        is_fracture = (last["trend"] > FRACTURE_THRESHOLD and last["mom"] > 0 and last["coh"] > COHERENCE_THRESHOLD)
        intensity = fracture_intensity(last) if is_fracture else fracture_intensity(last) * 0.5
        regime, risk, exposure, confidence = map_regime(intensity, float(last["trend"]), float(last["vol"]))
    except Exception as e:
        print(f"[engine] fallback for {market_id}: {e}")
        regime, risk, exposure, confidence = "BASE", "MED", "OFF", "LOW"

    return {
        "market_id": market_id,
        "regime": regime,
        "risk": risk,
        "exposure": exposure,
        "confidence": confidence,
        "timestamp": datetime.utcnow(),
    }