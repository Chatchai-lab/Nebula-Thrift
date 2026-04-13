"""Cost data endpoints: fetch live AWS cost data."""
from fastapi import APIRouter, HTTPException

from app.config import create_aws_provider

router = APIRouter(prefix="/api/costs", tags=["costs"])


@router.get("")
async def get_costs(account_id: str | None = None, days: int = 30) -> dict:
    """Fetch cost data from AWS Cost Explorer.

    Args:
        account_id: AWS account ID (uses local profile if omitted)
        days: Number of days to look back (default: 30)
    """
    try:
        provider = create_aws_provider(account_id)
        cost_data = await provider.get_cost_data(days=days)
        return cost_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/breakdown")
async def get_cost_breakdown(account_id: str | None = None, days: int = 30) -> dict:
    """Fetch costs grouped by service.

    Args:
        account_id: AWS account ID (uses local profile if omitted)
        days: Number of days to look back (default: 30)
    """
    try:
        provider = create_aws_provider(account_id)
        cost_data = await provider.get_cost_data(days=days)
        return {
            "currency": cost_data["currency"],
            "total": cost_data["total"],
            "breakdown": cost_data["by_service"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
