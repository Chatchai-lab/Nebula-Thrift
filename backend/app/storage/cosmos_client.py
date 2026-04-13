"""Cosmos DB client for recommendations and snapshots."""
import os
import uuid

from azure.cosmos import CosmosClient, PartitionKey
from azure.identity import DefaultAzureCredential


class CosmosDBClient:
    """Client for Cosmos DB operations on recommendations and snapshots."""

    def __init__(self):
        endpoint = os.getenv(
            "COSMOS_ENDPOINT",
            "https://nebula-thrift-db.documents.azure.com:443/",
        )
        self.credential = DefaultAzureCredential()
        self.client = CosmosClient(endpoint, credential=self.credential)
        self.database = self.client.get_database_client("nebulathrift")

    # ── Recommendations ──────────────────────────────────────────

    def get_recommendations(self, account_id: str | None = None) -> list[dict]:
        """Query all recommendations, optionally filtered by account_id."""
        container = self.database.get_container_client("recommendations")
        if account_id:
            query = "SELECT * FROM c WHERE c.account_id = @aid"
            params = [{"name": "@aid", "value": account_id}]
        else:
            query = "SELECT * FROM c"
            params = []
        return list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))

    def upsert_recommendation(self, recommendation: dict) -> dict:
        """Insert or update a single recommendation."""
        container = self.database.get_container_client("recommendations")
        if "id" not in recommendation:
            recommendation["id"] = recommendation.get("recommendation_id", str(uuid.uuid4()))
        return container.upsert_item(recommendation)

    def update_recommendation_status(self, recommendation_id: str, status: str) -> dict | None:
        """Update the status of a recommendation (open, implemented, dismissed)."""
        container = self.database.get_container_client("recommendations")
        query = "SELECT * FROM c WHERE c.recommendation_id = @rid"
        params = [{"name": "@rid", "value": recommendation_id}]
        items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
        if not items:
            return None
        item = items[0]
        item["status"] = status
        return container.upsert_item(item)

    # ── Snapshots ────────────────────────────────────────────────

    def save_snapshot(self, snapshot_date: str, payload: dict, account_id: str | None = None) -> dict:
        """Save a daily snapshot to Cosmos DB."""
        container = self.database.get_container_client("snapshots")
        doc = {
            "id": f"{account_id or 'local'}_{snapshot_date}",
            "snapshot_date": snapshot_date,
            "account_id": account_id or "local",
            **payload,
        }
        return container.upsert_item(doc)

    def get_latest_snapshot(self, account_id: str | None = None) -> dict | None:
        """Get the most recent snapshot for an account."""
        container = self.database.get_container_client("snapshots")
        aid = account_id or "local"
        query = "SELECT TOP 1 * FROM c WHERE c.account_id = @aid ORDER BY c.snapshot_date DESC"
        params = [{"name": "@aid", "value": aid}]
        items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
        return items[0] if items else None
