# Sugarcane Byproduct Matcher — Prototype

A minimal, working end-to-end prototype implementing the 8-step decision flow:
input collection → waste-stream estimation → industry matching → buyer lookup →
transport cost → revenue/net revenue → sustainability scoring → AI explanation.

## Stack

- **Frontend:** React (Vite) + Tailwind CSS v4, Leaflet (map pin), Recharts (chart)
- **Backend:** FastAPI, SQLite (buyer/industry facility DB)
- **Decision engine:** rule-based Steps 2–7 in `backend/app/engine.py` (XGBoost/LightGBM/
  scikit-learn are natural next steps for a learned feasibility/price model — see
  "Where ML plugs in" below; this prototype ships a transparent, auditable rule engine first)
- **Explanation layer (Step 8):** Anthropic API (`claude-sonnet-5`), with a deterministic
  template fallback so the app works with zero configuration

## Run it

### Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate   # optional but recommended
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Optional — enable the live AI explanation (Step 8) instead of the template fallback:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Backend runs at `http://localhost:8000`. Interactive API docs: `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and talks to the backend via `VITE_API_BASE`
(set in `frontend/.env`, defaults to `http://localhost:8000`).

## What's implemented vs. what's stubbed

| Piece | Status |
|---|---|
| 4-field input form + Leaflet map pin | ✅ working |
| Waste stream estimation (bagasse/trash/press mud) | ✅ working, **ratios validated against your uploaded CSV** (28% / 12% / 4% — exact match) |
| Molasses estimate for ethanol matching | ⚠️ estimated at 4.5% (industry benchmark) — not in your dataset, flag for review |
| Industry matching (Step 3 compatibility rules) | ✅ working |
| Buyer lookup / nearest neighbor | ✅ working, but **buyer database is seeded with 23 synthetic facilities** across real cane-growing states — replace `backend/app/db.py:SEED_BUYERS` with a real buyer registry before production use |
| Transport cost (trucks, per-km rate, seasonal multiplier) | ✅ working, uses your exact formula `trucks_required = ceil(qty/capacity)`, `cost = trucks * distance * rate` (+ flat loading charge per trip, as you also described) |
| Revenue / net revenue | ✅ working, **market prices are indicative placeholders** in `config.py` — swap for live mandi/offtake prices |
| Sustainability score (0-100) | ✅ working, composite of net revenue/tonne, distance, CO2 avoided, compatibility — weights in `config.py` |
| Feasibility label | ✅ working (High/Medium/Low derived from score + net revenue sign) |
| Step 8 explanation | ✅ working — calls Claude if `ANTHROPIC_API_KEY` is set, else uses a template |
| XGBoost / LightGBM / scikit-learn | ❌ not yet wired in — see below |
| LangChain | ❌ not used yet — current explanation is a single prompt call, see note in `explain.py` |

## Where ML plugs in next

Right now Steps 2–7 are deterministic formulas (transparent and auditable, good for a v1
farmers can trust). The natural places to introduce the ML stack you specified:

- **XGBoost/LightGBM** — train a *feasibility/price* model on historical mill transaction
  data (if/when available) to replace the fixed `MARKET_PRICE_PER_TON` table with a
  predicted price per waste stream, industry, region and season.
- **scikit-learn** — use for the sustainability-score normalization/weighting once you have
  labeled outcome data (e.g. did farmers who took the top recommendation actually transact?)
  to learn weights instead of the hand-set ones in `SCORE_WEIGHTS`.
- **LangChain** — swap into `explain.py` once the explanation step needs multi-step
  reasoning, memory across a farmer's sessions, or tool use (e.g. looking up live mandi
  prices before explaining) — a single prompt call doesn't need it yet.

## Project structure

```
backend/
  app/
    config.py     # all ratios, prices, transport constants, score weights
    db.py         # SQLite buyer table + seed data
    engine.py     # Steps 2–7
    explain.py    # Step 8 (Claude API + fallback)
    schemas.py    # Pydantic request/response models
    main.py        # FastAPI routes
  requirements.txt
frontend/
  src/
    components/   # InputForm, LocationMap, WasteBreakdown, ResultsList, RevenueChart
    api.js
    App.jsx
```
