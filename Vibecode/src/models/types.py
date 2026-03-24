from __future__ import annotations
from typing import Union, NotRequired, Literal
from pydantic import Field, BaseModel
from typing import Any


class ColumnInfo(BaseModel):
    name: str
    dtype: Literal["numeric", "categorical", "datetime", "string", "boolean"]
    unique_count: int
    null_count: int
    sample_values: list[Any] = Field(default_factory=list)


class DataProfile(BaseModel):
    row_count: int
    column_count: int
    columns: list[ColumnInfo]
    file_path: str
    quality_score: float = Field(ge=0.0, le=100.0)
    high_correlation_pairs: list[dict[str, Any]] = Field(default_factory=list)


class CleaningAction(BaseModel):
    action_type: Literal[
        "fill_null", "remove_duplicates", "fix_type", "remove_outliers", "standardize"
    ]
    column: str | None = None
    original_value: Any | None = None
    new_value: Any | None = None
    rows_affected: int


class PipelineError(BaseModel):
    stage: str
    error_message: str
    timestamp: str
    recoverable: bool = True


class PipelineWarning(BaseModel):
    stage: str
    warning_message: str
    timestamp: str


class PipelineState(BaseModel):
    job_id: str
    dataset_id: str
    file_path: str
    user_config: dict

    profile: DataProfile | None = None
    cleaning_log: list[CleaningAction] | None = None
    cleaned_file_path: str | None = None
    features: list[dict[str, Any]] | None = None
    stats: dict[str, Any] | None = None
    charts: list[dict[str, Any]] | None = None
    insights: list[dict[str, Any]] | None = None
    report_narrative: str | None = None
    report_url: str | None = None

    current_stage: str | None = None
    stage_attempts: dict[str, int] = Field(default_factory=dict)
    errors: list[PipelineError] = Field(default_factory=list)
    warnings: list[PipelineWarning] = Field(default_factory=list)

    total_tokens_used: int = 0
    total_cost_usd: float = 0.0

    last_checkpoint: str | None = None
    checkpoint_hash: str | None = None


class ChartSpec(BaseModel):
    type: Literal["histogram", "bar", "line", "scatter", "heatmap"]
    x: str | None = None
    y: str | None = None
    columns: list[str] | None = None
    title: str
    bins: int = 20


class InsightItem(BaseModel):
    title: str = Field(max_length=60)
    description: str = Field(max_length=300)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(min_length=1, max_length=3)
    insight_type: Literal["trend", "anomaly", "correlation", "distribution", "outlier"]
    affected_columns: list[str]
    business_impact: Literal["low", "medium", "high"] = "medium"


class FeatureSuggestion(BaseModel):
    name: str
    formula: str
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)
    required_columns: list[str]
    output_dtype: Literal["numeric", "categorical", "datetime"]


class NearDuplicateConfig(BaseModel):
    threshold_pct: float = Field(default=0.85, ge=0.5, le=1.0)
    exclude_columns: list[str] = Field(default_factory=list)
    min_comparison_columns: int = Field(default=3)


class PipelineStage(BaseModel):
    id: str
    job_id: str
    stage_name: str
    status: Literal["PENDING", "RUNNING", "COMPLETE", "FAILED"]
    output: dict[str, Any] | None = None
    started_at: str | None = None
    completed_at: str | None = None


class VerificationResult(BaseModel):
    status: Literal["VERIFIED", "HALLUCINATED", "UNVERIFIABLE"]
    claim: str
    reason: str | None = None
    actual_value: float | None = None


class NumericalClaim(BaseModel):
    type: Literal[
        "percentage_claim", "mean_claim", "correlation_claim", "row_pct_claim"
    ]
    column: str | None = None
    value: float
    secondary_column: str | None = None


# ── Multi-model tier system ──────────────────────────────────────────────────

class LLMTier:
    # FAST: Qwen3-8B — structured JSON output, classification, validation
    FAST = "Qwen/Qwen3-8B"

    # BALANCED: Qwen3-Next-80B — feature engineering, report narrative, chart context
    BALANCED = "Qwen/Qwen3-Next-80B-A3B-Instruct"

    # REASONING: DeepSeek-R1-0528 — deep insight generation, pattern discovery
    REASONING = "deepseek-ai/DeepSeek-R1-0528"


# Task → Model mapping
# Each task is matched to the best model for its cognitive demands
TASK_MODEL_MAPPING: dict[str, str] = {
    # FAST tier: deterministic, schema-bound tasks
    "classify_column_type": LLMTier.FAST,
    "format_json": LLMTier.FAST,
    "validate_schema": LLMTier.FAST,
    "chart_type_selection": LLMTier.FAST,
    "column_importance_scoring": LLMTier.FAST,

    # BALANCED tier: analytical tasks requiring domain understanding
    "feature_suggestions": LLMTier.BALANCED,
    "report_narrative": LLMTier.BALANCED,
    "chart_recommendations": LLMTier.BALANCED,
    "data_context_interpretation": LLMTier.BALANCED,
    "visualization_strategy": LLMTier.BALANCED,

    # REASONING tier: tasks requiring multi-step analysis and deep pattern recognition
    "insight_generation": LLMTier.REASONING,
    "anomaly_explanation": LLMTier.REASONING,
    "correlation_interpretation": LLMTier.REASONING,
    "business_impact_assessment": LLMTier.REASONING,
    "chart_insight_narrative": LLMTier.REASONING,
}

# Temperature config per task type
TASK_TEMPERATURE: dict[str, float] = {
    "classify_column_type": 0.0,
    "format_json": 0.0,
    "validate_schema": 0.0,
    "chart_type_selection": 0.0,
    "column_importance_scoring": 0.0,
    "feature_suggestions": 0.0,
    "report_narrative": 0.3,
    "chart_recommendations": 0.1,
    "data_context_interpretation": 0.1,
    "visualization_strategy": 0.1,
    "insight_generation": 0.6,
    "anomaly_explanation": 0.4,
    "correlation_interpretation": 0.5,
    "business_impact_assessment": 0.4,
    "chart_insight_narrative": 0.4,
}

# Max tokens per task type
TASK_MAX_TOKENS: dict[str, int] = {
    "classify_column_type": 100,
    "format_json": 2048,
    "validate_schema": 512,
    "chart_type_selection": 512,
    "column_importance_scoring": 256,
    "feature_suggestions": 2048,
    "report_narrative": 3000,
    "chart_recommendations": 2048,
    "data_context_interpretation": 1024,
    "visualization_strategy": 2048,
    "insight_generation": 8000,
    "anomaly_explanation": 2000,
    "correlation_interpretation": 2000,
    "business_impact_assessment": 2000,
    "chart_insight_narrative": 1500,
}


def get_model_for_task(task_name: str) -> str:
    return TASK_MODEL_MAPPING.get(task_name, LLMTier.BALANCED)


def get_temperature_for_task(task_name: str) -> float:
    return TASK_TEMPERATURE.get(task_name, 0.1)


def get_max_tokens_for_task(task_name: str) -> int:
    return TASK_MAX_TOKENS.get(task_name, 2048)
