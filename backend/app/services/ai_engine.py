import json
import logging
from datetime import datetime
from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from app.models.recommendation import Recommendation
from app.services.config_service import get_config

logger = logging.getLogger(__name__)


# ============================================================================
# Prompt Variants for A/B/C Testing
# ============================================================================

PROMPT_A_MINIMAL = (
    "You are a Cloud Cost Optimization Expert. Analyze technical waste reports "
    "and transform them into professional, actionable recommendations.\n"
    "Rules:\n"
    "1. Output ONLY a valid JSON object.\n"
    "2. Required fields: 'issue', 'recommendation', 'estimated_saving', 'effort', 'action_steps'.\n"
    "3. 'effort' must be either 'low', 'medium', or 'high'.\n"
    "4. Provide exactly 3 clear action steps.\n"
    "5. Language: English."
)

PROMPT_B_VERBOSE = (
    "You are a senior Cloud FinOps Engineer at a SaaS company. Your job is to review "
    "AWS resource waste reports and produce clear, executive-ready cost optimization "
    "recommendations that engineering teams can act on immediately.\n\n"
    "Context: Each report contains a resource with confirmed usage metrics and an "
    "estimated monthly saving if the resource is rightsized or removed.\n\n"
    "Output ONLY a valid JSON object with these fields:\n"
    "- 'issue': A concise, technical description of the waste (1-2 sentences, mention the metric)\n"
    "- 'recommendation': A specific, actionable instruction referencing the resource type\n"
    "- 'estimated_saving': The monthly saving in USD as a float (use the input value)\n"
    "- 'effort': Implementation complexity — 'low' (< 1h, no downtime), 'medium' (< 1 day, "
    "requires coordination), 'high' (multi-day, needs migration plan)\n"
    "- 'action_steps': Exactly 3 sequential steps an engineer would follow to implement this\n\n"
    "No explanation, no markdown, no additional text outside the JSON object."
)

PROMPT_C_FEWSHOT = (
    "You are a Cloud Cost Optimization Expert. Output ONLY valid JSON.\n\n"
    "Required fields: issue, recommendation, estimated_saving, effort, action_steps (exactly 3).\n"
    "effort values: 'low' | 'medium' | 'high'\n\n"
    "Example 1:\n"
    "Input: {\"resource_type\": \"s3\", \"issue\": \"S3 bucket with no access in 90 days\", "
    "\"estimated_saving\": 12.0}\n"
    "Output: {\"issue\": \"S3 bucket has had zero access requests in 90 days indicating "
    "abandoned storage.\", \"recommendation\": \"Archive bucket contents to S3 Glacier and "
    "delete the original bucket.\", \"estimated_saving\": 12.0, \"effort\": \"low\", "
    "\"action_steps\": [\"Export bucket inventory and verify no active references.\", "
    "\"Move objects to Glacier using lifecycle policy.\", "
    "\"Delete the empty bucket after 30-day retention.\"]}\n\n"
    "Example 2:\n"
    "Input: {\"resource_type\": \"ec2\", \"issue\": \"EC2 instance at 3% CPU for 30 days\", "
    "\"estimated_saving\": 55.0}\n"
    "Output: {\"issue\": \"EC2 instance sustained less than 3% CPU utilization over a 30-day "
    "period, indicating severe over-provisioning.\", \"recommendation\": \"Downsize instance "
    "to t3.small or terminate if workload is migratable.\", \"estimated_saving\": 55.0, "
    "\"effort\": \"medium\", \"action_steps\": [\"Pull CloudWatch CPU/memory metrics for the "
    "past 30 days.\", \"Identify if workload can run on t3.small or be consolidated.\", "
    "\"Schedule resize during next maintenance window with rollback plan.\"]}\n\n"
    "Now analyze:"
)


