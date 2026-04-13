"""Snapshot management: fetch AWS costs and save to Azure Blob Storage."""
from datetime import date, datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.providers.aws import AWSProvider
from app.storage.blob_client import BlobStorageClient
from app.services.key_vault import KeyVaultService

router = APIRouter(prefix="/api/snapshots", tags=["snapshots"])


class SnapshotResponse(BaseModel):
    """Response after saving a snapshot."""
    date: str
    status: str
    message: str
    blob_name: str
    cost_data: dict | None = None


@router.post("/save", response_model=SnapshotResponse)
async def save_cost_snapshot(account_id: str | None = None, days: int = 30) -> SnapshotResponse:
    """
    Fetch AWS cost data and save as JSON snapshot to Azure Blob Storage.

    Args:
        account_id: AWS account ID (required for multi-account, optional for backward compatibility)
        days: Number of days to fetch cost data for (default: 30)

    Returns:
        SnapshotResponse with status and blob location
    """
    try:
        # 1. Get AWS credentials
        if account_id:
            # Load credentials from Key Vault for multi-account
            key_vault = KeyVaultService()
            access_key_id, secret_access_key = key_vault.get_credentials(account_id)

            # Get account metadata to determine region
            blob_client = BlobStorageClient()
            account_metadata = blob_client.get_account_metadata(account_id)
            region = account_metadata.get("region", "eu-central-1")

            aws_provider = AWSProvider(
                access_key_id=access_key_id,
                secret_access_key=secret_access_key,
                region_name=region,
            )
        else:
            # Fallback to default profile for backward compatibility
            aws_provider = AWSProvider(profile_name="nebula-thrift")

        # 2. Fetch AWS cost data
        cost_data = await aws_provider.get_cost_data(days=days)

        # 3. Prepare snapshot payload
        snapshot_date = date.today()
        payload = {
            "date": snapshot_date.isoformat(),
            "fetched_at": datetime.now().isoformat(),
            "days": days,
            "cost_data": cost_data,
        }

        # 4. Upload to Azure Blob Storage
        blob_client = BlobStorageClient()
        blob_client.upload_snapshot(snapshot_date, payload, account_id=account_id)

        if account_id:
            blob_name = f"{account_id}/{snapshot_date.isoformat()}.json"
        else:
            blob_name = f"{snapshot_date.isoformat()}.json"

        return SnapshotResponse(
            date=snapshot_date.isoformat(),
            status="success",
            message=f"Snapshot saved successfully to Azure Blob Storage",
            blob_name=blob_name,
            cost_data=cost_data,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save snapshot: {str(e)}"
        )


@router.get("/latest")
async def get_latest_snapshot(account_id: str | None = None) -> dict:
    """
    Retrieve the latest cost snapshot from Azure Blob Storage.

    Args:
        account_id: AWS account ID (required for multi-account, optional for backward compatibility)

    Returns:
        The JSON content of today's snapshot
    """
    try:
        snapshot_date = date.today()
        blob_client = BlobStorageClient()
        data = blob_client.download_snapshot(snapshot_date, account_id=account_id)

        return {
            "status": "success",
            "date": snapshot_date.isoformat(),
            "data": data,
        }

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Snapshot not found or error reading: {str(e)}"
        )
