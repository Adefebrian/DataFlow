"""
DataFlow Ultimate Analysis System
=================================

Implements all 7 phases of the Ultimate System Prompt:
1. Data Profiling (Column Classification, Quality, Smart Sampling)
2. Chart Selection Intelligence (Scoring-based ranking)
3. Visualization Standards (Anatomy, Colors, Axes)
4. Business Narrative Engine (OBSERVATION/IMPLICATION/ACTION)
5. Dashboard Layout Rules (Card hierarchy)
6. Auto-Rejection Rules (Graceful explanations)
7. Language & Tone (Plain business language)

Every chart answers: What is happening? Why? What will happen? What should we do?
"""

import re
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.utils.math_utils import safe_histogram_range

warnings.filterwarnings("ignore")

import matplotlib

matplotlib.use("Agg")
import base64
import io
from datetime import datetime

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, Wedge

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial"]
plt.rcParams["axes.unicode_minus"] = False

GOLD = "#D4AF37"
TEAL = "#00CED1"
CORAL = "#FF6B6B"
PURPLE = "#9B59B6"
EMERALD = "#2ECC71"
MIDNIGHT = "#1a1a2e"
OBSIDIAN = "#0a0a0f"
FROST = "#ecf0f1"
CHARCOAL = "#888888"
AMBER = "#FFB300"
SLATE = "#64748B"

BUSINESS_KEYWORDS = {
    "revenue": 3,
    "sales": 3,
    "profit": 3,
    "cost": 3,
    "margin": 3,
    "growth": 3,
    "quantity": 2,
    "orders": 2,
    "customers": 2,
    "churn": 2,
    "conversion": 2,
    "rate": 1,
    "percentage": 1,
    "ratio": 1,
    "average": 1,
    "total": 1,
    "amount": 2,
    "price": 2,
    "discount": 2,
    "age": 1,
    "score": 1,
    "rating": 1,
    "satisfaction": 2,
}

ID_PATTERNS = [
    "id$",
    "_id$",
    "^id_",
    "uuid",
    "guid",
    "pk$",
    "^pk_",
    "key$",
    "^key_",
    "code$",
    "number$",
    "no\\.",
    "^order_?num",
    "^invoice_?num",
    "^customer_?id",
    "^product_?id",
    "^user_?id",
    "^unnamed",
    "^index$",
    "^row_?id$",
    "^row_?num$",
]

DATE_PATTERNS = [
    r"^\d{4}-\d{2}-\d{2}",
    r"^\d{4}/\d{2}/\d{2}",
    r"^\d{2}-\d{2}-\d{4}",
    r"^\d{2}/\d{2}/\d{4}",
    r"^\d{1,2}-\w{3}-\d{2,4}",
    r"^\w{3}\s+\d{1,2},?\s+\d{4}",
    r"^\d{4}\d{2}\d{2}",
]

BOOLEAN_PATTERNS = [
    r"^(true|false|yes|no|y|n|1|0|on|off|active|inactive)$",
]

HIGH_CARDINALITY_THRESHOLD = 50
OUTLIER_THRESHOLD = 1.5


@dataclass
class ColumnProfile:
    name: str
    column_type: str
    unique_count: int
    null_count: int
    null_percentage: float
    cardinality_ratio: float
    sample_values: List[Any] = field(default_factory=list)
    numeric_stats: Optional[Dict] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class ChartCandidate:
    chart_type: str
    dimensions: List[str]
    metrics: List[str]
    business_score: float
    insight_score: float
    total_score: float
    analytical_intent: str
    rejection_reason: Optional[str] = None


@dataclass
class BusinessInsight:
    observation: str
    implication: str
    recommended_action: str
    severity: str
    metric_value: Optional[float] = None
    benchmark_value: Optional[float] = None


