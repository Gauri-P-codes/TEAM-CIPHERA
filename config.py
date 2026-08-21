"""
Central configuration for the decision engine.

IMPORTANT: The waste-conversion ratios below were validated against the
uploaded ICAR/state-sugar-directorate-style dataset
(sugarcane_info_waste_dataset.csv), which shows, averaged across all
state/district/year rows:
    Bagasse    = 28.00% of cane production
    Trash      = 12.00% of cane production
    Press mud  =  4.00% of cane production
These match exactly, so they are hardcoded as-is. Molasses is NOT present
in that dataset, so a standard industry benchmark (4.0-5.0% of cane
crushed) is used instead -- flagged clearly as an estimate.
"""

# ---------------------------------------------------------------------------
# Step 2: Waste stream conversion ratios (validated against dataset)
# ---------------------------------------------------------------------------
WASTE_RATIOS = {
    "bagasse": 0.28,      # validated against dataset (exact match)
    "trash": 0.12,        # validated against dataset (exact match)
    "press_mud": 0.04,    # validated against dataset (exact match)
    "molasses": 0.045,    # NOT in dataset -> industry benchmark estimate, 4-5%
}

# ---------------------------------------------------------------------------
# Step 3: Industry <-> waste-stream compatibility map
# ---------------------------------------------------------------------------
# waste_stream -> list of (industry_key, compatibility_score 0-1)
INDUSTRY_COMPATIBILITY = {
    "bagasse": [
        ("cogeneration", 1.0),
        ("paper_pulp", 0.85),
    ],
    "molasses": [
        ("ethanol_distillery", 1.0),
    ],
    "press_mud": [
        ("biogas_cbg", 0.9),
    ],
    "trash": [
        ("biogas_cbg", 0.75),
    ],
}

INDUSTRY_LABELS = {
    "cogeneration": "Cogeneration / Bioelectricity",
    "ethanol_distillery": "Ethanol / Distillery",
    "paper_pulp": "Paper / Pulp",
    "biogas_cbg": "Biogas / CBG",
}

# ---------------------------------------------------------------------------
# Step 6: Market prices (INR per tonne of the WASTE STREAM sold as feedstock)
# These are indicative estimates for a prototype and should be replaced with
# live/regional mandi or industry offtake prices in production.
# ---------------------------------------------------------------------------
MARKET_PRICE_PER_TON = {
    ("bagasse", "cogeneration"): 1800,
    ("bagasse", "paper_pulp"): 2200,
    ("molasses", "ethanol_distillery"): 10000,
    ("press_mud", "biogas_cbg"): 500,
    ("trash", "biogas_cbg"): 700,
}

# ---------------------------------------------------------------------------
# Step 5: Transport constants
# ---------------------------------------------------------------------------
TRUCK_CAPACITY_TONS = 11.0          # midpoint of the 10-12 ton range
RATE_PER_KM = 25.0                  # INR/km, midpoint of Rs 20-30/km
LOADING_UNLOADING_CHARGE = 1200.0   # INR per trip (flat), midpoint of 500-2000
PEAK_SEASON_MULTIPLIER = 1.15       # applied to per-km rate during crushing season

# ---------------------------------------------------------------------------
# Step 7: CO2 baseline emission factors (kg CO2e per tonne of waste),
# relative to the *current disposal method* the farmer selects, vs the
# emissions of properly processing that tonne at the matched industry.
# ---------------------------------------------------------------------------
DISPOSAL_BASELINE_EMISSIONS_KG_PER_TON = {
    "burned_in_field": 1500.0,
    "dumped_unused": 400.0,
    "partially_composted": 200.0,
    "partially_utilized": 100.0,
}

INDUSTRY_PROCESSING_EMISSIONS_KG_PER_TON = {
    "cogeneration": 120.0,
    "ethanol_distillery": 180.0,
    "paper_pulp": 150.0,
    "biogas_cbg": 60.0,
}

# ---------------------------------------------------------------------------
# Step 7: Sustainability score weights (must sum to 1.0)
# ---------------------------------------------------------------------------
SCORE_WEIGHTS = {
    "net_revenue": 0.40,
    "distance_feasibility": 0.25,
    "co2_avoided": 0.25,
    "compatibility": 0.10,
}

DISPOSAL_METHODS = [
    "burned_in_field",
    "dumped_unused",
    "partially_composted",
    "partially_utilized",
]
