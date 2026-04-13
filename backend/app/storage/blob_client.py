import json
from datetime import date
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

class BlobStorageClient:
    def __init__(self, account_name="nebulathriftdata"):
        # Die URL deines Azure Speichers
        account_url = f"https://{account_name}.blob.core.windows.net"
        
        # DefaultAzureCredential nutzt automatisch deinen 'az login' aus dem Terminal
        self.credential = DefaultAzureCredential()
        self.service_client = BlobServiceClient(account_url, credential=self.credential)
        self.container_name = "snapshots"

    def upload_snapshot(self, snapshot_date: date, payload: dict, account_id: str | None = None):
        """
        Lädt ein JSON-Objekt (die AWS Daten) hoch.
        Dateiname im Container: {account_id}/YYYY-MM-DD.json (mit account_id) oder YYYY-MM-DD.json (legacy)
        """
        if account_id:
            blob_name = f"{account_id}/{snapshot_date.isoformat()}.json"
        else:
            blob_name = f"{snapshot_date.isoformat()}.json"
        blob_client = self.service_client.get_blob_client(container=self.container_name, blob=blob_name)
        
        # Daten in JSON umwandeln und hochladen
        json_data = json.dumps(payload, indent=4)
        blob_client.upload_blob(json_data, overwrite=True)
        print(f" Snapshot {blob_name} erfolgreich nach Azure hochgeladen.")

    def download_snapshot(self, snapshot_date: date, account_id: str | None = None):
        """Lädt einen Snapshot für ein bestimmtes Datum wieder herunter.

        Args:
            snapshot_date: Das Datum des Snapshots
            account_id: Optional - Account ID für Namespacing
        """
        if account_id:
            blob_name = f"{account_id}/{snapshot_date.isoformat()}.json"
        else:
            blob_name = f"{snapshot_date.isoformat()}.json"
        blob_client = self.service_client.get_blob_client(container=self.container_name, blob=blob_name)
        
        downloader = blob_client.download_blob()
        return json.loads(downloader.readall())

    def save_account_metadata(self, account_id: str, account_data: dict) -> None:
        """Save account metadata to the 'accounts' container."""
        try:
            container_client = self.service_client.get_container_client("accounts")
        except Exception:
            # Create container if it doesn't exist
            self.service_client.create_container(name="accounts")
            container_client = self.service_client.get_container_client("accounts")

        blob_client = container_client.get_blob_client(f"{account_id}.json")
        json_data = json.dumps(account_data, indent=4)
        blob_client.upload_blob(json_data, overwrite=True)

    def get_account_metadata(self, account_id: str) -> dict:
        """Retrieve account metadata from the 'accounts' container."""
        container_client = self.service_client.get_container_client("accounts")
        blob_client = container_client.get_blob_client(f"{account_id}.json")
        downloader = blob_client.download_blob()
        return json.loads(downloader.readall())

    def list_accounts(self) -> list[dict]:
        """List all account metadata blobs."""
        try:
            container_client = self.service_client.get_container_client("accounts")
            blobs = list(container_client.list_blobs())
            accounts = []
            for blob in blobs:
                account_data = self.get_account_metadata(blob.name.replace(".json", ""))
                accounts.append(account_data)
            return accounts
        except Exception:
            return []

    def delete_account_metadata(self, account_id: str) -> None:
        """Delete account metadata from the 'accounts' container."""
        try:
            container_client = self.service_client.get_container_client("accounts")
            blob_client = container_client.get_blob_client(f"{account_id}.json")
            blob_client.delete_blob()
        except Exception:
            pass  # Blob might not exist