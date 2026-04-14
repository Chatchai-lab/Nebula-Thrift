from pydantic import BaseModel, Field
import uuid

class Recommendation(BaseModel):
    # Wir fügen einen Default-Wert (UUID) hinzu, damit die ID nie fehlt
    recommendation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_id: str
    resource_type: str  # "ec2", "rds", "elastic_ip", etc.
    issue: str
    recommendation: str
    priority: str  # "high", "medium", "low"
    estimated_saving: float  # monthly USD
    estimated_annual_saving: float = 0.0
    effort: str  # "low", "medium", "high"
    action_steps: list[str]
    status: str = "open"
    account_id: str | None = None
    ai_enhanced: bool = False
    # Ein Zeitstempel ist für Cosmos DB immer gut
    created_at: str | None = None