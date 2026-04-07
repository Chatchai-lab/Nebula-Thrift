# Nebula Thrift — Umsetzungsplan Schritt für Schritt

> Diesen Plan kannst du Punkt für Punkt mit Claude Code durchgehen.
> Hake jeden Schritt ab, bevor du zum nächsten gehst.

---

## Phase 1 — Design & AWS Setup (Woche 1–2)

### Woche 1: Figma Design & AWS-Konto

**Design:**
- [ ] Figma-Projekt "Nebula Thrift" anlegen
- [ ] Design System erstellen: Farben (#0B0F1A, #131825, #34D399, #8B5CF6), Typografie (Inter), Spacing (8px Grid), Border Radius (12px Cards, 8px Buttons)
- [ ] Komponentenbibliothek bauen: Buttons, Inputs, Cards, Badges, Alerts, Navigation
- [ ] Landing Page designen (Hero, Features, Bento Grid, CTA, Footer)
- [ ] Login / Register Page designen
- [ ] Onboarding Wizard designen (3 Schritte: Provider wählen, Credentials eingeben, Validierung)
- [ ] Dashboard Page designen (Metric Cards, Cost Trend Chart, Service Breakdown, Recent Recommendations)
- [ ] Recommendations Page designen (Filter Bar, Empfehlungskarten)
- [ ] Savings Simulator Page designen (Checklist + Live Summary)
- [ ] Settings Page designen (AWS Connection, Notifications, Account)
- [ ] Demo-Banner Komponente designen ("You're viewing demo data...")
- [ ] Responsive Varianten prüfen (Desktop 1440px, Tablet 768px, Mobile 375px)

**AWS-Konto:**
- [ ] AWS Free Tier Konto erstellen
- [ ] MFA aktivieren auf Root-Account
- [ ] IAM User "nebula-thrift-dev" erstellen (kein Root für Entwicklung)
- [ ] IAM Policy schreiben: Lesezugriff auf Cost Explorer, CloudWatch, EC2, RDS, S3
- [ ] AWS CLI installieren
- [ ] `aws configure` mit IAM User Credentials einrichten
- [ ] AWS Budget Alert bei $5 einrichten
- [ ] Testen: `aws sts get-caller-identity` sollte deinen IAM User zurückgeben

### Woche 2: AWS Provider & erste Datenabrufe

- [ ] Python Virtual Environment einrichten (`python -m venv .venv`)
- [ ] boto3 und python-dotenv installieren
- [ ] `backend/app/providers/base.py` implementieren: Abstrakte Klasse `CloudProvider` mit den Methoden `get_cost_data()`, `get_usage_metrics()`, `list_resources()`, `validate_connection()`
- [ ] `backend/app/providers/aws.py` implementieren: `AWSProvider` erbt von `CloudProvider`
- [ ] `get_cost_data()` umsetzen: Cost Explorer API aufrufen, letzte 30 Tage, nach Service gruppiert
- [ ] `get_usage_metrics()` umsetzen: CloudWatch CPU-Metriken für EC2 Instanzen abrufen
- [ ] `list_resources()` umsetzen: EC2 Instanzen, RDS Instanzen, Elastic IPs auflisten
- [ ] `validate_connection()` umsetzen: STS `get-caller-identity` aufrufen
- [ ] Daten normalisieren und als einheitliches JSON-Format strukturieren
- [ ] S3 Bucket "nebula-thrift-data-{account-id}" erstellen
- [ ] Normalisierte Daten in S3 speichern
- [ ] Einfaches Test-Skript schreiben das den gesamten Flow durchläuft
- [ ] Ergebnis prüfen: Kostendaten liegen als JSON in S3

---

## Phase 2 — Backend & Waste Detection (Woche 3–4)

### Woche 3: FastAPI Backend & Lambda Functions

- [ ] FastAPI-Projektstruktur aufsetzen (`backend/app/main.py` erweitern)
- [ ] Pydantic Models definieren:
  - [ ] `CostDataModel` (service, cost, currency, date)
  - [ ] `RecommendationModel` (resource_id, resource_type, issue, recommendation, priority, estimated_saving, effort, action_steps)
  - [ ] `ResourceModel` (resource_id, type, region, status, metrics)
- [ ] Router erstellen:
  - [ ] `GET /api/health` — Health Check
  - [ ] `GET /api/costs` — Kostendaten abrufen (mit Zeitraum-Parameter)
  - [ ] `GET /api/costs/breakdown` — Kosten nach Service aufgeschlüsselt
  - [ ] `GET /api/recommendations` — Alle Empfehlungen abrufen
  - [ ] `PATCH /api/recommendations/{id}` — Empfehlung als umgesetzt markieren
  - [ ] `GET /api/resources` — Alle Ressourcen mit Status
- [ ] DynamoDB Tabellen anlegen:
  - [ ] `nebula-thrift-recommendations` (PK: recommendation_id)
  - [ ] `nebula-thrift-snapshots` (PK: snapshot_date)
- [ ] Lambda Function `daily_collector` schreiben (ruft AWSProvider auf, speichert in S3)
- [ ] Lambda lokal testen mit AWS SAM (`sam local invoke`)
- [ ] EventBridge Regel erstellen: Täglich um 08:00 UTC die Lambda triggern
- [ ] Lambda Execution Role mit nötigen Berechtigungen erstellen

### Woche 4: Waste Detection Regeln & Tests

- [ ] `WasteDetector` Klasse implementieren mit folgenden Regeln:
  - [ ] Idle EC2: CPU < 5% über 14+ Tage → Empfehlung: Downsizen oder stoppen
  - [ ] Oversized RDS: CPU < 10% und < 20% Storage genutzt → Empfehlung: Kleinere Instanz
  - [ ] Ungenutzte Elastic IPs: Nicht mit Instanz verknüpft → Empfehlung: Freigeben
  - [ ] Alte EBS Snapshots: Älter als 90 Tage, kein Backup-Tag → Empfehlung: Löschen
  - [ ] Ungenutzte Load Balancer: < 10 Requests/Tag → Empfehlung: Entfernen
  - [ ] S3 ohne Lifecycle Policy: Daten älter als 30 Tage, kein Tiering → Empfehlung: Lifecycle einrichten
- [ ] Anomalie-Erkennung: Kostenanstieg > 20% gegenüber Vorwoche erkennen
- [ ] Jede Regel gibt ein standardisiertes `WasteReport` Objekt zurück
- [ ] Unit Tests schreiben (Pytest):
  - [ ] Test: EC2 mit 3% CPU wird als idle erkannt
  - [ ] Test: EC2 mit 15% CPU wird NICHT als idle erkannt
  - [ ] Test: Elastic IP ohne Instanz wird als Waste erkannt
  - [ ] Test: Snapshot von vor 100 Tagen wird als löschbar erkannt
  - [ ] Test: Anomalie bei 25% Kostenanstieg wird getriggert
- [ ] End-to-End Test: Daten sammeln → Waste erkennen → Ergebnis in DynamoDB speichern
- [ ] Alle Tests grün? → Commit: "feat: waste detection rules with full test coverage"

---

## Phase 3 — KI-Integration mit Claude API (Woche 5–6)

### Woche 5: Prompt Engineering & Claude API Anbindung

- [ ] Anthropic SDK installieren (`pip install anthropic`)
- [ ] API Key als AWS Secret in Secrets Manager speichern (NICHT im Code!)
- [ ] `AIEngine` Klasse implementieren:
  - [ ] System-Prompt entwickeln: Claude als "Cloud Cost Optimization Expert"
  - [ ] Output-Format definieren: Strukturiertes JSON mit resource_id, issue, recommendation, priority, estimated_saving_usd, effort, action_steps
  - [ ] Kontext-Aufbereitung: Funktion die AWS-Rohdaten in lesbares Summary umwandelt
- [ ] Prompt-Varianten testen:
  - [ ] Variante A: Minimaler Kontext, nur Zahlen
  - [ ] Variante B: Ausführlicher Kontext mit Nutzungshistorie
  - [ ] Variante C: Kontext + Beispiel-Output (Few-Shot)
  - [ ] Qualität vergleichen: Welche Variante liefert die besten Empfehlungen?
- [ ] LangChain für Output-Parsing einbauen (JSON Output Parser)
- [ ] Ersten vollständigen Durchlauf testen: AWS-Daten → Prompt → Claude → JSON-Output

### Woche 6: Validierung, Fehlerbehandlung & Empfehlungs-Engine

- [ ] Pydantic-Validierung für Claude API Output implementieren
- [ ] Fehlerbehandlung:
  - [ ] Retry-Logik bei API-Fehlern (max. 3 Versuche mit Backoff)
  - [ ] Fallback wenn Claude ungültiges JSON liefert (erneuter Versuch mit strikterem Prompt)
  - [ ] Rate Limiting beachten
- [ ] Priorisierungs-Logik:
  - [ ] Hoch: Einsparung > $50/Monat
  - [ ] Mittel: Einsparung $10–$50/Monat
  - [ ] Niedrig: Einsparung < $10/Monat
- [ ] Einsparungsberechnung: Monatlich und Jahreswerte berechnen
- [ ] KI-Empfehlungen in DynamoDB speichern (mit Timestamp, Status "open")
- [ ] Lambda `ai_recommender` fertigstellen: Daten aus S3 laden → WasteDetector → AIEngine → DynamoDB
- [ ] Integration Test: Vollständiger Pipeline-Durchlauf automatisiert
- [ ] Commit: "feat: AI recommendation engine with Claude API integration"

---

## Phase 4 — React Frontend (Woche 7–8)

### Woche 7: Projekt-Setup, Layout & Dashboard

**Setup:**
- [ ] React Projekt mit Vite initialisieren (`npm create vite@latest`)
- [ ] TailwindCSS konfigurieren mit Custom Theme (Dark Mode Farben aus Design System)
- [ ] React Router einrichten (Routes für alle Seiten)
- [ ] React Query (TanStack Query) einrichten
- [ ] Axios API Client konfigurieren (`frontend/src/services/api.js`)
- [ ] Demo-Daten erstellen (`frontend/src/data/demo.json`) mit realistischen Beispieldaten

**Layout-Komponenten:**
- [ ] `Sidebar` Komponente (Logo, Navigation Links, Collapse Toggle)
- [ ] `TopBar` Komponente (Account Name, Notification Bell, User Avatar)
- [ ] `PageContainer` Komponente (Sidebar + TopBar + Content Area)
- [ ] `DemoBanner` Komponente ("You're viewing demo data...")

**Landing Page:**
- [ ] Hero Section mit Headline, Subtext, CTA Buttons
- [ ] Feature Cards (Connect & Scan, Intelligent Analysis, Optimize & Save)
- [ ] Bento Grid Section (Granular Visibility, Smart Insights, Anomaly Detection)
- [ ] CTA Section ("Ready to trim the fat?")
- [ ] Footer

**Dashboard Page:**
- [ ] 4 Metric Summary Cards (Total Spend, Identified Savings, Active Recommendations, Trend)
- [ ] Cost Trend Chart mit Recharts (Linie/Area, letzte 30 Tage, nach Service)
- [ ] Service Breakdown (Donut Chart + Tabelle)
- [ ] Recent Recommendations Preview (Top 3 Karten)
- [ ] Hook `useCloudData()`: Wenn eingeloggt → API, sonst → Demo-Daten

### Woche 8: Restliche Seiten & Auth

**Recommendations Page:**
- [ ] Filter Bar (Priority, Service, Status als Dropdown/Pills)
- [ ] Empfehlungskarten-Liste mit Priority Badge, Resource ID, Issue, Saving, Effort
- [ ] Expandierbarer Detail-Bereich mit Action Steps
- [ ] "Als umgesetzt markieren" Button (PATCH an API)
- [ ] Summary Header ("X Empfehlungen — Potenzielle Ersparnis: $XX/Monat")

**Savings Simulator Page:**
- [ ] Linke Spalte: Checkbox-Liste aller offenen Empfehlungen, gruppiert nach Service
- [ ] Rechte Spalte: Live-Summary Panel (monatliche/jährliche Ersparnis, Balkendiagramm Current vs Optimized)
- [ ] "Alle auswählen" und "Zurücksetzen" Buttons
- [ ] "Report herunterladen" Button (optional, kann Platzhalter sein)

**Login Page:**
- [ ] Zentrierte Card auf dunklem Hintergrund
- [ ] "Sign in with Google" Button (prominent)
- [ ] E-Mail/Passwort Felder (sekundär)
- [ ] "Just exploring? Try the demo" Link
- [ ] AWS Cognito Integration (Google OAuth konfigurieren)

**Onboarding Page:**
- [ ] Step Indicator (3 Schritte, verbundene Punkte)
- [ ] Step 1: Provider wählen — AWS (aktiv), Azure (Coming Soon, ausgegraut), GCP (Coming Soon, ausgegraut)
- [ ] Step 2: Credentials eingeben — IAM Role ARN oder Access Keys
- [ ] Step 3: Validierung — Loading Spinner → Erfolg/Fehler Anzeige
- [ ] "Skip for now" Link → führt zur Demo-Ansicht

**Settings Page:**
- [ ] AWS Connection Status (Connected/Disconnected Badge, Account Info, Disconnect Button)
- [ ] Notification Toggles (Anomalie-Alerts, Wochen-Report, Neue Empfehlungen)
- [ ] Account Info (Name, E-Mail, Delete Account)
- [ ] "Sync Now" Button mit letztem Sync-Timestamp

- [ ] Responsives Design testen (Desktop, Tablet, Mobile)
- [ ] Commit: "feat: complete frontend with all pages and demo mode"

---

## Phase 5 — Terraform, Deployment & Portfolio (Woche 9–10)

### Woche 9: Infrastructure as Code & CI/CD

**Terraform Module schreiben:**
- [ ] `modules/storage/` — S3 Buckets (Daten + Frontend) + DynamoDB Tabellen
- [ ] `modules/lambda/` — Lambda Functions + IAM Execution Roles + Layers
- [ ] `modules/api/` — API Gateway REST API + Stages + CORS
- [ ] `modules/frontend/` — S3 Static Website + CloudFront Distribution + OAI
- [ ] `modules/scheduler/` — EventBridge Rules für täglichen Trigger
- [ ] `modules/auth/` — Cognito User Pool + Google OAuth App Client
- [ ] `main.tf` — Alle Module verbinden, Variablen durchreichen
- [ ] Terraform Remote State in S3 konfigurieren (eigener State-Bucket + DynamoDB Lock)

**CI/CD Pipeline (GitHub Actions):**
- [ ] Workflow: `deploy.yml`
  - [ ] Trigger: Push auf `main`
  - [ ] Step 1: Pytest Unit Tests ausführen → bei Fehler abbrechen
  - [ ] Step 2: `npm run build` im Frontend-Ordner
  - [ ] Step 3: `aws s3 sync` — Build-Dateien nach S3 hochladen
  - [ ] Step 4: CloudFront Cache Invalidation auslösen
  - [ ] Step 5: Lambda Functions als ZIP packen und deployen
- [ ] GitHub Secrets einrichten: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
- [ ] Pipeline testen: Push → Tests → Build → Deploy → Seite live

### Woche 10: Domain, Dokumentation & Portfolio

**Domain & HTTPS:**
- [ ] Domain registrieren oder bestehende verwenden
- [ ] Route 53 Hosted Zone einrichten
- [ ] ACM SSL-Zertifikat beantragen (us-east-1 für CloudFront!)
- [ ] CloudFront mit Custom Domain und HTTPS konfigurieren
- [ ] DNS Records setzen (A-Record als Alias auf CloudFront)
- [ ] Testen: https://deinedomain.com zeigt die Landing Page

**README fertigstellen:**
- [ ] Projekt-Titel und Beschreibung
- [ ] Architektur-Diagramm erstellen (draw.io oder Mermaid)
- [ ] Screenshots vom Dashboard einfügen
- [ ] Tech Stack Übersicht
- [ ] Setup-Anleitung (lokal + Deployment)
- [ ] Abschnitt "Was ich gelernt habe"
- [ ] Konkreter Satz: "Nebula Thrift hat in meinem Test-Account $X/Jahr an ungenutzten Ressourcen identifiziert."

**Demo-Daten finalisieren:**
- [ ] Realistische Kosten für ein fiktives Startup erstellen
- [ ] Mindestens 7 Empfehlungen mit verschiedenen Prioritäten
- [ ] Verschiedene AWS Services abdecken (EC2, RDS, S3, Lambda, EBS)
- [ ] Gesamtersparnis sollte beeindruckend aber glaubwürdig sein (~$300–400/Jahr)

**Demo-Video:**
- [ ] 2–3 Minuten Walkthrough aufnehmen
- [ ] Zeigen: Landing Page → Demo Dashboard → Empfehlungen → Savings Simulator
- [ ] Kurz erklären: Problem, Lösung, Architektur
- [ ] Video auf YouTube/Loom hochladen und im README verlinken

**Portfolio-Eintrag:**
- [ ] Titel: "Nebula Thrift — AI-powered Cloud Cost Optimizer"
- [ ] Problem: "Unternehmen verschwenden 30–35% ihres Cloud-Budgets"
- [ ] Lösung: "Automatische Analyse + KI-Empfehlungen mit quantifizierten Einsparungen"
- [ ] Tech Stack aufzählen
- [ ] Live-Link + GitHub-Link
- [ ] Screenshot des Dashboards

---

## Optionale Features (nach MVP)

Falls du nach den 10 Wochen noch Zeit und Lust hast:

- [ ] **Anomalie-Alerts:** E-Mail über SES bei Kostenanstieg > 20% (2–3 Tage)
- [ ] **Slack-Integration:** Tägliche Zusammenfassung als Slack-Nachricht via Webhook (1–2 Tage)
- [ ] **PDF-Export:** Monatlichen Kostenbericht als PDF generieren (2–3 Tage)
- [ ] **Azure Provider:** `providers/azure.py` implementieren mit Azure Cost Management API (2 Wochen)
- [ ] **GCP Provider:** `providers/gcp.py` implementieren mit GCP Billing API (2 Wochen)
- [ ] **Multi-Account:** AWS Organizations + Cross-Account Roles (1 Woche)
