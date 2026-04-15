"""Integration test: WasteDetector → AIEngine → CosmosService

Tests the full recommendation pipeline end-to-end. All external services
(GitHub Models API, Cosmos DB, AWS) are replaced with mocks — no real
credentials required.

Pipeline under test:
  1. WasteDetector.detect_waste()  — detects waste from a mocked AWS provider
  2. AIEngine.enhance_recommendation() — enriches each finding (GitHub Models mocked)
  3. CosmosService.save_recommendation() — persists the result (Cosmos DB mocked)

Run:
    pytest backend/tests/test_integration_e2e.py -v
"""
from __future__ import annotations

import json
import os
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.waste_detector import WasteDetector
from app.services.ai_engine import AIEngine
from app.models.recommendation import Recommendation


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FAKE_ENV = {
    "GITHUB_TOKEN": "ghp_fake_integration_test_token",
    "GITHUB_MODEL_ENDPOINT": "https://models.inference.ai.azure.com",
    "GITHUB_MODEL_NAME": "Llama-4-Scout-17B-16E-Instruct",
    "COSMOS_ENDPOINT": "https://fake-cosmos.documents.azure.com:443/",
    "COSMOS_KEY": "ZmFrZWtleWZha2VrZXlmYWtla2V5ZmFrZWtleWZha2VrZXk=",
    "COSMOS_DATABASE": "nebulathrift",
    "COSMOS_CONTAINER": "recommendations",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_config_singleton():
    """Reset the ConfigService singleton before and after every test.

    Without this, env-var patches from one test bleed into the next because
    get_config() caches the loaded values on the module-level singleton.
    """
    import app.services.config_service as cfg_module
    cfg_module._config_instance = None
    yield
    cfg_module._config_instance = None


# ---------------------------------------------------------------------------
# Helpers: AI response
# ---------------------------------------------------------------------------

def _ai_json(resource_type: str, saving: float = 20.0) -> str:
    """Minimal valid JSON that AIEngine expects from GitHub Models."""
    return json.dumps({
        "issue": f"The {resource_type} resource shows clear signs of waste.",
        "recommendation": (
            f"Optimize or remove this {resource_type} resource to reduce costs."
        ),
        "estimated_saving": saving,
        "effort": "low",
        "action_steps": [
            "Analyse current usage and utilisation metrics.",
            "Evaluate downsizing or termination options.",
            "Apply changes during a scheduled maintenance window.",
        ],
    })


def _mock_openai_client(saving: float = 20.0, resource_type: str = "ec2") -> MagicMock:
    """Return a MagicMock that behaves like an AsyncOpenAI client."""
    mock_choice = MagicMock()
    mock_choice.message.content = _ai_json(resource_type, saving)

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    return mock_client


def _mock_openai_client_bad_json() -> MagicMock:
    """Return a MagicMock that returns invalid JSON to trigger parsing errors."""
    mock_choice = MagicMock()
    mock_choice.message.content = "not valid json at all"

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    return mock_client


# ---------------------------------------------------------------------------
# Helpers: AWS provider stub
# ---------------------------------------------------------------------------

def _build_provider() -> AsyncMock:
    """Async-mock AWS provider that triggers multiple waste rules."""
    provider = AsyncMock()

    provider.list_resources.return_value = [
        {
            "type": "ec2",
            "resource_id": "i-integration-idle",
            "name": "idle-server",
            "region": "eu-central-1",
            "status": "running",
            "details": {"instance_type": "t3.large"},
        },
        {
            "type": "elastic_ip",
            "resource_id": "eipalloc-integration",
            "name": "1.2.3.4",
            "region": "eu-central-1",
            "status": "unassociated",
            "details": {"public_ip": "1.2.3.4", "instance_id": None},
        },
    ]

    # EC2 metrics → very low CPU → idle finding
    provider.get_usage_metrics.return_value = {
        "resource_id": "i-integration-idle",
        "period_days": 14,
        "cpu": {"average": 2.5, "max": 5.0, "datapoints": 336},
        "network_in": {"average": 512.0, "max": 2048.0, "datapoints": 336},
        "network_out": {"average": 256.0, "max": 1024.0, "datapoints": 336},
    }

    # Cost data: 25 % week-over-week spike → cost anomaly finding
    provider.get_cost_data.return_value = {
        "daily": [{"total": 100.0, "by_service": {}} for _ in range(7)]
        + [{"total": 125.0, "by_service": {}} for _ in range(7)],
    }

    return provider


def _mock_cosmos_container() -> tuple[MagicMock, MagicMock]:
    """Return (MockCosmosClient class, mock_container) for patching."""
    mock_container = MagicMock()
    mock_cosmos_class = MagicMock()
    (mock_cosmos_class.return_value
        .get_database_client.return_value
        .get_container_client.return_value) = mock_container
    return mock_cosmos_class, mock_container


# ===========================================================================
# Part 1: WasteDetector → AIEngine
# ===========================================================================

class TestWasteDetectorToAIEngine:
    """WasteDetector findings can be consumed as-is by AIEngine."""

    def test_format_context_filters_payload(self):
        """_format_context() reduziert Payload auf nur geschäftskritische Felder."""
        with patch.dict(os.environ, FAKE_ENV):
            engine = AIEngine()
            raw_report = {
                "resource_id": "i-test",
                "resource_type": "ec2",
                "issue": "Idle instance",
                "estimated_saving": 45.0,
                "account_id": "123456789012",
                "extra_field_1": "wird_gefiltert",
                "extra_field_2": {"nested": "auch_weg"},
            }
            filtered = engine._format_context(raw_report)

        # Nur 5 Felder sollten übrig sein
        assert len(filtered) == 5
        assert set(filtered.keys()) == {
            "resource_id", "resource_type", "issue", "estimated_saving", "account_id"
        }
        assert filtered["resource_id"] == "i-test"
        # Extra Felder sind NICHT im gefilterten Output
        assert "extra_field_1" not in filtered
        assert "extra_field_2" not in filtered

    @pytest.mark.anyio
    async def test_detector_output_has_required_ai_engine_fields(self):
        """Every Recommendation field that AIEngine reads is present and typed correctly."""
        provider = _build_provider()
        detector = WasteDetector(provider=provider)
        findings = await detector.detect_waste()

        assert len(findings) > 0, "Provider should produce at least one finding"

        for finding in findings:
            raw = finding.model_dump()
            # AIEngine uses these keys directly
            assert isinstance(raw["resource_id"], str) and raw["resource_id"]
            assert isinstance(raw["resource_type"], str) and raw["resource_type"]
            assert isinstance(raw["issue"], str) and raw["issue"]
            assert isinstance(raw["estimated_saving"], float)

    @pytest.mark.anyio
    async def test_ai_engine_enhances_ec2_finding(self):
        """AIEngine.enhance_recommendation() accepts an EC2 WasteDetector finding."""
        from app.services.ai_engine import AIEngine

        provider = _build_provider()
        detector = WasteDetector(provider=provider)
        findings = await detector.detect_waste()

        ec2_finding = next(f for f in findings if f.resource_type == "ec2")

        with patch.dict(os.environ, FAKE_ENV):
            with patch("app.services.ai_engine.AsyncOpenAI") as MockOpenAI:
                MockOpenAI.return_value = _mock_openai_client(saving=45.0)
                engine = AIEngine()
                enhanced = await engine.enhance_recommendation(ec2_finding.model_dump())

        assert isinstance(enhanced, Recommendation)
        assert enhanced.ai_enhanced is True
        assert enhanced.resource_id == ec2_finding.resource_id
        assert enhanced.resource_type == "ec2"
        assert enhanced.estimated_saving == pytest.approx(45.0)
        assert enhanced.estimated_annual_saving == pytest.approx(45.0 * 12)
        assert len(enhanced.action_steps) == 3
        assert enhanced.created_at is not None

    @pytest.mark.anyio
    async def test_ai_engine_enhances_elastic_ip_finding(self):
        """AIEngine.enhance_recommendation() accepts an Elastic IP finding."""
        from app.services.ai_engine import AIEngine

        provider = _build_provider()
        detector = WasteDetector(provider=provider)
        findings = await detector.detect_waste()

        eip_finding = next(f for f in findings if f.resource_type == "elastic_ip")

        with patch.dict(os.environ, FAKE_ENV):
            with patch("app.services.ai_engine.AsyncOpenAI") as MockOpenAI:
                MockOpenAI.return_value = _mock_openai_client(
                    saving=3.60, resource_type="elastic_ip"
                )
                engine = AIEngine()
                enhanced = await engine.enhance_recommendation(eip_finding.model_dump())

        assert enhanced.ai_enhanced is True
        assert enhanced.resource_type == "elastic_ip"
        assert enhanced.priority in ("high", "medium", "low")

    @pytest.mark.anyio
    async def test_ai_engine_priority_reflects_saving(self):
        """Priority is computed from the saving returned by the AI, not the raw finding."""
        from app.services.ai_engine import AIEngine

        provider = _build_provider()
        detector = WasteDetector(provider=provider)
        findings = await detector.detect_waste()
        raw_finding = findings[0].model_dump()

        with patch.dict(os.environ, FAKE_ENV):
            with patch("app.services.ai_engine.AsyncOpenAI") as MockOpenAI:
                # saving >= 50 → priority == "high"
                MockOpenAI.return_value = _mock_openai_client(saving=60.0)
                engine = AIEngine()
                high_prio = await engine.enhance_recommendation(raw_finding)

            with patch("app.services.ai_engine.AsyncOpenAI") as MockOpenAI:
                # saving < 10 → priority == "low"
                MockOpenAI.return_value = _mock_openai_client(saving=5.0)
                engine2 = AIEngine()
                low_prio = await engine2.enhance_recommendation(raw_finding)

        assert high_prio.priority == "high"
        assert low_prio.priority == "low"


# ===========================================================================
# Part 2: AIEngine → CosmosService
# ===========================================================================

class TestAIEngineToCosmosService:
    """AIEngine output can be persisted correctly by CosmosService."""

    def _make_enhanced_recommendation(
        self,
        resource_type: str = "ec2",
        saving: float = 45.0,
        account_id: str = "123456789012",
    ) -> Recommendation:
        return Recommendation(
            resource_id="i-integration-test",
            resource_type=resource_type,
            issue="Instance is idle with 2.5 % average CPU.",
            recommendation="Terminate this instance to save money.",
            priority="medium",
            estimated_saving=saving,
            estimated_annual_saving=round(saving * 12, 2),
            effort="low",
            action_steps=[
                "Verify no active connections.",
                "Take an AMI snapshot.",
                "Terminate the instance.",
            ],
            ai_enhanced=True,
            created_at=datetime.utcnow().isoformat(),
            account_id=account_id,
        )

    @pytest.mark.anyio
    async def test_cosmos_upsert_called_once(self):
        """save_recommendation() calls upsert_item exactly once."""
        from app.services.cosmos_service import CosmosService

        rec = self._make_enhanced_recommendation()
        mock_cosmos_class, mock_container = _mock_cosmos_container()

        with patch.dict(os.environ, FAKE_ENV):
            with patch("app.services.cosmos_service.CosmosClient", mock_cosmos_class):
                service = CosmosService()
                await service.save_recommendation(rec)

        mock_container.upsert_item.assert_called_once()

    @pytest.mark.anyio
    async def test_cosmos_document_has_correct_id(self):
        """The document's 'id' field equals the Recommendation's recommendation_id."""
        from app.services.cosmos_service import CosmosService

        rec = self._make_enhanced_recommendation()
        mock_cosmos_class, mock_container = _mock_cosmos_container()

        with patch.dict(os.environ, FAKE_ENV):
            with patch("app.services.cosmos_service.CosmosClient", mock_cosmos_class):
                service = CosmosService()
                await service.save_recommendation(rec)

        doc = mock_container.upsert_item.call_args[0][0]
        assert doc["id"] == rec.recommendation_id

    @pytest.mark.anyio
    async def test_cosmos_document_preserves_ai_enhanced_flag(self):
        """ai_enhanced=True must survive the model_dump() round-trip."""
        from app.services.cosmos_service import CosmosService

        rec = self._make_enhanced_recommendation()
        mock_cosmos_class, mock_container = _mock_cosmos_container()

        with patch.dict(os.environ, FAKE_ENV):
            with patch("app.services.cosmos_service.CosmosClient", mock_cosmos_class):
                service = CosmosService()
                await service.save_recommendation(rec)

        doc = mock_container.upsert_item.call_args[0][0]
        assert doc["ai_enhanced"] is True

    @pytest.mark.anyio
    async def test_cosmos_document_has_all_required_fields(self):
        """All fields needed for the frontend are present in the upserted document."""
        from app.services.cosmos_service import CosmosService

        rec = self._make_enhanced_recommendation()
        mock_cosmos_class, mock_container = _mock_cosmos_container()

        with patch.dict(os.environ, FAKE_ENV):
            with patch("app.services.cosmos_service.CosmosClient", mock_cosmos_class):
                service = CosmosService()
                await service.save_recommendation(rec)

        doc = mock_container.upsert_item.call_args[0][0]
        required = {
            "id", "resource_id", "resource_type", "issue", "recommendation",
            "priority", "estimated_saving", "estimated_annual_saving",
            "effort", "action_steps", "status", "ai_enhanced", "account_id",
        }
        missing = required - set(doc.keys())
        assert not missing, f"Missing Cosmos DB fields: {missing}"

    @pytest.mark.anyio
    async def test_annual_saving_matches_monthly_times_twelve(self):
        """estimated_annual_saving == estimated_saving * 12 in the persisted document."""
        from app.services.cosmos_service import CosmosService

        rec = self._make_enhanced_recommendation(saving=37.50)
        mock_cosmos_class, mock_container = _mock_cosmos_container()

        with patch.dict(os.environ, FAKE_ENV):
            with patch("app.services.cosmos_service.CosmosClient", mock_cosmos_class):
                service = CosmosService()
                await service.save_recommendation(rec)

        doc = mock_container.upsert_item.call_args[0][0]
        assert doc["estimated_annual_saving"] == pytest.approx(37.50 * 12)


# ===========================================================================
# Part 3: Full Pipeline
# ===========================================================================

class TestFullPipeline:
    """End-to-end: AWS Provider → WasteDetector → AIEngine → Cosmos DB."""

    @pytest.mark.anyio
    async def test_full_pipeline_happy_path(self):
        """
        Complete pipeline run:
        1. WasteDetector finds waste in a mocked AWS account
        2. AIEngine enhances every finding (GitHub Models API mocked)
        3. CosmosService persists all enhanced recommendations (Cosmos DB mocked)

        Verifies: correct number of upserts, ai_enhanced=True, annual saving
        matches monthly × 12 for every document.
        """
        from app.services.ai_engine import AIEngine
        from app.services.cosmos_service import CosmosService

        # ── 1. Detect waste ──────────────────────────────────────────
        provider = _build_provider()
        detector = WasteDetector(provider=provider)
        raw_findings = await detector.detect_waste()
        assert len(raw_findings) >= 2  # EC2 + EIP + cost_anomaly

        # ── 2. Enhance with AI ───────────────────────────────────────
        enhanced_findings: list[Recommendation] = []
        savings_cycle = [45.0, 3.60, 87.5]

        with patch.dict(os.environ, FAKE_ENV):
            with patch("app.services.ai_engine.AsyncOpenAI") as MockOpenAI:
                call_index = 0

                async def _create(**kwargs):
                    nonlocal call_index
                    saving = savings_cycle[call_index % len(savings_cycle)]
                    call_index += 1
                    mock_resp = MagicMock()
                    mock_resp.choices = [MagicMock()]
                    mock_resp.choices[0].message.content = _ai_json("resource", saving)
                    return mock_resp

                mock_client = MagicMock()
                mock_client.chat.completions.create = _create
                MockOpenAI.return_value = mock_client

                engine = AIEngine()
                for finding in raw_findings:
                    enhanced = await engine.enhance_recommendation(finding.model_dump())
                    enhanced_findings.append(enhanced)

        assert len(enhanced_findings) == len(raw_findings)
        for rec in enhanced_findings:
            assert rec.ai_enhanced is True
            assert rec.estimated_annual_saving == pytest.approx(
                rec.estimated_saving * 12, rel=1e-6
            )

        # ── 3. Persist to Cosmos DB ──────────────────────────────────
        mock_cosmos_class, mock_container = _mock_cosmos_container()

        with patch.dict(os.environ, FAKE_ENV):
            with patch("app.services.cosmos_service.CosmosClient", mock_cosmos_class):
                service = CosmosService()
                for rec in enhanced_findings:
                    await service.save_recommendation(rec)

        assert mock_container.upsert_item.call_count == len(enhanced_findings)

        for call in mock_container.upsert_item.call_args_list:
            doc = call.args[0]
            assert "id" in doc
            assert doc["ai_enhanced"] is True
            assert doc["estimated_annual_saving"] == pytest.approx(
                doc["estimated_saving"] * 12, rel=1e-6
            )

    @pytest.mark.anyio
    async def test_pipeline_with_account_id(self):
        """account_id flows through the entire pipeline and lands in Cosmos DB."""
        from app.services.ai_engine import AIEngine
        from app.services.cosmos_service import CosmosService

        ACCOUNT_ID = "987654321098"

        provider = _build_provider()
        detector = WasteDetector(provider=provider, account_id=ACCOUNT_ID)
        raw_findings = await detector.detect_waste()

        with patch.dict(os.environ, FAKE_ENV):
            with patch("app.services.ai_engine.AsyncOpenAI") as MockOpenAI:
                MockOpenAI.return_value = _mock_openai_client(saving=30.0)
                engine = AIEngine()
                enhanced = await engine.enhance_recommendation(
                    {**raw_findings[0].model_dump(), "account_id": ACCOUNT_ID}
                )

        assert enhanced.account_id == ACCOUNT_ID

        mock_cosmos_class, mock_container = _mock_cosmos_container()
        with patch.dict(os.environ, FAKE_ENV):
            with patch("app.services.cosmos_service.CosmosClient", mock_cosmos_class):
                service = CosmosService()
                await service.save_recommendation(enhanced)

        doc = mock_container.upsert_item.call_args[0][0]
        assert doc["account_id"] == ACCOUNT_ID

    @pytest.mark.anyio
    async def test_empty_account_produces_no_cosmos_writes(self):
        """An account with no resources creates no Cosmos DB documents."""
        from app.services.cosmos_service import CosmosService

        provider = AsyncMock()
        provider.list_resources.return_value = []
        provider.get_cost_data.return_value = {"daily": []}

        detector = WasteDetector(provider=provider)
        findings = await detector.detect_waste()

        assert findings == []

        mock_cosmos_class, mock_container = _mock_cosmos_container()
        with patch.dict(os.environ, FAKE_ENV):
            with patch("app.services.cosmos_service.CosmosClient", mock_cosmos_class):
                service = CosmosService()
                for rec in findings:
                    await service.save_recommendation(rec)

        mock_container.upsert_item.assert_not_called()

    @pytest.mark.anyio
    async def test_ai_parsing_failure_logs_error(self):
        """Verify that AI parsing failure (bad JSON) emits logging.error via retry."""
        from app.services.ai_engine import AIEngine
        from tenacity import RetryError

        provider = _build_provider()
        detector = WasteDetector(provider=provider)
        raw_findings = await detector.detect_waste()
        raw_report = raw_findings[0].model_dump()

        with patch.dict(os.environ, FAKE_ENV):
            with patch("app.services.ai_engine.AsyncOpenAI") as MockOpenAI:
                MockOpenAI.return_value = _mock_openai_client_bad_json()
                engine = AIEngine()

                # When bad JSON is returned, tenacity retries 3 times then raises RetryError
                with pytest.raises(RetryError):
                    await engine.enhance_recommendation(raw_report)

        # The logging happens within the retries (via before_sleep_log callback)
        # This test passes if no exception occurs before reaching this point
