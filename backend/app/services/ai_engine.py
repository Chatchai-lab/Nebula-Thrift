import json
from datetime import datetime
from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from app.models.recommendation import Recommendation
from app.services.config_service import get_config

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

        print(f"✅ AIEngine initialized: {self.model} @ {self.endpoint}")

        # Client Initialisierung (nutzt OpenAI SDK kompatiblen Endpoint)
        self.client = AsyncOpenAI(
            base_url=self.endpoint,
            api_key=self.token,
        )

    def _get_system_prompt(self) -> str:
        """
        Definiert die 'Persönlichkeit' der KI.
        Hier wird festgelegt, dass die KI nur JSON antworten darf
        und welche Felder enthalten sein müssen.
        """
        return (
            "You are a Cloud Cost Optimization Expert. Analyze technical waste reports "
            "and transform them into professional, actionable recommendations.\n"
            "Rules:\n"
            "1. Output ONLY a valid JSON object.\n"
            "2. Required fields: 'issue', 'recommendation', 'estimated_saving', 'effort', 'action_steps'.\n"
            "3. 'effort' must be either 'low', 'medium', or 'high'.\n"
            "4. Provide exactly 3 clear action steps.\n"
            "5. Language: English."
        )

    def _calculate_priority(self, saving: float) -> str:
        """Priorisierung basierend auf monatlicher Ersparnis: 
        >$50=high, $10-50=medium, <$10=low
        """
        if saving >= 50: return "high"
        if saving >= 10: return "medium"
        return "low"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception), 
    )
    async def enhance_recommendation(self, raw_report: dict) -> Recommendation:
        """
        Sendet Rohdaten an GitHub Models und gibt ein validiertes Recommendation-Objekt zurück.
        """
        user_content = f"Improve this AWS Waste Report: {json.dumps(raw_report)}"

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
            print(f"❌ AI Parsing Error: {e}. Raw content: {raw_text}")
            # Fallback oder Exception werfen für Retry
            raise ValueError("AI response could not be parsed into a Recommendation.")