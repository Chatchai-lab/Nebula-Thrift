"""AWS cloud provider implementation."""
import asyncio
from datetime import datetime, timedelta, timezone

import boto3

from .base import CloudProvider


class AWSProvider(CloudProvider):
    """AWS implementation using boto3 for Cost Explorer, CloudWatch, EC2, RDS, S3.

    boto3 is synchronous, so every SDK call is wrapped in `asyncio.to_thread`
    to avoid blocking FastAPI's event loop.
    """

    def __init__(
        self,
        profile_name: str | None = None,
        region_name: str = "eu-central-1",
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
    ):
        self.session = boto3.Session(
            profile_name=profile_name,
            region_name=region_name,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )
        self.sts = self.session.client("sts")
        self.ce = self.session.client("ce", region_name="us-east-1")

    # ------------------------------------------------------------------
    # validate_connection
    # ------------------------------------------------------------------

    async def validate_connection(self) -> dict:
        """Call STS GetCallerIdentity to verify the credentials work.

        Returns a dict with `account`, `user_id`, and `arn`.
        """
        identity = await asyncio.to_thread(self.sts.get_caller_identity)
        return {
            "account": identity["Account"],
            "user_id": identity["UserId"],
            "arn": identity["Arn"],
        }

    # ------------------------------------------------------------------
    # get_cost_data
    # ------------------------------------------------------------------

    async def get_cost_data(self, days: int = 30) -> dict:
        """Fetch cost data from AWS Cost Explorer API.

        Returns a dict with:
          - period: {start, end}
          - currency: str
          - total: float
          - by_service: [{service, amount}]
          - daily: [{date, total, by_service: {service: amount}}]
        """
        now = datetime.now(timezone.utc)
        start = (now - timedelta(days=days)).strftime("%Y-%m-%d")
        end = now.strftime("%Y-%m-%d")

        # --- Total by service (one call) ---
        try:
            by_service_raw = await asyncio.to_thread(
                self.ce.get_cost_and_usage,
                TimePeriod={"Start": start, "End": end},
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )
        except self.ce.exceptions.DataUnavailableException:
            return {
                "period": {"start": start, "end": end},
                "currency": "USD",
                "total": 0.0,
                "by_service": [],
                "daily": [],
                "warning": "Cost Explorer data not available yet. "
                           "Enable it in the AWS Console and wait ~24h.",
            }

        by_service = []
        total = 0.0
        currency = "USD"
        for group in by_service_raw.get("ResultsByTime", []):
            for item in group.get("Groups", []):
                service_name = item["Keys"][0]
                amount = float(item["Metrics"]["UnblendedCost"]["Amount"])
                unit = item["Metrics"]["UnblendedCost"]["Unit"]
                if amount == 0:
                    continue
                currency = unit
                by_service.append({"service": service_name, "amount": round(amount, 4)})
                total += amount

        # Merge across months and sort descending
        merged: dict[str, float] = {}
        for entry in by_service:
            merged[entry["service"]] = merged.get(entry["service"], 0) + entry["amount"]
        by_service = sorted(
            [{"service": k, "amount": round(v, 4)} for k, v in merged.items()],
            key=lambda x: x["amount"],
            reverse=True,
        )

        # --- Daily breakdown (second call) ---
        daily_raw = await asyncio.to_thread(
            self.ce.get_cost_and_usage,
            TimePeriod={"Start": start, "End": end},
            Granularity="DAILY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )

        daily = []
        for period in daily_raw.get("ResultsByTime", []):
            date = period["TimePeriod"]["Start"]
            day_total = 0.0
            day_services: dict[str, float] = {}
            for item in period.get("Groups", []):
                service_name = item["Keys"][0]
                amount = float(item["Metrics"]["UnblendedCost"]["Amount"])
                if amount == 0:
                    continue
                day_services[service_name] = round(amount, 4)
                day_total += amount
            daily.append({
                "date": date,
                "total": round(day_total, 4),
                "by_service": day_services,
            })

        return {
            "period": {"start": start, "end": end},
            "currency": currency,
            "total": round(total, 4),
            "by_service": by_service,
            "daily": daily,
        }

    # ------------------------------------------------------------------
    # get_usage_metrics
    # ------------------------------------------------------------------

    async def get_usage_metrics(self, resource_id: str) -> dict:
        """Fetch CloudWatch CPU and network metrics for an EC2 instance.

        Returns a dict with:
          - resource_id: str
          - period_days: int
          - cpu: {average, max, datapoints}
          - network_in: {average, max, datapoints}  (bytes)
          - network_out: {average, max, datapoints} (bytes)
        """
        cw = self.session.client("cloudwatch", region_name=self.session.region_name)
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=14)

        async def _get_metric(metric_name: str, namespace: str = "AWS/EC2") -> dict:
            response = await asyncio.to_thread(
                cw.get_metric_statistics,
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=[{"Name": "InstanceId", "Value": resource_id}],
                StartTime=start,
                EndTime=now,
                Period=3600,  # 1-hour granularity
                Statistics=["Average", "Maximum"],
            )
            datapoints = response.get("Datapoints", [])
            if not datapoints:
                return {"average": 0.0, "max": 0.0, "datapoints": 0}
            avg = sum(dp["Average"] for dp in datapoints) / len(datapoints)
            mx = max(dp["Maximum"] for dp in datapoints)
            return {
                "average": round(avg, 2),
                "max": round(mx, 2),
                "datapoints": len(datapoints),
            }

        cpu, net_in, net_out = await asyncio.gather(
            _get_metric("CPUUtilization"),
            _get_metric("NetworkIn"),
            _get_metric("NetworkOut"),
        )

        return {
            "resource_id": resource_id,
            "period_days": 14,
            "cpu": cpu,
            "network_in": net_in,
            "network_out": net_out,
        }

    # ------------------------------------------------------------------
    # list_resources
    # ------------------------------------------------------------------

    async def list_resources(self) -> list:
        """List EC2 instances, RDS databases, Elastic IPs, and S3 buckets.

        Returns a flat list of resource dicts, each with:
          type, resource_id, name, region, status, details
        """
        ec2 = self.session.client("ec2", region_name=self.session.region_name)
        rds = self.session.client("rds", region_name=self.session.region_name)
        s3 = self.session.client("s3")

        resources: list[dict] = []

        # --- EC2 Instances ---
        ec2_response = await asyncio.to_thread(
            ec2.describe_instances,
            Filters=[{"Name": "instance-state-name", "Values": ["running", "stopped"]}],
        )
        for reservation in ec2_response.get("Reservations", []):
            for inst in reservation.get("Instances", []):
                name = ""
                for tag in inst.get("Tags", []):
                    if tag["Key"] == "Name":
                        name = tag["Value"]
                        break
                resources.append({
                    "type": "ec2",
                    "resource_id": inst["InstanceId"],
                    "name": name,
                    "region": self.session.region_name,
                    "status": inst["State"]["Name"],
                    "details": {
                        "instance_type": inst["InstanceType"],
                        "launch_time": inst["LaunchTime"].isoformat(),
                    },
                })

        # --- Elastic IPs ---
        eip_response = await asyncio.to_thread(ec2.describe_addresses)
        for eip in eip_response.get("Addresses", []):
            resources.append({
                "type": "elastic_ip",
                "resource_id": eip.get("AllocationId", ""),
                "name": eip.get("PublicIp", ""),
                "region": self.session.region_name,
                "status": "associated" if eip.get("InstanceId") else "unassociated",
                "details": {
                    "public_ip": eip.get("PublicIp", ""),
                    "instance_id": eip.get("InstanceId"),
                },
            })

        # --- RDS Instances ---
        rds_response = await asyncio.to_thread(rds.describe_db_instances)
        for db in rds_response.get("DBInstances", []):
            resources.append({
                "type": "rds",
                "resource_id": db["DBInstanceIdentifier"],
                "name": db["DBInstanceIdentifier"],
                "region": self.session.region_name,
                "status": db["DBInstanceStatus"],
                "details": {
                    "engine": db["Engine"],
                    "instance_class": db["DBInstanceClass"],
                    "storage_gb": db.get("AllocatedStorage", 0),
                },
            })

        # --- S3 Buckets ---
        buckets_response = await asyncio.to_thread(s3.list_buckets)
        for bucket in buckets_response.get("Buckets", []):
            bucket_name = bucket["Name"]
            try:
                loc = await asyncio.to_thread(
                    s3.get_bucket_location,
                    Bucket=bucket_name,
                )
                region = loc["LocationConstraint"] or "us-east-1"
            except Exception:  # noqa: BLE001
                region = "unknown"
            resources.append({
                "type": "s3",
                "resource_id": bucket_name,
                "name": bucket_name,
                "region": region,
                "status": "active",
                "details": {
                    "created": bucket["CreationDate"].isoformat(),
                },
            })

        return resources
