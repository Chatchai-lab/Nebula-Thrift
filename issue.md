## 📝 Beschreibung
Die `AIEngine` ist produktionsreif und integriert mit GitHub Models (Llama-4-Scout) für Cloud-Waste-Analyse. Die vollständige Pipeline (WasteDetector → AIEngine → CosmosService) ist implementiert und getestet. Verbleibende Optimierungen betreffen Token-Effizienz und Observability.

## 🛠 Aufgaben
- [x] **Basis-Klasse:** `AIEngine` mit `AsyncOpenAI` Integration erstellt.
- [x] **Prompt-Engineering:** System-Prompt für "Cloud Cost Expert" mit striktem JSON-Output definiert.
- [x] **Fehlerbehandlung:** Resilience durch `tenacity` Retry-Logic (Exponential Backoff) implementiert.
- [x] **Daten-Modellierung:** Mapping der KI-Antwort auf das `Recommendation` Modell mit Pydantic V2.
- [x] **Sicherheit:** ConfigService mit Azure Key Vault Integration (DefaultAzureCredential).
- [x] **Persistierung:** CosmosService speichert alle Empfehlungen in Cosmos DB Container `recommendations`.
- [x] **Azure Functions:** function_app.py mit AIRecommender (HTTP), daily_collector (Timer), api (ASGI) konsolidiert.
- [x] **Integration Test:** 14 E2E-Tests (test_integration_e2e.py) decken vollständige Pipeline ab.
- [x] **Kontext-Optimierung:** `_format_context()` reduziert API-Payload um 40–50% (nur geschäftskritische Felder).
- [x] **Observability:** CloudWatch/Application Insights Logging mit strukturierten Logs in AIEngine und CosmosService.

## 📋 Akzeptanzkriterien
- [x] **Zero-Secret-Leak:** Keine API-Keys im Code. `.env` und `local.settings.json` sind gitignored. Secrets werden via ConfigService aus .env (lokal) oder Key Vault (Azure) geladen.
- [x] **Struktur-Garantie:** Die KI liefert konsistent valides JSON, das direkt vom `Recommendation` Modell validiert wird.
- [x] **Business-Logic:** Priorisierung (`high` ≥$50, `medium` $10–50, `low` <$10) erfolgt konsistent in AIEngine._calculate_priority().
- [x] **Daten-Integrität:** Alle Empfehlungen in Cosmos DB haben `ai_enhanced=true`, `account_id`, `created_at`, `estimated_annual_saving` (saving × 12).
- [x] **Integration Test:** Vollständiger Flow WasteDetector → AIEngine → CosmosService erfolgreich (14/14 Tests grün).
- [x] **Token-Effizienz:** `_format_context()` filtert auf geschäftskritische Felder (API-Payload um 40–50% reduziert).

## 🧬 Technisches Schema (Target JSON)
```json
{
  "issue": "Detailed description of the waste",
  "recommendation": "Clear instruction on how to fix it",
  "estimated_saving": 45.50,
  "effort": "low | medium | high",
  "action_steps": ["Step 1", "Step 2", "Step 3"]
}
```

## ✅ Status: Production Ready ✨
Die AIEngine und alle zugehörigen Services sind vollständig implementiert, optimiert und getestet.
Alle Aufgaben abgeschlossen:
- ✅ WasteDetector mit 7 Erkennungsregeln
- ✅ AIEngine mit GitHub Models Integration (Llama-4-Scout)
- ✅ Kontext-Optimierung (Token-Effizienz 40–50%)
- ✅ CosmosService mit persistenter Speicherung
- ✅ Azure Functions Pipeline
- ✅ Umfassende Integration Tests (14/14 grün)
- ✅ Strukturierte Observability Logging

**Nächster Schritt:** Phase 4 — React Frontend Entwicklung
