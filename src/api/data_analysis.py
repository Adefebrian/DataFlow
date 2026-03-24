"""
Comprehensive Analysis Module for DataFlow Platform
====================================================

This module provides advanced analysis capabilities for:
- Data Engineers: Data Quality, Schema, Pipeline Health, ETL Analysis
- Data Analysts: Statistical Analysis, Business Metrics, Trends, Comparisons

Key Features:
- NOT all records analyzed - smart sampling and aggregation
- Domain-aware analysis selection
- Impactful metrics focus
- Actionable output
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from scipy import stats
import warnings

warnings.filterwarnings("ignore")


def analyze_data_quality(df: pd.DataFrame) -> Dict:
    """
    DATA ENGINEER: Comprehensive Data Quality Analysis

    Returns quality metrics and actionable insights
    """
    row_count = len(df)

    null_counts = df.isnull().sum()
    null_pcts = (null_counts / row_count * 100).to_dict()

    duplicate_count = df.duplicated().sum()

    dtypes = df.dtypes.value_counts().to_dict()

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime"]).columns.tolist()

    quality_issues = []

    for col, null_pct in null_pcts.items():
        if null_pct > 10:
            quality_issues.append(
                {
                    "column": col,
                    "issue": "high_null",
                    "percentage": null_pct,
                    "count": int(null_counts.get(col, 0)),
                }
            )

    constant_cols = []
    for col in numeric_cols:
        if df[col].nunique() <= 1:
            constant_cols.append(col)

    if constant_cols:
        quality_issues.append(
            {"columns": constant_cols, "issue": "constant_values", "severity": "medium"}
        )

    unique_id_cols = []
    for col in cat_cols:
        if df[col].nunique() == row_count:
            unique_id_cols.append(col)

    if unique_id_cols:
        quality_issues.append(
            {"columns": unique_id_cols, "issue": "unique_identifier", "severity": "low"}
        )

    completeness = 100 - np.mean(list(null_pcts.values()))
    completeness = max(0, min(100, completeness))

    quality_score = 100
    if null_pcts:
        quality_score -= np.mean(list(null_pcts.values())) * 0.5
    if duplicate_count > 0:
        quality_score -= (duplicate_count / row_count * 100) * 0.3
    quality_score -= len(constant_cols) * 5
    quality_score = max(0, min(100, quality_score))

    return {
        "row_count": row_count,
        "column_count": len(df.columns),
        "null_counts": null_counts.to_dict(),
        "null_percentages": null_pcts,
        "duplicate_count": duplicate_count,
        "duplicate_percentage": (duplicate_count / row_count * 100)
        if row_count > 0
        else 0,
        "dtypes": dtypes,
        "numeric_columns": numeric_cols,
        "categorical_columns": cat_cols,
        "date_columns": date_cols,
        "constant_columns": constant_cols,
        "unique_identifier_columns": unique_id_cols,
        "quality_issues": quality_issues,
        "completeness": completeness,
        "quality_score": quality_score,
        "health_status": "excellent"
        if quality_score > 85
        else "good"
        if quality_score > 70
        else "needs_attention"
        if quality_score > 50
        else "poor",
    }


def analyze_numeric_distribution(df: pd.DataFrame, column: str) -> Dict:
    """
    ANALYST: Comprehensive distribution analysis for numeric column
    Uses smart sampling for large datasets
    """
    data = df[column].dropna()
    n = len(data)

    if n == 0:
        return {"error": "No data available"}

    if n > 10000:
        data = data.sample(n=10000, random_state=42)

    data = pd.to_numeric(data, errors="coerce").dropna()
    if len(data) < 5:
        return {"error": "Insufficient numeric data for distribution analysis"}

    try:
        mean = data.mean()
        median = data.median()
        std = data.std()
        var = data.var()
        min_val = data.min()
        max_val = data.max()
        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)
        iqr = q3 - q1

        skewness = data.skew()
        kurtosis = data.kurtosis()

        cv = (std / mean * 100) if mean != 0 else 0

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        outlier_count = len(outliers)
        outlier_pct = (outlier_count / n * 100) if n > 0 else 0

        percentiles = {
            "p5": float(data.quantile(0.05)),
            "p10": float(data.quantile(0.10)),
            "p25": float(data.quantile(0.25)),
            "p50": float(data.quantile(0.50)),
            "p75": float(data.quantile(0.75)),
            "p90": float(data.quantile(0.90)),
            "p95": float(data.quantile(0.95)),
        }

        distribution_type = "normal"
        if abs(skewness) > 2:
            distribution_type = "highly_skewed"
        elif abs(skewness) > 1:
            distribution_type = "moderately_skewed"
        elif abs(skewness) > 0.5:
            distribution_type = "slightly_skewed"

        if kurtosis > 3:
            distribution_type += "_heavy_tailed"
        elif kurtosis < -1:
            distribution_type += "_light_tailed"

        return {
            "column": column,
            "count": n,
            "mean": float(mean),
            "median": float(median),
            "std": float(std),
            "variance": float(var),
            "min": float(min_val),
            "max": float(max_val),
            "q1": float(q1),
            "q3": float(q3),
            "iqr": float(iqr),
            "skewness": float(skewness),
            "kurtosis": float(kurtosis),
            "coefficient_of_variation": float(cv),
            "outlier_count": outlier_count,
            "outlier_percentage": float(outlier_pct),
            "outlier_bounds": {
                "lower": float(lower_bound),
                "upper": float(upper_bound),
            },
            "percentiles": percentiles,
            "distribution_type": distribution_type,
            "normal_test_pvalue": float(stats.normaltest(data)[1]) if n >= 20 else None,
        }
    except (TypeError, ValueError):
        return {"error": "Cannot compute distribution for this column type"}

    distribution_type = "normal"
    if abs(skewness) > 2:
        distribution_type = "highly_skewed"
    elif abs(skewness) > 1:
        distribution_type = "moderately_skewed"
    elif abs(skewness) > 0.5:
        distribution_type = "slightly_skewed"

    if kurtosis > 3:
        distribution_type += "_heavy_tailed"
    elif kurtosis < -1:
        distribution_type += "_light_tailed"

    return {
        "column": column,
        "count": n,
        "mean": float(mean),
        "median": float(median),
        "std": float(std),
        "variance": float(var),
        "min": float(min_val),
        "max": float(max_val),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "skewness": float(skewness),
        "kurtosis": float(kurtosis),
        "coefficient_of_variation": float(cv),
        "outlier_count": outlier_count,
        "outlier_percentage": float(outlier_pct),
        "outlier_bounds": {"lower": float(lower_bound), "upper": float(upper_bound)},
        "percentiles": percentiles,
        "distribution_type": distribution_type,
        "normal_test_pvalue": float(stats.normaltest(data)[1]) if n >= 20 else None,
    }


def analyze_correlations(df: pd.DataFrame, columns: List[str] = None) -> Dict:
    """
    ANALYST: Correlation analysis with smart insights
    """
    if columns:
        numeric_df = df[columns].select_dtypes(include=["number"]).copy()
    else:
        numeric_df = df.select_dtypes(include=["number"]).copy()

    if numeric_df.shape[1] < 2:
        return {"error": "Need at least 2 numeric columns"}

    corr_matrix = numeric_df.corr()

    correlations = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            r = corr_matrix.iloc[i, j]
            if not np.isnan(r):
                correlations.append(
                    {
                        "var1": corr_matrix.columns[i],
                        "var2": corr_matrix.columns[j],
                        "r": float(r),
                        "abs_r": float(abs(r)),
                        "strength": "very_strong"
                        if abs(r) >= 0.8
                        else "strong"
                        if abs(r) >= 0.6
                        else "moderate"
                        if abs(r) >= 0.4
                        else "weak",
                        "direction": "positive" if r > 0 else "negative",
                    }
                )

    correlations.sort(key=lambda x: x["abs_r"], reverse=True)

    strong_positive = [c for c in correlations if c["r"] >= 0.6]
    strong_negative = [c for c in correlations if c["r"] <= -0.6]
    moderate = [c for c in correlations if 0.4 <= abs(c["r"]) < 0.6]

    multicollinearity = []
    for col in corr_matrix.columns:
        correlations_with_col = [
            abs(corr_matrix.loc[col, other])
            for other in corr_matrix.columns
            if other != col
        ]
        max_corr = max(correlations_with_col) if correlations_with_col else 0
        if max_corr >= 0.8:
            multicollinearity.append(
                {"column": col, "max_correlation": float(max_corr)}
            )

    return {
        "correlation_matrix": corr_matrix.to_dict(),
        "correlations": correlations,
        "strong_positive": strong_positive,
        "strong_negative": strong_negative,
        "moderate": moderate,
        "multicollinearity": multicollinearity,
        "summary": {
            "total_pairs": len(correlations),
            "strong_pairs": len(strong_positive) + len(strong_negative),
            "moderate_pairs": len(moderate),
            "has_multicollinearity": len(multicollinearity) > 0,
        },
    }


def analyze_segments(
    df: pd.DataFrame, segment_column: str, metric_columns: List[str] = None
) -> Dict:
    """
    ANALYST: Segment analysis with aggregated insights
    """
    if segment_column not in df.columns:
        return {"error": f"Column {segment_column} not found"}

    segment_counts = df[segment_column].value_counts()

    if len(segment_counts) > 50:
        top_segments = segment_counts.head(20)
        other_count = segment_counts.iloc[20:].sum()
        segment_counts = pd.concat([top_segments, pd.Series({"_other_": other_count})])

    segments_analysis = []

    for segment in segment_counts.index:
        segment_data = df[df[segment_column] == segment]
        segment_info = {
            "segment": str(segment),
            "count": len(segment_data),
            "percentage": len(segment_data) / len(df) * 100,
        }

        if metric_columns:
            for col in metric_columns[:5]:
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    segment_info[f"{col}_mean"] = float(segment_data[col].mean())
                    segment_info[f"{col}_sum"] = float(segment_data[col].sum())
                    segment_info[f"{col}_median"] = float(segment_data[col].median())

        segments_analysis.append(segment_info)

    segments_df = pd.DataFrame(segments_analysis)

    if metric_columns:
        for col in metric_columns[:5]:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                segments_df[f"{col}_rank"] = segments_df[f"{col}_mean"].rank(
                    ascending=False
                )

    segments_analysis.sort(key=lambda x: x["count"], reverse=True)

    return {
        "segment_column": segment_column,
        "total_segments": len(segment_counts),
        "segments": segments_analysis,
        "concentration": {
            "top_segment": segments_analysis[0]["segment"]
            if segments_analysis
            else None,
            "top_segment_pct": segments_analysis[0]["percentage"]
            if segments_analysis
            else 0,
            "top_3_pct": sum(s["percentage"] for s in segments_analysis[:3]),
            "top_5_pct": sum(s["percentage"] for s in segments_analysis[:5]),
            "gini_coefficient": _calculate_gini(
                [s["percentage"] for s in segments_analysis]
            )
            if segments_analysis
            else 0,
        },
    }


def _calculate_gini(values: List[float]) -> float:
    """Calculate Gini coefficient for concentration measurement"""
    if not values or sum(values) == 0:
        return 0

    sorted_values = sorted(values)
    n = len(values)
    cumsum = np.cumsum(sorted_values)

    return (2 * np.sum((n + 1 - np.arange(1, n + 1)) * sorted_values)) / (
        n * cumsum[-1]
    ) - (n + 1) / n


def analyze_trends(
    df: pd.DataFrame, date_column: str, metric_column: str, freq: str = "auto"
) -> Dict:
    """
    ANALYST: Trend analysis with aggregation
    """
    if date_column not in df.columns or metric_column not in df.columns:
        return {"error": "Required columns not found"}

    df_trend = df[[date_column, metric_column]].copy()
    df_trend[date_column] = pd.to_datetime(df_trend[date_column], errors="coerce")
    df_trend = df_trend.dropna()

    if len(df_trend) < 10:
        return {"error": "Insufficient data for trend analysis"}

    if freq == "auto":
        date_range = df_trend[date_column].max() - df_trend[date_column].min()
        days = date_range.days if hasattr(date_range, "days") else 0

        if days < 7:
            freq = "D"
        elif days < 60:
            freq = "W"
        elif days < 365:
            freq = "ME"
        else:
            freq = "YE"

    try:
        aggregated = (
            df_trend.groupby(pd.Grouper(key=date_column, freq=freq))[metric_column]
            .agg(["mean", "sum", "count", "min", "max", "std"])
            .reset_index()
        )
        aggregated = aggregated.dropna()
    except:
        return {"error": "Failed to aggregate data"}

    if len(aggregated) < 3:
        return {"error": "Insufficient aggregated data points"}

    mean_values = aggregated["mean"].values
    x = np.arange(len(mean_values))

    slope, intercept, r_value, p_value, std_err = stats.linregr(x, mean_values)

    trend_direction = "upward" if slope > 0 else "downward" if slope < 0 else "stable"
    trend_magnitude = (
        abs(slope * len(mean_values) / mean_values[0] * 100)
        if mean_values[0] != 0
        else 0
    )

    first_value = mean_values[0]
    last_value = mean_values[-1]
    change_pct = (
        ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
    )

    if len(mean_values) >= 3:
        rolling_avg = (
            pd.Series(mean_values)
            .rolling(window=min(3, len(mean_values) // 3), min_periods=1)
            .mean()
            .values
        )
        recent_vs_early = (
            (rolling_avg[-1] - rolling_avg[0]) / rolling_avg[0] * 100
            if rolling_avg[0] != 0
            else 0
        )
    else:
        recent_vs_early = 0
        rolling_avg = mean_values

    volatility = (
        np.std(mean_values) / np.mean(mean_values) * 100
        if np.mean(mean_values) != 0
        else 0
    )

    return {
        "date_column": date_column,
        "metric_column": metric_column,
        "frequency": freq,
        "period_count": len(aggregated),
        "trend": {
            "direction": trend_direction,
            "slope": float(slope),
            "r_squared": float(r_value**2),
            "p_value": float(p_value),
            "magnitude_pct": float(trend_magnitude),
            "total_change_pct": float(change_pct),
            "recent_vs_early_pct": float(recent_vs_early),
            "is_significant": p_value < 0.05,
        },
        "volatility": {
            "std": float(np.std(mean_values)),
            "cv": float(volatility),
            "label": "high"
            if volatility > 30
            else "moderate"
            if volatility > 15
            else "low",
        },
        "summary": {
            "first_value": float(first_value),
            "last_value": float(last_value),
            "peak_value": float(max(mean_values)),
            "low_value": float(min(mean_values)),
            "average": float(np.mean(mean_values)),
        },
        "periods": aggregated.to_dict("records"),
    }


def analyze_outliers(df: pd.DataFrame, columns: List[str] = None) -> Dict:
    """
    ANALYST: Outlier analysis with business impact
    """
    if columns is None:
        columns = df.select_dtypes(include=["number"]).columns.tolist()

    outlier_results = {}

    for col in columns[:20]:
        data = df[col].dropna()

        if len(data) < 10:
            continue

        data = pd.to_numeric(data, errors="coerce").dropna()
        if len(data) < 10:
            continue

        try:
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            outliers = data[(data < lower) | (data > upper)]

            extreme_lower = q1 - 3 * iqr
            extreme_upper = q3 + 3 * iqr
            extreme_outliers = data[(data < extreme_lower) | (data > extreme_upper)]

            outlier_results[col] = {
                "count": len(outliers),
                "percentage": len(outliers) / len(data) * 100,
                "extreme_count": len(extreme_outliers),
                "extreme_percentage": len(extreme_outliers) / len(data) * 100,
                "bounds": {"lower": float(lower), "upper": float(upper)},
                "severity": "high"
                if len(outliers) / len(data) > 0.05
                else "moderate"
                if len(outliers) / len(data) > 0.02
                else "low",
                "outlier_values": {
                    "min": float(outliers.min()) if len(outliers) > 0 else None,
                    "max": float(outliers.max()) if len(outliers) > 0 else None,
                    "mean": float(outliers.mean()) if len(outliers) > 0 else None,
                },
            }
        except (TypeError, ValueError):
            continue

    high_severity_cols = [
        k for k, v in outlier_results.items() if v["severity"] == "high"
    ]

    return {
        "columns_analyzed": list(outlier_results.keys()),
        "outlier_details": outlier_results,
        "high_severity_columns": high_severity_cols,
        "summary": {
            "total_columns": len(outlier_results),
            "high_severity_count": len(high_severity_cols),
            "total_outlier_records": sum(v["count"] for v in outlier_results.values()),
            "needs_investigation": len(high_severity_cols) > 0,
        },
    }


def generate_comprehensive_stats(df: pd.DataFrame) -> Dict:
    """
    COMPREHENSIVE: Generate all statistics at once
    """
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    numeric_stats = {}
    for col in numeric_cols:
        numeric_stats[col] = analyze_numeric_distribution(df, col)

    categorical_stats = {}
    for col in cat_cols[:20]:
        value_counts = df[col].value_counts()
        categorical_stats[col] = {
            "unique_count": int(df[col].nunique()),
            "top_values": value_counts.head(10).to_dict(),
            "distribution": (value_counts / len(df) * 100).head(10).to_dict(),
        }

    correlations = (
        analyze_correlations(df, numeric_cols[:20]) if len(numeric_cols) >= 2 else {}
    )

    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "numeric_columns": numeric_cols,
        "categorical_columns": cat_cols,
        "numeric_statistics": numeric_stats,
        "categorical_statistics": categorical_stats,
        "correlations": correlations,
    }
