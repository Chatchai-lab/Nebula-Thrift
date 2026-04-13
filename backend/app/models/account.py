"""AWS account models."""
from pydantic import BaseModel


class AWSAccountCreate(BaseModel):
    """Input model for registering a new AWS account."""

    name: str
    access_key_id: str
    secret_access_key: str
    region: str = "eu-central-1"


class AWSAccount(BaseModel):
    """Output model for an AWS account (no secrets)."""

    account_id: str
    name: str
    region: str
    created_at: str
