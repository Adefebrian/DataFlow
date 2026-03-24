"""
Report Generation Agent — Qwen3-Next-80B-A3B-Instruct
=======================================================
Uses the BALANCED tier model for professional narrative generation.
Qwen3-Next-80B excels at coherent, domain-aware business prose.
"""

import json
import logging
from src.services.llm import get_llm
from src.models.types import LLMTier
from src.prompts.templates import PROMPT_REPORT_NARRATIVE, SYSTEM_PROMPT_DATA_ANALYST

logger = logging.getLogger(__name__)


class ReportGenerationAgent:
    async def generate(
        self,
        filename: str,
        row_count: int,
        stats: dict,
        insights: list[dict],
        cleaning_summary: dict,
        data_context: dict | None = None,
    ) -> str:
        if data_context is None:
            data_context = {}

        domain = data_context.get("business_domain", "General Business")
        industry_benchmarks = data_context.get("industry_benchmarks", {})

        # Build stats summary — only numeric, top 12 columns
        numeric_stats = stats.get("numeric", {})
        stats_summary = {}
        for col, col_stats in list(numeric_stats.items())[:12]:
            if "mean" in col_stats:
                friendly = data_context.get("friendly_names", {}).get(col, col)
                stats_summary[friendly] = {
                    "mean": round(col_stats["mean"], 2),
                    "median": round(col_stats["median"], 2),
                    "min": round(col_stats["min"], 2),
                    "max": round(col_stats["max"], 2),
                    "std": round(col_stats.get("std", 0), 2),
                    "total": round(col_stats.get("total", 0), 2),
                }

        # Build numbered insights list
        if insights:
            insights_list = "\n".join(
                f"{i+1}. [{ins.get('business_impact', 'medium').upper()}] "
                f"{ins.get('title', '')}: {ins.get('description', '')}"
                for i, ins in enumerate(insights[:8])
            )
        else:
            insights_list = "No significant patterns found in this dataset."

        quality_score = self._calculate_quality(cleaning_summary)

        # Industry context
        if industry_benchmarks:
            industry_context = "Industry benchmarks:\n" + "\n".join(
                f"- {k}: {v}" for k, v in list(industry_benchmarks.items())[:5]
            )
        else:
            industry_context = f"Domain: {domain} — no specific benchmarks available."

        prompt = PROMPT_REPORT_NARRATIVE.format(
            system_prompt=SYSTEM_PROMPT_DATA_ANALYST,
            filename=filename,
            row_count=row_count,
            domain=domain,
            analysis_date="today",
            stats_summary_json=json.dumps(stats_summary, default=str, indent=2),
            insight_count=len(insights),
            insights_list_numbered=insights_list,
            cleaning_summary=json.dumps(cleaning_summary, default=str),
            quality_score=quality_score,
            industry_context=industry_context,
        )

        llm = await get_llm()

        logger.info(f"[ReportGen] Generating report with Qwen3-Next-80B for domain={domain}")

        # BALANCED tier — Qwen3-Next-80B for business narrative
        response = await llm.complete(
            prompt=prompt,
            model=LLMTier.BALANCED,
            temperature=0.3,
            max_tokens=3000,
        )

        if not response:
            logger.warning("[ReportGen] Empty response from Qwen3-Next-80B")
            return self._fallback_report(filename, row_count, stats_summary, insights, quality_score, domain)

        logger.info(f"[ReportGen] Report generated, length={len(response)}")
        return response

    def _calculate_quality(self, cleaning_summary: dict) -> float:
        total_issues = cleaning_summary.get("total_issues", 0)
        if total_issues == 0:
            return 100.0
        return max(0, 100 - (total_issues * 2))

    def _fallback_report(
        self, filename: str, row_count: int, stats: dict, insights: list, quality: float, domain: str
    ) -> str:
        """Simple fallback report when LLM is unavailable."""
        lines = [
            f"## Executive Summary",
            f"Analysis of {filename} ({row_count:,} records) in the {domain} domain. "
            f"Data quality score: {quality}/100.",
            "",
            "## Key Findings",
        ]
        for ins in insights[:5]:
            lines.append(f"- {ins.get('title', '')}: {ins.get('description', '')}")
        lines += [
            "",
            "## Recommendations",
            "1. Review high-impact insights identified above.",
            "2. Investigate anomalies for data quality issues.",
            "3. Set up monitoring for key metrics.",
        ]
        return "\n".join(lines)
