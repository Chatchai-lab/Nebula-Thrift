"""Unit tests for Pydantic models — no AWS credentials needed."""
import pytest
from app.models import CostData, ServiceCost, DailyCost, Resource, UsageMetrics, MetricSummary


class TestCostData:
    def test_valid_cost_data(self):
        data = CostData(
            period={"start": "2026-03-10", "end": "2026-04-09"},
            currency="USD",
            total=142.35,
            by_service=[
                ServiceCost(service="Amazon EC2", amount=80.0),
                ServiceCost(service="Amazon RDS", amount=62.35),
            ],
            daily=[
                DailyCost(date="2026-04-08", total=4.75, by_service={"Amazon EC2": 3.0, "Amazon RDS": 1.75}),
            ],
        )
        assert data.total == 142.35
        assert len(data.by_service) == 2
        assert data.by_service[0].service == "Amazon EC2"
        assert data.daily[0].by_service["Amazon RDS"] == 1.75

    def test_cost_data_with_warning(self):
        data = CostData(
            period={"start": "2026-03-10", "end": "2026-04-09"},
            currency="USD",
            total=0.0,
            by_service=[],
            daily=[],
            warning="Cost Explorer data not available yet.",
        )
        assert data.warning is not None
        assert data.total == 0.0
        assert data.by_service == []

    def test_cost_data_warning_defaults_to_none(self):
        data = CostData(
            period={"start": "2026-03-10", "end": "2026-04-09"},
            currency="USD",
            total=10.0,
            by_service=[],
            daily=[],
        )
        assert data.warning is None

    def test_invalid_cost_data_missing_field(self):
        with pytest.raises(Exception):
            CostData(
                period={"start": "2026-03-10", "end": "2026-04-09"},
                currency="USD",
                # total missing
                by_service=[],
                daily=[],
            )


class TestResource:
    def test_ec2_resource(self):
        res = Resource(
            type="ec2",
            resource_id="i-0abc123def456",
            name="web-server-1",
            region="eu-central-1",
            status="running",
            details={"instance_type": "t3.micro", "launch_time": "2026-04-01T10:00:00+00:00"},
        )
        assert res.type == "ec2"
        assert res.details["instance_type"] == "t3.micro"

    def test_s3_resource(self):
        res = Resource(
            type="s3",
            resource_id="my-bucket",
            name="my-bucket",
            region="eu-central-1",
            status="active",
            details={"created": "2026-01-15T08:00:00+00:00"},
        )
        assert res.status == "active"

    def test_elastic_ip_unassociated(self):
        res = Resource(
            type="elastic_ip",
            resource_id="eipalloc-abc123",
            name="3.120.45.67",
            region="eu-central-1",
            status="unassociated",
            details={"public_ip": "3.120.45.67", "instance_id": None},
        )
        assert res.status == "unassociated"
        assert res.details["instance_id"] is None


class TestUsageMetrics:
    def test_valid_metrics(self):
        metrics = UsageMetrics(
            resource_id="i-0abc123def456",
            period_days=14,
            cpu=MetricSummary(average=3.2, max=12.5, datapoints=336),
            network_in=MetricSummary(average=1024.0, max=8192.0, datapoints=336),
            network_out=MetricSummary(average=512.0, max=4096.0, datapoints=336),
        )
        assert metrics.cpu.average == 3.2
        assert metrics.period_days == 14

    def test_empty_metrics(self):
        metrics = UsageMetrics(
            resource_id="i-0abc123def456",
            period_days=14,
            cpu=MetricSummary(average=0.0, max=0.0, datapoints=0),
            network_in=MetricSummary(average=0.0, max=0.0, datapoints=0),
            network_out=MetricSummary(average=0.0, max=0.0, datapoints=0),
        )
        assert metrics.cpu.datapoints == 0
