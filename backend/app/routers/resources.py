"""Resource endpoints: list AWS resources."""
from fastapi import APIRouter, HTTPException

from app.config import create_aws_provider

router = APIRouter(prefix="/api/resources", tags=["resources"])


@router.get("")
async def list_resources(account_id: str | None = None) -> list[dict]:
    """List all AWS resources (EC2, RDS, S3, Elastic IPs).

    Args:
        account_id: AWS account ID (uses local profile if omitted)
    """
    try:
        provider = create_aws_provider(account_id)
        resources = await provider.list_resources()
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
