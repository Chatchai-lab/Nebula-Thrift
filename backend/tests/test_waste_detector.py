"""Unit and integration tests for WasteDetector.

All tests are fully offline — no AWS credentials or network calls needed.
The provider is replaced with a lightweight AsyncMock/stub in every test.

Run:  pytest backend/tests/test_waste_detector.py -v --cov=app.services.waste_detector
"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

from app.services.waste_detector import WasteDetector, WasteDetectorThresholds
from app.models.recommendation import Recommendation


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ec2(resource_id: str = "i-0abc123", status: str = "running") -> dict:
    return {
        "type": "ec2",
        "resource_id": resource_id,
        "name": "test-instance",
        "region": "eu-central-1",
        "status": status,
        "details": {"instance_type": "t3.medium"},
    }


def _make_metrics(cpu_avg: float, datapoints: int = 336) -> dict:
    """Simulate what provider.get_usage_metrics() returns."""
    return {
        "resource_id": "i-0abc123",
        "period_days": 14,
        "cpu": {"average": cpu_avg, "max": cpu_avg * 2, "datapoints": datapoints},
        "network_in": {"average": 1024.0, "max": 8192.0, "datapoints": datapoints},
        "network_out": {"average": 512.0, "max": 4096.0, "datapoints": datapoints},
    }


def _make_rds_metrics(cpu_avg: float, storage_used_percent: float) -> dict:
    return {
        "cpu": {"average": cpu_avg, "max": cpu_avg * 1.5, "datapoints": 336},
        "storage_used_percent": storage_used_percent,
    }


def _make_eip(resource_id: str = "eipalloc-abc", associated: bool = False) -> dict:
    return {
        "type": "elastic_ip",
        "resource_id": resource_id,
        "name": "1.2.3.4",
        "region": "eu-central-1",
        "status": "associated" if associated else "unassociated",
        "details": {
            "public_ip": "1.2.3.4",
            "instance_id": "i-0abc123" if associated else None,
        },
    }


def _make_snapshot(
    snapshot_id: str = "snap-abc123",
    age_days: int = 100,
    tags: dict | None = None,
) -> dict:
    created_at = datetime.now(timezone.utc) - timedelta(days=age_days)
    return {
        "snapshot_id": snapshot_id,
        "created_at": created_at.isoformat(),
        "tags": tags or {},
    }


def _make_lb(name: str = "my-alb") -> dict:
    return {"lb_arn": f"arn:aws:elasticloadbalancing:::{name}", "name": name}


def _make_bucket(name: str = "my-bucket", has_lifecycle: bool = False) -> dict:
    return {"name": name, "has_lifecycle_policy": has_lifecycle}


def _detector(thresholds: WasteDetectorThresholds | None = None) -> WasteDetector:
    """Return a WasteDetector with a stub provider (no AWS calls)."""
    provider = MagicMock()
    return WasteDetector(provider=provider, thresholds=thresholds)


# ===========================================================================
# 1. Idle EC2
# ===========================================================================

class TestCheckIdleEC2:
    def test_low_cpu_flagged(self):
        """EC2 mit 3% CPU → wird als idle erkannt."""
        det = _detector()
        result = det.check_idle_ec2(_make_ec2(), _make_metrics(cpu_avg=3.0))
        assert result is not None
        assert isinstance(result, Recommendation)
        assert result.resource_type == "ec2"
        assert result.priority == "high"

    def test_high_cpu_not_flagged(self):
        """EC2 mit 15% CPU → wird NICHT als idle erkannt."""
        det = _detector()
        result = det.check_idle_ec2(_make_ec2(), _make_metrics(cpu_avg=15.0))
        assert result is None

    def test_exact_threshold_not_flagged(self):
        """CPU exactly at threshold (5%) is not flagged (boundary: must be *below*)."""
        det = _detector()
        result = det.check_idle_ec2(_make_ec2(), _make_metrics(cpu_avg=5.0))
        assert result is None

    def test_stopped_instance_skipped(self):
        """Stopped instances are ignored regardless of CPU data."""
        det = _detector()
        result = det.check_idle_ec2(_make_ec2(status="stopped"), _make_metrics(cpu_avg=1.0))
        assert result is None

    def test_no_datapoints_skipped(self):
        """When CloudWatch returns no data we cannot judge — skip."""
        det = _detector()
        result = det.check_idle_ec2(_make_ec2(), _make_metrics(cpu_avg=0.0, datapoints=0))
        assert result is None

    def test_custom_threshold(self):
        """Custom threshold: 10% CPU still flags an instance with 8% CPU."""
        det = _detector(WasteDetectorThresholds(ec2_cpu_percent=10.0))
        result = det.check_idle_ec2(_make_ec2(), _make_metrics(cpu_avg=8.0))
        assert result is not None

    def test_recommendation_contains_resource_id(self):
        result = _detector().check_idle_ec2(
            _make_ec2(resource_id="i-special99"), _make_metrics(cpu_avg=2.0)
        )
        assert "i-special99" in result.resource_id
        assert "i-special99" in result.issue


# ===========================================================================
# 2. Oversized RDS
# ===========================================================================

class TestCheckOversizedRDS:
    def _rds(self, db_id: str = "db-prod") -> dict:
        return {
            "type": "rds",
            "resource_id": db_id,
            "name": db_id,
            "region": "eu-central-1",
            "status": "available",
            "details": {"engine": "postgres", "instance_class": "db.t3.large"},
        }

    def test_low_cpu_and_low_storage_flagged(self):
        """RDS mit 2% CPU → wird als oversized erkannt."""
        det = _detector()
        result = det.check_oversized_rds(self._rds(), _make_rds_metrics(2.0, 10.0))
        assert result is not None
        assert result.resource_type == "rds"
        assert result.priority == "medium"

    def test_high_cpu_not_flagged(self):
        """RDS mit 30% CPU → wird NICHT als oversized erkannt."""
        det = _detector()
        result = det.check_oversized_rds(self._rds(), _make_rds_metrics(30.0, 10.0))
        assert result is None

    def test_low_cpu_but_high_storage_not_flagged(self):
        """Both CPU *and* storage must be below thresholds."""
        det = _detector()
        result = det.check_oversized_rds(self._rds(), _make_rds_metrics(2.0, 80.0))
        assert result is None

    def test_high_storage_but_low_cpu_not_flagged(self):
        det = _detector()
        result = det.check_oversized_rds(self._rds(), _make_rds_metrics(2.0, 50.0))
        assert result is None


# ===========================================================================
# 3. Unused Elastic IP
# ===========================================================================

class TestCheckUnusedElasticIP:
    def test_unassociated_flagged(self):
        """Elastic IP ohne Instanz → wird als Waste erkannt."""
        det = _detector()
        result = det.check_unused_elastic_ip(_make_eip(associated=False))
        assert result is not None
        assert result.resource_type == "elastic_ip"
        assert result.estimated_saving == pytest.approx(3.60)

    def test_associated_not_flagged(self):
        """Elastic IP mit Instanz → wird NICHT als Waste erkannt."""
        det = _detector()
        result = det.check_unused_elastic_ip(_make_eip(associated=True))
        assert result is None

    def test_public_ip_in_issue_text(self):
        result = _detector().check_unused_elastic_ip(_make_eip(associated=False))
        assert "1.2.3.4" in result.issue


# ===========================================================================
# 4. Old EBS Snapshot
# ===========================================================================

class TestCheckOldSnapshot:
    _now = datetime(2026, 4, 13, 12, 0, 0, tzinfo=timezone.utc)

    def test_old_snapshot_without_backup_tag_flagged(self):
        """Snapshot 100 Tage alt → wird als löschbar erkannt."""
        det = _detector()
        snap = _make_snapshot(age_days=100, tags={})
        result = det.check_old_snapshot(snap, now=self._now)
        assert result is not None
        assert result.resource_type == "ebs_snapshot"

    def test_young_snapshot_not_flagged(self):
        """Snapshot 30 Tage alt → wird NICHT als löschbar erkannt."""
        det = _detector()
        snap = _make_snapshot(age_days=30, tags={})
        result = det.check_old_snapshot(snap, now=self._now)
        assert result is None

    def test_old_snapshot_with_backup_tag_not_flagged(self):
        """Old snapshot with 'Backup' tag is intentionally kept — skip."""
        det = _detector()
        snap = _make_snapshot(age_days=100, tags={"Backup": "true"})
        result = det.check_old_snapshot(snap, now=self._now)
        assert result is None

    def test_backup_tag_case_insensitive(self):
        """'backup' lowercase should also protect the snapshot."""
        det = _detector()
        snap = _make_snapshot(age_days=150, tags={"backup": "yes"})
        result = det.check_old_snapshot(snap, now=self._now)
        assert result is None

    def test_exactly_at_threshold_not_flagged(self):
        det = _detector()
        snap = _make_snapshot(age_days=90, tags={})
        result = det.check_old_snapshot(snap, now=self._now)
        assert result is None

    def test_missing_created_at_returns_none(self):
        """Missing created_at → cannot evaluate → skip."""
        det = _detector()
        result = det.check_old_snapshot({"snapshot_id": "snap-x", "tags": {}})
        assert result is None

    def test_naive_datetime_handled(self):
        """Naive (no tzinfo) datetime strings are accepted without error."""
        det = _detector()
        snap = {
            "snapshot_id": "snap-naive",
            "created_at": "2025-12-01T00:00:00",  # no +00:00
            "tags": {},
        }
        result = det.check_old_snapshot(snap, now=self._now)
        assert result is not None  # 133 days old


# ===========================================================================
# 5. Unused Load Balancer
# ===========================================================================

class TestCheckUnusedLoadBalancer:
    def test_low_traffic_flagged(self):
        """Load Balancer mit < 10 Requests/Tag → wird als unused erkannt."""
        det = _detector()
        result = det.check_unused_load_balancer(_make_lb(), requests_per_day=5.0)
        assert result is not None
        assert result.resource_type == "load_balancer"
        assert result.estimated_saving == pytest.approx(16.0)

    def test_high_traffic_not_flagged(self):
        """Load Balancer mit 100 Requests/Tag → wird NICHT als unused erkannt."""
        det = _detector()
        result = det.check_unused_load_balancer(_make_lb(), requests_per_day=100.0)
        assert result is None

    def test_exactly_at_threshold_not_flagged(self):
        det = _detector()
        result = det.check_unused_load_balancer(_make_lb(), requests_per_day=10.0)
        assert result is None

    def test_zero_requests_flagged(self):
        det = _detector()
        result = det.check_unused_load_balancer(_make_lb(), requests_per_day=0.0)
        assert result is not None


# ===========================================================================
# 6. S3 Lifecycle Policy
# ===========================================================================

class TestCheckS3Lifecycle:
    def test_bucket_without_lifecycle_flagged(self):
        """S3 Bucket ohne Lifecycle → wird erkannt."""
        det = _detector()
        result = det.check_s3_lifecycle(_make_bucket(has_lifecycle=False))
        assert result is not None
        assert result.resource_type == "s3"

    def test_bucket_with_lifecycle_not_flagged(self):
        """S3 Bucket mit Lifecycle → wird NICHT erkannt."""
        det = _detector()
        result = det.check_s3_lifecycle(_make_bucket(has_lifecycle=True))
        assert result is None

    def test_bucket_name_in_issue(self):
        result = _detector().check_s3_lifecycle(_make_bucket(name="my-important-bucket"))
        assert "my-important-bucket" in result.issue


# ===========================================================================
# 7. Cost Anomaly
# ===========================================================================

class TestCheckCostAnomaly:
    def test_large_increase_flagged(self):
        """25% Kostenanstieg → Anomalie wird erkannt."""
        det = _detector()
        result = det.check_cost_anomaly(
            current_week_cost=125.0, previous_week_cost=100.0
        )
        assert result is not None
        assert result.resource_type == "cost_anomaly"
        assert result.priority == "high"

    def test_small_increase_not_flagged(self):
        """5% Kostenanstieg → keine Anomalie."""
        det = _detector()
        result = det.check_cost_anomaly(
            current_week_cost=105.0, previous_week_cost=100.0
        )
        assert result is None

    def test_exactly_at_threshold_not_flagged(self):
        det = _detector()
        result = det.check_cost_anomaly(
            current_week_cost=120.0, previous_week_cost=100.0
        )
        assert result is None

    def test_zero_baseline_skipped(self):
        """When previous week was $0 we cannot compute a percentage — skip."""
        det = _detector()
        result = det.check_cost_anomaly(
            current_week_cost=50.0, previous_week_cost=0.0
        )
        assert result is None

    def test_cost_decrease_not_flagged(self):
        det = _detector()
        result = det.check_cost_anomaly(
            current_week_cost=80.0, previous_week_cost=100.0
        )
        assert result is None

    def test_percentage_in_issue_text(self):
        result = _detector().check_cost_anomaly(200.0, 100.0)
        assert "100.0%" in result.issue


# ===========================================================================
# 8. End-to-End Test
# ===========================================================================

class TestDetectWasteEndToEnd:
    """Full pipeline: mock provider → detect_waste() → Cosmos DB upsert."""

    def _build_provider(self):
        provider = AsyncMock()

        # list_resources: one idle EC2, one unassociated EIP, one RDS, one S3 bucket
        provider.list_resources.return_value = [
            _make_ec2(resource_id="i-idle"),
            _make_eip(associated=False),
            {
                "type": "rds",
                "resource_id": "db-small",
                "name": "db-small",
                "region": "eu-central-1",
                "status": "available",
                "details": {},
            },
            {
                "type": "s3",
                "resource_id": "bucket-no-lifecycle",
                "name": "bucket-no-lifecycle",
                "region": "eu-central-1",
                "status": "active",
                "details": {},
            },
        ]

        # EC2 metrics → idle
        provider.get_usage_metrics.return_value = _make_metrics(cpu_avg=2.0)

        # RDS metrics → oversized
        provider.get_rds_metrics = AsyncMock(
            return_value=_make_rds_metrics(cpu_avg=3.0, storage_used_percent=5.0)
        )

        # EBS snapshots → one old, one fresh
        provider.get_snapshots = AsyncMock(
            return_value=[
                _make_snapshot("snap-old", age_days=120),
                _make_snapshot("snap-new", age_days=10),
            ]
        )

        # Load balancers → one unused
        provider.get_load_balancers = AsyncMock(
            return_value=[
                (_make_lb("unused-alb"), 2.0),
                (_make_lb("busy-alb"), 500.0),
            ]
        )

        # S3 lifecycle info
        async def _lifecycle(bucket_name: str) -> dict:
            return {"name": bucket_name, "has_lifecycle_policy": False}

        provider.get_s3_lifecycle_info = _lifecycle

        # Cost data: 14 days → 25% spike in second week
        provider.get_cost_data.return_value = {
            "daily": [{"total": 10.0, "by_service": {}} for _ in range(7)]
            + [{"total": 12.5, "by_service": {}} for _ in range(7)],
        }

        return provider

    @pytest.mark.anyio
    async def test_all_rules_fire(self):
        """All 7 rule categories return at least one finding."""
        provider = self._build_provider()
        det = WasteDetector(provider=provider)
        findings = await det.detect_waste()

        types = {f.resource_type for f in findings}
        assert "ec2" in types
        assert "elastic_ip" in types
        assert "rds" in types
        assert "ebs_snapshot" in types
        assert "load_balancer" in types
        assert "s3" in types
        assert "cost_anomaly" in types

    @pytest.mark.anyio
    async def test_findings_are_recommendations(self):
        provider = self._build_provider()
        det = WasteDetector(provider=provider)
        findings = await det.detect_waste()
        for f in findings:
            assert isinstance(f, Recommendation)
            assert f.recommendation_id  # non-empty UUID
            assert f.status == "open"

    @pytest.mark.anyio
    async def test_cosmos_db_upsert_called_per_finding(self):
        """Each finding is persisted to Cosmos DB exactly once."""
        provider = self._build_provider()
        cosmos = MagicMock()
        det = WasteDetector(provider=provider, cosmos_client=cosmos, account_id="123456789")
        findings = await det.detect_waste()

        assert cosmos.upsert_recommendation.call_count == len(findings)

        # Every upserted doc must have account_id and id
        for call in cosmos.upsert_recommendation.call_args_list:
            doc = call.args[0]
            assert doc["account_id"] == "123456789"
            assert "id" in doc

    @pytest.mark.anyio
    async def test_no_cosmos_client_no_error(self):
        """Without a cosmos_client, detect_waste() still returns findings."""
        provider = self._build_provider()
        det = WasteDetector(provider=provider, cosmos_client=None)
        findings = await det.detect_waste()
        assert len(findings) > 0

    @pytest.mark.anyio
    async def test_empty_resources_returns_empty(self):
        """When the account has no resources, findings list is empty."""
        provider = AsyncMock()
        provider.list_resources.return_value = []
        provider.get_cost_data.return_value = {"daily": []}
        det = WasteDetector(provider=provider)
        findings = await det.detect_waste()
        assert findings == []
