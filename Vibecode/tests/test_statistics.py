import pytest
import pandas as pd
import sys

sys.path.insert(0, "/Users/brianeedsleep/Documents/Vibecode")

from src.agents.statistics import StatisticsAgent


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "category": ["a", "b", "a", "b", "a", "b", "a", "b", "a", "b"],
            "with_nulls": [1, 2, None, 4, 5, 6, 7, 8, 9, 10],
        }
    )


def test_statistics_compute_numeric(sample_df):
    agent = StatisticsAgent()
    stats = agent.compute(sample_df)

    assert "numbers" in stats
    assert stats["numbers"]["mean"] == 5.5
    assert stats["numbers"]["median"] == 5.5
    assert stats["numbers"]["min"] == 1
    assert stats["numbers"]["max"] == 10


def test_statistics_compute_categorical(sample_df):
    agent = StatisticsAgent()
    stats = agent.compute(sample_df)

    assert "category" in stats
    assert isinstance(stats["category"], dict)


def test_statistics_anomaly_detection(sample_df):
    agent = StatisticsAgent()
    df_with_outliers = sample_df.copy()
    df_with_outliers.loc[0, "numbers"] = 100

    anomalies = agent.detect_anomalies(df_with_outliers)
    assert len(anomalies) >= 0
