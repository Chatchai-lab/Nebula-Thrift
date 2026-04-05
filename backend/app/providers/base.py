"""Abstract base class for cloud providers."""
from abc import ABC, abstractmethod


class CloudProvider(ABC):
    """Interface that all cloud providers must implement.
    Currently supported: AWS
    Planned: Azure, GCP
    """

    @abstractmethod
    async def get_cost_data(self, days: int = 30) -> dict:
        """Retrieve cost data for the specified period."""
        pass

    @abstractmethod
    async def get_usage_metrics(self, resource_id: str) -> dict:
        """Retrieve usage metrics for a specific resource."""
        pass

    @abstractmethod
    async def list_resources(self) -> list:
        """List all active resources in the account."""
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """Test if the provider credentials are valid."""
        pass
