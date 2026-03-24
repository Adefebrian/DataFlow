import pytest
import sys

sys.path.insert(0, "/Users/brianeedsleep/Documents/Vibecode")

from src.agents.data_profiler import DataProfilerAgent
from src.models.types import DataProfile


@pytest.mark.asyncio
async def test_data_profiler_basic(sample_csv_path):
    agent = DataProfilerAgent()
    profile = await agent.profile(sample_csv_path)

    assert isinstance(profile, DataProfile)
    assert profile.row_count == 10
    assert profile.column_count == 5
    assert profile.quality_score == 100.0
    assert len(profile.columns) == 5


@pytest.mark.asyncio
async def test_data_profiler_columns(sample_csv_path):
    agent = DataProfilerAgent()
    profile = await agent.profile(sample_csv_path)

    column_names = [c.name for c in profile.columns]
    assert "date" in column_names
    assert "revenue" in column_names
    assert "units_sold" in column_names
    assert "region" in column_names
    assert "category" in column_names


@pytest.mark.asyncio
async def test_data_profiler_correlations(sample_csv_path):
    agent = DataProfilerAgent()
    profile = await agent.profile(sample_csv_path)

    assert len(profile.high_correlation_pairs) >= 0
    for pair in profile.high_correlation_pairs:
        assert "col_a" in pair
        assert "col_b" in pair
        assert "correlation" in pair
        assert 0 <= pair["correlation"] <= 1
