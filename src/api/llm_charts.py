"""
LLM-Powered Chart Recommendation Engine
=========================================
Uses Qwen3-Next-80B-A3B-Instruct to generate context-aware Recharts
visualization strategies, then enriches the interactive_charts data
with LLM-generated narratives and recommendations.

Model tier: BALANCED (Qwen3-Next-80B) for chart strategy
Model tier: REASONING (DeepSeek-R1) for chart insight narratives
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def generate_llm_chart_recommendations(
    df,
    data_context: dict,
    stats: dict,
    profile: dict,
) -> dict:
    """
    Main entry point: uses Qwen3-Next-80B to recommend the best chart
    configurations for this specific dataset, then DeepSeek-R1 to generate
    insight narratives for each chart.

    Returns a dict with:
      - recommendations: list of chart configs for Recharts
      - narratives: insight text per chart
      - visualization_strategy: overall approach
    """
    from src.services.llm import get_llm
    from src.models.types import LLMTier
    from src.prompts.templates import (
        PROMPT_CHART_RECOMMENDATIONS,
        PROMPT_CHART_INSIGHT_NARRATIVE,
        SYSTEM_PROMPT_CHART_STRATEGIST,
        SYSTEM_PROMPT_REASONING_ANALYST,
    )

    llm = await get_llm()
    domain = data_context.get("business_domain", "General Business")

    # ── Build context for chart recommendations ────────────────────────────
    numeric_stats = stats.get("numeric", {})
    correlations = stats.get("correlations", [])

    top_correlations = [
        f"{c['var1']} ↔ {c['var2']}: r={c['r']:.2f} ({c.get('strength', '')})"
        for c in correlations[:5]
    ] if correlations else ["No significant correlations"]

    patterns = data_context.get("patterns", [])
    pattern_descriptions = [p.get("description", "") for p in patterns[:4]]

    business_questions = "\n".join(
        f"- {q}" for q in data_context.get("business_questions", [])[:5]
    ) or "- What drives performance?\n- How do segments compare?\n- Are there trends?"

    # ── Step 1: Chart Recommendations (Qwen3-Next-80B) ────────────────────
    rec_prompt = PROMPT_CHART_RECOMMENDATIONS.format(
        system_prompt=SYSTEM_PROMPT_CHART_STRATEGIST,
        domain=domain,
        row_count=profile.get("row_count", 0),
        key_metrics=", ".join(data_context.get("key_metrics", [])[:8]),
        category_columns=", ".join(data_context.get("category_columns", [])[:5]),
        date_columns=", ".join(data_context.get("date_columns", [])[:3]),
        price_columns=", ".join(data_context.get("price_columns", [])[:3]),
        top_correlations="\n".join(f"- {c}" for c in top_correlations),
        patterns="\n".join(f"- {p}" for p in pattern_descriptions) or "None detected",
        business_questions=business_questions,
    )

    logger.info(f"[ChartLLM] Requesting chart recommendations (Qwen3-Next-80B) for domain={domain}")

    rec_raw = await llm.complete(
        prompt=rec_prompt,
        model=LLMTier.BALANCED,
        temperature=0.1,
        max_tokens=3000,
        json_mode=True,
    )

    recommendations = _parse_chart_recommendations(rec_raw)
    logger.info(f"[ChartLLM] Got {len(recommendations)} chart recommendations")

    # ── Step 2: Chart Insight Narratives (DeepSeek-R1) ────────────────────
    narratives = {}
    if recommendations:
        # Build context for narrative generation
        charts_context = []
        for rec in recommendations[:6]:  # Limit to 6 to avoid huge prompts
            chart_ctx = {
                "chart_id": rec.get("id", ""),
                "title": rec.get("title", ""),
                "type": rec.get("recharts_type", ""),
                "x_column": rec.get("x_column", ""),
                "y_columns": rec.get("y_columns", []),
                "aggregation": rec.get("aggregation", "mean"),
            }
            # Add relevant stats for this chart's columns
            for col in [rec.get("x_column")] + (rec.get("y_columns") or []):
                if col and col in numeric_stats:
                    chart_ctx[f"{col}_stats"] = {
                        k: numeric_stats[col][k]
                        for k in ["mean", "median", "min", "max", "std", "skewness"]
                        if k in numeric_stats[col]
                    }
            charts_context.append(chart_ctx)

        narr_prompt = PROMPT_CHART_INSIGHT_NARRATIVE.format(
            system_prompt=SYSTEM_PROMPT_REASONING_ANALYST,
            domain=domain,
            key_metrics=", ".join(data_context.get("key_metrics", [])[:6]),
            business_questions=business_questions,
            charts_context_json=json.dumps(charts_context, indent=2, default=str),
            stats_json=json.dumps(numeric_stats, indent=2, default=str),
        )

        logger.info(f"[ChartLLM] Requesting chart narratives (DeepSeek-R1)")

        narr_raw = await llm.complete(
            prompt=narr_prompt,
            model=LLMTier.REASONING,
            temperature=0.4,
            max_tokens=3000,
        )

        narratives = _parse_chart_narratives(narr_raw)
        logger.info(f"[ChartLLM] Got narratives for {len(narratives)} charts")

    return {
        "success": True,
        "recommendations": recommendations,
        "narratives": narratives,
        "domain": domain,
        "total_charts": len(recommendations),
    }


def _parse_chart_recommendations(raw: str) -> list[dict]:
    """Parse chart recommendation JSON from LLM."""
    import re
    if not raw:
        return []

    clean = re.sub(r"```(?:json)?\s*", "", raw).replace("```", "").strip()

    try:
        parsed = json.loads(clean)
        recs = parsed.get("recommendations", [])
    except json.JSONDecodeError:
        match = re.search(r'\{.*"recommendations".*\}', clean, re.DOTALL)
        if match:
            try:
                recs = json.loads(match.group()).get("recommendations", [])
            except Exception:
                return []
        else:
            return []

    # Normalize and validate each recommendation
    valid = []
    seen_configs = set()

    for rec in recs:
        if not isinstance(rec, dict):
            continue

        # Dedup by (type, x_col, y_cols)
        key = (
            rec.get("recharts_type", ""),
            rec.get("x_column", ""),
            str(sorted(rec.get("y_columns", []))),
        )
        if key in seen_configs:
            continue
        seen_configs.add(key)

        valid.append({
            "id": rec.get("id", f"chart_{len(valid)+1:03d}"),
            "title": rec.get("title", "Chart"),
            "business_question": rec.get("business_question", ""),
            "recharts_type": rec.get("recharts_type", "BarChart"),
            "x_column": rec.get("x_column", ""),
            "y_columns": rec.get("y_columns", []),
            "color_column": rec.get("color_column"),
            "aggregation": rec.get("aggregation", "mean"),
            "sort_by": rec.get("sort_by", "value_desc"),
            "chart_config": rec.get("chart_config", {
                "stacked": False,
                "show_legend": True,
                "show_brush": False,
                "show_reference_line": False,
                "reference_value": None,
            }),
            "insight_hint": rec.get("insight_hint", ""),
            "priority": rec.get("priority", 99),
        })

    # Sort by priority
    valid.sort(key=lambda x: x.get("priority", 99))
    return valid[:8]


def _parse_chart_narratives(raw: str) -> dict[str, dict]:
    """Parse chart narrative JSON, returns {chart_id: narrative_dict}."""
    import re
    if not raw:
        return {}

    clean = re.sub(r"```(?:json)?\s*", "", raw).replace("```", "").strip()

    try:
        parsed = json.loads(clean)
        narratives_list = parsed.get("chart_narratives", [])
    except json.JSONDecodeError:
        match = re.search(r'\{.*"chart_narratives".*\}', clean, re.DOTALL)
        if match:
            try:
                narratives_list = json.loads(match.group()).get("chart_narratives", [])
            except Exception:
                return {}
        else:
            return {}

    result = {}
    for narr in narratives_list:
        if isinstance(narr, dict) and narr.get("chart_id"):
            result[narr["chart_id"]] = narr

    return result


async def enrich_analytics_with_llm(
    analytics_data: dict,
    data_context: dict,
    stats: dict,
    profile: dict,
) -> dict:
    """
    Post-process the analytics data dict with LLM-generated chart recommendations.
    Adds 'llm_charts' key with Qwen/DeepSeek powered recommendations.
    """
    try:
        import pandas as pd
        df_placeholder = pd.DataFrame()  # Not needed for recommendation generation

        llm_result = await generate_llm_chart_recommendations(
            df=df_placeholder,
            data_context=data_context,
            stats=stats,
            profile=profile,
        )

        analytics_data["llm_charts"] = llm_result
        analytics_data["llm_powered"] = True

    except Exception as e:
        logger.error(f"[ChartLLM] Enrichment failed: {e}")
        analytics_data["llm_charts"] = {"success": False, "recommendations": [], "narratives": {}}
        analytics_data["llm_powered"] = False

    return analytics_data
