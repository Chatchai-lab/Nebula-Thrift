"""Azure Functions for Nebula Thrift.

All functions live in this single file (Azure Functions V2 Python model).

- AIRecommender:   HTTP POST  /api/recommend     — enriches waste reports via AI
- daily_collector: Timer      08:00 UTC daily     — collects AWS data
- api:             HTTP       /api/{*route}       — serves the FastAPI backend
"""
import json
import logging
import sys
from datetime import date
from pathlib import Path

import azure.functions as func

# Ensure the backend app package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

app = func.FunctionApp()


# ── Function 1: AI Recommender (HTTP Trigger) ─────────────────────

@app.function_name(name="AIRecommender")
@app.route(route="recommend", methods=["POST"])
async def ai_recommender(req: func.HttpRequest) -> func.HttpResponse:
    """Enhance a raw waste report with AI and persist to Cosmos DB."""
    logging.info("AIRecommender triggered")

    try:
        from app.services.ai_engine import AIEngine
        from app.services.cosmos_service import CosmosService

        raw_report = req.get_json()
        if not raw_report:
            return func.HttpResponse(
                "Please pass a waste report in the request body",
                status_code=400,
            )

        ai_engine = AIEngine()
        cosmos_db = CosmosService()

        logging.info("Enhancing report for resource: %s", raw_report.get("resource_id"))
        enriched_rec = await ai_engine.enhance_recommendation(raw_report)

        await cosmos_db.save_recommendation(enriched_rec)

        return func.HttpResponse(
            json.dumps({"status": "success", "id": enriched_rec.recommendation_id}),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error("Error in AIRecommender: %s", e)
        return func.HttpResponse(f"Error: {e}", status_code=500)


# ── Function 2: Daily Collector (Timer Trigger) ───────────────────

@app.timer_trigger(
    schedule="0 0 8 * * *",  # Every day at 08:00 UTC
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

        accounts = blob.list_accounts()
        if not accounts:
            logging.warning("No accounts registered — skipping collection")
            return

        for account in accounts:
            account_id = account["account_id"]
            logging.info("Collecting data for account %s", account_id)

            try:
                provider = create_aws_provider(account_id)

                cost_data = provider.get_cost_data(days=30)
                resources = provider.list_resources()

                snapshot = {
                    "account_id": account_id,
                    "snapshot_date": date.today().isoformat(),
                    "costs": cost_data,
                    "resources": resources,
                }

                blob.upload_snapshot(date.today(), snapshot, account_id)
                cosmos.save_snapshot(date.today().isoformat(), snapshot, account_id)
                logging.info("Snapshot saved for account %s", account_id)

            except Exception as e:
                logging.error("Failed to collect data for %s: %s", account_id, e)

    except Exception as e:
        logging.error("daily_collector failed: %s", e)


# ── Function 3: API (HTTP Trigger → FastAPI) ──────────────────────

@app.route(
    route="{*route}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    auth_level=func.AuthLevel.ANONYMOUS,
)
async def api(req: func.HttpRequest) -> func.HttpResponse:
    """Serve the FastAPI backend via Azure Functions HTTP trigger."""
    from app.main import app as fastapi_app
    from azure.functions import AsgiMiddleware

    return await AsgiMiddleware(fastapi_app).handle_async(req)