"""Daily data collection Lambda — triggered by EventBridge at 08:00 UTC."""


def lambda_handler(event, context):
    """Collect cost data and usage metrics from AWS."""
    # 1. Initialize AWSProvider
    # 2. Fetch cost data (last 30 days)
    # 3. Fetch usage metrics for all resources
    # 4. Store normalized data in S3
    # 5. Return summary
    return {"statusCode": 200, "body": "Collection complete"}
