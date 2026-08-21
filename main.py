from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .db import init_db, get_all_buyers
from .engine import build_candidates, score_candidates
from .explain import generate_explanation
from .schemas import EstimateRequest, EstimateResponse, IndustryResult

app = FastAPI(title="Sugarcane Waste-to-Value Decision Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only -- restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/meta")
def meta():
    """Static reference data for the frontend form (disposal methods, industries)."""
    return {
        "disposal_methods": config.DISPOSAL_METHODS,
        "industries": config.INDUSTRY_LABELS,
    }


@app.get("/api/buyers")
def buyers():
    return get_all_buyers()


@app.post("/api/estimate", response_model=EstimateResponse)
def estimate(req: EstimateRequest):
    if req.disposal_method not in config.DISPOSAL_METHODS:
        raise HTTPException(
            status_code=400,
            detail=f"disposal_method must be one of {config.DISPOSAL_METHODS}",
        )

    candidates, waste_breakdown, peak = build_candidates(req)
    ranked = score_candidates(candidates)

    if not ranked:
        raise HTTPException(
            status_code=404,
            detail="No matching buyers found for the estimated waste streams near this location.",
        )

    explanation = generate_explanation(ranked, req.disposal_method, peak)

    results = [IndustryResult(**{k: v for k, v in r.items() if k != "compatibility_score"}) for r in ranked]

    return EstimateResponse(
        waste_breakdown=waste_breakdown,
        results=results,
        explanation=explanation,
        is_peak_season=peak,
    )
