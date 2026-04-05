"""Waste detection service — identifies idle and underutilized resources."""


class WasteDetector:
    """Rule-based detection of wasted cloud resources."""

    def __init__(self, provider):
        self.provider = provider

    async def detect_waste(self):
        """Scan for idle EC2, unused Elastic IPs, old snapshots, etc."""
        raise NotImplementedError
