import pytest
import sys

sys.path.insert(0, "/Users/brianeedsleep/Documents/Vibecode")

from src.services.anti_halucination import HallucinationDetector, InsightVerifier


def test_hallucination_detector_absolute_markers():
    detector = HallucinationDetector()

    text = "Based on my training data, I believe the data shows..."
    is_hallucination, reason = detector.is_hallucination(text)
    assert is_hallucination == True
    assert "Absolute hallucination marker" in reason


def test_hallucination_detector_statistical_hedging():
    detector = HallucinationDetector()

    text = "The revenue seems to be approximately 1000"
    is_hallucination, reason = detector.is_hallucination(
        text, context="statistical_claim"
    )
    assert is_hallucination == True
    assert "Statistical hedging" in reason


def test_hallucination_detector_methodology_allowed():
    detector = HallucinationDetector()

    text = "Isolation Forest typically uses contamination=0.05"
    is_hallucination, reason = detector.is_hallucination(
        text, context="statistical_claim"
    )
    assert is_hallucination == False


def test_hallucination_detector_clean_text():
    detector = HallucinationDetector()

    text = "Revenue is 2040.0 with standard deviation 416.87"
    is_hallucination, reason = detector.is_hallucination(text)
    assert is_hallucination == False


def test_insight_verifier_extract_claims():
    verifier = InsightVerifier()

    claims = verifier._extract_numerical_claims("Revenue is 50% of total")
    assert len(claims) == 1
    assert claims[0]["type"] == "percentage_claim"
