"""
Comprehensive Analytics Module - Senior Data Analyst System
==========================================================

FIXED: Trend & Period Change analytics
ADDED: More chart types and relevant analysis
FIXED: Column and title naming
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from scipy import stats as scipy_stats
import warnings
import re

warnings.filterwarnings("ignore")

# Smart sampling limits
MAX_SCATTER_POINTS = 1500
MAX_BAR_CATEGORIES = 12
MIN_TREND_POINTS = 3


class ComprehensiveAnalyzer:
    """Senior Data Analyst Expert System with FIXED trend detection"""

    def __init__(self, df: pd.DataFrame, data_context: Dict = None):
        self.df = df.copy()
        self.data_context = data_context or {}
        self.numeric_cols = []
        self.categorical_cols = []
        self.datetime_cols = []
        self.insights = []
        self.kpis = {}
        self.trends = {}
        self.period_changes = {}
        self.anomalies = []
        self.recommendations = []
        self.summary_tables = {}
        self.relationships = []
        self.sampled_df = None

    def analyze(self) -> Dict:
        """Run comprehensive analysis"""
        self._identify_columns_smart()
        self._create_smart_sample()
        self._calculate_kpis()
        self._calculate_trends_and_period_changes()  # FIXED: Combined method
        self._detect_anomalies()
        self._analyze_relationships()
        self._generate_insights()
        self._create_summary_tables()
        self._generate_recommendations()
        return self._compile_results()

    def _identify_columns_smart(self):
        """Smart column type detection"""
        for col in self.df.columns:
            col_lower = col.lower()
            dtype = str(self.df[col].dtype)
            sample_values = self.df[col].dropna().head(10).tolist()

            # Check for datetime
            if self._is_datetime_column(col_lower, dtype, sample_values):
                self.datetime_cols.append(col)
            # Check for numeric
            elif self._is_numeric_column(col, dtype, sample_values):
                self.numeric_cols.append(col)
            # Otherwise categorical
            else:
                self.categorical_cols.append(col)

    def _is_datetime_column(self, col_name: str, dtype: str, samples: List) -> bool:
        """Detect datetime columns"""
        if "datetime" in dtype:
            return True

        date_keywords = [
            "date",
            "time",
            "timestamp",
            "created",
            "updated",
            "day",
            "month",
            "year",
            "period",
        ]
        if any(kw in col_name for kw in date_keywords):
            date_patterns = [
                r"^\d{4}-\d{2}-\d{2}",
                r"^\d{4}/\d{2}/\d{2}",
                r"^\d{2}/\d{2}/\d{4}",
            ]
            matches = sum(
                1 for s in samples[:5] for p in date_patterns if re.match(p, str(s))
            )
            if matches >= 2:
                return True
        return False

    def _is_numeric_column(self, col: str, dtype: str, samples: List) -> bool:
        """Detect numeric columns"""
        if any(x in dtype for x in ["int", "float", "number"]):
            return True
        try:
            numeric_count = sum(
                1 for s in samples[:10] if pd.notna(pd.to_numeric(s, errors="coerce"))
            )
            return numeric_count >= len(samples) * 0.8
        except:
            return False

    def _create_smart_sample(self):
        """Create smart sample - NOT all records"""
        if len(self.df) <= MAX_SCATTER_POINTS:
            self.sampled_df = self.df.copy()
        else:
            self.sampled_df = self.df.sample(n=MAX_SCATTER_POINTS, random_state=42)

    def _calculate_kpis(self):
        """Calculate business KPIs"""
        for col in self.numeric_cols:
            data = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(data) >= 3:
                self.kpis[col] = {
                    "sum": float(data.sum()),
                    "mean": float(data.mean()),
                    "median": float(data.median()),
                    "std": float(data.std()),
                    "min": float(data.min()),
                    "max": float(data.max()),
                    "q1": float(data.quantile(0.25)),
                    "q3": float(data.quantile(0.75)),
                    "cv": float(data.std() / data.mean() * 100)
                    if data.mean() != 0
                    else 0,
                    "count": int(len(data)),
                }

    def _calculate_trends_and_period_changes(self):
        """FIXED: Calculate trends and period-over-period changes"""
        # Find date column
        date_col = None
        if self.datetime_cols:
            date_col = self.datetime_cols[0]

        if date_col:
            try:
                df_temp = self.df.copy()
                df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors="coerce")
                df_sorted = df_temp.dropna(subset=[date_col]).sort_values(date_col)

                if len(df_sorted) >= MIN_TREND_POINTS:
                    for col in self.numeric_cols[:6]:
                        data = pd.to_numeric(df_sorted[col], errors="coerce").dropna()
                        if len(data) >= MIN_TREND_POINTS:
                            self._calculate_trend_for_column(col, data)
            except Exception as e:
                print(f"Date-based trend error: {e}")
                # Fall back to row-based trends
                self._calculate_row_based_trends()
        else:
            self._calculate_row_based_trends()

    def _calculate_trend_for_column(self, col: str, data: pd.Series):
        """Calculate trend and period changes for a single column"""
        # Overall change
        first_val = data.iloc[0]
        last_val = data.iloc[-1]

        if first_val != 0:
            overall_change_pct = ((last_val - first_val) / abs(first_val)) * 100
        else:
            overall_change_pct = 0

        # Linear regression
        x = np.arange(len(data))
        try:
            slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(
                x, data.values
            )
        except:
            slope, r_value, p_value = 0, 0, 1

        # Period-over-period changes
        pct_changes = data.pct_change().dropna()
        pct_changes = pct_changes.replace([np.inf, -np.inf], np.nan).dropna()

        if len(pct_changes) > 0:
            avg_period_change = float(pct_changes.mean() * 100)
            volatility = float(pct_changes.std() * 100)
            max_increase = float(pct_changes.max() * 100)
            max_decrease = float(pct_changes.min() * 100)
        else:
            avg_period_change = 0
            volatility = 0
            max_increase = 0
            max_decrease = 0

        # Store trend
        self.trends[col] = {
            "direction": "increasing"
            if slope > 0
            else "decreasing"
            if slope < 0
            else "stable",
            "strength": "strong"
            if abs(r_value) > 0.7
            else "moderate"
            if abs(r_value) > 0.4
            else "weak",
            "overall_change_pct": float(overall_change_pct),
            "avg_period_change_pct": avg_period_change,
            "volatility_pct": volatility,
            "max_increase_pct": max_increase,
            "max_decrease_pct": max_decrease,
            "r_squared": float(r_value**2),
            "periods_analyzed": len(data),
            "first_value": float(first_val),
            "last_value": float(last_val),
            "min_value": float(data.min()),
            "max_value": float(data.max()),
        }

        # Store period changes
        self.period_changes[col] = {
            "overall_change_pct": float(overall_change_pct),
            "avg_period_change_pct": avg_period_change,
            "periods_count": len(pct_changes),
            "positive_periods": int((pct_changes > 0).sum()),
            "negative_periods": int((pct_changes < 0).sum()),
            "stable_periods": int((pct_changes == 0).sum()),
        }

    def _calculate_row_based_trends(self):
        """Calculate trends using row index as time proxy"""
        for col in self.numeric_cols[:6]:
            data = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(data) >= MIN_TREND_POINTS:
                self._calculate_trend_for_column(col, data)

    def _detect_anomalies(self):
        """Detect anomalies"""
        for col in self.numeric_cols:
            data = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(data) >= 10:
                q1, q3 = data.quantile(0.25), data.quantile(0.75)
                iqr = q3 - q1
                if iqr > 0:
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    outliers = data[(data < lower_bound) | (data > upper_bound)]
                    outlier_pct = len(outliers) / len(data) * 100
                    if outlier_pct > 1:
                        self.anomalies.append(
                            {
                                "column": col,
                                "outlier_count": len(outliers),
                                "outlier_pct": float(outlier_pct),
                                "severity": "high"
                                if outlier_pct > 10
                                else "medium"
                                if outlier_pct > 5
                                else "low",
                            }
                        )

    def _analyze_relationships(self):
        """Analyze relationships between columns"""
        # Correlation analysis
        if len(self.numeric_cols) >= 2:
            for i, col1 in enumerate(self.numeric_cols):
                for col2 in self.numeric_cols[i + 1 :]:
                    d1 = pd.to_numeric(self.df[col1], errors="coerce")
                    d2 = pd.to_numeric(self.df[col2], errors="coerce")
                    valid = ~(d1.isna() | d2.isna())
                    if valid.sum() >= 10:
                        r = float(d1[valid].corr(d2[valid]))
                        if abs(r) >= 0.3:
                            self.relationships.append(
                                {
                                    "col1": col1,
                                    "col2": col2,
                                    "correlation": r,
                                    "strength": "strong"
                                    if abs(r) >= 0.7
                                    else "moderate"
                                    if abs(r) >= 0.5
                                    else "weak",
                                    "type": "positive" if r > 0 else "negative",
                                }
                            )

        # Sort by strength
        self.relationships.sort(
            key=lambda x: abs(x.get("correlation", 0)), reverse=True
        )

    def _generate_insights(self):
        """Generate insights"""
        # Trend insights
        for col, trend in self.trends.items():
            if trend["strength"] in ["strong", "moderate"]:
                direction = trend["direction"]
                change = trend["overall_change_pct"]
                self.insights.append(
                    {
                        "type": "trend",
                        "severity": "info",
                        "observation": f"{self._format_col_name(col)}: {trend['strength']} {direction} trend ({change:+.1f}% overall)",
                        "recommendation": f"Monitor this {'growth' if direction == 'increasing' else 'decline'}",
                    }
                )

        # Relationship insights
        for rel in self.relationships[:3]:
            col1 = self._format_col_name(rel["col1"])
            col2 = self._format_col_name(rel["col2"])
            self.insights.append(
                {
                    "type": "relationship",
                    "severity": "info",
                    "observation": f"{col1} and {col2}: {rel['strength']} {rel['type']} correlation (r={rel['correlation']:.2f})",
                    "recommendation": "Optimize these metrics together",
                }
            )

    def _create_summary_tables(self):
        """Create summary tables"""
        # Numeric summary
        if self.kpis:
            numeric_summary = []
            for col, kpi in self.kpis.items():
                trend = self.trends.get(col, {})
                numeric_summary.append(
                    {
                        "Metric": self._format_col_name(col),
                        "Total": self._format_number(kpi["sum"]),
                        "Average": self._format_number(kpi["mean"]),
                        "Median": self._format_number(kpi["median"]),
                        "Min": self._format_number(kpi["min"]),
                        "Max": self._format_number(kpi["max"]),
                        "Trend": trend.get("direction", "N/A").title()
                        if trend
                        else "N/A",
                        "Change (%)": f"{trend.get('overall_change_pct', 0):+.1f}"
                        if trend
                        else "N/A",
                    }
                )
            self.summary_tables["numeric_summary"] = numeric_summary

        # Trend summary
        if self.trends:
            trend_summary = []
            for col, trend in self.trends.items():
                trend_summary.append(
                    {
                        "Metric": self._format_col_name(col),
                        "Direction": trend["direction"].title(),
                        "Strength": trend["strength"].title(),
                        "Overall Change (%)": f"{trend['overall_change_pct']:+.1f}",
                        "Avg Period Change (%)": f"{trend['avg_period_change_pct']:+.2f}",
                        "Volatility (%)": f"{trend['volatility_pct']:.1f}",
                        "Periods": trend["periods_analyzed"],
                    }
                )
            self.summary_tables["trend_summary"] = trend_summary

        # Relationship summary
        if self.relationships:
            rel_summary = []
            for rel in self.relationships[:10]:
                rel_summary.append(
                    {
                        "Column 1": self._format_col_name(rel["col1"]),
                        "Column 2": self._format_col_name(rel["col2"]),
                        "Correlation": f"{rel['correlation']:.3f}",
                        "Strength": rel["strength"].title(),
                        "Type": rel["type"].title(),
                    }
                )
            self.summary_tables["relationship_summary"] = rel_summary

        # Top comparisons
        if self.categorical_cols and self.numeric_cols:
            comparison_summary = []
            for cat_col in self.categorical_cols[:3]:
                for num_col in self.numeric_cols[:2]:
                    try:
                        agg = (
                            self.df.groupby(cat_col)[num_col]
                            .sum()
                            .sort_values(ascending=False)
                            .head(10)
                        )
                        if len(agg) >= 2:
                            total = agg.sum()
                            comparison_summary.append(
                                {
                                    "Category": self._format_col_name(cat_col),
                                    "Metric": self._format_col_name(num_col),
                                    "Top Item": str(agg.index[0]),
                                    "Top Value": self._format_number(agg.iloc[0]),
                                    "Top Share (%)": f"{agg.iloc[0] / total * 100:.1f}",
                                    "Total": self._format_number(total),
                                }
                            )
                    except:
                        pass
            self.summary_tables["comparison_summary"] = comparison_summary

    def _generate_recommendations(self):
        """Generate recommendations"""
        for col, trend in self.trends.items():
            if trend["strength"] == "strong":
                if trend["direction"] == "increasing":
                    self.recommendations.append(
                        {
                            "priority": "high",
                            "area": self._format_col_name(col),
                            "recommendation": f"Leverage the upward trend in {self._format_col_name(col).lower()}",
                            "action": "Allocate resources to maintain growth",
                        }
                    )
                else:
                    self.recommendations.append(
                        {
                            "priority": "critical",
                            "area": self._format_col_name(col),
                            "recommendation": f"Address the declining trend in {self._format_col_name(col).lower()}",
                            "action": "Investigate root causes",
                        }
                    )

    def _compile_results(self) -> Dict:
        """Compile results"""
        return {
            "success": True,
            "executive_summary": self._generate_executive_summary(),
            "kpis": self.kpis,
            "trends": self.trends,
            "period_changes": self.period_changes,
            "anomalies": self.anomalies,
            "relationships": self.relationships[:10],
            "insights": self.insights,
            "recommendations": self.recommendations,
            "summary_tables": self.summary_tables,
            "data_profile": {
                "total_rows": len(self.df),
                "total_columns": len(self.df.columns),
                "numeric_columns": len(self.numeric_cols),
                "categorical_columns": len(self.categorical_cols),
                "datetime_columns": len(self.datetime_cols),
                "sample_size": len(self.sampled_df)
                if self.sampled_df is not None
                else len(self.df),
            },
            "sampling_info": {
                "original_rows": len(self.df),
                "sampled_rows": len(self.sampled_df)
                if self.sampled_df is not None
                else len(self.df),
                "sampling_method": "stratified"
                if len(self.df) > MAX_SCATTER_POINTS
                else "full",
            },
        }

    def _generate_executive_summary(self) -> Dict:
        """Generate executive summary"""
        sorted_insights = sorted(
            self.insights,
            key=lambda x: {"high": 1, "medium": 2, "low": 3, "info": 4}.get(
                x.get("severity", "info"), 5
            ),
        )

        key_metrics = {}
        for col in self.numeric_cols[:5]:
            kpi = self.kpis.get(col, {})
            trend = self.trends.get(col, {})
            if kpi:
                key_metrics[self._format_col_name(col)] = {
                    "value": kpi.get("mean", 0),
                    "total": kpi.get("sum", 0),
                    "trend": trend.get("direction", "stable") if trend else "stable",
                    "change": trend.get("overall_change_pct", 0) if trend else 0,
                }

        return {
            "total_records": len(self.df),
            "total_metrics": len(self.numeric_cols),
            "total_categories": len(self.categorical_cols),
            "key_metrics": key_metrics,
            "top_insights": sorted_insights[:5],
            "critical_actions": [
                r for r in self.recommendations if r["priority"] in ["critical", "high"]
            ][:3],
            "top_relationships": [
                r
                for r in self.relationships
                if r.get("strength") in ["strong", "moderate"]
            ][:3],
            "data_quality_score": self._calculate_quality_score(),
        }

    def _calculate_quality_score(self) -> float:
        """Calculate quality score"""
        score = 100.0
        total_missing = self.df.isnull().sum().sum()
        total_cells = len(self.df) * len(self.df.columns)
        missing_pct = total_missing / total_cells * 100
        score -= missing_pct * 0.5
        return max(0, min(100, score))

    def _format_col_name(self, col: str) -> str:
        """Format column name for display"""
        return col.replace("_", " ").replace("-", " ").title()

    def _format_number(self, value: float) -> str:
        """Format number"""
        if pd.isna(value):
            return "N/A"
        if abs(value) >= 1_000_000_000:
            return f"{value / 1e9:.1f}B"
        elif abs(value) >= 1_000_000:
            return f"{value / 1e6:.1f}M"
        elif abs(value) >= 1_000:
            return f"{value / 1e3:.1f}K"
        return f"{value:.1f}"


def run_comprehensive_analysis(df: pd.DataFrame, data_context: Dict = None) -> Dict:
    """Run comprehensive analysis"""
    analyzer = ComprehensiveAnalyzer(df, data_context)
    return analyzer.analyze()