class DataProfiler:
    """
    PHASE 1: Data Profiling (Enhanced)
    - Column Classification (IDENTIFIER, CATEGORICAL, HIGH_CARDINALITY, CONTINUOUS, DATETIME, BOOLEAN, TEXT_FREE)
    - Data Quality Assessment
    - Smart Sampling Recommendations
    - Pattern Detection (seasonality, trends, outliers, distributions)
    - Correlation Analysis
    - Business Relevance Scoring
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.row_count = len(df)
        self.column_count = len(df.columns)
        self.column_profiles: Dict[str, ColumnProfile] = {}
        self.numeric_columns: List[str] = []
        self.categorical_columns: List[str] = []
        self.date_columns: List[str] = []
        self.identifier_columns: List[str] = []
        self.high_cardinality_columns: List[str] = []
        self.boolean_columns: List[str] = []
        self.quality_report: Dict = {}
        self.warnings: List[str] = []
        self.patterns_detected: Dict[str, List[str]] = {}
        self.correlations: List[Dict] = []
        self.business_scores: Dict[str, float] = {}

    def profile(self) -> Dict:
        """Run complete data profiling with enhanced detection"""
        self._classify_columns_enhanced()
        self._assess_quality()
        self._detect_patterns_and_warnings()
        self._compute_correlations()
        self._compute_business_scores()
        return self._generate_profile_report()

    def _classify_columns(self):
        """Classify each column according to taxonomy"""
        for col in self.df.columns:
            profile = self._classify_single_column(col)
            self.column_profiles[col] = profile

            if profile.column_type == "CONTINUOUS":
                self.numeric_columns.append(col)
            elif profile.column_type in ("CATEGORICAL", "BOOLEAN"):
                self.categorical_columns.append(col)
            elif profile.column_type == "DATETIME":
                self.date_columns.append(col)
            elif profile.column_type == "IDENTIFIER":
                self.identifier_columns.append(col)
            elif profile.column_type == "HIGH_CARDINALITY":
                self.high_cardinality_columns.append(col)

    def _classify_columns_enhanced(self):
        """Enhanced column classification with better detection"""
        for col in self.df.columns:
            profile = self._classify_single_column_enhanced(col)
            self.column_profiles[col] = profile

            if profile.column_type == "CONTINUOUS":
                self.numeric_columns.append(col)
            elif profile.column_type in ("CATEGORICAL", "BOOLEAN"):
                self.categorical_columns.append(col)
            elif profile.column_type == "DATETIME":
                self.date_columns.append(col)
            elif profile.column_type == "IDENTIFIER":
                self.identifier_columns.append(col)
            elif profile.column_type == "HIGH_CARDINALITY":
                self.high_cardinality_columns.append(col)

    def _classify_single_column(self, col: str) -> ColumnProfile:
        """Classify a single column"""
        null_count = int(self.df[col].isnull().sum())
        null_pct = null_count / self.row_count * 100
        unique_count = int(self.df[col].nunique())
        cardinality_ratio = unique_count / self.row_count if self.row_count > 0 else 0
        sample_values = self.df[col].dropna().head(5).tolist()
        warnings_list = []

        if null_pct > 30:
            warnings_list.append(f"High null rate: {null_pct:.1f}%")

        dtype = str(self.df[col].dtype)

        # Check for datetime FIRST (before identifier, since dates often have high cardinality)
        if self._is_datetime_column(col, dtype, sample_values):
            col_type = "DATETIME"
        elif self._is_identifier_column(col, unique_count, sample_values):
            col_type = "IDENTIFIER"
            warnings_list.append("Identifier column - use for grouping only")
        elif self._is_numeric_column(dtype):
            col_type = "CONTINUOUS"
        elif self._is_boolean_column(col, unique_count):
            col_type = "BOOLEAN"
        elif unique_count > HIGH_CARDINALITY_THRESHOLD:
            col_type = "HIGH_CARDINALITY"
            warnings_list.append("High cardinality - aggregate to top-N only")
        elif unique_count <= 2:
            col_type = "BOOLEAN"
        else:
            col_type = "CATEGORICAL"

        numeric_stats = None
        if col_type == "CONTINUOUS":
            numeric_stats = self._compute_numeric_stats(col)
            if numeric_stats:
                if abs(numeric_stats.get("skewness", 0)) > 1.5:
                    warnings_list.append(
                        "Distribution is highly skewed - median may be more representative"
                    )
                if numeric_stats.get("cv", 0) > 100:
                    warnings_list.append(
                        "High variability - averages may be unreliable"
                    )

        return ColumnProfile(
            name=col,
            column_type=col_type,
            unique_count=unique_count,
            null_count=null_count,
            null_percentage=null_pct,
            cardinality_ratio=cardinality_ratio,
            sample_values=[str(v) for v in sample_values[:5]],
            numeric_stats=numeric_stats,
            warnings=warnings_list,
        )

    def _classify_single_column_enhanced(self, col: str) -> ColumnProfile:
        """Enhanced column classification with better detection logic"""
        null_count = int(self.df[col].isnull().sum())
        null_pct = null_count / self.row_count * 100
        unique_count = int(self.df[col].nunique())
        cardinality_ratio = unique_count / self.row_count if self.row_count > 0 else 0
        sample_values = self.df[col].dropna().head(10).tolist()
        warnings_list = []

        if null_pct > 30:
            warnings_list.append(f"High null rate: {null_pct:.1f}%")

        dtype = str(self.df[col].dtype)
        col_lower = col.lower()

        # Enhanced datetime detection
        if self._is_datetime_enhanced(col, dtype, sample_values):
            col_type = "DATETIME"
        # Enhanced identifier detection
        elif self._is_identifier_enhanced(
            col, unique_count, sample_values, cardinality_ratio
        ):
            col_type = "IDENTIFIER"
            warnings_list.append("Identifier column - use for grouping only")
        # Enhanced numeric detection (including numeric strings)
        elif self._is_numeric_enhanced(col, dtype, sample_values):
            col_type = "CONTINUOUS"
        # Enhanced boolean detection
        elif self._is_boolean_enhanced(col, unique_count, sample_values):
            col_type = "BOOLEAN"
            self.boolean_columns.append(col)
        # High cardinality check
        elif unique_count > HIGH_CARDINALITY_THRESHOLD:
            col_type = "HIGH_CARDINALITY"
            warnings_list.append("High cardinality - aggregate to top-N only")
        # Very low cardinality (likely boolean or categorical)
        elif unique_count <= 2:
            col_type = "BOOLEAN"
            self.boolean_columns.append(col)
        # Check if looks like categorical (limited unique values)
        elif unique_count <= 20 or cardinality_ratio < 0.05:
            col_type = "CATEGORICAL"
        else:
            col_type = "CATEGORICAL"

        # Enhanced numeric stats
        numeric_stats = None
        if col_type == "CONTINUOUS":
            numeric_stats = self._compute_numeric_stats_enhanced(col)
            if numeric_stats:
                if abs(numeric_stats.get("skewness", 0)) > 1.5:
                    warnings_list.append(
                        "Distribution is highly skewed - median may be more representative"
                    )
                if numeric_stats.get("cv", 0) > 100:
                    warnings_list.append(
                        "High variability - averages may be unreliable"
                    )
                if numeric_stats.get("outlier_pct", 0) > 10:
                    warnings_list.append(
                        f"Outliers detected: {numeric_stats['outlier_pct']:.1f}%"
                    )

        return ColumnProfile(
            name=col,
            column_type=col_type,
            unique_count=unique_count,
            null_count=null_count,
            null_percentage=null_pct,
            cardinality_ratio=cardinality_ratio,
            sample_values=[str(v) for v in sample_values[:5]],
            numeric_stats=numeric_stats,
            warnings=warnings_list,
        )

    def _is_datetime_enhanced(self, col: str, dtype: str, samples: List) -> bool:
        """Enhanced datetime detection"""
        # Check dtype first
        if (
            "datetime" in dtype.lower()
            or "date" in dtype.lower()
            or "time" in dtype.lower()
        ):
            return True

        # Check column name patterns
        col_lower = col.lower()
        date_keywords = [
            "date",
            "time",
            "timestamp",
            "created",
            "updated",
            "modified",
            "day",
            "month",
            "year",
            "period",
            "week",
        ]
        if any(keyword in col_lower for keyword in date_keywords):
            # Verify with sample values
            date_match_count = 0
            for sample in samples[:10]:
                sample_str = str(sample)
                for pattern in DATE_PATTERNS:
                    if re.match(pattern, sample_str):
                        date_match_count += 1
                        break
            if (
                date_match_count >= 3
            ):  # At least 3 out of 10 samples match date patterns
                return True

        # Check sample values directly
        date_match_count = 0
        for sample in samples[:10]:
            sample_str = str(sample)
            for pattern in DATE_PATTERNS:
                if re.match(pattern, sample_str):
                    date_match_count += 1
                    break

        # If 70%+ of samples match date patterns, it's likely a date column
        if date_match_count >= len(samples) * 0.7 and len(samples) >= 3:
            return True

        return False

    def _is_identifier_enhanced(
        self, col: str, unique_count: int, samples: List, cardinality_ratio: float
    ) -> bool:
        """Enhanced identifier detection"""
        col_lower = col.lower()

        # Check column name patterns
        for pattern in ID_PATTERNS:
            if re.search(pattern, col_lower):
                return True

        # High cardinality with unique values per row
        if unique_count == self.row_count and unique_count > 10:
            return True

        # Very high cardinality ratio
        if cardinality_ratio > 0.9 and unique_count > 50:
            return True

        # Check sample patterns
        identifier_match_count = 0
        for sample in samples[:5]:
            sample_str = str(sample)
            # Check for common ID patterns
            if re.match(
                r"^(ORD|PROD|USER|CUST|EMP|INV|TXN|REF|DOC)[-_]?\d+$",
                sample_str,
                re.IGNORECASE,
            ):
                identifier_match_count += 1
            elif re.match(r"^[A-Z]{2,4}[-_]?\d{4,}$", sample_str):
                identifier_match_count += 1
            elif (
                len(sample_str) > 20
                and "-" in sample_str
                and any(c.isdigit() for c in sample_str)
            ):
                identifier_match_count += 1

        if identifier_match_count >= 3:  # At least 3 out of 5 samples look like IDs
            return True

        return False

    def _is_numeric_enhanced(self, col: str, dtype: str, samples: List) -> bool:
        """Enhanced numeric detection including numeric strings"""
        # Check dtype first
        if any(
            x in dtype.lower() for x in ["int", "float", "double", "decimal", "number"]
        ):
            return True

        # Check if column can be converted to numeric
        try:
            numeric_count = 0
            for sample in samples[:10]:
                try:
                    float(
                        str(sample)
                        .replace(",", "")
                        .replace("$", "")
                        .replace("%", "")
                        .replace("€", "")
                        .replace("£", "")
                    )
                    numeric_count += 1
                except:
                    pass

            # If 80%+ of samples are numeric, consider it numeric
            if numeric_count >= len(samples) * 0.8 and len(samples) >= 3:
                return True
        except:
            pass

        return False

    def _is_boolean_enhanced(self, col: str, unique_count: int, samples: List) -> bool:
        """Enhanced boolean detection"""
        col_lower = col.lower()

        # Check column name patterns
        bool_indicators = [
            "is_",
            "has_",
            "was_",
            "flag",
            "status",
            "active",
            "enabled",
            "verified",
            "approved",
            "completed",
            "paid",
            "cancelled",
        ]
        if any(ind in col_lower for ind in bool_indicators):
            return True

        # Check if unique values are 2
        if unique_count == 2:
            return True

        # Check sample patterns for boolean values
        boolean_match_count = 0
        for sample in samples[:10]:
            sample_str = str(sample).lower().strip()
            if re.match(BOOLEAN_PATTERNS[0], sample_str):
                boolean_match_count += 1

        if boolean_match_count >= len(samples) * 0.8 and len(samples) >= 3:
            return True

        return False

    def _compute_numeric_stats_enhanced(self, col: str) -> Optional[Dict]:
        """Enhanced numeric statistics computation"""
        data = pd.to_numeric(self.df[col], errors="coerce").dropna()

        if len(data) < 3:
            return None

        try:
            mean = float(data.mean())
            median = float(data.median())
            std = float(data.std())
            min_val = float(data.min())
            max_val = float(data.max())
            q1 = float(data.quantile(0.25))
            q3 = float(data.quantile(0.75))
            skewness = float(data.skew())
            kurtosis = float(data.kurtosis())

            q1_iqr, q3_iqr = data.quantile(0.25), data.quantile(0.75)
            iqr = q3_iqr - q1_iqr
            outlier_bounds = (
                q1_iqr - OUTLIER_THRESHOLD * iqr,
                q3_iqr + OUTLIER_THRESHOLD * iqr,
            )
            outlier_count = int(
                ((data < outlier_bounds[0]) | (data > outlier_bounds[1])).sum()
            )
            outlier_pct = outlier_count / len(data) * 100

            concentration = (
                float(data.value_counts().iloc[0] / len(data) * 100)
                if len(data) > 0
                else 0
            )
            top1_share = concentration

            # Detect distribution type
            distribution_type = "normal"
            if abs(skewness) > 1.5:
                distribution_type = "right_skewed" if skewness > 0 else "left_skewed"
            elif abs(kurtosis) > 3:
                distribution_type = "heavy_tailed" if kurtosis > 0 else "light_tailed"

            return {
                "mean": mean,
                "median": median,
                "std": std,
                "min": min_val,
                "max": max_val,
                "q1": q1,
                "q3": q3,
                "skewness": skewness,
                "kurtosis": kurtosis,
                "cv": float(std / mean * 100) if mean != 0 else 0,
                "iqr": iqr,
                "outlier_count": outlier_count,
                "outlier_pct": outlier_pct,
                "outlier_bounds": outlier_bounds,
                "top1_share": top1_share,
                "p99": float(data.quantile(0.99)),
                "range": max_val - min_val,
                "distribution_type": distribution_type,
            }
        except:
            return None

    def _compute_correlations(self):
        """Compute correlations between numeric columns"""
        for i, col1 in enumerate(self.numeric_columns):
            for col2 in self.numeric_columns[i + 1 :]:
                try:
                    d1 = pd.to_numeric(self.df[col1], errors="coerce")
                    d2 = pd.to_numeric(self.df[col2], errors="coerce")
                    valid = ~(d1.isna() | d2.isna())

                    if valid.sum() > 10:
                        r = float(d1[valid].corr(d2[valid]))
                        if abs(r) >= 0.3:
                            self.correlations.append(
                                {
                                    "col1": col1,
                                    "col2": col2,
                                    "r": r,
                                    "strength": "strong"
                                    if abs(r) >= 0.7
                                    else "moderate"
                                    if abs(r) >= 0.5
                                    else "weak",
                                }
                            )
                except:
                    pass

        self.correlations.sort(key=lambda x: abs(x["r"]), reverse=True)

    def _compute_business_scores(self):
        """Compute business relevance scores for each column"""
        for col in self.df.columns:
            score = 0
            col_lower = col.lower()

            # Business keyword scoring
            for keyword, weight in BUSINESS_KEYWORDS.items():
                if keyword in col_lower:
                    score += weight

            # Null penalty
            profile = self.column_profiles.get(col)
            if profile:
                if profile.null_percentage > 50:
                    score -= 4
                elif profile.null_percentage > 30:
                    score -= 2

                # High cardinality penalty
                if profile.cardinality_ratio > 0.8:
                    score -= 2

                # Numeric columns get bonus
                if profile.column_type == "CONTINUOUS":
                    score += 2

                # Datetime columns get bonus
                if profile.column_type == "DATETIME":
                    score += 3

            self.business_scores[col] = max(0, min(10, score))

    def _is_identifier_column(self, col: str, unique_count: int, samples: List) -> bool:
        """Detect identifier columns"""
        col_lower = col.lower()

        for pattern in ID_PATTERNS:
            if re.search(pattern, col_lower):
                return True

        if unique_count == self.row_count and unique_count > 10:
            return True

        for sample in samples[:5]:
            sample_str = str(sample)
            if re.match(
                r"^(ORD|PROD|USER|CUST|EMP|INV)[-_]?\d+$", sample_str, re.IGNORECASE
            ):
                return True
            if len(sample_str) > 20 and "-" in sample_str:
                return True

        return False

    def _is_datetime_column(self, col: str, dtype: str, samples: List) -> bool:
        """Detect datetime columns"""
        if (
            "datetime" in dtype.lower()
            or "date" in dtype.lower()
            or "time" in dtype.lower()
        ):
            return True

        date_patterns = [
            r"^\d{4}-\d{2}-\d{2}",
            r"^\d{2}/\d{2}/\d{4}",
            r"^\d{1,2}-\w{3}-\d{2,4}",
        ]
        for sample in samples[:5]:
            for pattern in date_patterns:
                if re.match(pattern, str(sample)):
                    return True

        return False

    def _is_numeric_column(self, dtype: str) -> bool:
        """Detect numeric columns"""
        return any(x in dtype.lower() for x in ["int", "float", "double", "decimal"])

    def _is_boolean_column(self, col: str, unique_count: int) -> bool:
        """Detect boolean columns"""
        col_lower = col.lower()
        bool_indicators = ["is_", "has_", "was_", "flag", "status", "active", "enabled"]
        return any(ind in col_lower for ind in bool_indicators) or unique_count == 2

    def _compute_numeric_stats(self, col: str) -> Optional[Dict]:
        """Compute statistics for numeric columns"""
        data = pd.to_numeric(self.df[col], errors="coerce").dropna()

        if len(data) < 3:
            return None

        try:
            mean = float(data.mean())
            median = float(data.median())
            std = float(data.std())
            min_val = float(data.min())
            max_val = float(data.max())
            q1 = float(data.quantile(0.25))
            q3 = float(data.quantile(0.75))
            skewness = float(data.skew())

            q1_iqr, q3_iqr = data.quantile(0.25), data.quantile(0.75)
            iqr = q3_iqr - q1_iqr
            outlier_bounds = (
                q1_iqr - OUTLIER_THRESHOLD * iqr,
                q3_iqr + OUTLIER_THRESHOLD * iqr,
            )
            outlier_count = int(
                ((data < outlier_bounds[0]) | (data > outlier_bounds[1])).sum()
            )
            outlier_pct = outlier_count / len(data) * 100

            concentration = (
                float(data.value_counts().iloc[0] / len(data) * 100)
                if len(data) > 0
                else 0
            )
            top1_share = concentration

            return {
                "mean": mean,
                "median": median,
                "std": std,
                "min": min_val,
                "max": max_val,
                "q1": q1,
                "q3": q3,
                "skewness": skewness,
                "cv": float(std / mean * 100) if mean != 0 else 0,
                "outlier_count": outlier_count,
                "outlier_pct": outlier_pct,
                "outlier_bounds": outlier_bounds,
                "top1_share": top1_share,
                "p99": float(data.quantile(0.99)),
                "range": max_val - min_val,
            }
        except:
            return None

    def _assess_quality(self):
        """Assess overall data quality"""
        total_cells = self.row_count * self.column_count
        total_missing = sum(p.null_count for p in self.column_profiles.values())

        self.quality_report = {
            "completeness": (total_cells - total_missing) / total_cells * 100,
            "total_rows": self.row_count,
            "total_columns": self.column_count,
            "missing_cells": total_missing,
            "columns_with_high_null": [
                col for col, p in self.column_profiles.items() if p.null_percentage > 30
            ],
            "identifier_columns": self.identifier_columns,
            "categorical_columns": self.categorical_columns,
            "numeric_columns": self.numeric_columns,
            "date_columns": self.date_columns,
            "high_cardinality_columns": self.high_cardinality_columns,
        }

    def _detect_patterns_and_warnings(self):
        """Detect patterns and generate warnings"""
        for col, profile in self.column_profiles.items():
            if profile.null_percentage > 30:
                self.warnings.append(
                    f"'{col}' has {profile.null_percentage:.1f}% missing values"
                )

            if profile.column_type == "CONTINUOUS" and profile.numeric_stats:
                stats = profile.numeric_stats
                if stats.get("outlier_pct", 0) > 10:
                    self.warnings.append(
                        f"'{col}' has {stats['outlier_pct']:.1f}% outliers"
                    )
                if stats.get("top1_share", 0) > 70:
                    self.warnings.append(
                        f"'{col}' is highly concentrated - top value is {stats['top1_share']:.1f}%"
                    )

    def _generate_profile_report(self) -> Dict:
        """Generate comprehensive profile report with enhanced information"""
        return {
            "column_profiles": {
                col: {
                    "type": p.column_type,
                    "unique": p.unique_count,
                    "null_pct": p.null_percentage,
                    "cardinality_ratio": p.cardinality_ratio,
                    "stats": p.numeric_stats,
                    "warnings": p.warnings,
                    "business_score": self.business_scores.get(col, 0),
                }
                for col, p in self.column_profiles.items()
            },
            "column_types": {
                "numeric": self.numeric_columns,
                "categorical": self.categorical_columns,
                "datetime": self.date_columns,
                "identifier": self.identifier_columns,
                "high_cardinality": self.high_cardinality_columns,
                "boolean": self.boolean_columns,
            },
            "quality": self.quality_report,
            "warnings": self.warnings,
            "patterns_detected": self.patterns_detected,
            "correlations": self.correlations[:10],  # Top 10 correlations
            "business_scores": self.business_scores,
        }

    def get_sampling_strategy(self, column_type: str, total_rows: int) -> Dict:
        """Get sampling strategy based on column type"""
        strategies = {
            "IDENTIFIER": {
                "max_points": 10,
                "aggregate": True,
                "method": "top_n_with_others",
            },
            "CATEGORICAL": {
                "max_points": 15,
                "aggregate": True,
                "method": "top_n_with_others",
            },
            "HIGH_CARDINALITY": {
                "max_points": 10,
                "aggregate": True,
                "method": "top_n_with_others",
            },
            "CONTINUOUS": {"max_points": 2000, "aggregate": False, "method": "sample"},
            "DATETIME": {"max_points": 50, "aggregate": True, "method": "resample"},
            "BOOLEAN": {"max_points": 5, "aggregate": False, "method": "full"},
            "TEXT_FREE": {"max_points": 0, "aggregate": False, "method": "exclude"},
        }
        return strategies.get(
            column_type, {"max_points": 1000, "aggregate": False, "method": "sample"}
        )


class ChartSelector:
    """
    PHASE 2: Chart Selection Intelligence
    - Scoring system (Business Relevance + Insight Potential)
    - Decision tree for chart type selection
    - TOP 5-7 chart priority selection
    """

    def __init__(
        self,
        profile: Dict,
        correlations: List[Dict],
        data_context: Optional[Dict] = None,
    ):
        self.profile = profile
        self.correlations = correlations
        self.data_context = data_context or {}
        self.candidates: List[ChartCandidate] = []
        self.column_types = profile.get("column_types", {})

    def select_charts(self) -> List[ChartCandidate]:
        """Select optimal charts based on scoring with prioritized chart types"""
        self._score_all_combinations()

        # Categorize candidates by type
        histograms = [
            c
            for c in self.candidates
            if c.chart_type == "histogram" and c.total_score >= 0
        ]
        horizontal_bars = [
            c
            for c in self.candidates
            if c.chart_type == "horizontal_bar" and c.total_score >= 0
        ]
        lines = [
            c for c in self.candidates if c.chart_type == "line" and c.total_score >= 0
        ]
        scatters = [
            c
            for c in self.candidates
            if c.chart_type == "scatter" and c.total_score >= 0
        ]
        grouped_bars = [
            c
            for c in self.candidates
            if c.chart_type == "grouped_bar" and c.total_score >= 0
        ]
        waterfalls = [
            c
            for c in self.candidates
            if c.chart_type == "waterfall" and c.total_score >= 0
        ]
        stacked_areas = [
            c
            for c in self.candidates
            if c.chart_type == "stacked_area" and c.total_score >= 0
        ]
        donuts = [
            c for c in self.candidates if c.chart_type == "donut" and c.total_score >= 0
        ]
        stacked_bars = [
            c
            for c in self.candidates
            if c.chart_type == "stacked_bar" and c.total_score >= 0
        ]
        heatmaps = [
            c
            for c in self.candidates
            if c.chart_type == "heatmap" and c.total_score >= 0
        ]

        # Sort each type by score
        histograms.sort(key=lambda x: x.total_score, reverse=True)
        horizontal_bars.sort(key=lambda x: x.total_score, reverse=True)
        lines.sort(key=lambda x: x.total_score, reverse=True)
        scatters.sort(key=lambda x: x.total_score, reverse=True)
        grouped_bars.sort(key=lambda x: x.total_score, reverse=True)
        waterfalls.sort(key=lambda x: x.total_score, reverse=True)
        stacked_areas.sort(key=lambda x: x.total_score, reverse=True)
        donuts.sort(key=lambda x: x.total_score, reverse=True)
        stacked_bars.sort(key=lambda x: x.total_score, reverse=True)
        heatmaps.sort(key=lambda x: x.total_score, reverse=True)

        # Build selection with PRIORITIZED order
        selected = []

        # 1. Line chart (trend) - HIGH PRIORITY
        if lines:
            selected.append(lines[0])

        # 2. Scatter chart (correlation) - HIGH PRIORITY
        if scatters:
            selected.append(scatters[0])

        # 3. Waterfall chart (percentage changes) - HIGH PRIORITY
        if waterfalls:
            selected.append(waterfalls[0])

        # 4. Horizontal bar (ranking) - HIGH PRIORITY
        if horizontal_bars:
            selected.append(horizontal_bars[0])

        # 5. Histogram (distribution) - MEDIUM PRIORITY
        if histograms:
            selected.append(histograms[0])

        # 6. Heatmap (correlation matrix) - MEDIUM PRIORITY
        if heatmaps:
            selected.append(heatmaps[0])

        # 7. Stacked bar (composition) - MEDIUM PRIORITY
        if stacked_bars:
            selected.append(stacked_bars[0])

        # 8. Stacked area (composition over time) - MEDIUM PRIORITY
        if stacked_areas:
            selected.append(stacked_areas[0])

        # 9. Grouped bar (comparison) - MEDIUM PRIORITY
        if grouped_bars:
            selected.append(grouped_bars[0])

        # 10. Donut (ONLY if we have space and it's relevant) - LOW PRIORITY
        if donuts and len(selected) < 9:
            selected.append(donuts[0])

        # Fill remaining slots with highest scored charts
        all_remaining = [
            c for c in self.candidates if c not in selected and c.total_score >= 0
        ]
        all_remaining.sort(key=lambda x: x.total_score, reverse=True)

        for candidate in all_remaining:
            if len(selected) >= 10:
                break
            selected.append(candidate)

        return selected[:10]

    def _score_all_combinations(self):
        """Score all possible chart combinations"""
        numeric = self._prioritize_numeric_columns(self.column_types.get("numeric", []))
        categorical = self._prioritize_categorical_columns(
            self.column_types.get("categorical", [])
        )
        datetime_cols = self.column_types.get("datetime", [])
        high_card = self.column_types.get("high_cardinality", [])

        for col in numeric:
            stats = self.profile["column_profiles"].get(col, {}).get("stats", {})
            if not stats:
                continue

            biz_score = self._calculate_business_score(col, stats)
            insight_score = self._calculate_insight_score(col, stats)
            total = biz_score + insight_score

            self.candidates.append(
                ChartCandidate(
                    chart_type="histogram",
                    dimensions=[],
                    metrics=[col],
                    business_score=biz_score,
                    insight_score=insight_score,
                    total_score=total,
                    analytical_intent="What is the distribution?",
                )
            )

        for cat in categorical + high_card[:3]:
            for num in numeric[:4]:
                biz_score = self._calculate_business_score(num, {})
                insight_score = self._score_combination(cat, num)
                total = biz_score + insight_score

                self.candidates.append(
                    ChartCandidate(
                        chart_type="horizontal_bar",
                        dimensions=[cat],
                        metrics=[num],
                        business_score=biz_score,
                        insight_score=insight_score,
                        total_score=total,
                        analytical_intent="What are the top performers?",
                    )
                )

        for i, corr in enumerate(self.correlations[:5]):
            biz_score = 4
            insight_score = 5 if abs(corr.get("r", 0)) >= 0.6 else 3
            total = biz_score + insight_score

            self.candidates.append(
                ChartCandidate(
                    chart_type="scatter",
                    dimensions=[corr.get("col1", "")],
                    metrics=[corr.get("col2", "")],
                    business_score=biz_score,
                    insight_score=insight_score,
                    total_score=total,
                    analytical_intent="Is there a relationship?",
                )
            )

        if datetime_cols and numeric:
            for num in numeric[:2]:
                biz_score = 5
                insight_score = 4
                total = biz_score + insight_score

                self.candidates.append(
                    ChartCandidate(
                        chart_type="line",
                        dimensions=datetime_cols[:1],
                        metrics=[num],
                        business_score=biz_score,
                        insight_score=insight_score,
                        total_score=total,
                        analytical_intent="How does it change over time?",
                    )
                )

        if len(categorical) >= 2 and numeric:
            biz_score = self._calculate_business_score(numeric[0], {})
            insight_score = 4
            total = biz_score + insight_score

            self.candidates.append(
                ChartCandidate(
                    chart_type="grouped_bar",
                    dimensions=categorical[:2],
                    metrics=[numeric[0]],
                    business_score=biz_score,
                    insight_score=insight_score,
                    total_score=total,
                    analytical_intent="How do segments compare?",
                )
            )

        # Add waterfall chart for percentage changes
        if datetime_cols and numeric:
            for num in numeric[:2]:
                biz_score = 5
                insight_score = 5
                total = biz_score + insight_score

                self.candidates.append(
                    ChartCandidate(
                        chart_type="waterfall",
                        dimensions=datetime_cols[:1],
                        metrics=[num],
                        business_score=biz_score,
                        insight_score=insight_score,
                        total_score=total,
                        analytical_intent="What is the percentage change breakdown?",
                    )
                )

        # Add stacked area chart for composition over time
        if datetime_cols and categorical and numeric:
            biz_score = self._calculate_business_score(numeric[0], {})
            insight_score = 4
            total = biz_score + insight_score

            self.candidates.append(
                ChartCandidate(
                    chart_type="stacked_area",
                    dimensions=datetime_cols[:1],
                    metrics=[numeric[0]],
                    business_score=biz_score,
                    insight_score=insight_score,
                    total_score=total,
                    analytical_intent="How does composition change over time?",
                )
            )

        # Add donut chart ONLY for categories with <=6 unique values (limit to 1 donut max)
        for cat in categorical[:2]:
            for num in numeric[:1]:
                profile_data = self.profile["column_profiles"].get(cat, {})
                unique_count = profile_data.get("unique", 0)
                if unique_count <= 6:  # Only if <=6 categories
                    biz_score = 3
                    insight_score = 4
                    total = biz_score + insight_score

                    self.candidates.append(
                        ChartCandidate(
                            chart_type="donut",
                            dimensions=[cat],
                            metrics=[num],
                            business_score=biz_score,
                            insight_score=insight_score,
                            total_score=total,
                            analytical_intent="What is the segment breakdown?",
                        )
                    )
                    break  # Only add ONE donut chart
            break  # Only add ONE donut chart

        # Add stacked bar chart for multi-category comparison
        if len(categorical) >= 2 and numeric:
            biz_score = self._calculate_business_score(numeric[0], {})
            insight_score = 3
            total = biz_score + insight_score

            self.candidates.append(
                ChartCandidate(
                    chart_type="stacked_bar",
                    dimensions=categorical[:2],
                    metrics=[numeric[0]],
                    business_score=biz_score,
                    insight_score=insight_score,
                    total_score=total,
                    analytical_intent="How do categories break down?",
                )
            )

        # Add heatmap for multi-metric correlation
        if len(numeric) >= 3:
            biz_score = 4
            insight_score = 5
            total = biz_score + insight_score

            self.candidates.append(
                ChartCandidate(
                    chart_type="heatmap",
                    dimensions=[],
                    metrics=numeric[:5],
                    business_score=biz_score,
                    insight_score=insight_score,
                    total_score=total,
                    analytical_intent="What are the correlations between metrics?",
                )
            )

    def _calculate_business_score(self, col: str, stats: Dict) -> float:
        """Calculate business relevance score (0-10)"""
        score = 0
        col_lower = col.lower()

        for keyword, weight in BUSINESS_KEYWORDS.items():
            if keyword in col_lower:
                score += weight

        key_metrics = set(self.data_context.get("key_metrics", []))
        price_columns = set(self.data_context.get("price_columns", []))
        metric_columns = set(self.data_context.get("metric_columns", []))
        count_columns = set(self.data_context.get("count_columns", []))
        score_columns = set(self.data_context.get("score_columns", []))
        ratio_columns = set(self.data_context.get("ratio_columns", []))

        if col in key_metrics:
            score += 4
        if col in price_columns:
            score += 6
        if col in metric_columns:
            score += 3
        if col in count_columns:
            score += 1
        if col in score_columns or col in ratio_columns:
            score += 1

        profile_data = self.profile["column_profiles"].get(col, {})
        score += profile_data.get("business_score", 0) * 0.4

        null_pct = profile_data.get("null_pct", 0)
        if null_pct > 50:
            score -= 4
        elif null_pct > 30:
            score -= 2

        if profile_data.get("cardinality_ratio", 0) > 0.8:
            score -= 2

        return max(0, min(10, score))

    def _calculate_insight_score(self, col: str, stats: Dict) -> float:
        """Calculate insight potential score (0-10)"""
        score = 0

        cv = stats.get("cv", 0)
        if cv > 50:
            score += 3
        elif cv > 20:
            score += 1

        skewness = abs(stats.get("skewness", 0))
        if skewness > 1.5:
            score += 2

        outlier_pct = stats.get("outlier_pct", 0)
        if outlier_pct > 5:
            score += 1

        top1_share = stats.get("top1_share", 0)
        if top1_share > 30:
            score += 2
        if top1_share > 50:
            score += 1

        return max(0, min(10, score))

    def _score_combination(self, cat_col: str, num_col: str) -> float:
        """Score a categorical-numeric combination"""
        score = 3

        profile_data = self.profile["column_profiles"].get(cat_col, {})
        unique = profile_data.get("unique", 0)

        if unique <= 10:
            score += 2
        elif unique <= 20:
            score += 1

        category_columns = set(self.data_context.get("category_columns", []))
        if cat_col in category_columns:
            score += 1

        cat_lower = cat_col.lower()
        for keyword in ["region", "category", "segment", "type", "status", "channel"]:
            if keyword in cat_lower:
                score += 1

        if num_col in set(self.data_context.get("key_metrics", [])):
            score += 2

        return max(0, min(10, score))

    def _prioritize_numeric_columns(self, columns: List[str]) -> List[str]:
        priority_cols = []
        seen = set()

        for collection in [
            self.data_context.get("price_columns", []),
            self.data_context.get("key_metrics", []),
            self.data_context.get("metric_columns", []),
            self.data_context.get("score_columns", []),
            self.data_context.get("ratio_columns", []),
            self.data_context.get("count_columns", []),
        ]:
            for col in collection:
                if col in columns and col not in seen:
                    priority_cols.append(col)
                    seen.add(col)

        scored_remaining = []
        for col in columns:
            if col in seen:
                continue
            profile_data = self.profile.get("column_profiles", {}).get(col, {})
            financial_bonus = (
                3 if col in set(self.data_context.get("price_columns", [])) else 0
            )
            count_penalty = (
                -1 if col in set(self.data_context.get("count_columns", [])) else 0
            )
            scored_remaining.append(
                (
                    col,
                    profile_data.get("business_score", 0)
                    + financial_bonus
                    + count_penalty,
                    self._calculate_business_score(col, {}),
                )
            )

        scored_remaining.sort(key=lambda item: (item[1], item[2]), reverse=True)
        priority_cols.extend([col for col, _, _ in scored_remaining])

        return priority_cols

    def _prioritize_categorical_columns(self, columns: List[str]) -> List[str]:
        priority_cols = []
        seen = set()

        for col in self.data_context.get("category_columns", []):
            if col in columns and col not in seen:
                priority_cols.append(col)
                seen.add(col)

        preferred_keywords = [
            "region",
            "category",
            "segment",
            "channel",
            "type",
            "status",
        ]
        scored_remaining = []
        for col in columns:
            if col in seen:
                continue
            score = 0
            col_lower = col.lower()
            for keyword in preferred_keywords:
                if keyword in col_lower:
                    score += 2
            profile_data = self.profile.get("column_profiles", {}).get(col, {})
            unique = profile_data.get("unique", 0)
            if 2 <= unique <= 12:
                score += 2
            elif unique <= 20:
                score += 1
            scored_remaining.append((col, score))

        scored_remaining.sort(key=lambda item: item[1], reverse=True)
        priority_cols.extend([col for col, _ in scored_remaining])

        return priority_cols

    def get_rejection_reason(self, candidate: ChartCandidate) -> Optional[str]:
        """Get rejection reason for low-scoring charts"""
        if candidate.total_score <= 5:
            return "Score too low - insufficient business value"

        if candidate.chart_type in ["pie", "donut"] and len(candidate.dimensions) > 0:
            profile_data = self.profile["column_profiles"].get(
                candidate.dimensions[0], {}
            )
            if profile_data.get("unique", 0) > 6:
                return "Too many categories for pie chart - using bar chart instead"

        return None


class BusinessNarrator:
    """
    PHASE 4: Business Narrative Engine
    - OBSERVATION/IMPLICATION/ACTION framework
    - Severity flags (CRITICAL, WARNING, HEALTHY, INFO)
    - Plain business language
    """

    def __init__(self, profile: Dict, charts: List[Dict]):
        self.profile = profile
        self.charts = charts

    def generate_top_findings(self) -> List[BusinessInsight]:
        """Generate top 3 business findings"""
        findings = []

        quality = self.profile.get("quality", {})
        completeness = quality.get("completeness", 100)

        if completeness < 70:
            findings.append(
                BusinessInsight(
                    observation=f"Data completeness is {completeness:.1f}%",
                    implication="Significant missing data may affect analysis accuracy",
                    recommended_action="Investigate data collection processes for missing fields",
                    severity="critical",
                    metric_value=completeness,
                )
            )
        elif completeness < 90:
            findings.append(
                BusinessInsight(
                    observation=f"Data completeness is {completeness:.1f}%",
                    implication="Some analysis may be affected by missing values",
                    recommended_action="Consider data imputation or exclude incomplete records",
                    severity="warning",
                    metric_value=completeness,
                )
            )

        warnings_list = self.profile.get("warnings", [])
        high_concentration = [w for w in warnings_list if "concentrated" in w.lower()]
        if high_concentration:
            findings.append(
                BusinessInsight(
                    observation=high_concentration[0],
                    implication="High concentration means one segment dominates - diversification may be limited",
                    recommended_action="Focus on growing the dominant segment or diversify other areas",
                    severity="warning",
                )
            )

        correlations = []
        for chart in self.charts:
            if chart.get("type") == "scatter" and chart.get("correlation_r"):
                correlations.append(chart.get("correlation_r"))

        if correlations:
            strong_corr = max(correlations, key=abs)
            direction = "positive" if strong_corr > 0 else "negative"
            findings.append(
                BusinessInsight(
                    observation=f"Strong {direction} correlation detected (r={strong_corr:.2f})",
                    implication="These metrics move together - changes in one will affect the other",
                    recommended_action="Optimize both metrics together for maximum impact",
                    severity="info",
                    metric_value=strong_corr,
                )
            )

        return findings[:3]

    def generate_insight(self, chart_type: str, data: Dict) -> BusinessInsight:
        """Generate insight for a specific chart"""
        metric = data.get("metric", "")
        value = data.get("value", 0)
        benchmark = data.get("benchmark", value)
        change = data.get("change", 0)
        top_item = data.get("top_item", "")
        top_share = data.get("top_share", 0)

        if chart_type == "horizontal_bar":
            if change and abs(change) > 10:
                direction = "up" if change > 0 else "down"
                return BusinessInsight(
                    observation=f"{top_item} leads with {top_share:.1f}% of total",
                    implication=f"This represents a significant concentration in the category",
                    recommended_action="Consider whether to focus efforts on this top performer or diversify",
                    severity="warning" if top_share > 50 else "info",
                    metric_value=top_share,
                )

        if chart_type == "line":
            if change:
                direction = "up" if change > 0 else "down"
                return BusinessInsight(
                    observation=f"{metric} is trending {direction} at {abs(change):.1f}%",
                    implication=f"This suggests {'growth opportunity' if change > 0 else 'potential decline'}",
                    recommended_action=f"{'Continue current strategy' if change > 0 else 'Investigate cause of decline'}",
                    severity="healthy" if change > 0 else "warning",
                    metric_value=change,
                )

        if chart_type == "scatter":
            r = data.get("correlation_r", 0)
            return BusinessInsight(
                observation=f"Correlation coefficient: r={r:.2f}",
                implication=f"{'Strong' if abs(r) > 0.6 else 'Moderate'} relationship between metrics",
                recommended_action="Consider optimizing both metrics simultaneously for compound effect",
                severity="info",
            )

        if chart_type == "histogram":
            return BusinessInsight(
                observation=f"{metric} distribution shows {data.get('shape', 'normal')} pattern",
                implication=f"{data.get('distribution_note', 'The typical value is around the median')}",
                recommended_action=f"Use {'median' if data.get('skewed') else 'mean'} for planning purposes",
                severity="info",
            )

        if chart_type == "waterfall":
            cumulative_change = data.get("cumulative_change", 0)
            max_change = data.get("max_change", 0)
            direction = "positive" if cumulative_change > 0 else "negative"

            if abs(cumulative_change) > 20:
                severity = "critical"
            elif abs(cumulative_change) > 10:
                severity = "warning"
            else:
                severity = "healthy" if cumulative_change > 0 else "info"

            return BusinessInsight(
                observation=f"{metric} shows {abs(cumulative_change):.1f}% {direction} change overall",
                implication=f"Biggest single period change was {max_change:+.1f}%",
                recommended_action=f"{'Maintain current trajectory' if cumulative_change > 0 else 'Investigate cause of decline and consider corrective action'}",
                severity=severity,
                metric_value=cumulative_change,
            )

        if chart_type == "donut":
            return BusinessInsight(
                observation=f"Segment breakdown shows concentration in top performers",
                implication=f"Top segment holds {data.get('top_share', 0):.1f}% share",
                recommended_action="Consider diversification strategies if concentration is too high",
                severity="info",
            )

        if chart_type == "stacked_area":
            return BusinessInsight(
                observation=f"Composition analysis reveals segment dynamics over time",
                implication=f"{data.get('top_contributor', 'Top segment')} is the primary driver",
                recommended_action="Monitor growing vs declining segments for strategic decisions",
                severity="info",
            )

        return BusinessInsight(
            observation=f"Analysis of {metric} complete",
            implication="Review the visualization for patterns and opportunities",
            recommended_action="Drill down into specific segments for more insights",
            severity="info",
        )

    def format_severity(self, severity: str) -> str:
        """Format severity with emoji"""
        icons = {
            "critical": "CRITICAL",
            "warning": "WARNING",
            "healthy": "HEALTHY",
            "info": "INFO",
        }
        return icons.get(severity, severity.upper())


class DataFlowVisualizer:
    """
    Main visualization class that orchestrates all phases
    """

    def __init__(self, df: pd.DataFrame, data_context: Dict = None):
        self.df = df
        self.data_context = data_context or {}
        self.profile = None
        self.correlations = []
        self.selected_charts = []
        self.narrator = None
        self.excluded_columns: Dict[str, str] = {}

    def run_pipeline(self) -> List[Dict]:
        """Run complete analysis pipeline"""
        profile_obj = DataProfiler(self.df)
        self.profile = profile_obj.profile()

        self._compute_correlations()
        self._apply_auto_rejection()

        selector = ChartSelector(self.profile, self.correlations, self.data_context)
        self.selected_charts = selector.select_charts()

        self.narrator = BusinessNarrator(self.profile, [])

        charts = self._generate_visualizations()

        return charts

    def _compute_correlations(self):
        """Compute correlations between numeric columns"""
        numeric_cols = self.profile.get("column_types", {}).get("numeric", [])

        for i, col1 in enumerate(numeric_cols):
            for col2 in numeric_cols[i + 1 :]:
                d1 = pd.to_numeric(self.df[col1], errors="coerce")
                d2 = pd.to_numeric(self.df[col2], errors="coerce")
                valid = ~(d1.isna() | d2.isna())

                if valid.sum() > 10:
                    r = float(d1[valid].corr(d2[valid]))
                    if abs(r) >= 0.3:
                        self.correlations.append(
                            {
                                "col1": col1,
                                "col2": col2,
                                "r": r,
                                "strength": "strong" if abs(r) >= 0.7 else "moderate",
                            }
                        )

        self.correlations.sort(key=lambda x: abs(x["r"]), reverse=True)

    def _apply_auto_rejection(self):
        """Apply auto-rejection rules"""
        for col in self.profile.get("column_types", {}).get("identifier", []):
            self.excluded_columns[col] = (
                "Identifier column - use for filtering/grouping only"
            )

        if self.df.shape[0] < 10:
            self.excluded_columns["_all"] = (
                "Insufficient data for visualization (less than 10 rows)"
            )

    def _generate_visualizations(self) -> List[Dict]:
        """Generate all visualizations with RELEVANT chart types"""
        charts = []

        charts.append(self._create_executive_summary())

        for candidate in self.selected_charts:
            if candidate.chart_type == "horizontal_bar":
                charts.append(self._create_ranking_chart(candidate))
            elif candidate.chart_type == "line":
                charts.append(self._create_trend_chart(candidate))
            elif candidate.chart_type == "histogram":
                charts.append(self._create_distribution_chart(candidate))
            elif candidate.chart_type == "scatter":
                charts.append(self._create_correlation_chart(candidate))
            elif candidate.chart_type == "grouped_bar":
                charts.append(self._create_comparison_chart(candidate))
            elif candidate.chart_type == "waterfall":
                charts.append(self._create_waterfall_chart(candidate))
            elif candidate.chart_type == "stacked_area":
                charts.append(self._create_stacked_area_chart(candidate))
            elif candidate.chart_type == "donut":
                charts.append(self._create_donut_chart(candidate))
            elif candidate.chart_type == "stacked_bar":
                charts.append(self._create_stacked_bar_chart(candidate))
            elif candidate.chart_type == "heatmap":
                charts.append(self._create_heatmap_chart(candidate))

        charts.append(self._create_data_quality_chart())

        return charts

    def _create_executive_summary(self) -> Dict:
        """Create Executive Summary Dashboard"""
        fig = plt.figure(figsize=(18, 12), facecolor=OBSIDIAN)
        gs = GridSpec(4, 4, figure=fig, hspace=0.35, wspace=0.3)

        domain = self.data_context.get("business_domain", "Data Analysis")
        fig.suptitle(
            f"{domain.upper()}\nExecutive Overview",
            fontsize=20,
            fontweight="bold",
            color=GOLD,
            y=0.96,
        )

        numeric_cols = self.profile.get("column_types", {}).get("numeric", [])[:4]

        for i, col in enumerate(numeric_cols):
            stats = self.profile["column_profiles"].get(col, {}).get("stats", {})
            if not stats:
                continue

            ax = fig.add_subplot(gs[0, i])
            ax.set_facecolor(MIDNIGHT)

            rect = FancyBboxPatch(
                (0.05, 0.1),
                0.9,
                0.8,
                boxstyle="round,pad=0.02",
                facecolor=MIDNIGHT,
                edgecolor=self._get_color(i),
                linewidth=3,
            )
            ax.add_patch(rect)

            ax.text(
                0.5,
                0.85,
                self._format_name(col),
                ha="center",
                va="top",
                fontsize=11,
                color=FROST,
                fontweight="bold",
                transform=ax.transAxes,
            )

            mean_val = stats.get("mean", 0)
            ax.text(
                0.5,
                0.55,
                self._format_value(mean_val),
                ha="center",
                va="center",
                fontsize=20,
                color=self._get_color(i),
                fontweight="bold",
                transform=ax.transAxes,
            )

            cv = stats.get("cv", 0)
            ax.text(
                0.5,
                0.2,
                f"Variability: {cv:.0f}%",
                ha="center",
                va="bottom",
                fontsize=9,
                color=CHARCOAL,
                transform=ax.transAxes,
            )

            ax.axis("off")

        ax_findings = fig.add_subplot(gs[1, :])
        ax_findings.set_facecolor(MIDNIGHT)
        ax_findings.set_title(
            "KEY FINDINGS", fontsize=13, color=GOLD, fontweight="bold", pad=10
        )

        findings = self.narrator.generate_top_findings()

        for i, finding in enumerate(findings[:4]):
            severity_text = self.narrator.format_severity(finding.severity)
            color = (
                CORAL
                if finding.severity == "critical"
                else (
                    AMBER
                    if finding.severity == "warning"
                    else (EMERALD if finding.severity == "healthy" else TEAL)
                )
            )

            text = f"{severity_text}: {finding.observation}"
            ax_findings.text(
                0.02,
                0.85 - i * 0.25,
                text,
                fontsize=11,
                color=color,
                va="top",
                transform=ax_findings.transAxes,
                fontweight="bold",
            )

            ax_findings.text(
                0.04,
                0.65 - i * 0.25,
                f"-> {finding.implication}",
                fontsize=10,
                color=FROST,
                va="top",
                transform=ax_findings.transAxes,
            )

        ax_findings.set_xlim(0, 1)
        ax_findings.set_ylim(0, 1)
        ax_findings.axis("off")

        ax_kpi = fig.add_subplot(gs[2:, :])
        ax_kpi.set_facecolor(MIDNIGHT)
        ax_kpi.set_title(
            "PERFORMANCE BY SEGMENT", fontsize=13, color=GOLD, fontweight="bold", pad=10
        )

        categorical = self.profile.get("column_types", {}).get("categorical", [])
        numeric = self.profile.get("column_types", {}).get("numeric", [])

        if categorical and numeric:
            cat_col = categorical[0]
            metric_col = numeric[0]

            agg_data = (
                self.df.groupby(cat_col)[metric_col]
                .sum()
                .sort_values(ascending=False)
                .head(10)
            )

            if len(agg_data) > 0:
                colors = [GOLD if i == 0 else SLATE for i in range(len(agg_data))]
                bars = ax_kpi.barh(
                    range(len(agg_data)),
                    agg_data.values,
                    color=colors,
                    edgecolor="white",
                    height=0.7,
                )

                ax_kpi.set_yticks(range(len(agg_data)))
                ax_kpi.set_yticklabels(agg_data.index, color=FROST, fontsize=10)
                ax_kpi.invert_yaxis()

                for bar, val in zip(bars, agg_data.values):
                    pct = val / agg_data.sum() * 100
                    ax_kpi.text(
                        val + agg_data.max() * 0.02,
                        bar.get_y() + bar.get_height() / 2,
                        f"{self._format_value(val)} ({pct:.1f}%)",
                        va="center",
                        fontsize=9,
                        color=FROST,
                    )

                ax_kpi.set_xlim(0, agg_data.max() * 1.4)

        ax_kpi.tick_params(colors=CHARCOAL)
        ax_kpi.spines["top"].set_visible(False)
        ax_kpi.spines["right"].set_visible(False)
        ax_kpi.grid(True, alpha=0.1, axis="x")

        quality = self.profile.get("quality", {})
        completeness = quality.get("completeness", 100)

        plt.figtext(
            0.5,
            0.01,
            f"Data Quality: {completeness:.1f}% complete | {len(self.df):,} records | {len(self.df.columns)} columns",
            ha="center",
            fontsize=9,
            color=CHARCOAL,
        )

        plt.tight_layout(rect=[0, 0.02, 1, 0.94])

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        findings_text = " | ".join([f.observation[:50] for f in findings[:2]])

        return {
            "type": "executive_summary",
            "title": "Executive Dashboard",
            "subtitle": f"{len(self.df):,} records analyzed",
            "image_base64": img,
            "summary": findings_text,
            "business_insight": findings[0].recommended_action
            if findings
            else "Review all findings for actionable insights",
            "findings": [
                {
                    "severity": f.severity,
                    "observation": f.observation,
                    "implication": f.implication,
                    "action": f.recommended_action,
                }
                for f in findings
            ],
        }

    def _create_ranking_chart(self, candidate: ChartCandidate) -> Dict:
        """Create horizontal bar ranking chart"""
        cat_col = (
            candidate.dimensions[0]
            if candidate.dimensions
            else self.profile["column_types"]["categorical"][0]
        )
        metric_col = candidate.metrics[0]

        agg_data = (
            self.df.groupby(cat_col)[metric_col]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        others_sum = self.df[metric_col].sum() - agg_data.sum()

        fig, ax = plt.subplots(figsize=(14, 8), facecolor=OBSIDIAN)
        ax.set_facecolor(MIDNIGHT)

        colors = [GOLD] + [SLATE] * (len(agg_data) - 1)
        bars = ax.barh(
            range(len(agg_data)),
            agg_data.values,
            color=colors,
            edgecolor="white",
            height=0.7,
        )

        ax.set_yticks(range(len(agg_data)))
        ax.set_yticklabels(agg_data.index, color=FROST, fontsize=11)
        ax.invert_yaxis()

        for bar, val in zip(bars, agg_data.values):
            pct = val / agg_data.sum() * 100
            ax.text(
                val + agg_data.max() * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{self._format_value(val)} ({pct:.1f}%)",
                va="center",
                fontsize=10,
                color=FROST,
                fontweight="bold",
            )

        if others_sum > 0:
            ax.text(
                agg_data.max() * 0.5,
                -1,
                f"+ Others: {self._format_value(others_sum)}",
                fontsize=9,
                color=CHARCOAL,
                ha="center",
            )

        top_item = agg_data.index[0]
        top_share = agg_data.iloc[0] / agg_data.sum() * 100

        ax.annotate(
            f"TOP: {top_item}: {top_share:.1f}%",
            xy=(agg_data.max() * 0.7, 0),
            fontsize=12,
            color=GOLD,
            fontweight="bold",
            bbox=dict(boxstyle="round", facecolor=MIDNIGHT, edgecolor=GOLD),
        )

        ax.set_xlim(0, agg_data.max() * 1.5)
        ax.set_title(
            f"Top Performers by {self._format_name(metric_col)}",
            fontsize=16,
            color=FROST,
            fontweight="bold",
            pad=15,
        )
        ax.set_xlabel(self._format_name(metric_col), color=CHARCOAL)
        ax.tick_params(colors=CHARCOAL)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(True, alpha=0.1, axis="x")

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        insight = self.narrator.generate_insight(
            "horizontal_bar",
            {"metric": metric_col, "top_item": top_item, "top_share": top_share},
        )

        return {
            "type": "horizontal_bar",
            "title": f"Top {self._format_name(cat_col)} Ranking",
            "subtitle": f"Top 10 segments by {self._format_name(metric_col)} | {len(agg_data)} categories shown",
            "image_base64": img,
            "summary": f"{top_item} leads with {top_share:.1f}% of total",
            "business_insight": f"{insight.implication} - {insight.recommended_action}",
            "severity": insight.severity,
            "data": {"top_item": top_item, "top_share": top_share},
        }

    def _create_trend_chart(self, candidate: ChartCandidate) -> Dict:
        """Create line/area trend chart"""
        date_col = (
            candidate.dimensions[0]
            if candidate.dimensions
            else self.profile["column_types"]["datetime"][0]
        )
        metric_col = candidate.metrics[0]

        df_plot = self.df.copy()
        df_plot[date_col] = pd.to_datetime(df_plot[date_col], errors="coerce")
        df_plot[metric_col] = pd.to_numeric(df_plot[metric_col], errors="coerce")
        df_plot = df_plot.dropna(subset=[date_col, metric_col])

        if len(df_plot) < 5:
            return {
                "type": "skipped",
                "reason": "Insufficient data points for trend analysis",
            }

        freq = "W" if len(df_plot) < 50 else "ME"
        agg = (
            df_plot.groupby(pd.Grouper(key=date_col, freq=freq))[metric_col]
            .mean()
            .dropna()
        )

        if len(agg) < 3:
            return {"type": "skipped", "reason": "Insufficient aggregated periods"}

        fig, ax = plt.subplots(figsize=(14, 7), facecolor=OBSIDIAN)
        ax.set_facecolor(MIDNIGHT)

        ax.fill_between(agg.index, agg.values, alpha=0.3, color=GOLD)
        ax.plot(
            agg.index, agg.values, color=GOLD, linewidth=2.5, marker="o", markersize=6
        )

        if len(agg) > 3:
            z = np.polyfit(range(len(agg)), agg.values, 1)
            p = np.poly1d(z)
            ax.plot(
                agg.index,
                p(range(len(agg))),
                color=TEAL,
                linewidth=2,
                linestyle="--",
                label="Trend",
            )

        change = 0
        if len(agg) >= 2:
            change = (agg.iloc[-1] - agg.iloc[0]) / abs(agg.iloc[0]) * 100
            direction = "up" if change > 0 else "down"
            color = EMERALD if change > 0 else CORAL
            icon = "+" if change > 0 else ""

            ax.annotate(
                f"{icon}{change:.1f}% {direction}",
                xy=(agg.index[-1], agg.iloc[-1]),
                xytext=(10, 10),
                textcoords="offset points",
                fontsize=14,
                color=color,
                fontweight="bold",
            )

            # Add period-over-period percentage changes
            pct_changes = agg.pct_change().dropna() * 100
            if len(pct_changes) > 0:
                # Find biggest period-over-period change
                max_change_idx = abs(pct_changes).idxmax()
                max_change = pct_changes.loc[max_change_idx]
                max_change_val = agg.loc[max_change_idx]

                if abs(max_change) > 5:  # Only annotate if change > 5%
                    ax.annotate(
                        f"Max: {max_change:+.1f}%",
                        xy=(max_change_idx, max_change_val),
                        xytext=(10, -20),
                        textcoords="offset points",
                        fontsize=10,
                        color=AMBER,
                        fontweight="bold",
                        arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.5),
                    )

        ax.set_title(
            f"{self._format_name(metric_col)} Over Time",
            fontsize=16,
            color=FROST,
            fontweight="bold",
            pad=15,
        )
        ax.set_ylabel(self._format_name(metric_col), color=CHARCOAL)
        ax.tick_params(colors=CHARCOAL)
        ax.grid(True, alpha=0.1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(
            loc="upper left", facecolor=MIDNIGHT, edgecolor=CHARCOAL, labelcolor=FROST
        )

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        insight = self.narrator.generate_insight(
            "line", {"metric": metric_col, "change": change}
        )

        return {
            "type": "line",
            "title": f"{self._format_name(metric_col)} Trend",
            "subtitle": f"{len(agg)} periods analyzed | {change:+.1f}% overall change",
            "image_base64": img,
            "summary": f"Trend shows {'upward' if change > 0 else 'downward'} movement over the period",
            "business_insight": f"{insight.implication} - {insight.recommended_action}",
            "severity": insight.severity,
            "data": {"change": change},
        }

    def _create_distribution_chart(self, candidate: ChartCandidate) -> Dict:
        """Create histogram distribution chart"""
        metric_col = candidate.metrics[0]

        data = pd.to_numeric(self.df[metric_col], errors="coerce").dropna()

        if len(data) < 20:
            return {
                "type": "skipped",
                "reason": "Insufficient data for distribution analysis",
            }

        stats = self.profile["column_profiles"].get(metric_col, {}).get("stats", {})

        outlier_pct = stats.get("outlier_pct", 0)
        p99 = stats.get("p99", data.max())

        if outlier_pct > 5:
            data = data[data <= p99]

        fig, axes = plt.subplots(
            1,
            2,
            figsize=(14, 6),
            facecolor=OBSIDIAN,
            gridspec_kw={"width_ratios": [2, 1]},
        )

        ax = axes[0]
        ax.set_facecolor(MIDNIGHT)

        n_bins = min(40, max(20, int(np.sqrt(len(data)))))
        ax.hist(
            data,
            range=safe_histogram_range(data),
            bins=n_bins,
            color=GOLD,
            edgecolor="white",
            alpha=0.8,
        )

        mean_val = data.mean()
        median_val = data.median()

        ax.axvline(
            mean_val,
            color=CORAL,
            linestyle="--",
            linewidth=2.5,
            label=f"Mean: {self._format_value(mean_val)}",
        )
        ax.axvline(
            median_val,
            color=TEAL,
            linestyle="-",
            linewidth=2.5,
            label=f"Median: {self._format_value(median_val)}",
        )

        skewness = stats.get("skewness", 0)
        if abs(skewness) < 0.5:
            shape = "Normal"
            shape_icon = "="
        elif skewness > 0:
            shape = "Right-skewed"
            shape_icon = ">"
        else:
            shape = "Left-skewed"
            shape_icon = "<"

        ax.set_title(
            f"{self._format_name(metric_col)} Distribution",
            fontsize=16,
            color=FROST,
            fontweight="bold",
            pad=15,
        )
        ax.set_xlabel(self._format_name(metric_col), color=CHARCOAL)
        ax.set_ylabel("Frequency", color=CHARCOAL)
        ax.legend(
            loc="upper right", facecolor=MIDNIGHT, edgecolor=CHARCOAL, labelcolor=FROST
        )
        ax.tick_params(colors=CHARCOAL)
        ax.grid(True, alpha=0.1, axis="y")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax_stats = axes[1]
        ax_stats.set_facecolor(MIDNIGHT)
        ax_stats.axis("off")

        q1 = stats.get("q1", data.quantile(0.25))
        q3 = stats.get("q3", data.quantile(0.75))

        stats_text = f"""STATISTICS

