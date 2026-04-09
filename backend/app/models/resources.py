"""Models for resources returned by CloudProvider.list_resources()."""
from typing import Any

from pydantic import BaseModel


class ResourceDetails(BaseModel, extra="allow"):
    """Flexible details dict — fields vary by resource type."""
    pass


class Resource(BaseModel):
    type: str           # "ec2", "rds", "s3", "elastic_ip"
    resource_id: str
    name: str
    region: str
    status: str
    details: dict[str, Any]
