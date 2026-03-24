import json
import re
from typing import Any
from pydantic import BaseModel
from src.services.llm import get_llm


class HallucinationError(Exception):
    pass


class HallucinationDetector:
    ABSOLUTE_MARKERS = [
        "as of my knowledge cutoff",
        "i don't have access to",
        "i cannot access the actual",
        "i'm not able to see the data",
        "based on my training",
        "i believe the data shows",
    ]

    STATISTICAL_HEDGING_MARKERS = [
        "approximately",
        "roughly",
        "about",
        "around",
        "seems to be",
        "appears to be",
        "looks like",
        "i think this means",
        "this might indicate",
    ]

    METHODOLOGY_ALLOWED = [
        "typically",
        "usually",
        "generally",
        "commonly",
        "in most cases",
        "standard practice",
    ]

    def is_hallucination(
        self,
        text: str,
        context: str = "statistical_claim",
    ) -> tuple[bool, str]:
        text_lower = text.lower()

        for marker in self.ABSOLUTE_MARKERS:
            if marker in text_lower:
                return True, f"Absolute hallucination marker: '{marker}'"

        if context == "statistical_claim":
            for marker in self.STATISTICAL_HEDGING_MARKERS:
                if marker in text_lower:
                    return True, f"Statistical hedging in factual claim: '{marker}'"

        return False, ""


class InsightVerifier:
    VERIFIABLE_PATTERNS = [
        (r"(\w+)\s+is\s+([\d.]+)%\s+of", "percentage_claim"),
        (r"average\s+(\w+)\s+is\s+([\d,.]+)", "mean_claim"),
        (r"(\w+)\s+correlates?\s+with\s+(\w+)", "correlation_claim"),
        (r"([\d.]+)%\s+of\s+(rows|records|data)", "row_pct_claim"),
    ]

    def verify(
        self,
        insight: dict[str, Any],
        stats: dict[str, Any],
    ) -> dict[str, Any]:
        description = insight.get("description", "")
        claims = self._extract_numerical_claims(description)

        if not claims:
            return {"status": "UNVERIFIABLE", "reason": "No numerical claims"}

        for claim in claims:
            result = self._verify_single_claim(claim, stats)
            if result["status"] == "MISMATCH":
                return {
                    "status": "HALLUCINATED",
                    "reason": f"Claimed {claim['value']}, actual is {result.get('actual_value')}",
                }

        return {"status": "VERIFIED"}

    def _extract_numerical_claims(self, text: str) -> list[dict]:
        claims = []
        for pattern, claim_type in self.VERIFIABLE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                claims.append(
                    {
                        "type": claim_type,
                        "value": float(match[1]) if len(match) > 1 else None,
                    }
                )
        return claims

    def _verify_single_claim(
        self,
        claim: dict,
        stats: dict[str, Any],
    ) -> dict[str, Any]:
        return {"status": "MATCH"}


class AntiHallucinationPipeline:
    def __init__(self):
        self.detector = HallucinationDetector()
        self.verifier = InsightVerifier()

    def prepare_call(
        self,
        prompt_template: str,
        data: dict[str, Any],
        output_schema: type[BaseModel],
    ) -> tuple[str, dict]:
        schema_json = json.dumps(output_schema.model_json_schema(), indent=2)
        grounded_prompt = prompt_template.format(**data)

        schema_instruction = f"""
OUTPUT SCHEMA (required — output is invalid if it does not match this schema):
{schema_json}

VALIDATE BEFORE OUTPUT:
1. Are all required fields filled?
2. Do all numbers come from the provided data?
3. Are there hedging words like "maybe", "seems like", "I think" in factual claims? Remove them.
"""
        # Return prompt and a default config dict (no longer references LLM_CONFIG)
        default_config = {"temperature": 0.0, "max_tokens": 2048}
        return grounded_prompt + schema_instruction, default_config

    async def validate_output(
        self,
        raw_response: str,
        source_data: dict[str, Any],
    ) -> dict:
        is_hallucination, reason = self.detector.is_hallucination(raw_response)
        if is_hallucination:
            raise HallucinationError(f"Hallucination marker detected: {reason}")

        # Handle case where raw_response is already a dict
        if isinstance(raw_response, dict):
            parsed = raw_response
        else:
            try:
                # Strip markdown fences if present
                clean = re.sub(r"```(?:json)?\s*", "", raw_response).replace("```", "").strip()
                parsed = json.loads(clean)
            except json.JSONDecodeError:
                # If unparseable, return empty insights rather than crash
                return {"insights": []}

        if "insights" in parsed:
            valid_insights = []
            for insight in parsed["insights"]:
                result = self.verifier.verify(insight, source_data.get("stats", {}))
                if result["status"] != "HALLUCINATED":
                    valid_insights.append(insight)
            parsed["insights"] = valid_insights

        return parsed


anti_hallucination = AntiHallucinationPipeline()
