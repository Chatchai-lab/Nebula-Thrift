"""Recommendation endpoints: list and update optimization recommendations."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.recommendation import Recommendation
from app.storage.blob_client import BlobStorageClient

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


class StatusUpdate(BaseModel):
    status: str  # "implemented" or "dismissed"


@router.get("", response_model=list[Recommendation])
async def get_recommendations(account_id: str | None = None) -> list[Recommendation]:
    """Get all recommendations for an account.

    Args:
        account_id: AWS account ID
    """
    try:
        blob_client = BlobStorageClient()
        data = blob_client.load_recommendations(account_id)
        return [Recommendation(**r) for r in data]
    except Exception:
        return []


@router.patch("/{recommendation_id}")
async def update_recommendation(
    recommendation_id: str,
    update: StatusUpdate,
    account_id: str | None = None,
) -> dict:
    """Mark a recommendation as implemented or dismissed.

    Args:
        recommendation_id: The recommendation to update
        update: New status
        account_id: AWS account ID
    """
    try:
        blob_client = BlobStorageClient()
        recommendations = blob_client.load_recommendations(account_id)

        found = False
        for rec in recommendations:
            if rec["recommendation_id"] == recommendation_id:
                rec["status"] = update.status
                found = True
                break

        if not found:
            raise HTTPException(status_code=404, detail="Recommendation not found")

        blob_client.save_recommendations(account_id, recommendations)
        return {"status": "success", "recommendation_id": recommendation_id, "new_status": update.status}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
