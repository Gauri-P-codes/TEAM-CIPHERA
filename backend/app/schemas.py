from pydantic import BaseModel, Field
from typing import Optional, List


class EstimateRequest(BaseModel):
    location_label: str = Field(..., description="Address / district / place name")
    lat: float
    lon: float
    production_tons: float = Field(..., gt=0, description="Total tonnes of cane crushed/expected")
    disposal_method: str = Field(
        ..., description="burned_in_field | dumped_unused | partially_composted | partially_utilized"
    )
    season_start_month: int = Field(..., ge=1, le=12)
    season_end_month: int = Field(..., ge=1, le=12)
    current_month: int = Field(..., ge=1, le=12)


class IndustryResult(BaseModel):
    industry_key: str
    industry_label: str
    waste_stream: str
    waste_quantity_tons: float
    buyer_name: str
    buyer_state: str
    distance_km: float
    trucks_required: int
    transport_cost_inr: float
    estimated_revenue_inr: float
    net_revenue_inr: float
    co2_avoided_kg: float
    sustainability_score: float
    feasibility: str


class EstimateResponse(BaseModel):
    waste_breakdown: dict
    results: List[IndustryResult]
    explanation: str
    is_peak_season: bool
