#!/usr/bin/env python3
"""
End-to-End Test: AWS Cost Data → Blob Storage Snapshot

This script demonstrates the complete flow:
1. Fetch AWS cost data using AWSProvider.get_cost_data()
2. Normalize the data
3. Upload to Azure Blob Storage as a JSON snapshot
4. Download and verify the snapshot

Prerequisites:
- AWS credentials configured (via ~/.aws/credentials or environment variables)
- Azure CLI logged in (`az login`)
- backend/app/ must be in PYTHONPATH

Usage:
    python scripts/test_blob_snapshot.py [--profile PROFILE] [--days DAYS] [--account-id ACCOUNT_ID]

Examples:
    # Use default AWS profile, last 7 days
    python scripts/test_blob_snapshot.py --days 7

    # Use specific AWS profile
    python scripts/test_blob_snapshot.py --profile nebula-thrift-dev --days 30

    # Upload under a specific account ID (for multi-account support)
    python scripts/test_blob_snapshot.py --account-id abc12345
"""

import asyncio
import json
import sys
from argparse import ArgumentParser
from datetime import date
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.providers.aws import AWSProvider
from app.storage.blob_client import BlobStorageClient


async def main():
    parser = ArgumentParser(description="Test AWS → Blob Storage snapshot flow")
    parser.add_argument("--profile", default=None, help="AWS profile name")
    parser.add_argument("--days", type=int, default=7, help="Days of cost data (default: 7)")
    parser.add_argument("--account-id", default=None, help="Account ID for Blob Storage namespacing")
    args = parser.parse_args()

    print("=" * 70)
    print("END-TO-END TEST: AWS Cost Data → Azure Blob Storage Snapshot")
    print("=" * 70)

    # ========================================================================
    # Step 1: Initialize AWS Provider
    # ========================================================================
    print(f"\n[1/5] Initializing AWS Provider (profile={args.profile or 'default'})...")
    try:
        aws_provider = AWSProvider(profile_name=args.profile)
        identity = await aws_provider.validate_connection()
        print(f"✓ AWS Connection validated")
        print(f"  Account: {identity['account']}")
        print(f"  User: {identity['user_id']}")
    except Exception as e:
        print(f"✗ Failed to connect to AWS: {e}")
        return False

    # ========================================================================
    # Step 2: Fetch Cost Data
    # ========================================================================
    print(f"\n[2/5] Fetching AWS cost data (last {args.days} days)...")
    try:
        cost_data = await aws_provider.get_cost_data(days=args.days)
        print(f"✓ Cost data retrieved")
        print(f"  Period: {cost_data['period']['start']} to {cost_data['period']['end']}")
        print(f"  Total spend: {cost_data['currency']} {cost_data['total']:.2f}")
        print(f"  Services: {len(cost_data['by_service'])} tracked")
        if cost_data['by_service']:
            top_service = cost_data['by_service'][0]
            print(f"  Top service: {top_service['service']} ({top_service['amount']:.2f})")
    except Exception as e:
        print(f"✗ Failed to fetch cost data: {e}")
        return False

    # ========================================================================
    # Step 3: Create snapshot payload (normalize)
    # ========================================================================
    print(f"\n[3/5] Creating snapshot payload...")
    try:
        from datetime import datetime

        snapshot_payload = {
            "date": str(date.today()),
            "fetched_at": datetime.now().isoformat(),
            "days": args.days,
            "cost_data": cost_data,
        }
        payload_size = len(json.dumps(snapshot_payload))
        print(f"✓ Snapshot created")
        print(f"  Size: {payload_size:,} bytes")
        print(f"  Keys: {list(snapshot_payload.keys())}")
    except Exception as e:
        print(f"✗ Failed to create snapshot: {e}")
        return False

    # ========================================================================
    # Step 4: Upload to Blob Storage
    # ========================================================================
    print(f"\n[4/5] Uploading to Azure Blob Storage...")
    try:
        blob_client = BlobStorageClient()
        blob_client.upload_snapshot(date.today(), snapshot_payload, account_id=args.account_id)

        if args.account_id:
            blob_path = f"{args.account_id}/{date.today().isoformat()}.json"
        else:
            blob_path = f"{date.today().isoformat()}.json"

        print(f"✓ Snapshot uploaded")
        print(f"  Container: snapshots")
        print(f"  Path: {blob_path}")
    except Exception as e:
        print(f"✗ Failed to upload snapshot: {e}")
        return False

    # ========================================================================
    # Step 5: Download and verify
    # ========================================================================
    print(f"\n[5/5] Downloading and verifying snapshot...")
    try:
        downloaded_data = blob_client.download_snapshot(date.today(), account_id=args.account_id)

        # Verify structure
        required_keys = {"date", "fetched_at", "days", "cost_data"}
        if not required_keys.issubset(downloaded_data.keys()):
            raise ValueError(f"Missing keys in downloaded data. Expected {required_keys}, got {downloaded_data.keys()}")

        # Verify cost_data structure
        cost_keys = {"period", "currency", "total", "by_service", "daily"}
        if not cost_keys.issubset(downloaded_data["cost_data"].keys()):
            raise ValueError(f"Missing cost_data keys")

        # Verify total matches
        if downloaded_data["cost_data"]["total"] != snapshot_payload["cost_data"]["total"]:
            raise ValueError(f"Total mismatch: {downloaded_data['cost_data']['total']} != {snapshot_payload['cost_data']['total']}")

        print(f"✓ Snapshot verified")
        print(f"  Date: {downloaded_data['date']}")
        print(f"  Total (match): {downloaded_data['cost_data']['total']:.2f}")
        print(f"  Services (match): {len(downloaded_data['cost_data']['by_service'])}")
        print(f"  Daily entries: {len(downloaded_data['cost_data']['daily'])}")
    except Exception as e:
        print(f"✗ Failed to verify snapshot: {e}")
        return False

    # ========================================================================
    # Summary
    # ========================================================================
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)
    print(f"\nSnapshot Summary:")
    print(f"  Account ID: {args.account_id or '(default/legacy)'}")
    print(f"  Date: {date.today()}")
    print(f"  Total Cost: {snapshot_payload['cost_data']['currency']} {snapshot_payload['cost_data']['total']:.2f}")
    print(f"  Services tracked: {len(snapshot_payload['cost_data']['by_service'])}")
    print(f"  Days of data: {args.days}")
    print(f"\nBlob Storage Location:")
    print(f"  Account: nebulathriftdata")
    print(f"  Container: snapshots")
    print(f"  Path: {blob_path}")
    print(f"\nYou can view this file in the Azure Portal:")
    print(f"  https://portal.azure.com → Storage Accounts → nebulathriftdata → Containers → snapshots")

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
