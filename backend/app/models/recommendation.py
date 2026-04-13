"""Models for optimization recommendations."""
from pydantic import BaseModel


class Recommendation(BaseModel):
    recommendation_id: str
    resource_id: str
    resource_type: str  # "ec2", "rds", "elastic_ip", "ebs_snapshot", "s3"
    issue: str
    recommendation: str
    priority: str  # "high", "medium", "low"
    estimated_saving: float  # monthly USD
    effort: str  # "low", "medium", "high"
    action_steps: list[str]
    status: str = "open"  # "open", "implemented", "dismissed"
