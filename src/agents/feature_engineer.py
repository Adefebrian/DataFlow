"""
Feature Engineering Agent — Qwen3-Next-80B-A3B-Instruct
=========================================================
Uses the BALANCED tier model for domain-aware feature suggestions.
Qwen3-Next-80B understands business context well enough to suggest
meaningful features tailored to the detected domain.
"""

import pandas as pd
import json
import logging
from src.models.types import FeatureSuggestion, LLMTier
from src.services.llm import get_llm
from src.agents.feature_validator import FeatureSuggestionValidator
from src.prompts.templates import PROMPT_FEATURE_SUGGESTIONS, SYSTEM_PROMPT_DATA_ANALYST

logger = logging.getLogger(__name__)


class FeatureEngineerAgent:
    def __init__(self):
        self.validator = FeatureSuggestionValidator()

    async def suggest_features(
        self,
        df: pd.DataFrame,
        data_context: dict | None = None,
    ) -> list[FeatureSuggestion]:
        if data_context is None:
            data_context = {}

        domain = data_context.get("business_domain", "General Business")

        try:
            column_info = [
                {
                    "name": col,
                    "dtype": self._classify_dtype(df[col]),
                    "unique_count": int(df[col].nunique()),
                    "sample_values": df[col].dropna().head(3).tolist(),
                }
                for col in df.columns
            ]

            sample_csv = df.head(20).to_csv(index=False)

            prompt = PROMPT_FEATURE_SUGGESTIONS.format(
                system_prompt=SYSTEM_PROMPT_DATA_ANALYST,
                column_info_json=json.dumps(column_info, default=str),
                sample_csv=sample_csv,
                domain=domain,
            )

            llm = await get_llm()

            logger.info(f"[FeatureEngineer] Running Qwen3-Next-80B for domain={domain}")

            # BALANCED tier — Qwen3-Next-80B for domain-aware feature suggestions
            raw = await llm.complete(
                prompt=prompt,
                model=LLMTier.BALANCED,
                temperature=0.0,
                max_tokens=2048,
                json_mode=True,
            )

            if not raw:
                return []

            result = self._parse_response(raw)
            suggestions = []

            for s in result.get("suggestions", []):
                try:
                    feat = FeatureSuggestion(**{
                        k: v for k, v in s.items()
                        if k in FeatureSuggestion.model_fields
                    })
                    validation = self.validator.validate(feat, df)
                    if validation.valid and feat.confidence >= 0.5:
                        suggestions.append(feat)
                        logger.info(f"[FeatureEngineer] Accepted: {feat.name} (conf={feat.confidence:.2f})")
                    else:
                        logger.debug(f"[FeatureEngineer] Rejected: {s.get('name')} — validation={validation.valid}, conf={s.get('confidence', 0)}")
                except Exception as e:
                    logger.warning(f"[FeatureEngineer] Skipping feature: {e}")
                    continue

            return suggestions

        except Exception as e:
            logger.error(f"[FeatureEngineer] Error: {e}")
            return []

    def _parse_response(self, raw: str) -> dict:
        """Parse JSON from LLM response, handling markdown fences."""
        import re
        clean = re.sub(r"```(?:json)?\s*", "", raw).replace("```", "").strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            match = re.search(r'\{.*"suggestions".*\}', clean, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
        return {}

    def _classify_dtype(self, series: pd.Series) -> str:
        if pd.api.types.is_numeric_dtype(series):
            return "numeric"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        elif series.nunique() <= 15:
            return "categorical"
        return "string"

    def apply_features(
        self,
        df: pd.DataFrame,
        suggestions: list[FeatureSuggestion],
    ) -> pd.DataFrame:
        for suggestion in suggestions:
            try:
                df[suggestion.name] = df.eval(suggestion.formula)
                logger.info(f"[FeatureEngineer] Applied: {suggestion.name}")
            except Exception as e:
                logger.warning(f"[FeatureEngineer] Could not apply {suggestion.name}: {e}")
        return df
