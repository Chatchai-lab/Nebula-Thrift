"""Abstract base class for cloud providers.

All methods are declared `async` so the implementations integrate cleanly with
FastAPI's event loop. Synchronous SDKs (e.g. boto3) should be wrapped in
`asyncio.to_thread(...)` inside the concrete provider so they don't block.
"""
from abc import ABC, abstractmethod


class CloudProvider(ABC):
    """Interface that all cloud providers must implement.
    Currently supported: AWS
    Planned: Azure, GCP
    """

    @abstractmethod
    async def get_cost_data(self, days: int = 30) -> dict:
        """Retrieve cost data for the specified period, grouped by service."""
        pass

    @abstractmethod
    async def get_usage_metrics(self, resource_id: str) -> dict:
        """Retrieve usage metrics (e.g. CPU, network) for a specific resource."""
        pass

    @abstractmethod
    async def list_resources(self) -> list:
        """List all active resources in the account."""
        pass

    @abstractmethod
    async def validate_connection(self) -> dict:
        """Verify provider credentials.

        Returns a dict describing the authenticated identity (account id,
        user/role arn, etc.). Raises on failure.
        """
        pass
