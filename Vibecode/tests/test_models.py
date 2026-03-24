import pytest
import sys

sys.path.insert(0, "/Users/brianeedsleep/Documents/Vibecode")

from src.models.types import (
    PipelineState,
    DataProfile,
    ColumnInfo,
    ChartSpec,
    InsightItem,
    FeatureSuggestion,
    NearDuplicateConfig,
    get_model_for_task,
    TASK_MODEL_MAPPING,
    LLMTier,
)


def test_pipeline_state_creation():
    state = PipelineState(
        job_id="test-001",
        dataset_id="ds-001",
        file_path="/test/data.csv",
        user_config={},
        stage_attempts={},
        errors=[],
        warnings=[],
    )

    assert state.job_id == "test-001"
    assert state.dataset_id == "ds-001"
    assert state.errors == []


def test_pipeline_state_with_profile():
    profile = DataProfile(
        row_count=100,
        column_count=5,
        columns=[],
        file_path="/test.csv",
        quality_score=95.0,
    )

    state = PipelineState(
        job_id="test-002",
        dataset_id="ds-002",
        file_path="/test.csv",
        user_config={},
        profile=profile.model_dump(),
        stage_attempts={},
        errors=[],
        warnings=[],
    )

    assert state.profile is not None
    assert state.profile.row_count == 100


def test_chart_spec():
    chart = ChartSpec(
        type="histogram", x="revenue", title="Revenue Distribution", bins=20
    )

    assert chart.type == "histogram"
    assert chart.x == "revenue"
    assert chart.bins == 20


def test_insight_item():
    insight = InsightItem(
        title="Revenue Growth",
        description="Revenue increased by 20%",
        confidence=0.95,
        evidence=["Revenue: 2040"],
        insight_type="trend",
        affected_columns=["revenue"],
        business_impact="high",
    )

    assert insight.title == "Revenue Growth"
    assert insight.confidence == 0.95
    assert insight.insight_type == "trend"


def test_near_duplicate_config():
    config = NearDuplicateConfig()
    assert config.threshold_pct == 0.85
    assert config.min_comparison_columns == 3


def test_near_duplicate_config_custom():
    config = NearDuplicateConfig(threshold_pct=0.9, exclude_columns=["id", "timestamp"])

    assert config.threshold_pct == 0.9
    assert "id" in config.exclude_columns


def test_get_model_for_task():
    model = get_model_for_task("classify_column_type")
    assert model == TASK_MODEL_MAPPING["classify_column_type"]

    model = get_model_for_task("insight_generation")
    assert model == TASK_MODEL_MAPPING["insight_generation"]


def test_llm_tier():
    assert LLMTier.FAST == "Qwen/Qwen2.5-VL-7B-Instruct"
    assert LLMTier.BALANCED == "meta-llama/Llama-3.3-70B-Instruct"