Count: {len(data):,}
Mean: {self._format_value(mean_val)}
Median: {self._format_value(median_val)}
Std Dev: {self._format_value(data.std())}

Range: {self._format_value(data.min())} - {self._format_value(data.max())}

Quartiles:
  Q1: {self._format_value(q1)}
  Q3: {self._format_value(q3)}

Distribution:
{shape_icon} {shape}

CV: {stats.get("cv", 0):.1f}%"""

        if outlier_pct > 5:
            stats_text += f"\n\n{outlier_pct:.1f}% outliers removed"

        ax_stats.text(
            0.1,
            0.95,
            stats_text,
            transform=ax_stats.transAxes,
            fontsize=10,
            color=FROST,
            va="top",
            family="monospace",
            bbox=dict(boxstyle="round", facecolor=MIDNIGHT, edgecolor=GOLD),
        )

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        insight = self.narrator.generate_insight(
            "histogram",
            {
                "metric": metric_col,
                "shape": shape.lower(),
                "skewed": abs(skewness) > 0.5,
                "distribution_note": "Mean is pulled by extreme values"
                if abs(skewness) > 0.5
                else "Mean represents typical value well",
            },
        )

        return {
            "type": "histogram",
            "title": f"{self._format_name(metric_col)} Distribution",
            "subtitle": f"{shape} distribution | {len(data):,} values analyzed",
            "image_base64": img,
            "summary": f"{shape} - median is {self._format_value(median_val)}",
            "business_insight": f"{insight.implication} - {insight.recommended_action}",
            "severity": insight.severity,
            "data": {"shape": shape, "mean": mean_val, "median": median_val},
        }

    def _create_correlation_chart(self, candidate: ChartCandidate) -> Dict:
        """Create scatter plot with correlation"""
        col1 = candidate.metrics[0]
        col2 = (
            candidate.dimensions[0]
            if candidate.dimensions
            else candidate.metrics[1]
            if len(candidate.metrics) > 1
            else self.profile["column_types"]["numeric"][0]
        )

        if col1 == col2 and len(self.profile["column_types"]["numeric"]) > 1:
            col2 = self.profile["column_types"]["numeric"][1]

        x_data = pd.to_numeric(self.df[col1], errors="coerce")
        y_data = pd.to_numeric(self.df[col2], errors="coerce")
        valid = ~(x_data.isna() | y_data.isna())

        if valid.sum() < 20:
            return {"type": "skipped", "reason": "Insufficient paired data points"}

        sample_size = min(2000, valid.sum())
        idx = np.random.choice(valid[valid].index, sample_size, replace=False)

        fig, ax = plt.subplots(figsize=(12, 9), facecolor=OBSIDIAN)
        ax.set_facecolor(MIDNIGHT)

        ax.scatter(
            x_data[idx], y_data[idx], c=GOLD, alpha=0.6, s=50, edgecolors=OBSIDIAN
        )

        z = np.polyfit(x_data[idx], y_data[idx], 1)
        p = np.poly1d(z)
        x_line = np.linspace(x_data[idx].min(), x_data[idx].max(), 100)
        ax.plot(
            x_line, p(x_line), color=CORAL, linewidth=2.5, linestyle="--", label="Trend"
        )

        r = x_data[valid].corr(y_data[valid])
        strength = "Strong" if abs(r) > 0.6 else "Moderate" if abs(r) > 0.4 else "Weak"
        direction = "positive" if r > 0 else "negative"

        ax.annotate(
            f"r = {r:.3f}\n{strength} {direction}",
            xy=(0.05, 0.95),
            xycoords="axes fraction",
            fontsize=14,
            color=GOLD,
            fontweight="bold",
            bbox=dict(boxstyle="round", facecolor=MIDNIGHT, edgecolor=GOLD),
            verticalalignment="top",
        )

        ax.set_title(
            f"{self._format_name(col1)} vs {self._format_name(col2)}",
            fontsize=16,
            color=FROST,
            fontweight="bold",
            pad=15,
        )
        ax.set_xlabel(self._format_name(col1), color=CHARCOAL)
        ax.set_ylabel(self._format_name(col2), color=CHARCOAL)
        ax.tick_params(colors=CHARCOAL)
        ax.grid(True, alpha=0.1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(
            loc="lower right", facecolor=MIDNIGHT, edgecolor=CHARCOAL, labelcolor=FROST
        )

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        insight = self.narrator.generate_insight("scatter", {"correlation_r": r})

        return {
            "type": "scatter",
            "title": f"{self._format_name(col1)} vs {self._format_name(col2)}",
            "subtitle": f"{strength} correlation (r={r:.2f}) | {sample_size:,} points sampled",
            "image_base64": img,
            "summary": f"{strength} {direction} relationship detected",
            "business_insight": f"{insight.implication} - {insight.recommended_action}",
            "severity": insight.severity,
            "correlation_r": r,
            "data": {"r": r, "strength": strength},
        }

    def _create_comparison_chart(self, candidate: ChartCandidate) -> Dict:
        """Create grouped bar comparison chart"""
        cat_cols = self.profile["column_types"]["categorical"][:2]
        metric_col = candidate.metrics[0]

        if len(cat_cols) < 2:
            return {"type": "skipped", "reason": "Insufficient categorical columns"}

        cat1, cat2 = cat_cols[0], cat_cols[1]

        agg_data = self.df.groupby([cat1, cat2])[metric_col].mean().unstack()
        agg_data = agg_data.dropna()

        if len(agg_data) == 0 or len(agg_data.columns) == 0:
            return {"type": "skipped", "reason": "No valid comparison data"}

        fig, ax = plt.subplots(figsize=(14, 8), facecolor=OBSIDIAN)
        ax.set_facecolor(MIDNIGHT)

        x = np.arange(len(agg_data))
        width = 0.8 / len(agg_data.columns)
        colors = [GOLD, TEAL, PURPLE, CORAL]

        for i, col in enumerate(agg_data.columns[:5]):
            offset = (i - len(agg_data.columns) / 2 + 0.5) * width
            values = agg_data[col].values
            bars = ax.bar(
                x + offset,
                values,
                width,
                label=self._format_name(col),
                color=colors[i % len(colors)],
                edgecolor="white",
                alpha=0.85,
            )

            for bar, val in zip(bars, values):
                if pd.notna(val):
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + agg_data.max().max() * 0.02,
                        self._format_value(val),
                        ha="center",
                        fontsize=8,
                        color=FROST,
                        fontweight="bold",
                    )

        ax.set_xticks(x)
        ax.set_xticklabels(
            agg_data.index, color=FROST, fontsize=10, rotation=30, ha="right"
        )

        ax.set_title(
            f"{self._format_name(cat1)} by {self._format_name(cat2)}",
            fontsize=16,
            color=FROST,
            fontweight="bold",
            pad=15,
        )
        ax.set_ylabel(self._format_name(metric_col), color=CHARCOAL)
        ax.legend(
            loc="upper right", facecolor=MIDNIGHT, edgecolor=CHARCOAL, labelcolor=FROST
        )
        ax.tick_params(colors=CHARCOAL)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(True, alpha=0.1, axis="y")

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        return {
            "type": "grouped_bar",
            "title": f"{self._format_name(cat1)} Comparison",
            "subtitle": f"Comparing {len(agg_data.columns)} segments across {len(agg_data)} categories",
            "image_base64": img,
            "summary": f"Grouped comparison of {self._format_name(metric_col)}",
            "business_insight": "Identifies which segments perform best across categories",
        }

    def _create_waterfall_chart(self, candidate: ChartCandidate) -> Dict:
        """Create waterfall chart showing percentage changes"""
        date_col = (
            candidate.dimensions[0]
            if candidate.dimensions
            else self.profile["column_types"]["datetime"][0]
        )
        metric_col = candidate.metrics[0]

        df_plot = self.df.copy()
        df_plot[date_col] = pd.to_datetime(df_plot[date_col], errors="coerce")
        df_plot[metric_col] = pd.to_numeric(df_plot[metric_col], errors="coerce")
        df_plot = df_plot.dropna(subset=[date_col, metric_col])

        if len(df_plot) < 5:
            return {
                "type": "skipped",
                "reason": "Insufficient data for waterfall chart",
            }

        # Aggregate by period
        freq = "W" if len(df_plot) < 50 else "ME"
        agg = (
            df_plot.groupby(pd.Grouper(key=date_col, freq=freq))[metric_col]
            .mean()
            .dropna()
        )

        if len(agg) < 3:
            return {"type": "skipped", "reason": "Insufficient aggregated periods"}

        # Calculate percentage changes
        pct_changes = agg.pct_change().dropna() * 100

        if len(pct_changes) < 2:
            return {
                "type": "skipped",
                "reason": "Insufficient periods for percentage changes",
            }

        pct_changes = (
            pct_changes.replace([np.inf, -np.inf], np.nan).dropna().clip(-100, 100)
        )
        if len(pct_changes) < 2:
            return {
                "type": "skipped",
                "reason": "Insufficient finite percentage changes",
            }

        if len(pct_changes) > 16:
            pct_changes = pct_changes.tail(16)
            agg = agg.loc[agg.index.isin([agg.index[0], *pct_changes.index])]

        fig, ax = plt.subplots(figsize=(14, 7), facecolor=OBSIDIAN)
        ax.set_facecolor(MIDNIGHT)

        x = np.arange(len(pct_changes))

        # Color bars based on positive/negative
        colors = [EMERALD if val >= 0 else CORAL for val in pct_changes.values]

        bars = ax.bar(x, pct_changes.values, color=colors, edgecolor="white", width=0.7)

        # Add percentage labels only for the most important moves
        top_label_idx = set(abs(pct_changes).nlargest(min(4, len(pct_changes))).index)
        top_label_idx.add(pct_changes.index[-1])

        for bar, idx_label, val in zip(bars, pct_changes.index, pct_changes.values):
            if idx_label not in top_label_idx:
                continue
            y_pos = bar.get_height()
            label = f"+{val:.1f}%" if val >= 0 else f"{val:.1f}%"
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                y_pos + (0.5 if y_pos >= 0 else -1.5),
                label,
                ha="center",
                va="bottom" if y_pos >= 0 else "top",
                fontsize=10,
                color=FROST,
                fontweight="bold",
            )

        # Add zero line
        ax.axhline(y=0, color=CHARCOAL, linestyle="--", linewidth=1, alpha=0.5)

        # Add cumulative percentage annotation
        cumulative_change = ((agg.iloc[-1] - agg.iloc[0]) / abs(agg.iloc[0])) * 100
        direction = "up" if cumulative_change > 0 else "down"
        ax.annotate(
            f"Cumulative: {abs(cumulative_change):.1f}% {direction}",
            xy=(0.02, 0.95),
            xycoords="axes fraction",
            fontsize=12,
            color=GOLD if cumulative_change > 0 else CORAL,
            fontweight="bold",
            bbox=dict(
                boxstyle="round",
                facecolor=MIDNIGHT,
                edgecolor=GOLD if cumulative_change > 0 else CORAL,
            ),
        )

        # Set x-axis labels
        ax.set_xticks(x)
        x_labels = []
        for idx_label in pct_changes.index:
            if hasattr(idx_label, "strftime"):
                x_labels.append(idx_label.strftime("%b %Y"))
            else:
                x_labels.append(str(idx_label))
        ax.set_xticklabels(x_labels, color=FROST, fontsize=10, rotation=30, ha="right")

        ax.set_title(
            f"{self._format_name(metric_col)} Percentage Change by Period",
            fontsize=16,
            color=FROST,
            fontweight="bold",
            pad=15,
        )
        ax.set_ylabel("Percentage Change (%)", color=CHARCOAL)
        ax.tick_params(colors=CHARCOAL)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(True, alpha=0.1, axis="y")

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        # Find period with biggest change
        max_change_idx = abs(pct_changes).idxmax()
        max_change_val = pct_changes.loc[max_change_idx]
        max_change_date = max_change_idx

        insight = self.narrator.generate_insight(
            "waterfall",
            {
                "metric": metric_col,
                "max_change": max_change_val,
                "cumulative_change": cumulative_change,
                "direction": "positive" if cumulative_change > 0 else "negative",
            },
        )

        return {
            "type": "waterfall",
            "title": f"{self._format_name(metric_col)} Momentum by Period",
            "subtitle": f"Recent period-over-period changes | Biggest move: {max_change_val:+.1f}%",
            "image_base64": img,
            "summary": f"Shows percentage changes across {len(pct_changes)} periods",
            "business_insight": f"{insight.implication} - {insight.recommended_action}",
            "severity": insight.severity,
            "data": {
                "cumulative_change": cumulative_change,
                "max_change": max_change_val,
                "periods": len(pct_changes),
            },
        }

    def _create_stacked_area_chart(self, candidate: ChartCandidate) -> Dict:
        """Create stacked area chart showing composition over time"""
        date_col = (
            candidate.dimensions[0]
            if candidate.dimensions
            else self.profile["column_types"]["datetime"][0]
        )
        metric_col = candidate.metrics[0]
        cat_cols = self.profile.get("column_types", {}).get("categorical", [])

        if not cat_cols:
            return {
                "type": "skipped",
                "reason": "No categorical column for segmentation",
            }

        cat_col = cat_cols[0]

        df_plot = self.df.copy()
        df_plot[date_col] = pd.to_datetime(df_plot[date_col], errors="coerce")
        df_plot[metric_col] = pd.to_numeric(df_plot[metric_col], errors="coerce")
        df_plot = df_plot.dropna(subset=[date_col, metric_col, cat_col])

        if len(df_plot) < 10:
            return {"type": "skipped", "reason": "Insufficient data for stacked area"}

        # Aggregate by date and category
        freq = "W" if len(df_plot) < 100 else "ME"
        agg_data = (
            df_plot.groupby([pd.Grouper(key=date_col, freq=freq), cat_col])[metric_col]
            .sum()
            .unstack()
        )
        agg_data = agg_data.fillna(0)

        if len(agg_data) < 3:
            return {"type": "skipped", "reason": "Insufficient time periods"}

        # Limit to top 5 categories
        top_cats = agg_data.sum().sort_values(ascending=False).head(5).index
        agg_data = agg_data[top_cats]

        fig, ax = plt.subplots(figsize=(14, 7), facecolor=OBSIDIAN)
        ax.set_facecolor(MIDNIGHT)

        colors = [GOLD, TEAL, PURPLE, CORAL, EMERALD]
        ax.stackplot(
            agg_data.index,
            *[agg_data[col].values for col in agg_data.columns],
            labels=[self._format_name(str(col)) for col in agg_data.columns],
            colors=colors,
            alpha=0.8,
        )

        # Calculate percentage changes for annotation
        total_by_period = agg_data.sum(axis=1)
        if len(total_by_period) >= 2:
            first_total = total_by_period.iloc[0]
            last_total = total_by_period.iloc[-1]
            change_pct = (
                ((last_total - first_total) / abs(first_total)) * 100
                if first_total != 0
                else 0
            )

            direction = "up" if change_pct > 0 else "down"
            color = EMERALD if change_pct > 0 else CORAL

            ax.annotate(
                f"Total: {abs(change_pct):.1f}% {direction}",
                xy=(0.02, 0.95),
                xycoords="axes fraction",
                fontsize=12,
                color=color,
                fontweight="bold",
                bbox=dict(boxstyle="round", facecolor=MIDNIGHT, edgecolor=color),
            )

        ax.set_title(
            f"{self._format_name(metric_col)} Composition Over Time",
            fontsize=16,
            color=FROST,
            fontweight="bold",
            pad=15,
        )
        ax.set_ylabel(self._format_name(metric_col), color=CHARCOAL)
        ax.legend(
            loc="upper left",
            facecolor=MIDNIGHT,
            edgecolor=CHARCOAL,
            labelcolor=FROST,
            fontsize=9,
        )
        ax.tick_params(colors=CHARCOAL)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(True, alpha=0.1)

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        # Find top contributor
        top_contributor = agg_data.sum().idxmax()
        top_share = agg_data[top_contributor].sum() / agg_data.sum().sum() * 100

        return {
            "type": "stacked_area",
            "title": f"{self._format_name(metric_col)} by {self._format_name(cat_col)}",
            "subtitle": f"Composition analysis | {self._format_name(str(top_contributor))} leads with {top_share:.1f}%",
            "image_base64": img,
            "summary": f"Shows how {self._format_name(cat_col)} composition changes over time",
            "business_insight": f"Monitor which segments are growing vs declining",
            "severity": "info",
            "data": {
                "top_contributor": str(top_contributor),
                "top_share": top_share,
                "categories": len(agg_data.columns),
            },
        }

    def _create_donut_chart(self, candidate: ChartCandidate) -> Dict:
        """Create donut chart showing segment breakdown with percentages"""
        cat_col = (
            candidate.dimensions[0]
            if candidate.dimensions
            else self.profile["column_types"]["categorical"][0]
        )
        metric_col = candidate.metrics[0]

        agg_data = (
            self.df.groupby(cat_col)[metric_col]
            .sum()
            .sort_values(ascending=False)
            .head(8)
        )

        if len(agg_data) < 2:
            return {
                "type": "skipped",
                "reason": "Insufficient categories for donut chart",
            }

        fig, ax = plt.subplots(figsize=(12, 10), facecolor=OBSIDIAN)
        ax.set_facecolor(MIDNIGHT)

        colors = [GOLD, TEAL, PURPLE, CORAL, EMERALD, "#E67E22", "#8E44AD", "#1ABC9C"]

        wedges, texts, autotexts = ax.pie(
            agg_data.values,
            labels=None,
            colors=colors[: len(agg_data)],
            autopct=lambda pct: f"{pct:.1f}%" if pct > 3 else "",
            startangle=90,
            pctdistance=0.75,
            wedgeprops=dict(width=0.5, edgecolor="white"),
        )

        for autotext in autotexts:
            autotext.set_color(OBSIDIAN)
            autotext.set_fontweight("bold")
            autotext.set_fontsize(10)

        # Add total in center
        total = agg_data.sum()
        ax.text(
            0,
            0,
            f"Total\n{self._format_value(total)}",
            ha="center",
            va="center",
            fontsize=16,
            color=FROST,
            fontweight="bold",
        )

        # Create legend with percentages
        legend_labels = []
        for label, val in zip(agg_data.index, agg_data.values):
            pct = val / total * 100
            legend_labels.append(f"{self._format_name(str(label))}: {pct:.1f}%")

        ax.legend(
            wedges,
            legend_labels,
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            facecolor=MIDNIGHT,
            edgecolor=CHARCOAL,
            labelcolor=FROST,
            fontsize=10,
        )

        # Add concentration insight
        top_pct = agg_data.iloc[0] / total * 100
        if top_pct > 50:
            ax.text(
                0,
                -0.15,
                f"High concentration: {top_pct:.1f}%",
                ha="center",
                fontsize=10,
                color=CORAL,
                fontweight="bold",
            )

        ax.set_title(
            f"{self._format_name(metric_col)} by {self._format_name(cat_col)}",
            fontsize=16,
            color=FROST,
            fontweight="bold",
            pad=15,
        )

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        return {
            "type": "donut",
            "title": f"{self._format_name(cat_col)} Breakdown",
            "subtitle": f"Composition by {self._format_name(metric_col)} | {len(agg_data)} segments",
            "image_base64": img,
            "summary": f"Shows distribution of {self._format_name(metric_col)} across segments",
            "business_insight": f"{self._format_name(str(agg_data.index[0]))} dominates with {top_pct:.1f}% share",
            "severity": "info",
            "data": {
                "top_segment": str(agg_data.index[0]),
                "top_share": top_pct,
                "segments": len(agg_data),
            },
        }

    def _create_stacked_bar_chart(self, candidate: ChartCandidate) -> Dict:
        """Create stacked bar chart for multi-category breakdown"""
        cat_cols = (
            candidate.dimensions[:2]
            if len(candidate.dimensions) >= 2
            else self.profile["column_types"]["categorical"][:2]
        )
        metric_col = candidate.metrics[0]

        if len(cat_cols) < 2:
            return {
                "type": "skipped",
                "reason": "Need 2 categorical columns for stacked bar",
            }

        cat1, cat2 = cat_cols[0], cat_cols[1]

        # Aggregate data
        agg_data = self.df.groupby([cat1, cat2])[metric_col].sum().unstack(fill_value=0)

        # Limit to top categories
        if len(agg_data) > 10:
            top_cats = agg_data.sum(axis=1).sort_values(ascending=False).head(10).index
            agg_data = agg_data.loc[top_cats]

        if len(agg_data.columns) > 6:
            top_cols = agg_data.sum().sort_values(ascending=False).head(6).index
            agg_data = agg_data[top_cols]

        fig, ax = plt.subplots(figsize=(14, 8), facecolor=OBSIDIAN)
        ax.set_facecolor(MIDNIGHT)

        colors = [GOLD, TEAL, PURPLE, CORAL, EMERALD, "#E67E22"]
        agg_data.plot(
            kind="barh",
            stacked=True,
            ax=ax,
            color=colors[: len(agg_data.columns)],
            edgecolor="white",
        )

        # Add total labels
        totals = agg_data.sum(axis=1)
        for i, (idx, total) in enumerate(totals.items()):
            ax.text(
                total + totals.max() * 0.02,
                i,
                self._format_value(total),
                va="center",
                fontsize=9,
                color=FROST,
            )

        ax.set_title(
            f"{self._format_name(metric_col)} by {self._format_name(cat1)} and {self._format_name(cat2)}",
            fontsize=16,
            color=FROST,
            fontweight="bold",
            pad=15,
        )
        ax.set_xlabel(self._format_name(metric_col), color=CHARCOAL)
        ax.legend(
            [self._format_name(str(c)) for c in agg_data.columns],
            loc="upper right",
            facecolor=MIDNIGHT,
            edgecolor=CHARCOAL,
            labelcolor=FROST,
            fontsize=9,
        )
        ax.tick_params(colors=CHARCOAL)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(True, alpha=0.1, axis="x")

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        return {
            "type": "stacked_bar",
            "title": f"{self._format_name(cat1)} Breakdown by {self._format_name(cat2)}",
            "subtitle": f"Stacked comparison | {len(agg_data)} categories shown",
            "image_base64": img,
            "summary": f"Shows how {self._format_name(cat2)} composition varies across {self._format_name(cat1)}",
            "business_insight": "Identify which segments contribute most to each category",
            "severity": "info",
        }

    def _create_heatmap_chart(self, candidate: ChartCandidate) -> Dict:
        """Create correlation heatmap for multiple metrics"""
        numeric_cols = (
            candidate.metrics[:6]
            if len(candidate.metrics) >= 3
            else self.profile["column_types"]["numeric"][:6]
        )

        if len(numeric_cols) < 3:
            return {
                "type": "skipped",
                "reason": "Need at least 3 numeric columns for heatmap",
            }

        # Calculate correlation matrix
        corr_data = self.df[numeric_cols].corr()

        fig, ax = plt.subplots(figsize=(12, 10), facecolor=OBSIDIAN)
        ax.set_facecolor(MIDNIGHT)

        # Create custom colormap
        cmap = LinearSegmentedColormap.from_list("custom", [CORAL, MIDNIGHT, GOLD])

        im = ax.imshow(corr_data.values, cmap=cmap, vmin=-1, vmax=1, aspect="auto")

        # Add labels
        formatted_labels = [self._format_name(col) for col in numeric_cols]
        ax.set_xticks(range(len(numeric_cols)))
        ax.set_yticks(range(len(numeric_cols)))
        ax.set_xticklabels(
            formatted_labels, color=FROST, fontsize=10, rotation=45, ha="right"
        )
        ax.set_yticklabels(formatted_labels, color=FROST, fontsize=10)

        # Add correlation values
        for i in range(len(numeric_cols)):
            for j in range(len(numeric_cols)):
                val = corr_data.iloc[i, j]
                color = OBSIDIAN if abs(val) > 0.5 else FROST
                ax.text(
                    j,
                    i,
                    f"{val:.2f}",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color=color,
                    fontweight="bold",
                )

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.ax.tick_params(colors=CHARCOAL)
        cbar.set_label("Correlation", color=CHARCOAL)

        ax.set_title(
            "Correlation Matrix", fontsize=16, color=FROST, fontweight="bold", pad=15
        )

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        # Find strongest correlations
        strong_corrs = []
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                r = corr_data.iloc[i, j]
                if abs(r) >= 0.5:
                    strong_corrs.append(
                        {"col1": numeric_cols[i], "col2": numeric_cols[j], "r": r}
                    )

        return {
            "type": "heatmap",
            "title": "Metric Correlations",
            "subtitle": f"{len(numeric_cols)} metrics analyzed | {len(strong_corrs)} strong correlations",
            "image_base64": img,
            "summary": "Shows how metrics correlate with each other",
            "business_insight": f"Strongest correlation: {strong_corrs[0]['col1']} & {strong_corrs[0]['col2']} (r={strong_corrs[0]['r']:.2f})"
            if strong_corrs
            else "No strong correlations",
            "severity": "info",
        }

    def _create_data_quality_chart(self) -> Dict:
        """Create data quality report chart"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=OBSIDIAN)

        ax = axes[0]
        ax.set_facecolor(MIDNIGHT)

        quality = self.profile.get("quality", {})
        completeness = quality.get("completeness", 100)
        total_cells = self.df.shape[0] * self.df.shape[1]
        missing_cells = total_cells * (1 - completeness / 100)

        color = (
            EMERALD if completeness > 90 else (AMBER if completeness > 70 else CORAL)
        )
        wedges, texts, autotexts = ax.pie(
            [completeness / 100, 1 - completeness / 100],
            labels=["Complete", "Missing"],
            colors=[color, CORAL],
            autopct="%1.1f%%",
            startangle=90,
        )
        for autotext in autotexts:
            autotext.set_fontweight("bold")
            autotext.set_fontsize(12)

        ax.set_title(
            "Data Completeness", fontsize=14, color=FROST, fontweight="bold", pad=10
        )

        ax2 = axes[1]
        ax2.set_facecolor(MIDNIGHT)

        null_cols = {}
        for col, p in self.profile.get("column_profiles", {}).items():
            null_pct = (
                p.get("null_pct", 0)
                if isinstance(p, dict)
                else getattr(p, "null_percentage", 0)
            )
            if null_pct > 0:
                null_cols[col] = null_pct

        if null_cols:
            null_cols = dict(
                sorted(null_cols.items(), key=lambda x: x[1], reverse=True)[:8]
            )

            bars = ax2.barh(
                range(len(null_cols)),
                list(null_cols.values()),
                color=CORAL,
                edgecolor="white",
                height=0.6,
            )

            ax2.set_yticks(range(len(null_cols)))
            ax2.set_yticklabels(
                [self._format_name(c) for c in null_cols.keys()],
                color=FROST,
                fontsize=10,
            )
            ax2.invert_yaxis()

            for bar, val in zip(bars, null_cols.values()):
                ax2.text(
                    val + 0.5,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}%",
                    va="center",
                    fontsize=10,
                    color=FROST,
                    fontweight="bold",
                )

            ax2.set_xlim(0, max(null_cols.values()) * 1.3)

        ax2.set_title(
            "Columns with Missing Data",
            fontsize=14,
            color=FROST,
            fontweight="bold",
            pad=10,
        )
        ax2.tick_params(colors=CHARCOAL)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        status = (
            "Excellent"
            if completeness > 90
            else "Good"
            if completeness > 70
            else "Needs Attention"
        )

        return {
            "type": "quality_chart",
            "title": "Data Quality Report",
            "subtitle": f"Overall completeness: {completeness:.1f}%",
            "image_base64": img,
            "summary": f"Data quality is {status}",
            "business_insight": f"{'Data is reliable for analysis' if completeness > 90 else 'Some insights may be affected by missing data'}",
            "data": {"completeness": completeness},
        }

    def _get_color(self, i: int) -> str:
        colors = [GOLD, TEAL, PURPLE, CORAL]
        return colors[i % len(colors)]

    def _format_name(self, col: str) -> str:
        col_str = str(col).strip()
        if re.match(r"^unnamed[:\s_-]*\d*$", col_str, re.IGNORECASE):
            return "Row Index"
        if col_str.lower() == "index":
            return "Row Index"

        friendly_names = self.data_context.get("friendly_names", {})
        if col_str in friendly_names and friendly_names[col_str]:
            return friendly_names[col_str]

        return col_str.replace("_", " ").replace("-", " ").title()

    def _format_value(self, value: float) -> str:
        if pd.isna(value):
            return "N/A"
        if abs(value) >= 1_000_000_000:
            return f"{value / 1e9:.1f}B"
        elif abs(value) >= 1_000_000:
            return f"{value / 1e6:.1f}M"
        elif abs(value) >= 1_000:
            return f"{value / 1e3:.1f}K"
        return f"{value:.1f}"


