"""Waste detection service — identifies idle and underutilised AWS resources.

Each rule method is *pure*: it accepts already-fetched data and returns a
Recommendation (or None). This keeps them fast and easy to unit-test without
any AWS credentials.

The async `detect_waste()` method orchestrates all data fetching and calls
every rule, then optionally persists the findings to Cosmos DB.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from app.models.recommendation import Recommendation


# ---------------------------------------------------------------------------
# Configurable thresholds
# ---------------------------------------------------------------------------

@dataclass
class WasteDetectorThresholds:
    """All rule thresholds in one place — pass a custom instance to override."""

    ec2_cpu_percent: float = 5.0        # avg CPU below this → idle EC2
    rds_cpu_percent: float = 10.0       # avg CPU below this  ┐ both must be
    rds_storage_percent: float = 20.0   # storage used below  ┘ true → oversized RDS
    snapshot_age_days: int = 90         # older than this (no Backup tag) → old snapshot
    lb_requests_per_day: float = 10.0   # below this → unused load balancer
    cost_anomaly_percent: float = 20.0  # week-over-week increase above this → anomaly


# ---------------------------------------------------------------------------
# WasteDetector
# ---------------------------------------------------------------------------

class WasteDetector:
    """Rule-based detection of wasted cloud resources.

    Args:
        provider:      A CloudProvider instance (must implement the base interface).
                       AWS-specific rules (EBS snapshots, load balancers, S3 lifecycle,
                       RDS metrics) are skipped when the provider lacks those methods.
        cosmos_client: Optional CosmosDBClient. When provided, findings are persisted
                       automatically after every `detect_waste()` run.
        thresholds:    Override default detection thresholds.
        account_id:    Written into every persisted recommendation so it can be
                       filtered per AWS account in Cosmos DB.
    """

    def __init__(
        self,
        provider,
        cosmos_client=None,
        thresholds: WasteDetectorThresholds | None = None,
        account_id: str | None = None,
    ):
        self.provider = provider
        self.cosmos_client = cosmos_client
        self.thresholds = thresholds or WasteDetectorThresholds()
        self.account_id = account_id

    # ------------------------------------------------------------------
    # Internal helper
    # ------------------------------------------------------------------

    def _make_recommendation(
        self,
        resource_id: str,
        resource_type: str,
        issue: str,
        recommendation: str,
        priority: str,
        estimated_saving: float,
        effort: str,
        action_steps: list[str],
    ) -> Recommendation:
        return Recommendation(
            recommendation_id=str(uuid.uuid4()),
            resource_id=resource_id,
            resource_type=resource_type,
            issue=issue,
            recommendation=recommendation,
            priority=priority,
            estimated_saving=estimated_saving,
            effort=effort,
            action_steps=action_steps,
        )

    # ------------------------------------------------------------------
    # Rule: Idle EC2
    # ------------------------------------------------------------------

    def check_idle_ec2(self, resource: dict, metrics: dict) -> Optional[Recommendation]:
        """Return a Recommendation when a running EC2 instance has low CPU.

        Args:
            resource: A resource dict as returned by ``provider.list_resources()``.
            metrics:  A metrics dict as returned by ``provider.get_usage_metrics()``.
        """
        if resource.get("status") != "running":
            return None

        cpu = metrics.get("cpu", {})
        datapoints = cpu.get("datapoints", 0)
        if datapoints == 0:
            return None  # no CloudWatch data — cannot judge

        cpu_avg = cpu.get("average", 0.0)
        if cpu_avg >= self.thresholds.ec2_cpu_percent:
            return None

        instance_id = resource["resource_id"]
        return self._make_recommendation(
            resource_id=instance_id,
            resource_type="ec2",
            issue=(
                f"Instance {instance_id} has been idle for 14 days "
                f"(avg CPU: {cpu_avg:.1f}%)"
            ),
            recommendation="Downsize or terminate this EC2 instance to eliminate waste.",
            priority="high",
            estimated_saving=0.0,  # AIEngine will calculate later
            effort="low",
            action_steps=[
                f"Verify instance {instance_id} is not needed.",
                "Take an AMI snapshot before any action.",
                "Stop the instance and monitor for 48 h, then terminate if safe.",
            ],
        )

    # ------------------------------------------------------------------
    # Rule: Oversized RDS
    # ------------------------------------------------------------------

    def check_oversized_rds(self, resource: dict, metrics: dict) -> Optional[Recommendation]:
        """Return a Recommendation when an RDS instance is significantly oversized.

        Args:
            resource: A resource dict (type == "rds").
            metrics:  Dict with keys ``cpu.average`` and ``storage_used_percent``.
        """
        cpu_avg = metrics.get("cpu", {}).get("average", 100.0)
        storage_pct = metrics.get("storage_used_percent", 100.0)

        oversized = (
            cpu_avg < self.thresholds.rds_cpu_percent
            and storage_pct < self.thresholds.rds_storage_percent
        )
        if not oversized:
            return None

        db_id = resource["resource_id"]
        return self._make_recommendation(
            resource_id=db_id,
            resource_type="rds",
            issue=(
                f"RDS instance {db_id} is oversized "
                f"(CPU: {cpu_avg:.1f}%, storage used: {storage_pct:.1f}%)"
            ),
            recommendation="Downgrade to a smaller RDS instance class.",
            priority="medium",
            estimated_saving=0.0,
            effort="medium",
            action_steps=[
                f"Review the usage pattern of {db_id} over the past 30 days.",
                "Create a manual RDS snapshot before modifying.",
                "Change the instance class to a smaller size (e.g. one tier down).",
                "Monitor performance for one week after the change.",
            ],
        )

    # ------------------------------------------------------------------
    # Rule: Unused Elastic IP
    # ------------------------------------------------------------------

    def check_unused_elastic_ip(self, resource: dict) -> Optional[Recommendation]:
        """Return a Recommendation for an Elastic IP not associated with any instance.

        Args:
            resource: A resource dict (type == "elastic_ip").
        """
        if resource.get("status") != "unassociated":
            return None

        public_ip = resource.get("details", {}).get("public_ip", resource["resource_id"])
        return self._make_recommendation(
            resource_id=resource["resource_id"],
            resource_type="elastic_ip",
            issue=f"Elastic IP {public_ip} is not associated with any instance.",
            recommendation="Release this Elastic IP to avoid the idle-IP charge (~$3.60/month).",
            priority="low",
            estimated_saving=3.60,
            effort="low",
            action_steps=[
                f"Confirm {public_ip} is no longer needed.",
                "Release the Elastic IP via the EC2 console or AWS CLI.",
            ],
        )

    # ------------------------------------------------------------------
    # Rule: Old EBS Snapshot
    # ------------------------------------------------------------------

    def check_old_snapshot(
        self,
        snapshot: dict,
        now: datetime | None = None,
    ) -> Optional[Recommendation]:
        """Return a Recommendation for an EBS snapshot that is old and untagged.

        The snapshot is flagged only when **both** conditions are met:
        - Age > ``thresholds.snapshot_age_days``
        - No ``Backup`` (case-insensitive) tag present

        Args:
            snapshot: Dict with ``snapshot_id``, ``created_at`` (ISO string or
                      datetime), and optional ``tags`` dict.
            now:      Override "today" — useful in tests.
        """
        if now is None:
            now = datetime.now(timezone.utc)

        created_at = snapshot.get("created_at")
        if created_at is None:
            return None

        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        age_days = (now - created_at).days

        tags: dict = snapshot.get("tags", {})
        has_backup_tag = any(k.lower() == "backup" for k in tags)

        if age_days <= self.thresholds.snapshot_age_days or has_backup_tag:
            return None

        snap_id = snapshot["snapshot_id"]
        return self._make_recommendation(
            resource_id=snap_id,
            resource_type="ebs_snapshot",
            issue=f"EBS snapshot {snap_id} is {age_days} days old and has no Backup tag.",
            recommendation="Delete or archive this snapshot to reduce EBS snapshot storage costs.",
            priority="low",
            estimated_saving=0.0,
            effort="low",
            action_steps=[
                f"Review snapshot {snap_id} to confirm it is no longer needed.",
                "Add a 'Backup' tag if the snapshot must be retained.",
                "Otherwise, delete the snapshot.",
            ],
        )

    # ------------------------------------------------------------------
    # Rule: Unused Load Balancer
    # ------------------------------------------------------------------

    def check_unused_load_balancer(
        self, lb: dict, requests_per_day: float
    ) -> Optional[Recommendation]:
        """Return a Recommendation for a load balancer with very low traffic.

        Args:
            lb:               Dict with at least ``lb_arn`` and optionally ``name``.
            requests_per_day: Average daily request count (from CloudWatch).
        """
        if requests_per_day >= self.thresholds.lb_requests_per_day:
            return None

        lb_arn = lb["lb_arn"]
        lb_name = lb.get("name", lb_arn)
        return self._make_recommendation(
            resource_id=lb_arn,
            resource_type="load_balancer",
            issue=(
                f"Load balancer '{lb_name}' has only {requests_per_day:.1f} "
                "requests/day — likely unused."
            ),
            recommendation="Delete this load balancer to save ~$16/month.",
            priority="medium",
            estimated_saving=16.0,
            effort="low",
            action_steps=[
                f"Confirm that '{lb_name}' is no longer serving traffic.",
                "Update or remove any DNS records pointing to this load balancer.",
                "Delete the load balancer.",
            ],
        )

    # ------------------------------------------------------------------
    # Rule: S3 Bucket without Lifecycle Policy
    # ------------------------------------------------------------------

    def check_s3_lifecycle(self, bucket: dict) -> Optional[Recommendation]:
        """Return a Recommendation for an S3 bucket without a lifecycle policy.

        Args:
            bucket: Dict with ``name`` and ``has_lifecycle_policy`` (bool).
        """
        if bucket.get("has_lifecycle_policy", False):
            return None

        name = bucket["name"]
        return self._make_recommendation(
            resource_id=name,
            resource_type="s3",
            issue=f"S3 bucket '{name}' has no lifecycle / Intelligent-Tiering policy.",
            recommendation=(
                "Add an S3 Intelligent-Tiering lifecycle rule to automatically "
                "move infrequently accessed objects to cheaper storage tiers."
            ),
            priority="low",
            estimated_saving=0.0,
            effort="low",
            action_steps=[
                f"Open bucket '{name}' in the S3 console.",
                "Navigate to Management → Lifecycle rules.",
                "Create a rule to transition objects to Intelligent-Tiering after 30 days.",
            ],
        )

    # ------------------------------------------------------------------
    # Rule: Cost Anomaly
    # ------------------------------------------------------------------

    def check_cost_anomaly(
        self, current_week_cost: float, previous_week_cost: float
    ) -> Optional[Recommendation]:
        """Return a Recommendation when weekly spend increases sharply.

        Args:
            current_week_cost:  Total cost (USD) for the most recent 7 days.
            previous_week_cost: Total cost (USD) for the 7 days before that.
        """
        if previous_week_cost == 0:
            return None  # no baseline → cannot calculate percentage

        increase_pct = (
            (current_week_cost - previous_week_cost) / previous_week_cost * 100
        )
        if increase_pct <= self.thresholds.cost_anomaly_percent:
            return None

        return self._make_recommendation(
            resource_id="account",
            resource_type="cost_anomaly",
            issue=(
                f"AWS spend increased {increase_pct:.1f}% week-over-week "
                f"(${current_week_cost:.2f} vs ${previous_week_cost:.2f} last week)."
            ),
            recommendation="Investigate the cost spike and identify the responsible service.",
            priority="high",
            estimated_saving=0.0,
            effort="medium",
            action_steps=[
                "Open AWS Cost Explorer and compare the last two weeks.",
                "Identify the service with the largest cost increase.",
                "Review recent deployments or auto-scaling events.",
                "Set up an AWS Budget alert to be notified of future spikes.",
            ],
        )

    # ------------------------------------------------------------------
    # Orchestrator
    # ------------------------------------------------------------------

    async def detect_waste(self) -> list[Recommendation]:
        """Run all waste-detection rules and return a list of Recommendations.

        Data fetching order:
        1. list_resources()            — EC2, EIP, RDS, S3
        2. get_usage_metrics()         — per-EC2 CloudWatch metrics
        3. get_rds_metrics()           — RDS CloudWatch (if provider supports it)
        4. get_snapshots()             — EBS snapshots (if provider supports it)
        5. get_load_balancers()        — LBs + daily request counts (if supported)
        6. get_s3_lifecycle_info()     — S3 lifecycle status per bucket (if supported)
        7. get_cost_data(days=14)      — for week-over-week anomaly detection

        Findings are persisted to Cosmos DB when a ``cosmos_client`` was supplied.
        """
        findings: list[Recommendation] = []

        # ── 1. Resources ────────────────────────────────────────────
        resources = await self.provider.list_resources()

        # ── 2. Idle EC2 ─────────────────────────────────────────────
        for res in resources:
            if res["type"] != "ec2":
                continue
            metrics = await self.provider.get_usage_metrics(res["resource_id"])
            finding = self.check_idle_ec2(res, metrics)
            if finding:
                findings.append(finding)

        # ── 3. Unused Elastic IPs ────────────────────────────────────
        for res in resources:
            if res["type"] == "elastic_ip":
                finding = self.check_unused_elastic_ip(res)
                if finding:
                    findings.append(finding)

        # ── 4. Oversized RDS (AWS-specific) ──────────────────────────
        if hasattr(self.provider, "get_rds_metrics"):
            for res in resources:
                if res["type"] != "rds":
                    continue
                metrics = await self.provider.get_rds_metrics(res["resource_id"])
                finding = self.check_oversized_rds(res, metrics)
                if finding:
                    findings.append(finding)

        # ── 5. Old EBS Snapshots (AWS-specific) ──────────────────────
        if hasattr(self.provider, "get_snapshots"):
            for snap in await self.provider.get_snapshots():
                finding = self.check_old_snapshot(snap)
                if finding:
                    findings.append(finding)

        # ── 6. Unused Load Balancers (AWS-specific) ───────────────────
        if hasattr(self.provider, "get_load_balancers"):
            for lb, req_per_day in await self.provider.get_load_balancers():
                finding = self.check_unused_load_balancer(lb, req_per_day)
                if finding:
                    findings.append(finding)

        # ── 7. S3 Lifecycle Policies (AWS-specific) ───────────────────
        if hasattr(self.provider, "get_s3_lifecycle_info"):
            for res in resources:
                if res["type"] != "s3":
                    continue
                bucket_info = await self.provider.get_s3_lifecycle_info(
                    res["resource_id"]
                )
                finding = self.check_s3_lifecycle(bucket_info)
                if finding:
                    findings.append(finding)

        # ── 8. Cost Anomaly ───────────────────────────────────────────
        cost_data = await self.provider.get_cost_data(days=14)
        daily = cost_data.get("daily", [])
        if len(daily) >= 14:
            prev_week = sum(d["total"] for d in daily[:7])
            curr_week = sum(d["total"] for d in daily[7:])
            finding = self.check_cost_anomaly(curr_week, prev_week)
            if finding:
                findings.append(finding)

        # ── 9. Persist to Cosmos DB ───────────────────────────────────
        if self.cosmos_client and findings:
            for rec in findings:
                doc = rec.model_dump()
                doc["id"] = rec.recommendation_id
                if self.account_id:
                    doc["account_id"] = self.account_id
                self.cosmos_client.upsert_recommendation(doc)

        return findings
