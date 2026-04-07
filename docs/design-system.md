# Nebula Thrift — Design System

Source of truth: [`frontend/src/styles/tailwind.css`](../frontend/src/styles/tailwind.css)

In diesem Projekt gilt **Code = Design**. Alle Design Tokens leben als CSS-Variablen
und werden über das Tailwind v4 Theme als Utility-Klassen verfügbar gemacht.

## Figma (Referenz)

[Figma — KI-basierter Cloud Kosten-Optimierer](https://www.figma.com/make/pi4bZ3r73z8XvuSvkO1rOn/KI-basierter-Cloud-Kosten-Optimierer)

Die Figma-Datei diente als initiale visuelle Referenz. Die Code-Implementierung
ist die führende Quelle — sollte das Figma-Design vom Code abweichen, gewinnt der Code.

---

## Farben

| Token              | Hex       | Verwendung                          |
|--------------------|-----------|-------------------------------------|
| `--background`     | `#0B0F1A` | Page Background (Dark)              |
| `--card`           | `#131825` | Card / Panel Background             |
| `--foreground`     | `#F8FAFC` | Primärtext                          |
| `--muted-foreground` | `#94A3B8` | Sekundärtext, Labels              |
| `--primary`        | `#34D399` | Brand Green — CTAs, Highlights      |
| `--secondary`      | `#8B5CF6` | Akzent Purple — AI / Secondary CTAs |
| `--destructive`    | `#EF4444` | Errors, High Priority               |
| `--warning`        | `#F59E0B` | Warnings, Medium Priority           |
| `--border`         | `#1E2A3A` | Borders, Dividers                   |
| `--ring`           | `#34D399` | Focus Ring                          |

### Priority

| Token               | Hex       |
|---------------------|-----------|
| `--priority-high`   | `#EF4444` |
| `--priority-medium` | `#F59E0B` |
| `--priority-low`    | `#10B981` |

### Charts

| Token              | Hex       |
|--------------------|-----------|
| `--chart-compute`  | `#3B82F6` |
| `--chart-database` | `#8B5CF6` |
| `--chart-storage`  | `#10B981` |
| `--chart-network`  | `#F59E0B` |

### Provider-Brand

| Token            | Hex       |
|------------------|-----------|
| `--provider-aws` | `#FF9900` |

---

## Typografie

**Font:** Inter (Google Fonts) — `--font-sans`

| Token         | Größe   | Pixel | Verwendung      |
|---------------|---------|-------|-----------------|
| `--text-h1`   | 3rem    | 48px  | Hero Headline   |
| `--text-h2`   | 2.25rem | 36px  | Section Title   |
| `--text-h3`   | 1.5rem  | 24px  | Subsection      |
| `--text-h4`   | 1.25rem | 20px  | Card Title      |
| `--text-h5`   | 1.125rem| 18px  | Panel Title     |
| `--text-h6`   | 1rem    | 16px  | Small Heading   |
| `--text-body` | 0.875rem| 14px  | Standard-Text   |
| `--text-small`| 0.75rem | 12px  | Captions, Hints |

Headings (h1–h4) haben definierte `line-height` und `font-weight: 500` als Browser-Default.

---

## Spacing

8px Grid via `--spacing: 0.5rem`. Tailwind-Utilities wie `p-4` (16px), `gap-6` (24px) etc.
folgen automatisch diesem Raster.

---

## Border Radius

| Token         | Wert  | Verwendung |
|---------------|-------|------------|
| `--radius-sm` | 6px   | Inputs     |
| `--radius-md` | 8px   | Buttons    |
| `--radius-lg` | 12px  | Cards      |
| `--radius-xl` | 16px  | Modals     |
| `--radius-2xl`| 24px  | Hero Cards |

---

## Komponenten

Wiederverwendbare Komponenten leben unter [`frontend/src/components/ui/`](../frontend/src/components/ui/)
(shadcn/ui basiert).

| Komponente | Datei | Varianten |
|------------|-------|-----------|
| Button     | [button.tsx](../frontend/src/components/ui/button.tsx) | default, secondary, destructive, outline, ghost, link |
| Input      | [input.tsx](../frontend/src/components/ui/input.tsx) | – |
| Card       | [card.tsx](../frontend/src/components/ui/card.tsx) | Header, Content, Footer, Title |
| Badge      | [badge.tsx](../frontend/src/components/ui/badge.tsx) | default, secondary, destructive, outline, **priority-high/medium/low**, **status-open/implemented/dismissed** |
| Alert      | [alert.tsx](../frontend/src/components/ui/alert.tsx) | default, destructive |
| Toggle     | [toggle.tsx](../frontend/src/components/ui/toggle.tsx) | default, outline |
| Switch     | [switch.tsx](../frontend/src/components/ui/switch.tsx) | – |
| Tooltip    | [tooltip.tsx](../frontend/src/components/ui/tooltip.tsx) | – |
| Dialog     | [dialog.tsx](../frontend/src/components/ui/dialog.tsx) | (Modal) |
| Skeleton   | [skeleton.tsx](../frontend/src/components/ui/skeleton.tsx) | – |

---

## Screenshots

Aktuelle Screens findest du unter [`docs/screenshots/`](screenshots/).

| Screen           | Datei                                   |
|------------------|-----------------------------------------|
| Landing — Hero   | [landing-hero.png](screenshots/landing-hero.png)             |
| Landing — How It Works | [landing-how-it-works.png](screenshots/landing-how-it-works.png) |
| Dashboard        | [dashboard.png](screenshots/dashboard.png) |
| Savings Simulator | [savings-simulator.png](screenshots/savings-simulator.png)  |

Beim Erweitern bitte denselben Stil verwenden (Desktop 1440px, Dark Theme, ohne Browser-Chrome).
