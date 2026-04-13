"""Azure Functions for Nebula Thrift.

- daily_collector: Timer trigger (08:00 UTC daily) — collects AWS data
- api: HTTP trigger — serves the FastAPI backend
"""
import json
import logging
import sys
from datetime import date
from pathlib import Path

import azure.functions as func

# Add parent directory to path so we can import the backend app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

app = func.FunctionApp()


# ── Function 1: Daily Collector (Timer Trigger) ─────────────────

@app.timer_trigger(
    schedule="0 0 8 * * *",       # Every day at 08:00 UTC
    arg_name="timer",
    run_on_startup=False,
)
def daily_collector(timer: func.TimerRequest) -> None:
    """Collect AWS cost data, resources and metrics, then store in Blob + Cosmos DB."""
    logging.info("daily_collector triggered")

    try:
        from app.config import create_aws_provider
        from app.storage.blob_client import BlobStorageClient
        from app.storage.cosmos_client import CosmosDBClient

        blob = BlobStorageClient()
        cosmos = CosmosDBClient()

        # Load all registered accounts
        accounts = blob.list_accounts()
        if not accounts:
            logging.warning("No accounts registered — skipping collection")
            return

        for account in accounts:
            account_id = account["account_id"]
            logging.info("Collecting data for account %s", account_id)

            try:
                provider = create_aws_provider(account_id)

                # Gather data
                cost_data = provider.get_cost_data(days=30)
                resources = provider.list_resources()

                snapshot = {
                    "account_id": account_id,
                    "snapshot_date": date.today().isoformat(),
                    "costs": cost_data,
                    "resources": resources,
                }

                # Store in Blob Storage (archive)
                blob.upload_snapshot(date.today(), snapshot, account_id)

                # Store in Cosmos DB (queryable)
                cosmos.save_snapshot(date.today().isoformat(), snapshot, account_id)

                logging.info("Snapshot saved for account %s", account_id)

            except Exception as e:
                logging.error("Failed to collect data for %s: %s", account_id, e)

    except Exception as e:
        logging.error("daily_collector failed: %s", e)


# ── Function 2: API (HTTP Trigger → FastAPI) ────────────────────

@app.route(route="{*route}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
async def api(req: func.HttpRequest) -> func.HttpResponse:
    """Serve the FastAPI backend via Azure Functions HTTP trigger."""
    from app.main import app as fastapi_app
    from azure.functions import AsgiMiddleware

    return await AsgiMiddleware(fastapi_app).handle_async(req)