def _adapt_profile_format(profile: Dict, df: pd.DataFrame) -> Dict:
    """Adapt existing profile format to the new internal format"""

    def is_identifier_column(col: str) -> bool:
        col_lower = str(col).strip().lower()
        if any(re.search(pattern, col_lower) for pattern in ID_PATTERNS):
            return True

        series = df[col].dropna()
        unique_count = int(df[col].nunique())
        row_count = len(df)
        if row_count > 10 and unique_count == row_count:
            return True

        samples = series.head(5).tolist()
        identifier_match_count = 0
        for sample in samples:
            sample_str = str(sample)
            if re.match(
                r"^(ORD|PROD|USER|CUST|EMP|INV|TXN|REF|DOC)[-_]?\d+$",
                sample_str,
                re.IGNORECASE,
            ):
                identifier_match_count += 1
            elif re.match(r"^[A-Z]{2,4}[-_]?\d{4,}$", sample_str):
                identifier_match_count += 1
            elif (
                len(sample_str) > 20
                and "-" in sample_str
                and any(c.isdigit() for c in sample_str)
            ):
                identifier_match_count += 1

        return identifier_match_count >= 3

    identifier_columns = [col for col in df.columns if is_identifier_column(col)]

    # Detect datetime columns from the dataframe
    datetime_columns = []
    for col in df.columns:
        # Check if column name suggests datetime
        col_lower = col.lower()
        if any(
            x in col_lower
            for x in ["date", "time", "timestamp", "day", "month", "year"]
        ):
            # Try to parse the first few values as dates
            samples = df[col].dropna().head(5)
            date_patterns = [
                r"^\d{4}-\d{2}-\d{2}",
                r"^\d{2}/\d{2}/\d{4}",
                r"^\d{1,2}-\w{3}-\d{2,4}",
            ]
            for sample in samples:
                for pattern in date_patterns:
                    if re.match(pattern, str(sample)):
                        datetime_columns.append(col)
                        break
                if col in datetime_columns:
                    break

    # Separate categorical columns - remove any that are detected as datetime
    categorical_columns = [
        c
        for c in profile.get("categorical_columns", [])
        if c not in datetime_columns and c not in identifier_columns
    ]
    numeric_columns = [
        c
        for c in profile.get("numeric_columns", [])
        if c not in datetime_columns and c not in identifier_columns
    ]

    adapted = {
        "column_types": {
            "numeric": numeric_columns,
            "categorical": categorical_columns,
            "datetime": datetime_columns,
            "identifier": identifier_columns,
            "high_cardinality": [],
        },
        "column_profiles": {},
        "quality": {
            "completeness": profile.get("completeness", 100),
            "total_rows": profile.get("row_count", len(df)),
            "total_columns": profile.get("column_count", len(df.columns)),
        },
        "warnings": [],
    }

    # Compute stats for numeric columns
    for col in numeric_columns:
        data = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(data) >= 3:
            try:
                stats = {
                    "mean": float(data.mean()),
                    "median": float(data.median()),
                    "std": float(data.std()),
                    "min": float(data.min()),
                    "max": float(data.max()),
                    "q1": float(data.quantile(0.25)),
                    "q3": float(data.quantile(0.75)),
                    "skewness": float(data.skew()),
                    "cv": float(data.std() / data.mean() * 100)
                    if data.mean() != 0
                    else 0,
                    "p99": float(data.quantile(0.99)),
                    "outlier_count": 0,
                    "outlier_pct": 0,
                    "top1_share": 0,
                }
                # Compute outliers using IQR
                q1, q3 = stats["q1"], stats["q3"]
                iqr = q3 - q1
                if iqr > 0:
                    outlier_mask = (data < q1 - 1.5 * iqr) | (data > q3 + 1.5 * iqr)
                    stats["outlier_count"] = int(outlier_mask.sum())
                    stats["outlier_pct"] = float(outlier_mask.sum() / len(data) * 100)
                # Compute top1 share
                if len(data) > 0:
                    stats["top1_share"] = float(
                        data.value_counts().iloc[0] / len(data) * 100
                    )
                adapted["column_profiles"][col] = {
                    "type": "CONTINUOUS",
                    "unique": int(data.nunique()),
                    "null_pct": profile.get("null_counts", {}).get(col, 0)
                    / len(df)
                    * 100,
                    "cardinality_ratio": int(data.nunique()) / len(df),
                    "stats": stats,
                    "warnings": [],
                }
            except:
                adapted["column_profiles"][col] = {
                    "type": "CONTINUOUS",
                    "unique": 0,
                    "null_pct": 0,
                    "cardinality_ratio": 0,
                    "stats": None,
                    "warnings": [],
                }

    # Handle categorical columns
    for col in categorical_columns:
        unique_count = df[col].nunique()
        adapted["column_profiles"][col] = {
            "type": "HIGH_CARDINALITY" if unique_count > 50 else "CATEGORICAL",
            "unique": int(unique_count),
            "null_pct": profile.get("null_counts", {}).get(col, 0) / len(df) * 100,
            "cardinality_ratio": unique_count / len(df),
            "stats": None,
            "warnings": [],
        }
        if unique_count > 50:
            adapted["column_types"]["high_cardinality"].append(col)

    # Handle datetime columns
    for col in datetime_columns:
        adapted["column_profiles"][col] = {
            "type": "DATETIME",
            "unique": int(df[col].nunique()),
            "null_pct": profile.get("null_counts", {}).get(col, 0) / len(df) * 100,
            "cardinality_ratio": int(df[col].nunique()) / len(df),
            "stats": None,
            "warnings": [],
        }

    for col in identifier_columns:
        adapted["column_profiles"][col] = {
            "type": "IDENTIFIER",
            "unique": int(df[col].nunique()),
            "null_pct": profile.get("null_counts", {}).get(col, 0) / len(df) * 100,
            "cardinality_ratio": int(df[col].nunique()) / len(df) if len(df) else 0,
            "stats": None,
            "warnings": ["Identifier column - excluded from chart metrics"],
        }

    return adapted


