# RegimeGuard Backend (FastAPI)

RegimeGuard is a backend API for monitoring market regimes and risk.

## Live URL (Render)
https://regimeguard.onrender.com

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
