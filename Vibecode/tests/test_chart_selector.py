import pytest
import sys

sys.path.insert(0, "/Users/brianeedsleep/Documents/Vibecode")

from src.agents.auto_chart_selector import AutoChartSelectorAgent
from src.models.types import DataProfile, ColumnInfo


@pytest.fixture
def sample_profile():
    return DataProfile(
        row_count=100,
        column_count=5,
        columns=[
            ColumnInfo(name="date", dtype="datetime", unique_count=10, null_count=0),
            ColumnInfo(name="revenue", dtype="numeric", unique_count=50, null_count=0),
            ColumnInfo(name="units", dtype="numeric", unique_count=30, null_count=0),
            ColumnInfo(
                name="region", dtype="categorical", unique_count=4, null_count=0
            ),
            ColumnInfo(
                name="category", dtype="categorical", unique_count=3, null_count=0
            ),
        ],
        file_path="/test/data.csv",
        quality_score=95.0,
        high_correlation_pairs=[
            {"col_a": "revenue", "col_b": "units", "correlation": 0.95}
        ],
    )


def test_select_charts_returns_list(sample_profile):
    agent = AutoChartSelectorAgent()
    charts = agent.select_charts(sample_profile)

    assert isinstance(charts, list)
    assert len(charts) > 0


def test_select_charts_max_count(sample_profile):
    agent = AutoChartSelectorAgent()
    max_count = 5
    charts = agent.select_charts(sample_profile, max_count=max_count)

    assert len(charts) <= max_count


def test_select_charts_deduplication(sample_profile):
    agent = AutoChartSelectorAgent()
    charts = agent.select_charts(sample_profile)

    chart_keys = []
    for chart in charts:
        key = f"{chart.type}:{chart.x}:{chart.y}"
        assert key not in chart_keys, "Duplicate chart found"
        chart_keys.append(key)