def run_ultimate_analysis(df: pd.DataFrame, data_context: Dict = None) -> Dict:
    """
    Main entry point for Ultimate Analysis Pipeline
    Implements all 7 phases of the Ultimate System Prompt
    """
    try:
        visualizer = DataFlowVisualizer(df, data_context)
        charts = visualizer.run_pipeline()

        findings = []
        if visualizer.narrator:
            findings = visualizer.narrator.generate_top_findings()

        return {
            "success": True,
            "profile": visualizer.profile,
            "charts": charts,
            "findings": findings,
            "excluded_columns": visualizer.excluded_columns,
            "warnings": visualizer.profile.get("warnings", []),
            "summary": {
                "total_records": len(df),
                "total_columns": len(df.columns),
                "charts_generated": len(
                    [c for c in charts if c.get("type") != "skipped"]
                ),
                "key_finding": findings[0].observation
                if findings
                else "Analysis complete",
            },
        }
    except Exception as e:
        import traceback

        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "charts": [],
            "findings": [],
            "profile": {},
            "excluded_columns": {},
            "warnings": [],
        }


def generate_beautiful_charts(
    df: pd.DataFrame, data_context: Dict, stats: Dict, profile: Dict
) -> List[Dict]:
    """Wrapper for backward compatibility - handles both old and new profile formats"""
    try:
        adapted_profile = _adapt_profile_format(profile, df)

        visualizer = DataFlowVisualizer(df, data_context)
        visualizer.profile = adapted_profile

        visualizer._compute_correlations()
        visualizer._apply_auto_rejection()

        selector = ChartSelector(adapted_profile, visualizer.correlations, data_context)
        visualizer.selected_charts = selector.select_charts()

        visualizer.narrator = BusinessNarrator(adapted_profile, [])

        charts = visualizer._generate_visualizations()

        return [
            chart
            for chart in charts
            if chart and chart.get("type") != "skipped" and chart.get("image_base64")
        ]
    except Exception as e:
        import traceback

        traceback.print_exc()
        return []


def create_analyst_visualizations(
    df: pd.DataFrame, data_context: Dict, stats: Dict, profile: Dict
) -> List[Dict]:
    """Wrapper for backward compatibility"""
    return generate_beautiful_charts(df, data_context, stats, profile)
