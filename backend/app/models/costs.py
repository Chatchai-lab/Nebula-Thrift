"""Models for cost data returned by CloudProvider.get_cost_data()."""
from pydantic import BaseModel


class ServiceCost(BaseModel):
    service: str
    amount: float


class DailyCost(BaseModel):
    date: str
    total: float
    by_service: dict[str, float]


class CostData(BaseModel):
    period: dict[str, str]  # {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
    currency: str
    total: float
    by_service: list[ServiceCost]
    daily: list[DailyCost]
    warning: str | None = None
