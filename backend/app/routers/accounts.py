"""Account management: register and manage multiple AWS accounts."""
from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.account import AWSAccountCreate, AWSAccount
from app.services.key_vault import KeyVaultService
from app.storage.blob_client import BlobStorageClient

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.post("", response_model=AWSAccount)
async def register_account(account_create: AWSAccountCreate) -> AWSAccount:
    """
    Register a new AWS account by storing credentials in Key Vault
    and metadata in Blob Storage.

    Args:
        account_create: Account details including AWS credentials

    Returns:
        AWSAccount with generated account_id and created_at timestamp
    """
    try:
        account_id = str(uuid4())[:8]  # Use first 8 chars of UUID
        created_at = datetime.utcnow().isoformat()

        # Store credentials in Key Vault
        key_vault = KeyVaultService()
        key_vault.store_credentials(
            account_id,
            account_create.access_key_id,
            account_create.secret_access_key,
        )

        # Store metadata in Blob Storage
        account = AWSAccount(
            account_id=account_id,
            name=account_create.name,
            region=account_create.region,
            created_at=created_at,
        )
        blob_client = BlobStorageClient()
        blob_client.save_account_metadata(account_id, account.model_dump())

        return account

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register account: {str(e)}",
        )


@router.get("", response_model=list[AWSAccount])
async def list_accounts() -> list[AWSAccount]:
    """
    List all registered AWS accounts (metadata only, no credentials).

    Returns:
        List of AWSAccount objects
    """
    try:
        blob_client = BlobStorageClient()
        accounts_data = blob_client.list_accounts()
        return [AWSAccount(**data) for data in accounts_data]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list accounts: {str(e)}",
        )


@router.get("/{account_id}", response_model=AWSAccount)
async def get_account(account_id: str) -> AWSAccount:
    """
    Retrieve a single AWS account's metadata.

    Args:
        account_id: The account ID to retrieve

    Returns:
        AWSAccount object with account details
    """
    try:
        blob_client = BlobStorageClient()
        data = blob_client.get_account_metadata(account_id)
        if not data:
            raise HTTPException(status_code=404, detail="Account not found")
        return AWSAccount(**data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve account: {str(e)}",
        )


@router.patch("/{account_id}/credentials")
async def update_account_credentials(account_id: str, credentials: AWSAccountCreate) -> dict:
    """
    Update AWS credentials for an existing account.

    Only updates credentials in Key Vault, does not modify account metadata.

    Args:
        account_id: The account ID to update
        credentials: New AWS credentials (access_key_id, secret_access_key)

    Returns:
        Success message
    """
    try:
        key_vault = KeyVaultService()
        key_vault.store_credentials(
            account_id,
            credentials.access_key_id,
            credentials.secret_access_key,
        )
        return {
            "status": "success",
            "message": f"Credentials for account {account_id} updated successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update credentials: {str(e)}",
        )


@router.delete("/{account_id}")
async def delete_account(account_id: str) -> dict:
    """
    Delete a registered AWS account.

    Removes:
    - Credentials from Key Vault
    - Metadata from Blob Storage

    Args:
        account_id: The account ID to delete

    Returns:
        Success message
    """
    try:
        # Delete from Key Vault
        key_vault = KeyVaultService()
        key_vault.delete_credentials(account_id)

        # Delete from Blob Storage
        blob_client = BlobStorageClient()
        blob_client.delete_account_metadata(account_id)

        return {
            "status": "success",
            "message": f"Account {account_id} deleted successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete account: {str(e)}",
        )
