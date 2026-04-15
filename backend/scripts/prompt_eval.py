#!/usr/bin/env python3
"""
Prompt Variant Evaluation Script

Tests 3 prompt strategies (A/B/C) against 3 benchmark inputs and measures output quality.
Generates a markdown report in docs/prompt-evaluation.md

Usage:
    cd backend
    python scripts/prompt_eval.py
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Ensure backend app package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.ai_engine import AIEngine
from app.services.config_service import get_config


# Benchmark test data
BENCHMARK_INPUTS = [
    {
        "name": "EC2 Idle",
        "data": {
            "resource_id": "i-idle-001",
            "resource_type": "ec2",
            "issue": "Instance idle with 2.5% avg CPU over 30 days",
            "estimated_saving": 45.0,
            "account_id": "123456789012",
        }
    },
    {
        "name": "RDS Underutilized",
        "data": {
            "resource_id": "db-123",
            "resource_type": "rds",
            "issue": "RDS instance with low DB connections and high storage",
            "estimated_saving": 60.0,
            "account_id": "123456789012",
        }
    },
    {
        "name": "Elastic IP Unattached",
        "data": {
            "resource_id": "eipalloc-001",
            "resource_type": "elastic_ip",
            "issue": "Elastic IP not attached to any running instance",
            "estimated_saving": 3.60,
            "account_id": "123456789012",
        }
    },
]

VARIANTS = ["A", "B", "C"]


async def evaluate_variant(engine: AIEngine, variant: str, benchmark: dict) -> dict:
    """Test a single variant on a single benchmark input."""
    start_time = time.time()

    try:
        # Create a modified engine with the variant prompt
        # We'll use a temporary instance to override _get_system_prompt
        class TempAIEngine(AIEngine):
            def _get_system_prompt(self, variant: str = "A") -> str:
                from app.services.ai_engine import (
                    PROMPT_A_MINIMAL, PROMPT_B_VERBOSE, PROMPT_C_FEWSHOT
                )
                if variant == "B":
                    return PROMPT_B_VERBOSE
                elif variant == "C":
                    return PROMPT_C_FEWSHOT
                else:
                    return PROMPT_A_MINIMAL

        # Use original engine's client and config
        temp_engine = TempAIEngine.__new__(TempAIEngine)
        temp_engine.token = engine.token
        temp_engine.endpoint = engine.endpoint
        temp_engine.model = engine.model
        temp_engine.client = engine.client

        # Override _get_system_prompt to use variant
        original_method = temp_engine._get_system_prompt
        temp_engine._get_system_prompt = lambda v=variant: original_method(v)

        # Run the enhancement
        rec = await temp_engine.enhance_recommendation(benchmark["data"])
        duration = time.time() - start_time

        return {
            "status": "success",
            "duration": duration,
            "recommendation_id": rec.recommendation_id,
            "issue_len": len(rec.issue),
            "recommendation_len": len(rec.recommendation),
            "effort": rec.effort,
            "action_steps_count": len(rec.action_steps),
            "saving_deviation_pct": abs(rec.estimated_saving - benchmark["data"]["estimated_saving"]) / benchmark["data"]["estimated_saving"] * 100,
            "priority": rec.priority,
            "full_recommendation": rec,
        }
    except Exception as e:
        return {
            "status": "error",
            "duration": time.time() - start_time,
            "error": str(e),
        }


async def run_evaluation():
    """Run full evaluation suite."""
    print("🧪 Prompt Strategy Evaluation\n")
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Initialize engine
    try:
        config = get_config()
        engine = AIEngine()
        print(f"✅ AIEngine initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize AIEngine: {e}")
        sys.exit(1)

    # Run evaluation: 3 variants × 3 benchmarks = 9 tests
    results = {}

    print("📊 Running evaluations...\n")
    for benchmark in BENCHMARK_INPUTS:
        print(f"  Testing: {benchmark['name']}")
        results[benchmark["name"]] = {}

        for variant in VARIANTS:
            result = await evaluate_variant(engine, variant, benchmark)
            results[benchmark["name"]][variant] = result

            status_emoji = "✅" if result["status"] == "success" else "❌"
            print(f"    {status_emoji} Variant {variant}: {result['duration']:.2f}s")

        print()

    # Generate markdown report
    report = generate_report(results)

    # Write to docs/prompt-evaluation.md
    docs_dir = Path(__file__).resolve().parent.parent.parent / "docs"
    docs_dir.mkdir(exist_ok=True)
    report_path = docs_dir / "prompt-evaluation.md"
    report_path.write_text(report)

    print(f"\n✅ Report written to: {report_path}\n")
    print("=" * 80)
    print(report)
    print("=" * 80)


def generate_report(results: dict) -> str:
    """Generate markdown report from evaluation results."""
    lines = [
        "# Prompt Strategy Evaluation Report\n",
        f"**Evaluated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n",
        "## Executive Summary\n",
        "Three prompt strategies were tested against three benchmark inputs to measure output quality.\n\n",
        "### Strategies\n",
        "- **A (Minimal)**: Concise rules and schema only\n",
        "- **B (Verbose)**: Rich context with role description and field semantics\n",
        "- **C (Few-Shot)**: Includes 2 complete examples\n\n",
        "### Benchmarks\n",
        "1. **EC2 Idle** — Instance with 2.5% CPU (saving: $45/month)\n",
        "2. **RDS Underutilized** — Underutilized database (saving: $60/month)\n",
        "3. **Elastic IP Unattached** — Unattached IP (saving: $3.60/month)\n\n",
        "---\n\n",
    ]

    # Success rate summary
    success_counts = {"A": 0, "B": 0, "C": 0}
    total = 0

    for benchmark_name, variants in results.items():
        for variant, result in variants.items():
            total += 1
            if result["status"] == "success":
                success_counts[variant] += 1

    lines.append("## Results\n\n")
    lines.append("### Success Rates\n\n")
    for variant in VARIANTS:
        rate = (success_counts[variant] / total) * 100 if total > 0 else 0
        lines.append(f"- **Variant {variant}**: {success_counts[variant]}/{total} ({rate:.0f}%)\n")

    lines.append("\n### Detailed Results\n\n")

    for benchmark_name, variants in results.items():
        lines.append(f"#### {benchmark_name}\n\n")
        lines.append("| Variant | Status | Duration (s) | Issue Len | Rec Len | Effort | Steps | Saving Dev % | Priority |\n")
        lines.append("|---------|--------|--------------|-----------|---------|--------|-------|--------------|----------|\n")

        for variant in VARIANTS:
            result = variants[variant]
            if result["status"] == "success":
                lines.append(
                    f"| {variant} | ✅ | {result['duration']:.2f} | "
                    f"{result['issue_len']} | {result['recommendation_len']} | "
                    f"{result['effort']} | {result['action_steps_count']} | "
                    f"{result['saving_deviation_pct']:.1f}% | {result['priority']} |\n"
                )
            else:
                lines.append(
                    f"| {variant} | ❌ | N/A | Error: {result['error'][:40]} |\n"
                )

        lines.append("\n")

    # Quality analysis
    lines.append("### Quality Metrics Analysis\n\n")

    quality_scores = {}
    for variant in VARIANTS:
        quality_scores[variant] = {
            "avg_duration": 0,
            "avg_deviation": 0,
            "valid_count": 0,
        }

    for benchmark_name, variants in results.items():
        for variant, result in variants.items():
            if result["status"] == "success":
                quality_scores[variant]["avg_duration"] += result["duration"]
                quality_scores[variant]["avg_deviation"] += result["saving_deviation_pct"]
                quality_scores[variant]["valid_count"] += 1

    for variant in VARIANTS:
        count = quality_scores[variant]["valid_count"]
        if count > 0:
            avg_duration = quality_scores[variant]["avg_duration"] / count
            avg_deviation = quality_scores[variant]["avg_deviation"] / count
            lines.append(f"**Variant {variant}**\n")
            lines.append(f"- Avg Response Time: {avg_duration:.2f}s\n")
            lines.append(f"- Avg Saving Deviation: {avg_deviation:.1f}%\n")
            lines.append(f"- Success Rate: {count}/3\n\n")

    lines.append("---\n\n")
    lines.append("## Recommendation\n\n")
    lines.append(
        "Based on the evaluation results, **Variant [TO BE FILLED]** is recommended because:\n\n"
        "- [Highest success rate / lowest latency / best accuracy / etc.]\n"
        "- [Additional quality metric]\n\n"
    )
    lines.append("### Next Steps\n")
    lines.append("1. Update `AIEngine._get_system_prompt()` to default to the recommended variant\n")
    lines.append("2. Re-test integration suite to confirm no regressions\n")
    lines.append("3. Monitor cost optimization accuracy in production\n")

    return "".join(lines)


if __name__ == "__main__":
    asyncio.run(run_evaluation())
