"""Smoke test for the AWSProvider.

Run from the repo root:

    cd backend
    python -m scripts.test_provider

Expects the AWS profile `nebula-thrift` to exist in `~/.aws/credentials`.
Override with the env var AWS_PROFILE if needed.
"""
import asyncio
import os
import sys

from app.providers.aws import AWSProvider
from app.models import CostData, Resource, UsageMetrics


async def main() -> int:
    profile = os.getenv("AWS_PROFILE", "nebula-thrift")
    region = os.getenv("AWS_REGION", "eu-central-1")

    print(f"→ Using profile '{profile}' in region '{region}'")
    provider = AWSProvider(profile_name=profile, region_name=region)

    try:
        identity = await provider.validate_connection()
    except Exception as exc:  # noqa: BLE001 — surface anything to the user
        print(f"✗ validate_connection failed: {exc}")
        return 1

    print("✓ Connection valid")
    print(f"  Account: {identity['account']}")
    print(f"  User ID: {identity['user_id']}")
    print(f"  ARN:     {identity['arn']}")

    # --- get_cost_data ---
    print()
    print("→ Fetching cost data (last 30 days)...")
    try:
        costs = await provider.get_cost_data(days=30)
    except Exception as exc:  # noqa: BLE001
        print(f"✗ get_cost_data failed: {exc}")
        return 1

    cost_model = CostData(**costs)
    if cost_model.warning:
        print(f"⚠ {cost_model.warning}")
    else:
        print(f"✓ Cost data retrieved ({cost_model.period['start']} → {cost_model.period['end']})")
        print(f"  Total: {cost_model.total} {cost_model.currency}")
        print(f"  Services:")
        for svc in cost_model.by_service:
            print(f"    {svc.service:40s} {svc.amount:>10.4f} {cost_model.currency}")
        print(f"  Daily data points: {len(cost_model.daily)}")
    print("  ✓ Pydantic CostData validated")

    # --- list_resources ---
    print()
    print("→ Listing resources...")
    try:
        resources = await provider.list_resources()
    except Exception as exc:  # noqa: BLE001
        print(f"✗ list_resources failed: {exc}")
        return 1

    resource_models = [Resource(**r) for r in resources]
    print(f"✓ Found {len(resource_models)} resource(s)")
    for res in resource_models:
        print(f"  [{res.type:10s}] {res.resource_id:30s} {res.status:15s} {res.name}")
    print(f"  ✓ Pydantic Resource validated ({len(resource_models)} items)")

    # --- get_usage_metrics (only if EC2 instances exist) ---
    ec2_instances = [r for r in resource_models if r.type == "ec2"]
    if ec2_instances:
        instance_id = ec2_instances[0].resource_id
        print()
        print(f"→ Fetching usage metrics for {instance_id}...")
        try:
            metrics = await provider.get_usage_metrics(instance_id)
        except Exception as exc:  # noqa: BLE001
            print(f"✗ get_usage_metrics failed: {exc}")
            return 1

        metrics_model = UsageMetrics(**metrics)
        print(f"✓ Metrics retrieved (last {metrics_model.period_days} days)")
        print(f"  CPU avg: {metrics_model.cpu.average}%  max: {metrics_model.cpu.max}%  ({metrics_model.cpu.datapoints} datapoints)")
        print(f"  Net In avg:  {metrics_model.network_in.average} bytes")
        print(f"  Net Out avg: {metrics_model.network_out.average} bytes")
        print("  ✓ Pydantic UsageMetrics validated")
    else:
        print()
        print("⚠ No EC2 instances found — skipping get_usage_metrics()")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
