"""
Insight Generation Agent — DeepSeek-R1-0528
=============================================
Uses DeepSeek's reasoning model to generate deep, data-grounded insights.
The R1 model "thinks" before answering — producing far more accurate and
nuanced insights than standard instruction-following models.
"""

import json
import logging
from src.models.types import DataProfile, LLMTier
from src.services.llm import get_llm
from src.services.anti_halucination import anti_hallucination
from src.prompts.templates import (
    PROMPT_INSIGHT_GENERATION,
    PROMPT_CORRELATION_INTERPRETATION,
    SYSTEM_PROMPT_REASONING_ANALYST,
)

logger = logging.getLogger(__name__)


class InsightGenerationAgent:
    """
    Uses DeepSeek-R1-0528 (reasoning tier) for deep pattern analysis.
    Also runs correlation interpretation as a second LLM pass for richer insights.
    """

    async def generate(
        self,
        profile: DataProfile,
        stats: dict,
        data_context: dict | None = None,
    ) -> list[dict]:
        if data_context is None:
            data_context = {}

        llm = await get_llm()

        # ── Build correlation table ────────────────────────────────────────
        corr_pairs = profile.high_correlation_pairs[:8]
        if corr_pairs:
            correlation_table = "\n".join(
                f"- {p['col_a']} ↔ {p['col_b']}: r={p['correlation']}"
                for p in corr_pairs
            )
        else:
            correlation_table = "No significant correlations detected (|r| > 0.4)"

        # ── Build anomaly summary ──────────────────────────────────────────
        anomalies = []
        for col, col_stats in stats.get("numeric", stats).items():
            if isinstance(col_stats, dict) and "outlier_count" in col_stats:
                if col_stats["outlier_count"] > 0:
                    anomalies.append(
                        f"- {col}: {col_stats['outlier_count']} outliers "
                        f"({col_stats.get('outlier_pct', 0):.1f}%)"
                    )
        anomaly_summary = (
            "\n".join(anomalies) if anomalies else "No anomalies detected"
        )

        # ── Build patterns summary ─────────────────────────────────────────
        patterns = data_context.get("patterns", [])
        if patterns:
            patterns_summary = "\n".join(
                f"- {p.get('type', '')}: {p.get('description', '')}"
                for p in patterns[:6]
            )
        else:
            patterns_summary = "No specific patterns flagged"

        # ── Key metrics & business questions ──────────────────────────────
        key_metrics = data_context.get("key_metrics", [])
        business_questions = data_context.get("business_questions", [])
        domain = data_context.get("business_domain", "General Business")

        # ── Main insight generation prompt (DeepSeek-R1) ──────────────────
        stats_for_prompt = {}
        if "numeric" in stats:
            stats_for_prompt = stats["numeric"]
        else:
            stats_for_prompt = {
                k: v for k, v in stats.items()
                if isinstance(v, dict) and "mean" in v
            }

        prompt = PROMPT_INSIGHT_GENERATION.format(
            system_prompt=SYSTEM_PROMPT_REASONING_ANALYST,
            row_count=profile.row_count,
            column_count=profile.column_count,
            domain=domain,
            profiled_at="today",
            stats_json=json.dumps(stats_for_prompt, default=str, indent=2),
            correlation_table=correlation_table,
            patterns_summary=patterns_summary,
            anomaly_summary=anomaly_summary,
            key_metrics=", ".join(key_metrics[:8]) if key_metrics else "Not identified",
            business_questions="\n".join(
                f"- {q}" for q in business_questions[:5]
            ) if business_questions else "- What drives performance?\n- Are there anomalies?\n- How do segments compare?",
        )

        logger.info(f"[InsightGen] Running DeepSeek-R1 for domain={domain}, cols={profile.column_count}")

        # Use REASONING tier — DeepSeek-R1-0528
        raw_response = await llm.complete(
            prompt=prompt,
            model=LLMTier.REASONING,
            temperature=0.6,
            max_tokens=8000,
        )

        if not raw_response:
            logger.warning("[InsightGen] Empty response from DeepSeek-R1")
            return []

        insights = self._parse_insights(raw_response)

        # ── Second pass: correlation interpretation ─────────────────────
        # Only if we have meaningful correlations
        if len(corr_pairs) >= 2:
            corr_insights = await self._interpret_correlations(
                llm=llm,
                corr_pairs=corr_pairs,
                stats=stats_for_prompt,
                domain=domain,
                key_metrics=key_metrics,
                row_count=profile.row_count,
            )
            insights.extend(corr_insights)

        # ── Validate against actual data ───────────────────────────────
        try:
            validated = await anti_hallucination.validate_output(
                json.dumps({"insights": insights}),
                {"stats": stats_for_prompt},
            )
            insights = validated.get("insights", insights)
        except Exception as e:
            logger.warning(f"[InsightGen] Anti-hallucination check skipped: {e}")

        logger.info(f"[InsightGen] Generated {len(insights)} insights")
        return insights

    def _parse_insights(self, raw: str) -> list[dict]:
        """Parse and validate insight JSON from LLM response."""
        import re

        # Strip any markdown code fences
        clean = re.sub(r"```(?:json)?\s*", "", raw).replace("```", "").strip()

        try:
            parsed = json.loads(clean)
            insights = parsed.get("insights", [])
        except json.JSONDecodeError:
            # Try extracting JSON object
            match = re.search(r'\{.*"insights".*\}', clean, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group())
                    insights = parsed.get("insights", [])
                except Exception:
                    logger.error("[InsightGen] Could not parse insight JSON")
                    return []
            else:
                logger.error(f"[InsightGen] No JSON found in response: {raw[:200]}")
                return []

        # Validate and normalize each insight
        valid_insights = []
        for ins in insights:
            if not isinstance(ins, dict):
                continue
            if ins.get("confidence", 0) < 0.70:
                continue
            if not ins.get("title") or not ins.get("description"):
                continue

            # Normalize fields
            normalized = {
                "title": str(ins.get("title", ""))[:80],
                "description": str(ins.get("description", ""))[:400],
                "confidence": float(ins.get("confidence", 0.75)),
                "evidence": ins.get("evidence", [])[:3],
                "type": ins.get("type", "distribution"),
                "affected_columns": ins.get("affected_columns", []),
                "business_impact": ins.get("business_impact", "medium"),
                "recommended_action": ins.get("recommended_action", ""),
                # Legacy compatibility
                "impact": ins.get("business_impact", "medium"),
                "action": ins.get("recommended_action", ""),
                "category": "data_analysis",
            }
            valid_insights.append(normalized)

        return valid_insights

    async def _interpret_correlations(
        self,
        llm,
        corr_pairs: list[dict],
        stats: dict,
        domain: str,
        key_metrics: list[str],
        row_count: int,
    ) -> list[dict]:
        """Run a second DeepSeek-R1 pass to interpret correlation patterns."""
        from src.prompts.templates import PROMPT_CORRELATION_INTERPRETATION

        prompt = PROMPT_CORRELATION_INTERPRETATION.format(
            system_prompt=SYSTEM_PROMPT_REASONING_ANALYST,
            correlation_data_json=json.dumps(corr_pairs, indent=2),
            domain=domain,
            key_metrics=", ".join(key_metrics[:6]) if key_metrics else "N/A",
            row_count=row_count,
        )

        raw = await llm.complete(
            prompt=prompt,
            model=LLMTier.REASONING,
            temperature=0.5,
            max_tokens=3000,
        )

        if not raw:
            return []

        try:
            import re
            clean = re.sub(r"```(?:json)?\s*", "", raw).replace("```", "").strip()
            parsed = json.loads(clean)
            interpretations = parsed.get("interpretations", [])

            result = []
            for interp in interpretations[:3]:
                if not interp.get("is_actionable"):
                    continue
                result.append({
                    "title": f"{interp.get('var1', '')} ↔ {interp.get('var2', '')} Relationship",
                    "description": interp.get("business_meaning", "")[:300],
                    "confidence": float(interp.get("confidence", 0.75)),
                    "evidence": [
                        f"r={interp.get('r', 0):.2f}",
                        interp.get("leverage_opportunity", "")[:100],
                    ],
                    "type": "correlation",
                    "affected_columns": [interp.get("var1", ""), interp.get("var2", "")],
                    "business_impact": "high" if abs(interp.get("r", 0)) >= 0.7 else "medium",
                    "recommended_action": interp.get("leverage_opportunity", ""),
                    "impact": "high" if abs(interp.get("r", 0)) >= 0.7 else "medium",
                    "action": interp.get("leverage_opportunity", ""),
                    "category": "data_analysis",
                })
            return result

        except Exception as e:
            logger.warning(f"[InsightGen] Correlation interpretation failed: {e}")
            return []