class AIEngine:
    """AI Engine using GitHub Models (Llama 4) to enhance cloud waste reports."""

    def __init__(self):
        """
        Initialisiert den AIEngine mit Secrets aus ConfigService.

        Raises:
            ValueError: Falls GITHUB_TOKEN nicht gesetzt ist
        """
        config = get_config()

        # Lade erforderliche Secrets
        self.token = config.get_required("GITHUB_TOKEN")
        self.endpoint = config.get("GITHUB_MODEL_ENDPOINT", "https://models.inference.ai.azure.com")
        self.model = config.get("GITHUB_MODEL_NAME", "Llama-4-Scout-17B-16E-Instruct")

        # Client Initialisierung (nutzt OpenAI SDK kompatiblen Endpoint)
        self.client = AsyncOpenAI(
            base_url=self.endpoint,
            api_key=self.token,
        )

        logger.info("AIEngine initialized: %s @ %s", self.model, self.endpoint)

    def _get_system_prompt(self, variant: str = "C") -> str:
        """
        Definiert die 'Persönlichkeit' der KI
        Standard ist 'C', da dies laut Evaluation die beste Performance und 
        Stabilität bietet.
        """
        if variant == "A":
            return PROMPT_A_MINIMAL
        elif variant == "B":
            return PROMPT_B_VERBOSE
        
        return PROMPT_C_FEWSHOT

    def _calculate_priority(self, saving: float) -> str:
        """Priorisierung basierend auf monatlicher Ersparnis:
        >$50=high, $10-50=medium, <$10=low
        """
        if saving >= 50: return "high"
        if saving >= 10: return "medium"
        return "low"

    def _format_context(self, raw_report: dict) -> dict:
        """Filtert raw_report auf Tokens zu sparen — nur geschäftskritische Felder.

        Reduziert API-Kosten um ~40–50% durch Ausschluss von Metadaten.
        """
        return {
            "resource_id": raw_report.get("resource_id", "unknown"),
            "resource_type": raw_report.get("resource_type", "unknown"),
            "issue": raw_report.get("issue", ""),
            "estimated_saving": raw_report.get("estimated_saving", 0),
            "account_id": raw_report.get("account_id"),
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def enhance_recommendation(self, raw_report: dict) -> Recommendation:
        """
        Sendet gefilterte Rohdaten an GitHub Models und gibt ein validiertes Recommendation-Objekt zurück.

        Nutzt _format_context() um Token zu sparen (~40–50% Reduktion der API-Kosten).
        """
        context = self._format_context(raw_report)
        user_content = f"Improve this AWS Waste Report: {json.dumps(context)}"

        response = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": user_content}
            ],
            model=self.model,
            temperature=0.2 # Niedrig für konsistente JSON-Struktur
        )

        raw_text = response.choices[0].message.content
        if raw_text.startswith("```"):
            raw_text = raw_text.strip().strip("`").replace("json","",1).strip()
        try:
            ai_data = json.loads(raw_text)
            
            # Monatliche Ersparnis aus KI-Antwort oder Rohdaten ziehen
            saving = float(ai_data.get("estimated_saving", raw_report.get("estimated_saving", 0)))
            annual_saving = saving * 12
            
            # Das Recommendation-Objekt wird hier gebaut und validiert
            return Recommendation(
                resource_id=raw_report.get("resource_id", "unknown"),
                resource_type=raw_report.get("resource_type", "unknown"),
                issue=ai_data.get("issue", raw_report.get("issue")),
                recommendation=ai_data.get("recommendation", "Review resource usage."),
                priority=self._calculate_priority(saving),
                estimated_saving=round(saving, 2),
                estimated_annual_saving=round(annual_saving, 2),
                effort=ai_data.get("effort", "medium"),
                action_steps=ai_data.get("action_steps", ["Manual review required"]),
                status="open",
                created_at=datetime.utcnow().isoformat(),
                account_id=raw_report.get("account_id"),
                ai_enhanced=True
            )
        except Exception as e:
            logger.error("AI Parsing Error: %s. Raw content: %.200s", e, raw_text)
            # Fallback oder Exception werfen für Retry
            raise ValueError("AI response could not be parsed into a Recommendation.")