import math
from typing import List, Dict

from . import config
from .db import get_buyers_by_industry


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def is_peak_season(current_month: int, start_month: int, end_month: int) -> bool:
    """Handles wraparound seasons like Nov(11) - Apr(4)."""
    if start_month <= end_month:
        return start_month <= current_month <= end_month
    return current_month >= start_month or current_month <= end_month


# ---------------------------------------------------------------------------
# Step 2: Waste stream estimation
# ---------------------------------------------------------------------------
def estimate_waste_streams(production_tons: float) -> Dict[str, float]:
    return {
        stream: round(production_tons * ratio, 2)
        for stream, ratio in config.WASTE_RATIOS.items()
    }


# ---------------------------------------------------------------------------
# Step 4: Buyer lookup (nearest neighbor per industry)
# ---------------------------------------------------------------------------
def find_nearest_buyer(industry_key: str, lat: float, lon: float):
    buyers = get_buyers_by_industry(industry_key)
    if not buyers:
        return None
    best = None
    best_dist = float("inf")
    for b in buyers:
        d = haversine_km(lat, lon, b["lat"], b["lon"])
        if d < best_dist:
            best_dist = d
            best = b
    return best, round(best_dist, 1)


# ---------------------------------------------------------------------------
# Step 5: Transport cost
# ---------------------------------------------------------------------------
def calc_transport(quantity_tons: float, distance_km: float, peak_season: bool):
    trucks_required = math.ceil(quantity_tons / config.TRUCK_CAPACITY_TONS)
    rate = config.RATE_PER_KM * (config.PEAK_SEASON_MULTIPLIER if peak_season else 1.0)
    # trucks_required * (distance * rate_per_km)  +  flat loading/unloading charge per trip
    transport_cost = trucks_required * (distance_km * rate) + trucks_required * config.LOADING_UNLOADING_CHARGE
    return trucks_required, round(transport_cost, 2)


# ---------------------------------------------------------------------------
# Step 6: Revenue and net revenue
# ---------------------------------------------------------------------------
def calc_revenue(waste_stream: str, industry_key: str, quantity_tons: float, transport_cost: float):
    price = config.MARKET_PRICE_PER_TON.get((waste_stream, industry_key), 0)
    estimated_revenue = quantity_tons * price
    net_revenue = estimated_revenue - transport_cost
    return round(estimated_revenue, 2), round(net_revenue, 2)


# ---------------------------------------------------------------------------
# Step 7: CO2 avoided
# ---------------------------------------------------------------------------
def calc_co2_avoided(waste_stream_ignored: str, industry_key: str, quantity_tons: float, disposal_method: str):
    baseline = config.DISPOSAL_BASELINE_EMISSIONS_KG_PER_TON.get(disposal_method, 0)
    processing = config.INDUSTRY_PROCESSING_EMISSIONS_KG_PER_TON.get(industry_key, 0)
    avoided_per_ton = max(baseline - processing, 0)
    return round(avoided_per_ton * quantity_tons, 1)


# ---------------------------------------------------------------------------
# Main pipeline: steps 2-7 combined, returns raw candidate rows before scoring
# ---------------------------------------------------------------------------
def build_candidates(req) -> List[dict]:
    waste_breakdown = estimate_waste_streams(req.production_tons)
    peak = is_peak_season(req.current_month, req.season_start_month, req.season_end_month)

    candidates = []
    for waste_stream, quantity in waste_breakdown.items():
        if quantity <= 0:
            continue
        compat_list = config.INDUSTRY_COMPATIBILITY.get(waste_stream, [])
        for industry_key, compat_score in compat_list:
            lookup = find_nearest_buyer(industry_key, req.lat, req.lon)
            if lookup is None:
                continue  # Step 3 rule: only score an industry it can process AND we have a buyer for
            buyer, distance_km = lookup

            trucks_required, transport_cost = calc_transport(quantity, distance_km, peak)
            estimated_revenue, net_revenue = calc_revenue(waste_stream, industry_key, quantity, transport_cost)
            co2_avoided = calc_co2_avoided(waste_stream, industry_key, quantity, req.disposal_method)

            candidates.append({
                "industry_key": industry_key,
                "industry_label": config.INDUSTRY_LABELS[industry_key],
                "waste_stream": waste_stream,
                "waste_quantity_tons": quantity,
                "buyer_name": buyer["name"],
                "buyer_state": buyer["state"],
                "distance_km": distance_km,
                "trucks_required": trucks_required,
                "transport_cost_inr": transport_cost,
                "estimated_revenue_inr": estimated_revenue,
                "net_revenue_inr": net_revenue,
                "co2_avoided_kg": co2_avoided,
                "compatibility_score": compat_score,
            })
    return candidates, waste_breakdown, peak


def _normalize(values: List[float]) -> List[float]:
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi == lo:
        return [1.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


# ---------------------------------------------------------------------------
# Step 7: Sustainability scoring (composite, normalized across this request's
# candidate set)
# ---------------------------------------------------------------------------
def score_candidates(candidates: List[dict]) -> List[dict]:
    if not candidates:
        return []

    net_rev_per_ton = [c["net_revenue_inr"] / c["waste_quantity_tons"] for c in candidates]
    inv_distance = [1.0 / (1.0 + c["distance_km"]) for c in candidates]
    co2 = [c["co2_avoided_kg"] for c in candidates]
    compat = [c["compatibility_score"] for c in candidates]

    n_rev = _normalize(net_rev_per_ton)
    n_dist = _normalize(inv_distance)
    n_co2 = _normalize(co2)
    n_compat = _normalize(compat)

    w = config.SCORE_WEIGHTS
    for i, c in enumerate(candidates):
        score = (
            w["net_revenue"] * n_rev[i]
            + w["distance_feasibility"] * n_dist[i]
            + w["co2_avoided"] * n_co2[i]
            + w["compatibility"] * n_compat[i]
        ) * 100
        c["sustainability_score"] = round(score, 1)

        if score >= 70 and c["net_revenue_inr"] > 0:
            c["feasibility"] = "High"
        elif score >= 40 and c["net_revenue_inr"] > 0:
            c["feasibility"] = "Medium"
        else:
            c["feasibility"] = "Low"

    candidates.sort(key=lambda c: c["sustainability_score"], reverse=True)
    return candidates
