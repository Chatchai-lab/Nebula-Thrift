"""Models for usage metrics returned by CloudProvider.get_usage_metrics()."""
from pydantic import BaseModel


class MetricSummary(BaseModel):
    average: float
    max: float
    datapoints: int


class UsageMetrics(BaseModel):
    resource_id: str
    period_days: int
    cpu: MetricSummary
    network_in: MetricSummary
    network_out: MetricSummary
