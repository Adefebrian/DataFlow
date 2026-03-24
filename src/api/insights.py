"""
Comprehensive Insights Generator for DataFlow Platform
=======================================================

This module generates insights for BOTH Data Engineer AND Data Analyst tasks:

DATA ENGINEER INSIGHTS:
- Data Quality Issues
- Schema Analysis
- Data Freshness
- Pipeline Health
- Data Lineage Indicators
- ETL Statistics
- Null/Missing Data Patterns
- Data Type Anomalies
- Duplicate Detection
- Column Cardinality Analysis

DATA ANALYST INSIGHTS:
- Executive Summary
- Financial Performance
- Key Relationships
- Segment Analysis
- Distribution Analysis
- Trend Analysis
- Anomaly Detection
- Benchmark Comparison
- Business Impact Analysis
- Actionable Recommendations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any


def generate_comprehensive_insights(
    df: pd.DataFrame, stats: Dict, profile: Dict, data_context: Dict
) -> Dict:
    """
    Generate comprehensive insights covering both DE and DA perspectives
    """
    insights = {
        "executive": [],
        "data_engineering": [],
        "data_analysis": [],
        "business": [],
        "actionable": [],
        "warnings": [],
    }

    domain = data_context.get("business_domain", "General Business")

    insights["executive"] = _generate_executive_insights(
        df, stats, profile, data_context, domain
    )
    insights["data_engineering"] = _generate_de_insights(
        df, stats, profile, data_context
    )
    insights["data_analysis"] = _generate_da_insights(df, stats, profile, data_context)
    insights["business"] = _generate_business_insights(df, stats, profile, data_context)
    insights["actionable"] = _generate_actionable_insights(
        df, stats, profile, data_context, domain
    )
    insights["warnings"] = _generate_warnings(df, stats, profile, data_context)

    all_insights = (
        insights["executive"]
        + insights["data_engineering"]
        + insights["data_analysis"]
        + insights["business"]
        + insights["actionable"]
        + insights["warnings"]
    )

    return {
        "all_insights": all_insights,
        "by_category": insights,
        "summary": {
            "total_insights": len(all_insights),
            "critical_count": len(
                [i for i in all_insights if i.get("impact") == "critical"]
            ),
            "high_count": len([i for i in all_insights if i.get("impact") == "high"]),
            "medium_count": len(
                [i for i in all_insights if i.get("impact") == "medium"]
            ),
            "warning_count": len(insights["warnings"]),
            "actionable_count": len(insights["actionable"]),
        },
    }


def _generate_executive_insights(
    df: pd.DataFrame, stats: Dict, profile: Dict, data_context: Dict, domain: str
) -> List[Dict]:
    """Executive-level insights for stakeholders"""
    insights = []

    row_count = profile.get("row_count", len(df))
    col_count = profile.get("column_count", len(df.columns))
    key_metrics = data_context.get("key_metrics", [])
    cat_cols = data_context.get("category_columns", [])

    insights.append(
        {
            "category": "executive",
            "type": "summary",
            "title": f"{domain} Analysis Overview",
            "description": f"Comprehensive analysis of {row_count:,} records across {col_count} dimensions. "
            f"Detected {len(key_metrics)} key metrics and {len(cat_cols)} categorical segments. "
            f"Industry context: {domain}.",
            "impact": "critical",
            "confidence": 95,
            "action": "Review findings below. Prioritize critical items for immediate action.",
        }
    )

    insights.append(
        {
            "category": "executive",
            "type": "data_scope",
            "title": "Analysis Scope",
            "description": f"This analysis covers {row_count:,} data points across {col_count} columns. "
            f"Data quality score: {profile.get('quality_score', 0)}%. "
            f"Completeness: {profile.get('completeness', 0)}%.",
            "impact": "medium",
            "confidence": 95,
            "action": "Ensure sample size is representative for your analysis needs.",
        }
    )

    return insights


def _generate_de_insights(
    df: pd.DataFrame, stats: Dict, profile: Dict, data_context: Dict
) -> List[Dict]:
    """
    DATA ENGINEER INSIGHTS
    ======================

    Focus: Data Quality, Pipeline Health, Schema Analysis
    """
    insights = []
    row_count = profile.get("row_count", len(df))

    null_counts = profile.get("null_counts", {})
    duplicates = profile.get("duplicate_count", 0)
    quality_score = profile.get("quality_score", 0)
    completeness = profile.get("completeness", 0)

    if null_counts:
        high_null_cols = []
        for col, count in null_counts.items():
            null_pct = (count / row_count * 100) if row_count > 0 else 0
            if null_pct > 5:
                friendly_name = data_context.get("friendly_names", {}).get(col, col)
                high_null_cols.append(f"{friendly_name}: {null_pct:.1f}%")

        if high_null_cols:
            insights.append(
                {
                    "category": "data_engineering",
                    "type": "missing_data",
                    "title": "Missing Data Analysis",
                    "description": f"Found missing data in {len(high_null_cols)} columns: {'; '.join(high_null_cols[:5])}",
                    "impact": "high"
                    if any(
                        p > 20
                        for p in [
                            float(h.split(": ")[1].replace("%", ""))
                            for h in high_null_cols
                        ]
                    )
                    else "medium",
                    "confidence": 95,
                    "action": "Investigate data pipeline for missing value causes. Consider imputation strategies.",
                }
            )

    if duplicates > 0:
        dup_pct = duplicates / row_count * 100 if row_count > 0 else 0
        insights.append(
            {
                "category": "data_engineering",
                "type": "duplicates",
                "title": "Duplicate Records Detected",
                "description": f"Found {duplicates:,} duplicate records ({dup_pct:.2f}% of data).",
                "impact": "medium",
                "confidence": 95,
                "action": "Deduplicate records to ensure analysis accuracy.",
            }
        )

    if quality_score < 70:
        insights.append(
            {
                "category": "data_engineering",
                "type": "quality_alert",
                "title": "Data Quality Alert",
                "description": f"Overall data quality score is {quality_score}%. This is below acceptable threshold (70%).",
                "impact": "critical",
                "confidence": 95,
                "action": "Review data quality issues before making business decisions. Check ETL pipeline.",
            }
        )

    insights.append(
        {
            "category": "data_engineering",
            "type": "schema_analysis",
            "title": "Schema Overview",
            "description": f"Dataset has {len(df.columns)} columns with mixed data types. "
            f"Contains {len(data_context.get('date_columns', []))} date columns, "
            f"{len(data_context.get('numeric_columns', []))} numeric columns, "
            f"{len(data_context.get('category_columns', []))} categorical columns.",
            "impact": "low",
            "confidence": 95,
            "action": "Schema is suitable for analysis. No schema changes recommended.",
        }
    )

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if numeric_cols:
        cardinality_issues = []
        for col in numeric_cols:
            unique_count = df[col].nunique()
            if unique_count == 1:
                friendly_name = data_context.get("friendly_names", {}).get(col, col)
                cardinality_issues.append(f"{friendly_name} (constant)")

        if cardinality_issues:
            insights.append(
                {
                    "category": "data_engineering",
                    "type": "cardinality",
                    "title": "Low Cardinality Columns",
                    "description": f"Found {len(cardinality_issues)} columns with no variation: {', '.join(cardinality_issues)}",
                    "impact": "medium",
                    "confidence": 95,
                    "action": "Remove constant columns as they provide no analytical value.",
                }
            )

    cat_cols = data_context.get("category_columns", [])
    high_cardinality = []
    for col in cat_cols:
        unique_count = df[col].nunique()
        if unique_count > 100:
            friendly_name = data_context.get("friendly_names", {}).get(col, col)
            high_cardinality.append(f"{friendly_name}: {unique_count} unique values")

    if high_cardinality:
        insights.append(
            {
                "category": "data_engineering",
                "type": "high_cardinality",
                "title": "High Cardinality Columns",
                "description": f"Found {len(high_cardinality)} high-cardinality columns. "
                f"Examples: {'; '.join(high_cardinality[:3])}",
                "impact": "medium",
                "confidence": 95,
                "action": "Consider bucketing or grouping high-cardinality columns for better analysis.",
            }
        )

    insights.append(
        {
            "category": "data_engineering",
            "type": "data_types",
            "title": "Data Type Summary",
            "description": f"Column type distribution: {len(numeric_cols)} numeric, "
            f"{len(cat_cols)} categorical, "
            f"{len(data_context.get('date_columns', []))} date, "
            f"{len(data_context.get('id_columns', []))} ID columns.",
            "impact": "low",
            "confidence": 95,
            "action": "Ensure proper data types are set in downstream systems.",
        }
    )

    return insights


def _generate_da_insights(
    df: pd.DataFrame, stats: Dict, profile: Dict, data_context: Dict
) -> List[Dict]:
    """
    DATA ANALYST INSIGHTS
    =====================

    Focus: Statistical Analysis, Correlations, Distributions
    """
    insights = []
    numeric_stats = stats.get("numeric", {})
    corrs = stats.get("correlations", [])

    strong_corrs = [c for c in corrs if abs(c.get("r", 0)) >= 0.6]

    if strong_corrs:
        for corr in strong_corrs[:3]:
            name1 = data_context.get("friendly_names", {}).get(
                corr.get("var1", ""), corr.get("var1", "")
            )
            name2 = data_context.get("friendly_names", {}).get(
                corr.get("var2", ""), corr.get("var2", "")
            )
            r = corr.get("r", 0)

            direction = "positive" if r > 0 else "inverse"
            strength = "very strong" if abs(r) >= 0.8 else "strong"

            insights.append(
                {
                    "category": "data_analysis",
                    "type": "correlation",
                    "title": f"{name1} ↔ {name2}",
                    "description": f"{strength.capitalize()} {direction} correlation (r={r:.2f}). "
                    f"When {name1} increases, {name2} tends to {'increase' if r > 0 else 'decrease'}.",
                    "impact": "high",
                    "confidence": int(abs(r) * 100),
                    "action": f"Use this relationship for predictive modeling. Optimizing {name1} should impact {name2}.",
                }
            )

    key_metrics = data_context.get("key_metrics", [])
    for col in key_metrics[:3]:
        friendly_name = data_context.get("friendly_names", {}).get(col, col)
        col_stats = numeric_stats.get(col, {})

        if col_stats:
            cv = col_stats.get("cv", 0)
            skew = col_stats.get("skewness", 0)

            if abs(skew) > 1:
                skew_type = "right-skewed" if skew > 0 else "left-skewed"
                insights.append(
                    {
                        "category": "data_analysis",
                        "type": "distribution",
                        "title": f"{friendly_name} Distribution",
                        "description": f"Distribution is {skew_type} (skewness: {skew:.2f}). "
                        f"Mean is {'higher' if skew > 0 else 'lower'} than median, indicating outliers.",
                        "impact": "medium",
                        "confidence": 85,
                        "action": "Consider transformation (log, Box-Cox) if used in parametric tests.",
                    }
                )

            if cv > 60:
                insights.append(
                    {
                        "category": "data_analysis",
                        "type": "variability",
                        "title": f"{friendly_name} Variability",
                        "description": f"High coefficient of variation ({cv:.1f}%). This metric shows significant variability.",
                        "impact": "medium",
                        "confidence": 90,
                        "action": "Investigate causes of high variability. Consider segment-level analysis.",
                    }
                )

    cat_cols = data_context.get("category_columns", [])
    if cat_cols:
        seg_col = cat_cols[0]
        friendly_seg = data_context.get("friendly_names", {}).get(seg_col, seg_col)

        seg_dist = df[seg_col].value_counts()
        top_cat = seg_dist.index[0]
        top_pct = seg_dist.iloc[0] / len(df) * 100

        if top_pct > 50:
            concentration = (
                "highly concentrated" if top_pct > 70 else "moderately concentrated"
            )
            insights.append(
                {
                    "category": "data_analysis",
                    "type": "concentration",
                    "title": f"{friendly_seg} Concentration",
                    "description": f"'{top_cat}' dominates with {top_pct:.1f}% share. Market is {concentration}.",
                    "impact": "high",
                    "confidence": 90,
                    "action": f"{'Defend and grow ' + top_cat if top_pct > 70 else 'Develop targeted growth for smaller segments'}.",
                }
            )

        if len(seg_dist) > 20:
            insights.append(
                {
                    "category": "data_analysis",
                    "type": "segmentation",
                    "title": f"{friendly_seg} Segmentation",
                    "description": f"Found {len(seg_dist)} unique segments. Top 5 account for {seg_dist.head(5).sum() / len(df) * 100:.1f}% of data.",
                    "impact": "medium",
                    "confidence": 90,
                    "action": "Focus analysis on top segments for actionable insights.",
                }
            )

    return insights


def _generate_business_insights(
    df: pd.DataFrame, stats: Dict, profile: Dict, data_context: Dict
) -> List[Dict]:
    """
    BUSINESS INSIGHTS
    =================

    Focus: Revenue, Performance, Comparisons
    """
    insights = []
    numeric_stats = stats.get("numeric", {})

    price_cols = data_context.get("price_columns", [])
    if price_cols:
        for price_col in price_cols[:2]:
            friendly_name = data_context.get("friendly_names", {}).get(
                price_col, price_col
            )
            price_data = numeric_stats.get(price_col, {})

            if price_data:
                avg = price_data.get("mean", 0)
                total = price_data.get("total", 0)
                median = price_data.get("median", 0)
                cv = price_data.get("cv", 0)

                insights.append(
                    {
                        "category": "business",
                        "type": "financial_snapshot",
                        "title": f"{friendly_name} Performance",
                        "description": f"Total: ${total:,.0f} | Average: ${avg:,.2f} | Median: ${median:,.2f} | CV: {cv:.1f}%",
                        "impact": "critical",
                        "confidence": 95,
                        "action": f"Use ${avg:,.2f} as baseline. Investigate drivers of variation above/below this.",
                    }
                )

    key_metrics = data_context.get("key_metrics", [])
    if len(key_metrics) >= 2:
        metric_pairs = []
        for i, m1 in enumerate(key_metrics[:4]):
            for m2 in key_metrics[i + 1 : 5]:
                for corr in stats.get("correlations", []):
                    if (corr.get("var1") == m1 and corr.get("var2") == m2) or (
                        corr.get("var1") == m2 and corr.get("var2") == m1
                    ):
                        if abs(corr.get("r", 0)) >= 0.5:
                            n1 = data_context.get("friendly_names", {}).get(m1, m1)
                            n2 = data_context.get("friendly_names", {}).get(m2, m2)
                            metric_pairs.append((n1, n2, corr.get("r", 0)))

        if metric_pairs:
            for n1, n2, r in metric_pairs[:2]:
                insights.append(
                    {
                        "category": "business",
                        "type": "kpi_relationship",
                        "title": f"{n1} → {n2} Relationship",
                        "description": f"Strong relationship between these KPIs (r={r:.2f}). They move together predictably.",
                        "impact": "high",
                        "confidence": int(abs(r) * 100),
                        "action": f"Optimize both KPIs together for amplified business impact.",
                    }
                )

    benchmarks = data_context.get("benchmarks", {})
    for col, benchmark_val in list(benchmarks.items())[:3]:
        col_stats = numeric_stats.get(col, {})
        if col_stats:
            actual_val = col_stats.get("mean", 0)
            friendly_name = data_context.get("friendly_names", {}).get(col, col)

            diff_pct = (
                ((actual_val - benchmark_val) / benchmark_val * 100)
                if benchmark_val != 0
                else 0
            )

            if abs(diff_pct) > 20:
                status = "above" if diff_pct > 0 else "below"
                insights.append(
                    {
                        "category": "business",
                        "type": "benchmark_comparison",
                        "title": f"{friendly_name} vs Benchmark",
                        "description": f"Actual: {actual_val:.2f} | Benchmark: {benchmark_val:.2f} | "
                        f"{status.capitalize()} by {abs(diff_pct):.1f}%",
                        "impact": "high",
                        "confidence": 85,
                        "action": f"{'Exceeding expectations - leverage best practices.' if diff_pct > 0 else 'Below benchmark - investigate underperformance.'}",
                    }
                )

    return insights


def _generate_actionable_insights(
    df: pd.DataFrame, stats: Dict, profile: Dict, data_context: Dict, domain: str
) -> List[Dict]:
    """
    ACTIONABLE RECOMMENDATIONS
    ===========================

    Focus: Clear, actionable next steps
    """
    insights = []

    insights.append(
        {
            "category": "actionable",
            "type": "recommended_actions",
            "title": "Top 3 Recommended Actions",
            "description": f"Based on {domain} analysis: "
            f"1) Focus on top-performing segments, "
            f"2) Investigate strong correlations for optimization opportunities, "
            f"3) Address any data quality issues before major decisions.",
            "impact": "critical",
            "confidence": 90,
            "action": "Prioritize these actions in your next planning cycle.",
        }
    )

    key_metrics = data_context.get("key_metrics", [])
    if key_metrics:
        top_metric = key_metrics[0]
        friendly_name = data_context.get("friendly_names", {}).get(
            top_metric, top_metric
        )

        insights.append(
            {
                "category": "actionable",
                "type": "metric_focus",
                "title": f"Focus on {friendly_name}",
                "description": f"{friendly_name} is identified as the primary metric for this analysis. "
                f"Track this metric closely for business health indicators.",
                "impact": "high",
                "confidence": 85,
                "action": f"Set up monitoring for {friendly_name}. Create alerts for anomalies.",
            }
        )

    strong_corrs = [
        c for c in stats.get("correlations", []) if abs(c.get("r", 0)) >= 0.7
    ]
    if strong_corrs:
        top_corr = strong_corrs[0]
        n1 = data_context.get("friendly_names", {}).get(top_corr.get("var1", ""), "")
        n2 = data_context.get("friendly_names", {}).get(top_corr.get("var2", ""), "")

        insights.append(
            {
                "category": "actionable",
                "type": "optimization_opportunity",
                "title": f"Optimization Opportunity: {n1} & {n2}",
                "description": f"These metrics show very strong correlation (r={top_corr.get('r', 0):.2f}). "
                f"Optimizing one should drive improvements in the other.",
                "impact": "high",
                "confidence": int(abs(top_corr.get("r", 0)) * 100),
                "action": "Design experiments to optimize both metrics simultaneously.",
            }
        )

    cat_cols = data_context.get("category_columns", [])
    if cat_cols:
        seg_col = cat_cols[0]
        seg_perf = (
            df.groupby(seg_col)[key_metrics[0]].mean().sort_values(ascending=False)
            if key_metrics
            else None
        )

        if seg_perf is not None and len(seg_perf) >= 2:
            top_seg = seg_perf.index[0]
            bottom_seg = seg_perf.index[-1]

            insights.append(
                {
                    "category": "actionable",
                    "type": "segment_strategy",
                    "title": f"Segment Strategy: {top_seg} vs {bottom_seg}",
                    "description": f"'{top_seg}' performs best while '{bottom_seg}' lags behind. "
                    f"Study '{top_seg}' to understand success factors.",
                    "impact": "high",
                    "confidence": 85,
                    "action": f"Conduct deep-dive on '{top_seg}'. Apply learnings to '{bottom_seg}'.",
                }
            )

    return insights


def _generate_warnings(
    df: pd.DataFrame, stats: Dict, profile: Dict, data_context: Dict
) -> List[Dict]:
    """
    WARNINGS & ALERTS
    ==================

    Focus: Issues that need attention
    """
    warnings = []
    row_count = profile.get("row_count", len(df))

    if row_count < 30:
        warnings.append(
            {
                "category": "warning",
                "type": "small_sample",
                "title": "Small Sample Size",
                "description": f"Only {row_count} records. Statistical significance may be limited.",
                "impact": "high",
                "confidence": 95,
                "action": "Consider collecting more data for robust analysis.",
            }
        )

    if profile.get("quality_score", 100) < 60:
        warnings.append(
            {
                "category": "warning",
                "type": "low_quality",
                "title": "Low Data Quality",
                "description": f"Data quality score: {profile.get('quality_score', 0)}%. Results may be unreliable.",
                "impact": "critical",
                "confidence": 95,
                "action": "Improve data quality before making decisions based on this analysis.",
            }
        )

    null_counts = profile.get("null_counts", {})
    critical_nulls = []
    for col, count in null_counts.items():
        null_pct = (count / row_count * 100) if row_count > 0 else 0
        if null_pct > 30:
            friendly_name = data_context.get("friendly_names", {}).get(col, col)
            critical_nulls.append(f"{friendly_name}: {null_pct:.1f}%")

    if critical_nulls:
        warnings.append(
            {
                "category": "warning",
                "type": "high_missing",
                "title": "Critical Missing Data",
                "description": f"Columns with >30% missing: {', '.join(critical_nulls[:3])}",
                "impact": "critical",
                "confidence": 95,
                "action": "These columns may need to be excluded or imputed before analysis.",
            }
        )

    cat_cols = data_context.get("category_columns", [])
    if cat_cols:
        for col in cat_cols[:3]:
            unique_count = df[col].nunique()
            if unique_count == len(df):
                friendly_name = data_context.get("friendly_names", {}).get(col, col)
                warnings.append(
                    {
                        "category": "warning",
                        "type": "unique_identifier",
                        "title": f"Unique Column: {friendly_name}",
                        "description": f"This column has {unique_count} unique values (one per row). Likely an ID.",
                        "impact": "low",
                        "confidence": 95,
                        "action": "Avoid using this column for aggregation or segmentation.",
                    }
                )

    return warnings


def generate_focused_insights(
    df: pd.DataFrame, stats: Dict, profile: Dict, data_context: Dict
) -> List[Dict]:
    """
    Main entry point for insight generation
    Returns a flat list of insights for backward compatibility
    """
    result = generate_comprehensive_insights(df, stats, profile, data_context)

    return result["all_insights"]


def get_skill_category(domain: str, data_context: Dict) -> Dict:
    """
    Map detected domain to relevant analyst skills (ENHANCED)
    Covers both Data Engineer and Data Analyst skills
    """

    skill_mapping = {
        "Sales": {
            "category": "Sales & Revenue Analytics",
            "analyst_skills": [
                "Revenue Analysis",
                "Pipeline Analysis",
                "Win Rate Calculation",
                "Sales Forecasting",
                "Territory Analysis",
                "Quota Tracking",
                "Conversion Funnel",
                "Customer Lifetime Value",
                "RFM Analysis",
                "YoY/MoM Comparison",
                "Attribution Modeling",
                "Cohort Analysis",
                "A/B Testing",
                "Territory Planning",
                "Deal Analysis",
            ],
            "engineer_skills": [
                "Data Pipeline",
                "CRM Integration",
                "Sales Data Quality",
                "Pipeline Monitoring",
                "Data Validation",
                "ETL Automation",
            ],
            "kpis": [
                "Revenue",
                "Win Rate",
                "Average Deal Size",
                "Sales Cycle",
                "Pipeline Coverage",
            ],
        },
        "Marketing": {
            "category": "Marketing Analytics",
            "analyst_skills": [
                "Campaign ROI Analysis",
                "Channel Attribution",
                "Funnel Analysis",
                "Conversion Rate Optimization",
                "A/B Testing",
                "Customer Segmentation",
                "Engagement Metrics",
                "CAC Calculation",
                "LTV Estimation",
                "Marketing Mix Modeling",
                "Incremental Lift Analysis",
                "Attribution Modeling",
                "Media Mix Optimization",
                "Customer Journey Analysis",
            ],
            "engineer_skills": [
                "Marketing Automation Data",
                "UTM Tracking",
                "Pixel Integration",
                "Marketing Stack Integration",
                "Campaign Data Quality",
            ],
            "kpis": ["CAC", "LTV", "ROI", "CTR", "Conversion Rate"],
        },
        "HR": {
            "category": "People Analytics",
            "analyst_skills": [
                "Turnover Analysis",
                "Retention Analysis",
                "Compensation Benchmarking",
                "Productivity Metrics",
                "Engagement Scoring",
                "Attrition Prediction",
                "Workforce Planning",
                "Diversity Analysis",
                "Tenure Analysis",
                "Performance Distribution",
                "Flight Risk Analysis",
                "Sentiment Scoring",
                "HR Dashboard",
                "Headcount Planning",
                "Succession Planning",
            ],
            "engineer_skills": [
                "HRIS Integration",
                "Payroll Data Quality",
                "Attendance Tracking",
                "Employee Data Pipeline",
                "Compliance Reporting",
            ],
            "kpis": [
                "Turnover Rate",
                "Engagement Score",
                "Productivity",
                "Retention Rate",
            ],
        },
        "Finance": {
            "category": "Financial Analytics",
            "analyst_skills": [
                "Profitability Analysis",
                "Margin Analysis",
                "Budget Variance",
                "Cost Benefit Analysis",
                "Break-Even Analysis",
                "Cash Flow Analysis",
                "ROI Calculation",
                "NPV/IRR Analysis",
                "Variance Decomposition",
                "Bridge Analysis",
                "Scenario Planning",
                "Unit Economics",
                "Financial Forecasting",
                "Ratio Analysis",
                "Working Capital Analysis",
            ],
            "engineer_skills": [
                "ERP Integration",
                "Financial Data Quality",
                "Reconciliation Pipeline",
                "Audit Trail",
                "Financial Reporting Automation",
            ],
            "kpis": ["Gross Margin", "Net Margin", "ROI", "ROA", "Burn Rate"],
        },
        "Operations": {
            "category": "Operational Analytics",
            "analyst_skills": [
                "Process Efficiency",
                "Throughput Analysis",
                "Bottleneck Detection",
                "Capacity Planning",
                "Inventory Turnover",
                "Lead Time Analysis",
                "Quality Metrics",
                "OEE Calculation",
                "Root Cause Analysis",
                "SLA Tracking",
                "Process Mining",
                "Kaizen Analysis",
                "Supply Chain Analytics",
                "Logistics Optimization",
            ],
            "engineer_skills": [
                "Supply Chain Integration",
                "IoT Data Pipeline",
                "Quality Control Data",
                "Operations Monitoring",
                "Real-time Analytics Infrastructure",
            ],
            "kpis": [
                "Throughput",
                "Cycle Time",
                "Quality Rate",
                "On-Time Delivery",
                "OEE",
            ],
        },
        "Retail/Ecommerce": {
            "category": "Retail Analytics",
            "analyst_skills": [
                "Basket Analysis",
                "Product Affinity",
                "Inventory Optimization",
                "Pricing Analysis",
                "Promotional Effectiveness",
                "Category Management",
                "Customer Segmentation",
                "RFM Analysis",
                "Churn Analysis",
                "Conversion Funnel",
                "Cart Abandonment",
                "Seasonality Analysis",
                "Store Performance",
                "Assortment Planning",
            ],
            "engineer_skills": [
                "POS Integration",
                "Inventory System",
                "E-commerce Platform Data",
                "Customer Data Platform",
                "Retail Data Quality",
            ],
            "kpis": ["AOV", "Basket Size", "Conversion Rate", "Inventory Turns", "GMV"],
        },
        "Customer Service": {
            "category": "Service Analytics",
            "analyst_skills": [
                "CSAT Analysis",
                "NPS Calculation",
                "Response Time Metrics",
                "Resolution Rate",
                "Ticket Classification",
                "Escalation Analysis",
                "Agent Performance",
                "SLA Compliance",
                "First Contact Resolution",
                "Churn Prediction",
                "Effort Score",
                "Service Cost Analysis",
                "Customer Journey Mapping",
            ],
            "engineer_skills": [
                "CRM Integration",
                "Helpdesk Data",
                "Call Center Integration",
                "Service Quality Monitoring",
            ],
            "kpis": [
                "CSAT",
                "NPS",
                "First Response Time",
                "Resolution Time",
                "CS Cost",
            ],
        },
        "Healthcare": {
            "category": "Healthcare Analytics",
            "analyst_skills": [
                "Patient Outcome Analysis",
                "Clinical Trials",
                "Population Health",
                "Readmission Analysis",
                "Length of Stay",
                "Cost per Case",
                "Bed Utilization",
                "Staffing Optimization",
                "HCAHPS Analysis",
            ],
            "engineer_skills": [
                "EHR Integration",
                "HIPAA Compliance",
                "Clinical Data Pipeline",
                "Claims Data Processing",
            ],
            "kpis": [
                "Readmission Rate",
                "Length of Stay",
                "Bed Occupancy",
                "Patient Satisfaction",
            ],
        },
        "General Business": {
            "category": "Business Analytics",
            "analyst_skills": [
                "Descriptive Statistics",
                "Trend Analysis",
                "Variance Analysis",
                "Correlation Analysis",
                "Benchmark Comparison",
                "KPI Design",
                "Dashboard Building",
                "Data Storytelling",
                "Gap Analysis",
                "SWOT Quantification",
                "Scenario Planning",
                "Drill-Down Analysis",
                "Executive Reporting",
                "Business Intelligence",
            ],
            "engineer_skills": [
                "Data Pipeline Architecture",
                "Data Quality Framework",
                "ETL/ELT Processes",
                "Data Governance",
                "Schema Design",
                "Data Cataloging",
                "Lineage Tracking",
                "Data Validation",
            ],
            "kpis": ["Revenue", "Growth Rate", "Efficiency", "Quality", "Satisfaction"],
        },
    }

    return skill_mapping.get(domain, skill_mapping["General Business"])
