"""
Interactive Analytics Data Generator
=====================================
Generates structured JSON data for frontend interactive charts (recharts-compatible).
Covers: KPIs w/ % change, time-series, distributions, segments, correlation matrix,
waterfall % change, box plots, composition (pie/donut), scatter, growth rates.
"""

import warnings
from src.utils.math_utils import safe_histogram_range
from collections import defaultdict
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── Keyword dictionaries ────────────────────────────────────────────────────

FINANCIAL_KW = {
    "price",
    "cost",
    "amount",
    "revenue",
    "sales",
    "profit",
    "budget",
    "fee",
    "charge",
    "payment",
    "expense",
    "income",
    "salary",
    "wage",
    "discount",
    "margin",
    "total",
    "cash",
    "capital",
    "investment",
    "turnover",
    "tax",
    "gross",
    "net",
    "commission",
    "bonus",
    "value",
    "worth",
}
RATE_KW = {
    "rate",
    "percentage",
    "pct",
    "percent",
    "ratio",
    "share",
    "contribution",
    "growth",
    "change",
    "conversion",
    "churn",
    "retention",
    "utilization",
    "efficiency",
    "yield",
    "return",
}
PRIORITY_KW = [
    "revenue",
    "sales",
    "profit",
    "cost",
    "amount",
    "price",
    "quantity",
    "count",
    "total",
    "score",
    "rate",
    "margin",
]

# ── Utility helpers ─────────────────────────────────────────────────────────


def safe_pct_change(new_val: float, old_val: float) -> Optional[float]:
    """Return % change from old_val → new_val, or None when undefined."""
    try:
        if old_val is None or old_val == 0:
            return None
        if np.isnan(float(old_val)) or np.isnan(float(new_val)):
            return None
        return round(((float(new_val) - float(old_val)) / abs(float(old_val))) * 100, 1)
    except Exception:
        return None


def fmt_value(val: float, col_name: str = "") -> str:
    """Human-readable display string, context-aware (financial / rate / plain)."""
    try:
        col_lower = col_name.lower()
        is_financial = any(kw in col_lower for kw in FINANCIAL_KW)
        is_rate = any(kw in col_lower for kw in RATE_KW)
        prefix = "$" if is_financial else ""
        if is_rate and 0 <= abs(val) <= 500:
            return f"{val:.1f}%"
        if abs(val) >= 1_000_000_000:
            return f"{prefix}{val / 1_000_000_000:.2f}B"
        if abs(val) >= 1_000_000:
            return f"{prefix}{val / 1_000_000:.2f}M"
        if abs(val) >= 1_000:
            return f"{prefix}{val / 1_000:.1f}K"
        return f"{prefix}{val:,.2f}"
    except Exception:
        return str(val)


def trend_direction(pct: Optional[float]) -> str:
    if pct is None:
        return "neutral"
    return "positive" if pct > 2 else "negative" if pct < -2 else "neutral"


def dname(col: str) -> str:
    """Convert snake_case / camelCase column to Title Case display name."""
    return col.replace("_", " ").replace("-", " ").title()


def safe_float(val: Any) -> Optional[float]:
    try:
        f = float(val)
        return None if (np.isnan(f) or np.isinf(f)) else round(f, 4)
    except Exception:
        return None


def clean_series(series: pd.Series) -> pd.Series:
    """Return numeric-coerced, inf-removed, NaN-dropped series."""
    return (
        pd.to_numeric(series, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )


def detect_datetime_columns(df: pd.DataFrame) -> List[str]:
    """Return list of column names that are (or can be parsed as) datetime."""
    found: List[str] = []
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            found.append(col)
        else:
            try:
                parsed = pd.to_datetime(
                    df[col], infer_datetime_format=True, errors="coerce"
                )
                if parsed.notna().sum() > len(df) * 0.7:
                    found.append(col)
            except Exception:
                pass
    return found


def prioritize_columns(cols: List[str]) -> List[str]:
    """Reorder columns so PRIORITY_KW matches come first."""
    selected: List[str] = []
    rest: List[str] = []
    for kw in PRIORITY_KW:
        for col in cols:
            if kw in col.lower() and col not in selected:
                selected.append(col)
    for col in cols:
        if col not in selected:
            rest.append(col)
    return selected + rest


# ── KPI computation ─────────────────────────────────────────────────────────


def compute_kpis(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """
    Up to 8 numeric KPI cards (sorted by business priority).
    Each card includes: mean, total, formatted values, period-over-period
    pct_change, trend direction, and a 20-point sparkline.
    """
    kpis: List[Dict] = []
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        return kpis

    dt_cols = detect_datetime_columns(df)
    has_time = len(dt_cols) > 0

    # Build first-half / second-half split
    if has_time:
        df_work = df.copy()
        df_work[dt_cols[0]] = pd.to_datetime(df_work[dt_cols[0]], errors="coerce")
        df_sorted = df_work.sort_values(dt_cols[0])
        mid = len(df_sorted) // 2
        df_first, df_second = df_sorted.iloc[:mid], df_sorted.iloc[mid:]
    else:
        mid = len(df) // 2
        df_first, df_second = df.iloc[:mid], df.iloc[mid:]

    for col in prioritize_columns(numeric_cols)[:8]:
        try:
            data = clean_series(df[col])
            if len(data) < 2:
                continue

            mean_val = float(data.mean())
            total_val = float(data.sum())
            min_val = float(data.min())
            max_val = float(data.max())
            median_val = float(data.median())
            std_val = float(data.std())

            first_mean = (
                safe_float(clean_series(df_first[col]).mean())
                if len(df_first) > 0
                else None
            )
            second_mean = (
                safe_float(clean_series(df_second[col]).mean())
                if len(df_second) > 0
                else None
            )
            pct_change = (
                safe_pct_change(second_mean, first_mean)
                if (first_mean and second_mean)
                else None
            )

            step = max(1, len(data) // 20)
            sparkline = [safe_float(v) for v in data.iloc[::step].tolist()[:20]]

            kpis.append(
                {
                    "name": col,
                    "display_name": dname(col),
                    "value": safe_float(mean_val),
                    "total": safe_float(total_val),
                    "formatted_value": fmt_value(mean_val, col),
                    "formatted_total": fmt_value(total_val, col),
                    "pct_change": pct_change,
                    "trend": trend_direction(pct_change),
                    "min": safe_float(min_val),
                    "max": safe_float(max_val),
                    "median": safe_float(median_val),
                    "std": safe_float(std_val),
                    "sparkline": sparkline,
                    "period_label": "vs prior period"
                    if has_time
                    else "first half vs second half",
                }
            )
        except Exception:
            continue

    return kpis


# ── Time series ─────────────────────────────────────────────────────────────


def compute_time_series(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """
    Detect datetime column, auto-select period granularity, resample up to 5
    numeric columns, attach per-period pct_change and cumulative pct from start.
    """
    dt_cols = detect_datetime_columns(df)
    if not dt_cols:
        return []

    date_col = dt_cols[0]
    df_ts = df.copy()
    df_ts[date_col] = pd.to_datetime(df_ts[date_col], errors="coerce")
    df_ts = df_ts.dropna(subset=[date_col]).sort_values(date_col)

    if len(df_ts) < 3:
        return []

    span_days = (df_ts[date_col].max() - df_ts[date_col].min()).days
    if span_days > 730:
        freq, period_label = "YE", "Yearly"
    elif span_days > 90:
        freq, period_label = "ME", "Monthly"
    elif span_days > 14:
        freq, period_label = "W", "Weekly"
    else:
        freq, period_label = "D", "Daily"

    numeric_cols = df_ts.select_dtypes(include=["number"]).columns.tolist()
    ordered = prioritize_columns(numeric_cols)[:5]
    if not ordered:
        return []

    try:
        agg = (
            df_ts.set_index(date_col)[ordered]
            .resample(freq)
            .mean()
            .dropna(how="all")
            .tail(60)
            .reset_index()
        )

        data_points: List[Dict] = []
        first_vals: Dict[str, float] = {}

        for i, row in agg.iterrows():
            point: Dict[str, Any] = {"period": str(row[date_col])[:10]}
            for col in ordered:
                val = safe_float(row.get(col))
                if val is None:
                    point[col] = None
                    point[f"{col}_pct_change"] = None
                    point[f"{col}_cumulative_pct"] = None
                    continue

                point[col] = val
                # period-over-period
                prev = data_points[-1].get(col) if data_points else None
                point[f"{col}_pct_change"] = (
                    safe_pct_change(val, prev) if prev is not None else None
                )
                # cumulative from first
                if col not in first_vals:
                    first_vals[col] = val
                    point[f"{col}_cumulative_pct"] = 0.0
                else:
                    point[f"{col}_cumulative_pct"] = safe_pct_change(
                        val, first_vals[col]
                    )

            data_points.append(point)

        return [
            {
                "date_column": date_col,
                "period": period_label,
                "metrics": [{"key": c, "display_name": dname(c)} for c in ordered],
                "data": data_points,
            }
        ]
    except Exception:
        return []


# ── Distributions ───────────────────────────────────────────────────────────


def compute_distributions(df: pd.DataFrame) -> List[Dict]:
    """
    25-bin histogram + stats + percentile breakdown for up to 10 numeric cols.
    """
    results: List[Dict] = []
    ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())

    for col in ordered[:10]:
        try:
            data = clean_series(df[col])
            if len(data) < 5:
                continue

            counts, bin_edges = np.histogram(data, range=safe_histogram_range(data), bins=25)
            total_count = int(counts.sum())

            histogram = []
            for i in range(len(counts)):
                center = (bin_edges[i] + bin_edges[i + 1]) / 2
                histogram.append(
                    {
                        "bin_start": safe_float(bin_edges[i]),
                        "bin_end": safe_float(bin_edges[i + 1]),
                        "label": fmt_value(center, col),
                        "count": int(counts[i]),
                        "pct": round(float(counts[i]) / total_count * 100, 1)
                        if total_count
                        else 0.0,
                    }
                )

            q1 = float(data.quantile(0.25))
            q3 = float(data.quantile(0.75))
            iqr = q3 - q1
            outlier_mask = (data < q1 - 1.5 * iqr) | (data > q3 + 1.5 * iqr)

            results.append(
                {
                    "column": col,
                    "display_name": dname(col),
                    "histogram": histogram,
                    "stats": {
                        "mean": safe_float(data.mean()),
                        "median": safe_float(data.median()),
                        "std": safe_float(data.std()),
                        "min": safe_float(data.min()),
                        "max": safe_float(data.max()),
                        "q1": safe_float(q1),
                        "q3": safe_float(q3),
                        "skewness": safe_float(data.skew()),
                        "kurtosis": safe_float(data.kurt()),
                        "outlier_pct": round(
                            float(outlier_mask.sum() / len(data) * 100), 1
                        ),
                        "outlier_count": int(outlier_mask.sum()),
                    },
                    "percentile_data": [
                        {"label": "P5", "value": safe_float(data.quantile(0.05))},
                        {"label": "P25", "value": safe_float(data.quantile(0.25))},
                        {"label": "P50", "value": safe_float(data.quantile(0.50))},
                        {"label": "P75", "value": safe_float(data.quantile(0.75))},
                        {"label": "P95", "value": safe_float(data.quantile(0.95))},
                    ],
                    "formatted_mean": fmt_value(float(data.mean()), col),
                    "formatted_median": fmt_value(float(data.median()), col),
                }
            )
        except Exception:
            continue

    return results


# ── Segment analysis ─────────────────────────────────────────────────────────


def compute_segments(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """
    For each categorical col (≤20 unique) × each numeric col (priority order):
    groupby mean/sum/count, enrich with share_pct and vs_avg_pct.
    """
    results: List[Dict] = []
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    num_ordered = prioritize_columns(
        df.select_dtypes(include=["number"]).columns.tolist()
    )

    for cat_col in cat_cols[:4]:
        u = df[cat_col].nunique()
        if u < 2 or u > 20:
            continue
        for num_col in num_ordered[:3]:
            try:
                valid = df[[cat_col, num_col]].dropna()
                if len(valid) < 5:
                    continue

                grp = (
                    valid.groupby(cat_col)[num_col]
                    .agg(["mean", "sum", "count"])
                    .reset_index()
                )
                grp.columns = [cat_col, "mean", "total", "count"]
                grp = grp.sort_values("total", ascending=False).head(15)

                grand_total = float(grp["total"].sum())
                overall_mean = float(valid[num_col].mean())

                rows = []
                for _, row in grp.iterrows():
                    rm = float(row["mean"])
                    rt = float(row["total"])
                    rows.append(
                        {
                            "category": str(row[cat_col]),
                            "mean": safe_float(rm),
                            "total": safe_float(rt),
                            "count": int(row["count"]),
                            "share_pct": round(rt / grand_total * 100, 1)
                            if grand_total
                            else 0.0,
                            "vs_avg_pct": safe_pct_change(rm, overall_mean),
                            "direction": "above" if rm > overall_mean else "below",
                            "formatted_mean": fmt_value(rm, num_col),
                            "formatted_total": fmt_value(rt, num_col),
                        }
                    )

                # Build multi-metric rows for radar chart support
                metrics_available = num_ordered[:5]
                for row_obj in rows:
                    cat_val = row_obj["category"]
                    for m in metrics_available:
                        if m == num_col:
                            continue
                        try:
                            seg_mean = float(valid[valid[cat_col] == cat_val][m].mean()) if m in valid.columns else None
                            if seg_mean is not None and not np.isnan(seg_mean):
                                row_obj[m] = safe_float(seg_mean)
                        except Exception:
                            pass

                results.append(
                    {
                        "dimension": cat_col,
                        "metric": num_col,
                        "display_dimension": dname(cat_col),
                        "display_metric": dname(num_col),
                        "metrics": [m for m in metrics_available if m != cat_col],
                        "data": rows,
                        "total": safe_float(grand_total),
                        "overall_mean": safe_float(overall_mean),
                        "formatted_total": fmt_value(grand_total, num_col),
                    }
                )
            except Exception:
                continue

    return results


# ── Correlation matrix ───────────────────────────────────────────────────────


def compute_correlation_matrix(df: pd.DataFrame) -> Dict:
    """
    Full Pearson correlation matrix for up to 12 numeric columns.
    Returns cells list + deduplicated top-15 pairs with |r| ≥ 0.3.
    """
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if len(num_cols) < 2:
        return {}

    # Prefer columns with highest average absolute cross-correlation
    if len(num_cols) > 12:
        try:
            full_corr = df[num_cols].corr().abs()
            num_cols = full_corr.mean().nlargest(12).index.tolist()
        except Exception:
            num_cols = num_cols[:12]

    try:
        corr = df[num_cols].corr()

        def strength(r: float) -> str:
            a = abs(r)
            if a >= 0.9:
                return "Very Strong"
            if a >= 0.7:
                return "Strong"
            if a >= 0.5:
                return "Moderate"
            if a >= 0.3:
                return "Weak"
            return "Negligible"

        cells = []
        for c1 in num_cols:
            for c2 in num_cols:
                val = corr.loc[c1, c2]
                if np.isnan(val):
                    continue
                cells.append(
                    {
                        "x": c1,
                        "y": c2,
                        "value": round(float(val), 3),
                        "abs_value": round(abs(float(val)), 3),
                        "strength": strength(float(val)),
                    }
                )

        seen: set = set()
        top_corr: List[Dict] = []
        for c in sorted(cells, key=lambda x: x["abs_value"], reverse=True):
            if c["x"] == c["y"]:
                continue
            if c["abs_value"] < 0.3:
                break
            pair = frozenset([c["x"], c["y"]])
            if pair in seen:
                continue
            seen.add(pair)
            top_corr.append(
                {
                    **c,
                    "display_x": dname(c["x"]),
                    "display_y": dname(c["y"]),
                    "direction": "positive" if c["value"] > 0 else "negative",
                }
            )

        return {
            "columns": num_cols,
            "display_columns": [dname(c) for c in num_cols],
            "cells": cells,
            "top_correlations": top_corr[:15],
        }
    except Exception:
        return {}


# ── Percentage change analysis ───────────────────────────────────────────────


def compute_percentage_changes(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """
    Three sub-analyses:
      1) quartile_comparison  – top-25% mean vs bottom-25% mean per numeric col
      2) vs_average           – each category mean vs overall mean (waterfall-style)
      3) top_bottom_5         – top-5 vs bottom-5 categories
    """
    results: List[Dict] = []
    num_ordered = prioritize_columns(
        df.select_dtypes(include=["number"]).columns.tolist()
    )
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # 1. Quartile comparison
    for col in num_ordered[:6]:
        try:
            data = clean_series(df[col])
            if len(data) < 10:
                continue
            q25, q75 = float(data.quantile(0.25)), float(data.quantile(0.75))
            top_mean = float(data[data >= q75].mean())
            bot_mean = float(data[data <= q25].mean())
            med = float(data.median())
            pct = safe_pct_change(top_mean, bot_mean)
            results.append(
                {
                    "type": "quartile_comparison",
                    "column": col,
                    "display_name": dname(col),
                    "top_quartile_mean": safe_float(top_mean),
                    "bottom_quartile_mean": safe_float(bot_mean),
                    "median": safe_float(med),
                    "pct_difference": pct,
                    "direction": trend_direction(pct),
                    "formatted_top": fmt_value(top_mean, col),
                    "formatted_bottom": fmt_value(bot_mean, col),
                    "bars": [
                        {
                            "label": "Bottom 25%",
                            "value": safe_float(bot_mean),
                            "formatted": fmt_value(bot_mean, col),
                        },
                        {
                            "label": "Median",
                            "value": safe_float(med),
                            "formatted": fmt_value(med, col),
                        },
                        {
                            "label": "Top 25%",
                            "value": safe_float(top_mean),
                            "formatted": fmt_value(top_mean, col),
                        },
                    ],
                }
            )
        except Exception:
            continue

    # 2. vs_average waterfall
    for cat_col in cat_cols[:3]:
        u = df[cat_col].nunique()
        if u < 2 or u > 20:
            continue
        for num_col in num_ordered[:2]:
            try:
                valid = df[[cat_col, num_col]].dropna()
                if len(valid) < 5:
                    continue
                overall_mean = float(valid[num_col].mean())
                grouped = valid.groupby(cat_col)[num_col].mean()

                waterfall = []
                for cat_val, cat_mean in grouped.items():
                    cm = float(cat_mean)
                    pct = safe_pct_change(cm, overall_mean)
                    waterfall.append(
                        {
                            "category": str(cat_val),
                            "value": safe_float(cm),
                            "vs_average": safe_float(cm - overall_mean),
                            "pct_vs_average": pct,
                            "direction": "above" if cm > overall_mean else "below",
                            "formatted_value": fmt_value(cm, num_col),
                        }
                    )
                waterfall.sort(key=lambda x: x["value"] or 0, reverse=True)

                results.append(
                    {
                        "type": "vs_average",
                        "dimension": cat_col,
                        "metric": num_col,
                        "display_dimension": dname(cat_col),
                        "display_metric": dname(num_col),
                        "overall_average": safe_float(overall_mean),
                        "formatted_average": fmt_value(overall_mean, num_col),
                        "data": waterfall,
                    }
                )
            except Exception:
                continue

    # 3. Top-5 vs Bottom-5
    for cat_col in cat_cols[:2]:
        u = df[cat_col].nunique()
        if u < 5 or u > 200:
            continue
        for num_col in num_ordered[:2]:
            try:
                valid = df[[cat_col, num_col]].dropna()
                if len(valid) < 10:
                    continue
                ranked = (
                    valid.groupby(cat_col)[num_col].mean().sort_values(ascending=False)
                )
                if len(ranked) < 5:
                    continue
                top5 = ranked.head(5)
                bot5 = ranked.tail(5)
                pct_gap = safe_pct_change(float(top5.mean()), float(bot5.mean()))
                results.append(
                    {
                        "type": "top_bottom_5",
                        "dimension": cat_col,
                        "metric": num_col,
                        "display_dimension": dname(cat_col),
                        "display_metric": dname(num_col),
                        "pct_gap": pct_gap,
                        "top_5": [
                            {
                                "category": str(k),
                                "value": safe_float(float(v)),
                                "formatted": fmt_value(float(v), num_col),
                            }
                            for k, v in top5.items()
                        ],
                        "bottom_5": [
                            {
                                "category": str(k),
                                "value": safe_float(float(v)),
                                "formatted": fmt_value(float(v), num_col),
                            }
                            for k, v in bot5.items()
                        ],
                    }
                )
            except Exception:
                continue

    return results


# ── Box plot data ────────────────────────────────────────────────────────────


def compute_boxplot_data(df: pd.DataFrame) -> List[Dict]:
    """
    Tukey IQR box plot for up to 6 numeric cols.
    Optionally breaks down by category (2–12 unique values).
    """
    results: List[Dict] = []
    num_ordered = prioritize_columns(
        df.select_dtypes(include=["number"]).columns.tolist()
    )
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    for col in num_ordered[:6]:
        try:
            data = clean_series(df[col])
            if len(data) < 5:
                continue

            q1 = float(data.quantile(0.25))
            q3 = float(data.quantile(0.75))
            iqr = q3 - q1
            wlo = (
                float(data[data >= q1 - 1.5 * iqr].min())
                if iqr > 0
                else float(data.min())
            )
            whi = (
                float(data[data <= q3 + 1.5 * iqr].max())
                if iqr > 0
                else float(data.max())
            )
            outs = data[(data < q1 - 1.5 * iqr) | (data > q3 + 1.5 * iqr)]

            by_cat: List[Dict] = []
            if cat_cols:
                c = cat_cols[0]
                if 2 <= df[c].nunique() <= 12:
                    for cat_val in df[c].dropna().unique():
                        cd = clean_series(df[df[c] == cat_val][col])
                        if len(cd) < 3:
                            continue
                        cq1 = float(cd.quantile(0.25))
                        cq3 = float(cd.quantile(0.75))
                        ci = cq3 - cq1
                        by_cat.append(
                            {
                                "category": str(cat_val),
                                "min": safe_float(
                                    float(cd[cd >= cq1 - 1.5 * ci].min())
                                    if ci > 0
                                    else float(cd.min())
                                ),
                                "q1": safe_float(cq1),
                                "median": safe_float(float(cd.median())),
                                "q3": safe_float(cq3),
                                "max": safe_float(
                                    float(cd[cd <= cq3 + 1.5 * ci].max())
                                    if ci > 0
                                    else float(cd.max())
                                ),
                                "mean": safe_float(float(cd.mean())),
                                "count": int(len(cd)),
                            }
                        )
                    by_cat.sort(key=lambda x: x.get("median") or 0, reverse=True)

            results.append(
                {
                    "column": col,
                    "display_name": dname(col),
                    "min": safe_float(wlo),
                    "q1": safe_float(q1),
                    "median": safe_float(float(data.median())),
                    "q3": safe_float(q3),
                    "max": safe_float(whi),
                    "mean": safe_float(float(data.mean())),
                    "iqr": safe_float(iqr),
                    "outlier_count": int(len(outs)),
                    "outliers": [safe_float(v) for v in outs.tolist()[:100]],
                    "by_category": by_cat[:12],
                    "formatted_median": fmt_value(float(data.median()), col),
                    "formatted_mean": fmt_value(float(data.mean()), col),
                }
            )
        except Exception:
            continue

    return results


# ── Composition (pie / donut) ────────────────────────────────────────────────


def compute_composition(df: pd.DataFrame) -> List[Dict]:
    """
    Pie (by count) and donut_metric (by numeric sum) for each categorical col.
    Groups long tails into 'Others'.
    """
    results: List[Dict] = []
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    num_ord = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())

    for cat_col in cat_cols[:3]:
        u = df[cat_col].nunique()
        if u < 2 or u > 15:
            continue
        try:
            vc = df[cat_col].value_counts()
            top_cats = vc.head(8)
            rest_count = int(vc.iloc[8:].sum()) if len(vc) > 8 else 0
            total_count = int(vc.sum())

            pie_data = [
                {
                    "name": str(k),
                    "value": int(v),
                    "pct": round(v / total_count * 100, 1),
                }
                for k, v in top_cats.items()
            ]
            if rest_count > 0:
                pie_data.append(
                    {
                        "name": "Others",
                        "value": rest_count,
                        "pct": round(rest_count / total_count * 100, 1),
                    }
                )

            results.append(
                {
                    "type": "pie",
                    "column": cat_col,
                    "display_name": dname(cat_col),
                    "data": pie_data,
                    "total": total_count,
                }
            )

            if num_ord:
                num_col = num_ord[0]
                stacked = (
                    df.groupby(cat_col)[num_col].sum().sort_values(ascending=False)
                )
                total_val = float(stacked.sum())

                donut_data = [
                    {
                        "name": str(k),
                        "value": safe_float(float(v)),
                        "pct": round(float(v) / total_val * 100, 1)
                        if total_val
                        else 0.0,
                    }
                    for k, v in stacked.head(8).items()
                ]
                rest_val = float(stacked.iloc[8:].sum()) if len(stacked) > 8 else 0.0
                if rest_val > 0:
                    donut_data.append(
                        {
                            "name": "Others",
                            "value": safe_float(rest_val),
                            "pct": round(rest_val / total_val * 100, 1)
                            if total_val
                            else 0.0,
                        }
                    )

                results.append(
                    {
                        "type": "donut_metric",
                        "column": cat_col,
                        "metric": num_col,
                        "display_name": f"{dname(cat_col)} by {dname(num_col)}",
                        "data": donut_data,
                        "total": safe_float(total_val),
                        "formatted_total": fmt_value(total_val, num_col),
                    }
                )
        except Exception:
            continue

    return results


# ── Scatter ───────────────────────────────────────────────────────────────────


def compute_scatter_data(df: pd.DataFrame) -> List[Dict]:
    """
    Smart scatter: uses ONLY low-cardinality categorical cols for color.
    Date columns and high-cardinality strings are NEVER used as category.
    Each point aggregated by category mean to keep points readable (<= 100 pts).
    """
    results: List[Dict] = []
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if len(num_cols) < 2:
        return results

    dt_col_names = set(detect_datetime_columns(df))

    # Only low-cardinality (2-12 unique) true categorical cols — never dates
    cat_cols = [
        c for c in df.select_dtypes(include=["object", "category"]).columns.tolist()
        if c not in dt_col_names and 2 <= df[c].nunique() <= 12
    ]

    pairs = []
    for i, c1 in enumerate(num_cols):
        for c2 in num_cols[i + 1:]:
            try:
                r = float(df[[c1, c2]].dropna().corr().iloc[0, 1])
                if not np.isnan(r):
                    pairs.append((c1, c2, abs(r), r))
            except Exception:
                pass

    pairs.sort(key=lambda x: x[2], reverse=True)

    for c1, c2, abs_r, r in pairs[:6]:
        if abs_r < 0.15:
            continue
        try:
            color_col = cat_cols[0] if cat_cols else None

            if color_col:
                # Aggregate: mean of x and y per category — clean readable scatter
                tmp = df[[c1, c2, color_col]].dropna()
                grp = tmp.groupby(color_col)[[c1, c2]].mean().reset_index()
                scatter_pts = [
                    {
                        "x": safe_float(float(row[c1])),
                        "y": safe_float(float(row[c2])),
                        "category": str(row[color_col]),
                        "label": str(row[color_col]),
                    }
                    for _, row in grp.iterrows()
                ]
            else:
                # No category: use percentile buckets (20 points max)
                tmp = df[[c1, c2]].dropna()
                n_bins = min(20, len(tmp))
                tmp["_bin"] = pd.qcut(tmp[c1], q=n_bins, duplicates="drop", labels=False)
                grp = tmp.groupby("_bin")[[c1, c2]].mean().reset_index()
                scatter_pts = [
                    {
                        "x": safe_float(float(row[c1])),
                        "y": safe_float(float(row[c2])),
                    }
                    for _, row in grp.iterrows()
                ]

            if len(scatter_pts) < 2:
                continue

            # Business insight: quadrant analysis
            x_med = float(np.median([p["x"] for p in scatter_pts if p.get("x") is not None]))
            y_med = float(np.median([p["y"] for p in scatter_pts if p.get("y") is not None]))
            for pt in scatter_pts:
                if pt.get("x") is not None and pt.get("y") is not None:
                    hi_x = pt["x"] >= x_med
                    hi_y = pt["y"] >= y_med
                    if hi_x and hi_y:
                        pt["quadrant"] = "High-High"
                    elif hi_x and not hi_y:
                        pt["quadrant"] = "High-Low"
                    elif not hi_x and hi_y:
                        pt["quadrant"] = "Low-High"
                    else:
                        pt["quadrant"] = "Low-Low"

            strength_label = (
                "Very Strong" if abs_r >= 0.9 else
                "Strong" if abs_r >= 0.7 else
                "Moderate" if abs_r >= 0.5 else "Weak"
            )

            results.append({
                "x_column": c1,
                "y_column": c2,
                "display_x": dname(c1),
                "display_y": dname(c2),
                "correlation": round(r, 3),
                "strength": strength_label,
                "direction": "Positive" if r > 0 else "Negative",
                "data": scatter_pts,
                "color_by": color_col,
                "x_median": safe_float(x_med),
                "y_median": safe_float(y_med),
            })
        except Exception:
            continue

    return results


# ── Growth rates ──────────────────────────────────────────────────────────────


def compute_growth_rates(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    results: List[Dict] = []
    dt_cols = detect_datetime_columns(df)
    num_ordered = prioritize_columns(
        df.select_dtypes(include=["number"]).columns.tolist()
    )[:5]
    if not num_ordered:
        return results

    has_time = len(dt_cols) > 0

    if has_time:
        date_col = dt_cols[0]
        try:
            df_work = df.copy()
            df_work[date_col] = pd.to_datetime(df_work[date_col], errors="coerce")
            df_work = df_work.dropna(subset=[date_col]).sort_values(date_col)
            if len(df_work) < 3:
                has_time = False
        except Exception:
            has_time = False

    if has_time:
        span_days = (df_work[date_col].max() - df_work[date_col].min()).days
        if span_days > 365:
            freq = "QE"
        elif span_days > 90:
            freq = "ME"
        elif span_days > 14:
            freq = "W"
        else:
            freq = "D"

        for col in num_ordered:
            try:
                s = (
                    df_work.set_index(date_col)[col]
                    .resample(freq)
                    .mean()
                    .dropna()
                    .tail(40)
                )
                if len(s) < 2:
                    continue

                periods = []
                base = float(s.iloc[0])
                prev = None
                for ts, val in s.items():
                    v = float(val)
                    growth = safe_pct_change(v, prev) if prev is not None else None
                    cumulative = safe_pct_change(v, base)
                    periods.append(
                        {
                            "period": str(ts)[:10],
                            "value": safe_float(v),
                            "growth_rate_pct": growth,
                            "cumulative_growth_pct": cumulative,
                        }
                    )
                    prev = v

                results.append(
                    {
                        "column": col,
                        "display_name": dname(col),
                        "has_time_data": True,
                        "periods": periods,
                    }
                )
            except Exception:
                continue
    else:
        # Pseudo-time fallback via row index and rolling means
        idx_df = df.reset_index(drop=True).copy()
        idx_df["_t"] = idx_df.index + 1
        for col in num_ordered:
            try:
                s = clean_series(idx_df[col])
                if len(s) < 6:
                    continue
                roll = s.rolling(window=5, min_periods=3).mean().dropna().tail(40)
                if len(roll) < 2:
                    continue

                periods = []
                base = float(roll.iloc[0])
                prev = None
                for i, val in enumerate(roll.tolist(), start=1):
                    v = float(val)
                    growth = safe_pct_change(v, prev) if prev is not None else None
                    cumulative = safe_pct_change(v, base)
                    periods.append(
                        {
                            "period": f"T{i}",
                            "value": safe_float(v),
                            "growth_rate_pct": growth,
                            "cumulative_growth_pct": cumulative,
                        }
                    )
                    prev = v

                results.append(
                    {
                        "column": col,
                        "display_name": dname(col),
                        "has_time_data": False,
                        "periods": periods,
                    }
                )
            except Exception:
                continue

    return results


# ── Orchestrator ──────────────────────────────────────────────────────────────


# ── Ranking analysis ─────────────────────────────────────────────────────────


def compute_ranking(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """Rank all categories by metric, compute gap-to-top, percentile rank, and tier."""
    results: List[Dict] = []
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())[:4]
    for cat_col in cat_cols[:3]:
        u = df[cat_col].nunique()
        if u < 2 or u > 50:
            continue
        for num_col in num_ordered[:2]:
            try:
                valid = df[[cat_col, num_col]].dropna()
                if len(valid) < 4:
                    continue
                ranked = valid.groupby(cat_col)[num_col].mean().sort_values(ascending=False).reset_index()
                ranked.columns = [cat_col, "value"]
                max_val = float(ranked["value"].max())
                min_val = float(ranked["value"].min())
                spread = max_val - min_val if max_val != min_val else 1
                rows = []
                for i, row in ranked.iterrows():
                    v = float(row["value"])
                    rank_n = int(i) + 1
                    pct_rank = round((1 - (rank_n - 1) / max(len(ranked) - 1, 1)) * 100, 1)
                    tier = "Gold" if pct_rank >= 80 else "Silver" if pct_rank >= 50 else "Bronze"
                    rows.append({"rank": rank_n, "category": str(row[cat_col]),
                        "value": safe_float(v), "formatted_value": fmt_value(v, num_col),
                        "gap_to_top_pct": safe_pct_change(v, max_val),
                        "percentile_rank": pct_rank, "tier": tier,
                        "normalized": round((v - min_val) / spread, 4)})
                results.append({"dimension": cat_col, "metric": num_col,
                    "display_dimension": dname(cat_col), "display_metric": dname(num_col),
                    "data": rows, "total_categories": len(rows),
                    "winner": rows[0]["category"] if rows else None,
                    "winner_value": rows[0]["formatted_value"] if rows else None,
                    "spread_pct": round((max_val - min_val) / max(abs(max_val), 1) * 100, 1)})
            except Exception:
                continue
    return results


# ── Outlier detail ─────────────────────────────────────────────────────────────


def compute_outlier_detail(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """Identify outliers, classify severity (mild/extreme), provide by-category context."""
    results: List[Dict] = []
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())[:8]
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    for col in num_ordered:
        try:
            data = clean_series(df[col])
            if len(data) < 10:
                continue
            q1 = float(data.quantile(0.25))
            q3 = float(data.quantile(0.75))
            iqr = q3 - q1
            if iqr == 0:
                continue
            low_mild = q1 - 1.5 * iqr; high_mild = q3 + 1.5 * iqr
            low_ext  = q1 - 3.0 * iqr; high_ext  = q3 + 3.0 * iqr
            outlier_vals = data[(data < low_mild) | (data > high_mild)]
            if outlier_vals.empty:
                continue
            classified = []
            for v in outlier_vals.tolist()[:40]:
                severity  = "extreme" if v < low_ext or v > high_ext else "mild"
                direction = "high" if v > high_mild else "low"
                classified.append({"value": safe_float(v), "formatted": fmt_value(v, col),
                    "severity": severity, "direction": direction,
                    "zscore": safe_float((v - float(data.mean())) / float(data.std()))})
            by_cat: List[Dict] = []
            if cat_cols:
                for cat_val in df[cat_cols[0]].dropna().unique():
                    cd = clean_series(df[df[cat_cols[0]] == cat_val][col])
                    if len(cd) < 3: continue
                    co = cd[(cd < low_mild) | (cd > high_mild)]
                    if len(co): by_cat.append({"category": str(cat_val), "outlier_count": len(co),
                        "outlier_pct": round(len(co)/len(cd)*100, 1)})
                by_cat.sort(key=lambda x: x["outlier_count"], reverse=True)
            results.append({"column": col, "display_name": dname(col),
                "total_outliers": len(outlier_vals),
                "outlier_pct": round(len(outlier_vals)/len(data)*100, 1),
                "extreme_count": sum(1 for x in classified if x["severity"]=="extreme"),
                "mild_count": sum(1 for x in classified if x["severity"]=="mild"),
                "high_count": sum(1 for x in classified if x["direction"]=="high"),
                "low_count": sum(1 for x in classified if x["direction"]=="low"),
                "fence_low": safe_float(low_mild), "fence_high": safe_float(high_mild),
                "mean": safe_float(float(data.mean())), "median": safe_float(float(data.median())),
                "q1": safe_float(q1), "q3": safe_float(q3),
                "samples": classified[:20], "by_category": by_cat[:10],
                "severity_data": [
                    {"label": "Extreme High", "count": sum(1 for x in classified if x["severity"]=="extreme" and x["direction"]=="high"), "fill": "#FF6B6B"},
                    {"label": "Mild High",    "count": sum(1 for x in classified if x["severity"]=="mild"    and x["direction"]=="high"), "fill": "#F39C12"},
                    {"label": "Mild Low",     "count": sum(1 for x in classified if x["severity"]=="mild"    and x["direction"]=="low"),  "fill": "#3498DB"},
                    {"label": "Extreme Low",  "count": sum(1 for x in classified if x["severity"]=="extreme" and x["direction"]=="low"),  "fill": "#9B59B6"},
                ]})
        except Exception:
            continue
    return results


# ── Cohort / cross-tab ─────────────────────────────────────────────────────────


def compute_cohort(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """Cross-tabulation of two categoricals x one numeric: grouped bar / stacked bar / heatmap."""
    results: List[Dict] = []
    cat_cols = [c for c in df.select_dtypes(include=["object","category"]).columns.tolist() if 2 <= df[c].nunique() <= 12]
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())[:3]
    if len(cat_cols) < 2 or not num_ordered:
        return results
    for num_col in num_ordered[:2]:
        for i, row_col in enumerate(cat_cols[:2]):
            for col_col in cat_cols[i+1:i+3]:
                if row_col == col_col: continue
                try:
                    valid = df[[row_col, col_col, num_col]].dropna()
                    if len(valid) < 10: continue
                    pivot = valid.groupby([row_col, col_col])[num_col].mean().unstack(fill_value=0)
                    if pivot.shape[0] < 2 or pivot.shape[1] < 2: continue
                    col_labels = [str(c) for c in pivot.columns]
                    rows_data = []
                    for row_val, row_data in pivot.iterrows():
                        entry: Dict = {"category": str(row_val)}
                        for cl, val in zip(col_labels, row_data.values):
                            entry[cl] = safe_float(float(val))
                        rows_data.append(entry)
                    results.append({"row_dim": row_col, "col_dim": col_col, "metric": num_col,
                        "display_row": dname(row_col), "display_col": dname(col_col),
                        "display_metric": dname(num_col),
                        "col_labels": col_labels, "data": rows_data,
                        "total_cells": len(rows_data) * len(col_labels)})
                except Exception:
                    continue
    return results


# ── Multi-metric comparison ────────────────────────────────────────────────────


def compute_multi_metric(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """Compare multiple numeric metrics per category, normalized 0-1 for radar."""
    results: List[Dict] = []
    cat_cols = [c for c in df.select_dtypes(include=["object","category"]).columns.tolist() if 2 <= df[c].nunique() <= 10]
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())
    if len(num_ordered) < 3:
        return results
    metrics = num_ordered[:6]
    for cat_col in cat_cols[:2]:
        try:
            valid = df[[cat_col] + metrics].dropna()
            if len(valid) < 5: continue
            grouped = valid.groupby(cat_col)[metrics].mean()
            mins = grouped.min(); maxs = grouped.max()
            norms = (grouped - mins) / (maxs - mins + 1e-9)
            radar_rows = []
            for cat_val, row in grouped.iterrows():
                entry: Dict = {"category": str(cat_val)}
                for m in metrics:
                    entry[m] = safe_float(float(row[m]))
                    entry[f"{m}_norm"] = safe_float(float(norms.loc[cat_val, m]))
                radar_rows.append(entry)
            metric_rows = []
            for m in metrics:
                entry = {"metric": dname(m), "raw_key": m}
                for cat_val in grouped.index:
                    entry[str(cat_val)] = safe_float(float(grouped.loc[cat_val, m]))
                    entry[f"{str(cat_val)}_norm"] = safe_float(float(norms.loc[cat_val, m]))
                metric_rows.append(entry)
            results.append({"dimension": cat_col, "display_dimension": dname(cat_col),
                "metrics": metrics, "display_metrics": [dname(m) for m in metrics],
                "categories": [str(x) for x in grouped.index.tolist()],
                "radar_data": radar_rows, "grouped_data": metric_rows})
        except Exception:
            continue
    return results


# ── Percentile bands ────────────────────────────────────────────────────────────


def compute_percentile_bands(df: pd.DataFrame) -> List[Dict]:
    """P10/P25/P50/P75/P90 per column as stacked band data for area-range charts."""
    results: List[Dict] = []
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())[:8]
    for col in num_ordered:
        try:
            data = clean_series(df[col])
            if len(data) < 10: continue
            p10  = safe_float(float(data.quantile(0.10)))
            p25  = safe_float(float(data.quantile(0.25)))
            p50  = safe_float(float(data.quantile(0.50)))
            p75  = safe_float(float(data.quantile(0.75)))
            p90  = safe_float(float(data.quantile(0.90)))
            mean = safe_float(float(data.mean()))
            std  = safe_float(float(data.std()))
            results.append({"column": col, "display_name": dname(col),
                "p10": p10, "p25": p25, "p50": p50, "p75": p75, "p90": p90,
                "mean": mean, "std": std,
                "formatted_median": fmt_value(float(p50 or 0), col),
                "formatted_mean":   fmt_value(float(mean or 0), col),
                "bands": [
                    {"label": "P10",    "value": p10,  "pct": 10,  "fill": "#5C6BC0"},
                    {"label": "P25",    "value": p25,  "pct": 25,  "fill": "#3498DB"},
                    {"label": "Median", "value": p50,  "pct": 50,  "fill": "#2ECC71"},
                    {"label": "P75",    "value": p75,  "pct": 75,  "fill": "#F39C12"},
                    {"label": "P90",    "value": p90,  "pct": 90,  "fill": "#FF6B6B"},
                    {"label": "Mean",   "value": mean, "pct": None,"fill": "#D4AF37"},
                ],
                "steps": [
                    {"label": "P10",  "value": p10,  "band_low": p10, "band_high": p25},
                    {"label": "P25",  "value": p25,  "band_low": p25, "band_high": p50},
                    {"label": "P50",  "value": p50,  "band_low": p50, "band_high": p75},
                    {"label": "P75",  "value": p75,  "band_low": p75, "band_high": p90},
                    {"label": "P90",  "value": p90,  "band_low": p90, "band_high": p90},
                ],
            })
        except Exception:
            continue
    return results


# ── Running total / Pareto ─────────────────────────────────────────────────────


def compute_running_total(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """Pareto: sort categories by value desc, compute running total + cumulative %."""
    results: List[Dict] = []
    cat_cols = [c for c in df.select_dtypes(include=["object","category"]).columns.tolist() if 2 <= df[c].nunique() <= 40]
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())[:3]
    for cat_col in cat_cols[:3]:
        for num_col in num_ordered[:2]:
            try:
                valid = df[[cat_col, num_col]].dropna()
                if len(valid) < 4: continue
                ranked = valid.groupby(cat_col)[num_col].sum().sort_values(ascending=False).reset_index()
                ranked.columns = [cat_col, "value"]
                total = float(ranked["value"].sum())
                if total == 0: continue
                running = 0.0
                rows = []
                for _, row in ranked.head(20).iterrows():
                    v = float(row["value"])
                    running += v
                    cum_pct = round(running / total * 100, 1)
                    rows.append({"category": str(row[cat_col]), "value": safe_float(v),
                        "running_total": safe_float(running), "cumulative_pct": cum_pct,
                        "formatted_value": fmt_value(v, num_col), "is_vital_few": cum_pct <= 80})
                vital_few = [r for r in rows if r["is_vital_few"]]
                results.append({"dimension": cat_col, "metric": num_col,
                    "display_dimension": dname(cat_col), "display_metric": dname(num_col),
                    "data": rows, "total": safe_float(total),
                    "formatted_total": fmt_value(total, num_col),
                    "vital_few_count": len(vital_few),
                    "vital_few_pct": round(len(vital_few)/max(len(rows),1)*100, 0)})
            except Exception:
                continue
    return results


# ── Value at Risk / Statistical Risk ─────────────────────────────────────────


def compute_value_at_risk(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """Per numeric column: VaR(95%), CVaR, best/worst case, risk tier."""
    results: List[Dict] = []
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())[:8]
    for col in num_ordered:
        try:
            data = clean_series(df[col])
            if len(data) < 10: continue
            sorted_d = data.sort_values()
            n = len(sorted_d)
            var_95  = safe_float(float(sorted_d.quantile(0.05)))
            var_99  = safe_float(float(sorted_d.quantile(0.01)))
            cvar_95 = safe_float(float(sorted_d[sorted_d <= (sorted_d.quantile(0.05))].mean()))
            best    = safe_float(float(sorted_d.quantile(0.95)))
            worst   = safe_float(float(sorted_d.quantile(0.05)))
            mean    = safe_float(float(data.mean()))
            std     = safe_float(float(data.std()))
            cv      = abs(std / mean * 100) if mean and mean != 0 else 0
            risk_tier = "High" if cv > 50 else "Medium" if cv > 20 else "Low"

            # Histogram for loss distribution
            counts, edges = np.histogram(data, bins=20, range=(float(data.min()), float(data.max())))
            hist_data = [{"bin": round((edges[i]+edges[i+1])/2,2), "count": int(counts[i]),
                          "is_risk": (edges[i]+edges[i+1])/2 < float(sorted_d.quantile(0.05))}
                         for i in range(len(counts))]

            results.append({
                "column": col, "display_name": dname(col),
                "var_95": var_95, "var_99": var_99, "cvar_95": cvar_95,
                "best_case": best, "worst_case": worst,
                "mean": mean, "std": std, "cv_pct": safe_float(cv),
                "risk_tier": risk_tier,
                "formatted_var95": fmt_value(float(var_95 or 0), col),
                "formatted_mean": fmt_value(float(mean or 0), col),
                "histogram": hist_data,
                "risk_bars": [
                    {"label": "Worst 1%",    "value": var_99,  "fill": "#FF6B6B"},
                    {"label": "Worst 5%",    "value": var_95,  "fill": "#F39C12"},
                    {"label": "Mean",         "value": mean,    "fill": "#D4AF37"},
                    {"label": "Best 5%",     "value": best,    "fill": "#2ECC71"},
                ],
            })
        except Exception:
            continue
    return results


# ── Moving statistics ─────────────────────────────────────────────────────────


def compute_moving_statistics(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """Rolling mean/std/min/max with multiple window sizes for up to 4 numeric cols."""
    results: List[Dict] = []
    dt_cols = detect_datetime_columns(df)
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())[:4]

    for col in num_ordered:
        try:
            data = clean_series(df[col])
            if len(data) < 15: continue

            # Use date index if available, else row index
            if dt_cols:
                df_w = df.copy(); df_w[dt_cols[0]] = pd.to_datetime(df_w[dt_cols[0]], errors="coerce")
                series = df_w.sort_values(dt_cols[0])[col].reset_index(drop=True)
                series = pd.to_numeric(series, errors="coerce").dropna()
            else:
                series = data.reset_index(drop=True)

            windows = [3, 7] if len(series) >= 14 else [3]
            rows = []
            for i in range(len(series)):
                point: Dict = {"index": i, "value": safe_float(float(series.iloc[i]))}
                for w in windows:
                    if i >= w-1:
                        window_data = series.iloc[i-w+1:i+1]
                        point[f"ma{w}"]     = safe_float(float(window_data.mean()))
                        point[f"std{w}"]    = safe_float(float(window_data.std()) if len(window_data) > 1 else 0)
                        point[f"upper{w}"]  = safe_float(float(window_data.mean()) + float(window_data.std() if len(window_data) > 1 else 0))
                        point[f"lower{w}"]  = safe_float(float(window_data.mean()) - float(window_data.std() if len(window_data) > 1 else 0))
                rows.append(point)

            results.append({
                "column": col, "display_name": dname(col),
                "windows": windows,
                "data": rows[:80],  # cap at 80 points for performance
                "overall_mean": safe_float(float(series.mean())),
                "overall_std": safe_float(float(series.std())),
            })
        except Exception:
            continue
    return results


# ── Concentration / Gini / HHI ───────────────────────────────────────────────────


def compute_concentration(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """Gini coefficient, HHI, and Lorenz curve data per categorical × numeric."""
    results: List[Dict] = []
    cat_cols = [c for c in df.select_dtypes(include=["object","category"]).columns.tolist() if 2 <= df[c].nunique() <= 50]
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())[:3]

    for cat_col in cat_cols[:3]:
        for num_col in num_ordered[:2]:
            try:
                valid = df[[cat_col, num_col]].dropna()
                if len(valid) < 4: continue
                group_sums = valid.groupby(cat_col)[num_col].sum().sort_values()
                vals = group_sums.values.astype(float)
                n = len(vals)
                if n < 2: continue
                total = vals.sum()
                if total <= 0: continue

                # Gini coefficient
                vals_sorted = np.sort(vals)
                cumvals = np.cumsum(vals_sorted)
                gini = float((n + 1 - 2 * np.sum(cumvals) / cumvals[-1]) / n)

                # HHI (Herfindahl-Hirschman Index)
                shares = vals / total
                hhi = float(np.sum(shares ** 2))

                # Lorenz curve
                lorenz_x = np.linspace(0, 1, n+1)
                lorenz_y = np.concatenate([[0], cumvals / cumvals[-1]])
                lorenz_data = [{"x": round(float(lorenz_x[i]),3), "y": round(float(lorenz_y[i]),3),
                                "equality": round(float(lorenz_x[i]),3)} for i in range(n+1)]

                # Category shares
                share_data = [{"category": str(k), "share_pct": round(float(v/total*100),1),
                               "value": safe_float(float(v)), "formatted": fmt_value(float(v), num_col)}
                              for k,v in group_sums.items()]
                share_data = sorted(share_data, key=lambda x: x["share_pct"], reverse=True)

                concentration_level = "Highly Concentrated" if hhi > 0.25 else "Moderately Concentrated" if hhi > 0.10 else "Competitive"

                results.append({
                    "dimension": cat_col, "metric": num_col,
                    "display_dimension": dname(cat_col), "display_metric": dname(num_col),
                    "gini": round(gini, 4),
                    "hhi": round(hhi, 4),
                    "gini_pct": round(gini * 100, 1),
                    "hhi_pct": round(hhi * 100, 1),
                    "concentration_level": concentration_level,
                    "top1_share": share_data[0]["share_pct"] if share_data else 0,
                    "top3_share": sum(d["share_pct"] for d in share_data[:3]),
                    "lorenz_data": lorenz_data,
                    "share_data": share_data[:15],
                    "total": safe_float(total),
                    "formatted_total": fmt_value(total, num_col),
                })
            except Exception:
                continue
    return results


# ── Benchmark comparison ─────────────────────────────────────────────────────────


def compute_benchmark_comparison(df: pd.DataFrame, data_context: Dict, stats: Dict) -> List[Dict]:
    """Compare actual metric values against industry benchmarks."""
    results: List[Dict] = []
    benchmarks = data_context.get("industry_benchmarks", {})
    if not benchmarks: return results

    numeric_stats = stats.get("numeric", {})
    for bench_col, bench_val in benchmarks.items():
        # Try to match benchmark key to a column
        matched_col = None
        for col in df.columns:
            if bench_col.lower().replace("_"," ") in col.lower().replace("_"," ") or \
               col.lower().replace("_"," ") in bench_col.lower().replace("_"," "):
                matched_col = col
                break

        if not matched_col or matched_col not in numeric_stats: continue
        try:
            col_stats = numeric_stats[matched_col]
            actual = float(col_stats.get("mean", 0))
            diff   = actual - float(bench_val)
            diff_pct = diff / float(bench_val) * 100 if bench_val != 0 else 0
            status = "above" if diff > 0 else "below"

            results.append({
                "metric": matched_col, "display_name": dname(matched_col),
                "actual": safe_float(actual), "benchmark": safe_float(float(bench_val)),
                "diff": safe_float(diff), "diff_pct": safe_float(diff_pct),
                "status": status,
                "formatted_actual": fmt_value(actual, matched_col),
                "formatted_benchmark": fmt_value(float(bench_val), matched_col),
                "rating": "excellent" if diff_pct > 20 else "good" if diff_pct > 0 else "needs_improvement" if diff_pct > -20 else "critical",
                "gauge_data": [
                    {"label": "Benchmark", "value": safe_float(float(bench_val)), "fill": "#5C6BC0"},
                    {"label": "Actual",    "value": safe_float(actual),            "fill": "#2ECC71" if status == "above" else "#FF6B6B"},
                ],
            })
        except Exception:
            continue
    return results


# ── Data quality detail ───────────────────────────────────────────────────────────


def compute_data_quality_detail(df: pd.DataFrame, profile: Dict) -> List[Dict]:
    """Per-column quality breakdown: null%, unique%, type, anomaly flags."""
    results: List[Dict] = []
    total_rows = len(df)
    if total_rows == 0: return results

    for col in df.columns:
        try:
            null_count = int(df[col].isnull().sum())
            null_pct   = round(null_count / total_rows * 100, 1)
            unique_count = int(df[col].nunique())
            unique_pct   = round(unique_count / total_rows * 100, 1)

            dtype_str = str(df[col].dtype)
            if pd.api.types.is_numeric_dtype(df[col]): col_type = "numeric"
            elif pd.api.types.is_datetime64_any_dtype(df[col]): col_type = "datetime"
            elif unique_count <= 15: col_type = "categorical"
            else: col_type = "string"

            # Quality score for this column
            score = 100.0
            issues = []
            if null_pct > 30:  score -= 30; issues.append(f"{null_pct}% missing")
            elif null_pct > 10: score -= 15; issues.append(f"{null_pct}% missing")
            elif null_pct > 0:  score -= 5;  issues.append(f"{null_pct}% missing")

            if col_type == "string" and unique_pct == 100: issues.append("All unique (likely ID)")
            if col_type == "categorical" and unique_count == 1: score -= 20; issues.append("No variation")

            if pd.api.types.is_numeric_dtype(df[col]):
                data = clean_series(df[col])
                if len(data) > 0:
                    q1,q3 = data.quantile(0.25), data.quantile(0.75)
                    iqr = q3 - q1
                    outlier_pct = float(((data < q1-1.5*iqr)|(data > q3+1.5*iqr)).sum()) / len(data) * 100
                    if outlier_pct > 10: score -= 10; issues.append(f"{outlier_pct:.1f}% outliers")

            results.append({
                "column": col, "display_name": dname(col),
                "dtype": dtype_str, "col_type": col_type,
                "null_count": null_count, "null_pct": null_pct,
                "unique_count": unique_count, "unique_pct": unique_pct,
                "quality_score": round(max(0, score), 1),
                "issues": issues,
                "status": "good" if score >= 80 else "warning" if score >= 50 else "critical",
                "fill": "#2ECC71" if score >= 80 else "#F39C12" if score >= 50 else "#FF6B6B",
            })
        except Exception:
            continue
    return results


# ── Summary statistics table ───────────────────────────────────────────────────────


def compute_summary_stats(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """Full descriptive stats table for all numeric columns."""
    results: List[Dict] = []
    num_cols = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())
    for col in num_cols:
        try:
            data = clean_series(df[col])
            if len(data) < 2: continue
            q1,med,q3 = float(data.quantile(.25)), float(data.median()), float(data.quantile(.75))
            mean_v = float(data.mean())
            std_v  = float(data.std())
            results.append({
                "column": col, "display_name": dname(col),
                "count": int(len(data)),
                "mean": safe_float(mean_v),
                "median": safe_float(med),
                "std": safe_float(std_v),
                "min": safe_float(float(data.min())),
                "max": safe_float(float(data.max())),
                "q1": safe_float(q1), "q3": safe_float(q3),
                "iqr": safe_float(q3 - q1),
                "skewness": safe_float(float(data.skew())),
                "kurtosis": safe_float(float(data.kurtosis())),
                "cv_pct": safe_float(abs(std_v/mean_v*100) if mean_v != 0 else 0),
                "total": safe_float(float(data.sum())),
                "null_count": int(df[col].isnull().sum()),
                "formatted_mean": fmt_value(mean_v, col),
                "formatted_total": fmt_value(float(data.sum()), col),
            })
        except Exception:
            continue
    return results


# ── Category frequency / string patterns ─────────────────────────────────────────


def compute_frequency_analysis(df: pd.DataFrame) -> List[Dict]:
    """Detailed frequency table for categorical columns: count, pct, cumulative."""
    results: List[Dict] = []
    cat_cols = [c for c in df.select_dtypes(include=["object","category"]).columns.tolist() if 2 <= df[c].nunique() <= 100]
    for col in cat_cols[:6]:
        try:
            vc = df[col].value_counts(dropna=True)
            total = int(vc.sum())
            cum = 0
            rows = []
            for val, cnt in vc.items():
                pct = round(float(cnt)/total*100, 2)
                cum += pct
                rows.append({
                    "category": str(val),
                    "count": int(cnt),
                    "pct": pct,
                    "cumulative_pct": round(cum, 1),
                    "is_majority": pct >= 50,
                    "fill": "#D4AF37" if pct >= 20 else "#3498DB" if pct >= 10 else "#607D8B",
                })
            results.append({
                "column": col, "display_name": dname(col),
                "total": total,
                "unique": int(df[col].nunique()),
                "data": rows[:30],
                "top_category": rows[0]["category"] if rows else None,
                "top_pct": rows[0]["pct"] if rows else 0,
                "entropy": round(float(-sum((c/total) * np.log2(c/total) for c in vc.values if c > 0)), 3),
            })
        except Exception:
            continue
    return results


# ── Time decomposition (trend + seasonal) ────────────────────────────────────────


def compute_time_decomposition(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """For time series: linear trend + centered moving average + residual."""
    results: List[Dict] = []
    dt_cols = detect_datetime_columns(df)
    if not dt_cols: return results

    date_col = dt_cols[0]
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())[:3]

    try:
        df_ts = df.copy()
        df_ts[date_col] = pd.to_datetime(df_ts[date_col], errors="coerce")
        df_ts = df_ts.dropna(subset=[date_col]).sort_values(date_col)

        span = (df_ts[date_col].max() - df_ts[date_col].min()).days
        if span > 365: freq = "ME"
        elif span > 30: freq = "W"
        else: freq = "D"

        for col in num_ordered:
            try:
                s = df_ts.set_index(date_col)[col].resample(freq).mean().dropna().tail(60)
                if len(s) < 8: continue
                vals = s.values.astype(float)
                n = len(vals)

                # Linear trend
                x = np.arange(n)
                slope, intercept = np.polyfit(x, vals, 1)
                trend = slope * x + intercept

                # Centered moving average (window=3)
                window = min(5, n//4)
                if window < 2: window = 2
                cma = pd.Series(vals).rolling(window=window, center=True).mean().values

                # Residual = actual - trend
                residual = vals - trend

                data_points = []
                for i in range(n):
                    data_points.append({
                        "period": str(s.index[i])[:10],
                        "actual": safe_float(vals[i]),
                        "trend": safe_float(trend[i]),
                        "moving_avg": safe_float(float(cma[i])) if not np.isnan(cma[i]) else None,
                        "residual": safe_float(residual[i]),
                    })

                results.append({
                    "column": col, "display_name": dname(col),
                    "slope": round(float(slope), 4),
                    "trend_direction": "upward" if slope > 0 else "downward",
                    "trend_strength": "strong" if abs(slope) > float(np.std(vals))*0.1 else "weak",
                    "data": data_points,
                })
            except Exception:
                continue
    except Exception:
        pass
    return results


# ── Gauge / KPI vs Target ─────────────────────────────────────────────────────


def compute_gauge_data(df: pd.DataFrame, data_context: Dict, stats: Dict) -> List[Dict]:
    """Gauge/speedometer data: actual vs target (P75 as target) per key metric."""
    results: List[Dict] = []
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())[:6]
    numeric_stats = stats.get("numeric", {})
    benchmarks = data_context.get("industry_benchmarks", {})

    for col in num_ordered:
        try:
            data = clean_series(df[col])
            if len(data) < 5: continue
            actual = float(data.mean())
            p75    = float(data.quantile(0.75))
            p90    = float(data.quantile(0.90))
            min_v  = float(data.min())
            max_v  = float(data.max())

            # Use industry benchmark if available, else p75
            target = None
            for bk, bv in benchmarks.items():
                if bk.lower().replace("_"," ") in col.lower().replace("_"," "):
                    target = float(bv); break
            if target is None: target = p75

            pct_of_target = round(actual / target * 100, 1) if target != 0 else 0
            status = "excellent" if pct_of_target >= 110 else "good" if pct_of_target >= 90 else "warning" if pct_of_target >= 70 else "critical"
            # Gauge arc: 0-180 degrees mapped to min-max
            gauge_pct = round(min(max((actual - min_v) / max((max_v - min_v), 1) * 100, 0), 100), 1)

            results.append({
                "column": col, "display_name": dname(col),
                "actual": safe_float(actual), "target": safe_float(target),
                "min": safe_float(min_v), "max": safe_float(max_v),
                "p75": safe_float(p75), "p90": safe_float(p90),
                "pct_of_target": pct_of_target,
                "gauge_pct": gauge_pct,
                "status": status,
                "formatted_actual": fmt_value(actual, col),
                "formatted_target": fmt_value(target, col),
                # Zones for gauge coloring
                "zones": [
                    {"from": 0,  "to": 33,  "color": "#FF6B6B", "label": "Critical"},
                    {"from": 33, "to": 66,  "color": "#F39C12", "label": "Warning"},
                    {"from": 66, "to": 100, "color": "#2ECC71", "label": "Good"},
                ],
                # Bullet chart bands
                "bullet_bands": [
                    {"label": "Poor",   "value": safe_float(float(data.quantile(0.25))), "fill": "rgba(255,107,107,0.2)"},
                    {"label": "Average","value": safe_float(p75),  "fill": "rgba(243,156,18,0.2)"},
                    {"label": "Good",   "value": safe_float(max_v), "fill": "rgba(46,204,113,0.2)"},
                ],
            })
        except Exception:
            continue
    return results


# ── Slope chart (period comparison) ───────────────────────────────────────────────


def compute_slope_chart(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """Dumbbell/slope: compare first-half vs second-half for each category."""
    results: List[Dict] = []
    cat_cols = [c for c in df.select_dtypes(include=["object","category"]).columns.tolist() if 2 <= df[c].nunique() <= 15]
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())[:3]
    dt_cols = detect_datetime_columns(df)

    for cat_col in cat_cols[:2]:
        for num_col in num_ordered[:2]:
            try:
                valid = df[[cat_col, num_col]].dropna().reset_index(drop=True)
                if len(valid) < 10: continue

                # Split into two halves (time-aware if possible)
                if dt_cols:
                    df_t = df.copy(); df_t[dt_cols[0]] = pd.to_datetime(df_t[dt_cols[0]], errors="coerce")
                    df_t = df_t.sort_values(dt_cols[0]).dropna(subset=[dt_cols[0]])
                    mid = len(df_t) // 2
                    first_half  = df_t.iloc[:mid]
                    second_half = df_t.iloc[mid:]
                    period_a = "First Half"; period_b = "Second Half"
                else:
                    mid = len(valid) // 2
                    first_half  = valid.iloc[:mid]
                    second_half = valid.iloc[mid:]
                    period_a = "Period A"; period_b = "Period B"

                g1 = first_half.groupby(cat_col)[num_col].mean()
                g2 = second_half.groupby(cat_col)[num_col].mean()
                common = list(set(g1.index) & set(g2.index))
                if len(common) < 2: continue

                rows = []
                for cat in common:
                    v1, v2 = float(g1[cat]), float(g2[cat])
                    change = safe_pct_change(v2, v1)
                    rows.append({
                        "category": str(cat),
                        "period_a": safe_float(v1), "period_b": safe_float(v2),
                        "change_pct": change,
                        "direction": "up" if (v2 or 0) > (v1 or 0) else "down",
                        "formatted_a": fmt_value(v1, num_col),
                        "formatted_b": fmt_value(v2, num_col),
                    })
                rows.sort(key=lambda x: x["period_b"] or 0, reverse=True)

                results.append({
                    "dimension": cat_col, "metric": num_col,
                    "display_dimension": dname(cat_col), "display_metric": dname(num_col),
                    "period_a": period_a, "period_b": period_b,
                    "data": rows,
                    "improvers": len([r for r in rows if r["direction"]=="up"]),
                    "decliners": len([r for r in rows if r["direction"]=="down"]),
                })
            except Exception:
                continue
    return results


# ── Error bars / Confidence Intervals ─────────────────────────────────────────


def compute_error_bars(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """Mean ± 1.96*SEM (95% CI) and ± 1 std dev per category."""
    results: List[Dict] = []
    cat_cols = [c for c in df.select_dtypes(include=["object","category"]).columns.tolist() if 2 <= df[c].nunique() <= 20]
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())[:4]

    for cat_col in cat_cols[:3]:
        for num_col in num_ordered[:2]:
            try:
                valid = df[[cat_col, num_col]].dropna()
                if len(valid) < 10: continue

                grp = valid.groupby(cat_col)[num_col]
                stats_df = grp.agg(["mean","std","count"]).reset_index()
                stats_df.columns = [cat_col,"mean","std","count"]
                stats_df = stats_df[stats_df["count"] >= 3].sort_values("mean", ascending=False)

                rows = []
                for _, row in stats_df.iterrows():
                    m, s, n_s = float(row["mean"]), float(row["std"]) if not np.isnan(row["std"]) else 0, int(row["count"])
                    sem = s / np.sqrt(n_s) if n_s > 0 else 0
                    ci95 = 1.96 * sem
                    rows.append({
                        "category": str(row[cat_col]),
                        "mean": safe_float(m),
                        "std": safe_float(s),
                        "sem": safe_float(sem),
                        "ci_lower": safe_float(m - ci95),
                        "ci_upper": safe_float(m + ci95),
                        "std_lower": safe_float(m - s),
                        "std_upper": safe_float(m + s),
                        "count": n_s,
                        "formatted_mean": fmt_value(m, num_col),
                        "error_low": safe_float(ci95),
                        "error_high": safe_float(ci95),
                    })

                results.append({
                    "dimension": cat_col, "metric": num_col,
                    "display_dimension": dname(cat_col), "display_metric": dname(num_col),
                    "data": rows,
                    "overall_mean": safe_float(float(valid[num_col].mean())),
                })
            except Exception:
                continue
    return results


# ── Marimekko / Mosaic chart ─────────────────────────────────────────────────────


def compute_marimekko(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """Two categorical dimensions: x-width = col1 share, y-height = col2 composition."""
    results: List[Dict] = []
    cat_cols = [c for c in df.select_dtypes(include=["object","category"]).columns.tolist() if 2 <= df[c].nunique() <= 10]
    if len(cat_cols) < 2: return results
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())[:2]

    for i, dim1 in enumerate(cat_cols[:2]):
        for dim2 in cat_cols[i+1:i+3]:
            if dim1 == dim2: continue
            try:
                cols_needed = [dim1, dim2] + (num_ordered[:1] if num_ordered else [])
                valid = df[cols_needed].dropna()
                if len(valid) < 10: continue

                num_col = num_ordered[0] if num_ordered else None

                if num_col:
                    pivot = valid.groupby([dim1, dim2])[num_col].sum().unstack(fill_value=0)
                else:
                    pivot = valid.groupby([dim1, dim2]).size().unstack(fill_value=0)

                row_totals = pivot.sum(axis=1)
                grand_total = float(row_totals.sum())
                if grand_total == 0: continue

                blocks = []
                x_offset = 0.0
                for row_cat, row_data in pivot.iterrows():
                    row_total = float(row_totals[row_cat])
                    width_pct = round(row_total / grand_total * 100, 2)
                    col_total = float(row_data.sum())
                    y_offset = 0.0
                    for col_cat, val in row_data.items():
                        v = float(val)
                        height_pct = round(v / col_total * 100, 2) if col_total > 0 else 0
                        blocks.append({
                            "dim1": str(row_cat), "dim2": str(col_cat),
                            "value": safe_float(v),
                            "x": round(x_offset, 2), "width": width_pct,
                            "y": round(y_offset, 2), "height": height_pct,
                            "share_of_row": height_pct,
                            "share_of_total": round(v / grand_total * 100, 2),
                        })
                        y_offset += height_pct
                    x_offset += width_pct

                results.append({
                    "dim1": dim1, "dim2": dim2,
                    "display_dim1": dname(dim1), "display_dim2": dname(dim2),
                    "metric": num_col, "display_metric": dname(num_col) if num_col else "Count",
                    "blocks": blocks,
                    "dim1_categories": [str(x) for x in pivot.index.tolist()],
                    "dim2_categories": [str(x) for x in pivot.columns.tolist()],
                    "total": safe_float(grand_total),
                })
            except Exception:
                continue
    return results


# ── Gantt / Timeline chart ──────────────────────────────────────────────────────


def compute_gantt(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """
    Detect start/end date column pairs and optional category/status columns.
    Returns Gantt bar data suitable for horizontal bar chart rendering.
    """
    results: List[Dict] = []
    dt_cols = detect_datetime_columns(df)
    if len(dt_cols) < 2:
        return results

    # Try to find start/end pairs by keyword matching
    start_kw = {"start", "begin", "from", "open", "created", "launch", "arrival"}
    end_kw   = {"end", "finish", "complete", "close", "due", "deadline", "departure", "closed"}

    start_cols = [c for c in dt_cols if any(k in c.lower() for k in start_kw)]
    end_cols   = [c for c in dt_cols if any(k in c.lower() for k in end_kw)]

    # If no explicit start/end, fall back to first two datetime cols
    if not start_cols or not end_cols:
        start_cols = [dt_cols[0]]
        end_cols   = [dt_cols[1]] if len(dt_cols) > 1 else []

    if not start_cols or not end_cols:
        return results

    cat_cols = [c for c in df.select_dtypes(include=["object","category"]).columns
                if 2 <= df[c].nunique() <= 40]
    status_kw = {"status", "stage", "phase", "state", "type", "priority", "category"}
    status_cols = [c for c in cat_cols if any(k in c.lower() for k in status_kw)]
    label_cols  = [c for c in cat_cols if c not in status_cols]

    for start_col in start_cols[:2]:
        for end_col in end_cols[:2]:
            if start_col == end_col:
                continue
            try:
                work = df.copy()
                work["_start"] = pd.to_datetime(work[start_col], errors="coerce")
                work["_end"]   = pd.to_datetime(work[end_col],   errors="coerce")
                valid = work.dropna(subset=["_start", "_end"])
                valid = valid[valid["_end"] >= valid["_start"]]
                if len(valid) < 3:
                    continue

                global_start = valid["_start"].min()

                # Label column: use first available non-status cat col or index
                lbl_col = label_cols[0] if label_cols else None
                stat_col = status_cols[0] if status_cols else None

                # Limit to 30 rows, sorted by start date
                sample = valid.sort_values("_start").head(30)

                # Compute unique status values for color mapping
                statuses: List[str] = []
                if stat_col:
                    statuses = sorted(sample[stat_col].dropna().unique().tolist())

                rows = []
                for row_n, (idx, row) in enumerate(sample.iterrows()):
                    s = row["_start"]
                    e = row["_end"]
                    dur_days  = max(1, int((e - s).total_seconds() / 86400))
                    start_day = max(0, int((s - global_start).total_seconds() / 86400))
                    label = str(row[lbl_col])[:30] if lbl_col and pd.notna(row.get(lbl_col)) else f"Task {row_n+1}"
                    status = str(row[stat_col]) if stat_col and pd.notna(row.get(stat_col)) else "default"
                    rows.append({
                        "task":       label,
                        "start":      s.strftime("%Y-%m-%d"),
                        "end":        e.strftime("%Y-%m-%d"),
                        "start_day":  start_day,
                        "duration":   dur_days,
                        "status":     status,
                        "display_start": s.strftime("%b %d, %Y"),
                        "display_end":   e.strftime("%b %d, %Y"),
                    })

                # Stats
                durations = [(r["duration"]) for r in rows]
                avg_dur   = round(float(np.mean(durations)), 1) if durations else 0

                results.append({
                    "start_col":      start_col,
                    "end_col":        end_col,
                    "display_start":  dname(start_col),
                    "display_end":    dname(end_col),
                    "label_col":      lbl_col,
                    "status_col":     stat_col,
                    "statuses":       statuses,
                    "global_start":   global_start.strftime("%Y-%m-%d"),
                    "data":           rows,
                    "avg_duration_days": avg_dur,
                    "total_tasks":    len(rows),
                    "date_span_days": int((valid["_end"].max() - global_start).total_seconds() / 86400),
                })
            except Exception:
                continue
    return results


# ── Sankey / Flow diagram ─────────────────────────────────────────────────────


def compute_sankey(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """
    Build Sankey flow data from pairs of categorical columns.
    Each pair forms source → target links weighted by count or numeric sum.
    """
    results: List[Dict] = []
    cat_cols = [c for c in df.select_dtypes(include=["object","category"]).columns
                if 2 <= df[c].nunique() <= 12]
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())[:2]

    # Look for natural flow column pairs (funnel / pipeline / stage progression)
    flow_kw = {"stage", "step", "phase", "status", "channel", "source", "medium",
               "region", "country", "category", "segment", "group", "type"}

    flow_cols = [c for c in cat_cols if any(k in c.lower() for k in flow_kw)]
    if len(flow_cols) < 2:
        flow_cols = cat_cols  # fallback to all cat cols

    for i in range(min(len(flow_cols)-1, 3)):
        src_col = flow_cols[i]
        tgt_col = flow_cols[i+1]
        if src_col == tgt_col:
            continue
        try:
            num_col = num_ordered[0] if num_ordered else None
            cols = [src_col, tgt_col] + ([num_col] if num_col else [])
            valid = df[cols].dropna()
            if len(valid) < 5:
                continue

            if num_col:
                grouped = valid.groupby([src_col, tgt_col])[num_col].sum().reset_index()
                grouped = grouped.rename(columns={src_col:"source", tgt_col:"target", num_col:"value"})
            else:
                grouped = valid.groupby([src_col, tgt_col]).size().reset_index(name="value")
                grouped = grouped.rename(columns={src_col:"source", tgt_col:"target"})

            grouped = grouped[grouped["value"] > 0]
            if len(grouped) < 2:
                continue

            # Build nodes list (deduplicated)
            sources = grouped["source"].astype(str).tolist()
            targets = grouped["target"].astype(str).tolist()
            all_nodes_ordered = list(dict.fromkeys(sources + targets))  # preserve order, dedup
            node_idx = {n: i for i, n in enumerate(all_nodes_ordered)}

            links = []
            for _, row in grouped.iterrows():
                s = str(row["source"])
                t = str(row["target"])
                v = float(row["value"])
                links.append({
                    "source": node_idx[s],
                    "target": node_idx[t],
                    "value":  safe_float(v),
                    "source_name": s,
                    "target_name": t,
                    "display_value": fmt_value(v, num_col or ""),
                })

            # Sort links by value desc, cap at 20
            links = sorted(links, key=lambda x: x["value"] or 0, reverse=True)[:20]

            # Node totals
            out_flow: dict = defaultdict(float)
            in_flow:  dict = defaultdict(float)
            for lnk in links:
                out_flow[lnk["source"]] += lnk["value"] or 0
                in_flow[lnk["target"]]  += lnk["value"] or 0

            nodes = [
                {
                    "id":    i,
                    "name":  n,
                    "total": safe_float(max(out_flow.get(i, 0), in_flow.get(i, 0))),
                }
                for i, n in enumerate(all_nodes_ordered)
            ]

            total_flow = safe_float(grouped["value"].sum())

            results.append({
                "source_col":     src_col,
                "target_col":     tgt_col,
                "display_source": dname(src_col),
                "display_target": dname(tgt_col),
                "metric":         num_col,
                "display_metric": dname(num_col) if num_col else "Count",
                "nodes":          nodes,
                "links":          links,
                "total_flow":     total_flow,
                "n_sources":      len(set(sources)),
                "n_targets":      len(set(targets)),
            })
        except Exception:
            continue
    return results[:3]


# ── Drill-through data ────────────────────────────────────────────────────────


def compute_drill_through(df: pd.DataFrame, data_context: Dict) -> List[Dict]:
    """
    Pre-computes drill-down data for each category value in top categorical columns.
    When a user clicks a bar/segment, the frontend can show this detail view.
    Each entry: for one (dim, metric) pair, per-category stats on secondary metrics.
    """
    results: List[Dict] = []
    cat_cols = [c for c in df.select_dtypes(include=["object","category"]).columns
                if 2 <= df[c].nunique() <= 20]
    num_ordered = prioritize_columns(df.select_dtypes(include=["number"]).columns.tolist())[:6]
    if not cat_cols or not num_ordered:
        return results

    for cat_col in cat_cols[:3]:
        try:
            cats = df[cat_col].dropna().value_counts().head(12).index.tolist()
            all_categories: Dict[str, List[Dict]] = {}

            for cat_val in cats:
                subset = df[df[cat_col] == cat_val]
                if len(subset) < 2:
                    continue

                metrics_detail = []
                for num_col in num_ordered:
                    s = clean_series(subset[num_col])
                    if len(s) < 2:
                        continue
                    mean_v = float(s.mean())
                    total_v = float(s.sum())
                    metrics_detail.append({
                        "metric":          num_col,
                        "display_metric":  dname(num_col),
                        "count":           len(s),
                        "mean":            safe_float(mean_v),
                        "total":           safe_float(total_v),
                        "min":             safe_float(float(s.min())),
                        "max":             safe_float(float(s.max())),
                        "std":             safe_float(float(s.std())),
                        "formatted_mean":  fmt_value(mean_v, num_col),
                        "formatted_total": fmt_value(total_v, num_col),
                    })

                # Distribution of primary numeric col for sparkline
                prim_col = num_ordered[0]
                prim_series = clean_series(subset[prim_col])
                hist_vals: List[float] = []
                if len(prim_series) >= 4:
                    try:
                        n_bins = max(2, min(10, len(prim_series)//2))
                        hist_vals = np.histogram(prim_series.values, bins=n_bins)[0].tolist()
                    except Exception:
                        pass

                # Secondary breakdown: sub-category if another cat col exists
                sub_cats = [c for c in cat_cols if c != cat_col]
                sub_breakdown: List[Dict] = []
                if sub_cats:
                    try:
                        sub_col = sub_cats[0]
                        sub_grp = subset.groupby(sub_col)[num_ordered[0]].agg(["sum","count"]).reset_index()
                        sub_grp.columns = [sub_col, "_sum", "_count"]
                        sub_grp = sub_grp.sort_values("_sum", ascending=False).head(8)
                        for _, sr in sub_grp.iterrows():
                            v = float(sr["_sum"]) if pd.notna(sr["_sum"]) else 0.0
                            sub_breakdown.append({
                                "label":  str(sr[sub_col]),
                                "value":  safe_float(v),
                                "count":  int(sr["_count"]),
                                "display_value": fmt_value(v, num_ordered[0]),
                            })
                    except Exception:
                        pass

                all_categories[str(cat_val)] = {
                    "category_value":  str(cat_val),
                    "row_count":       int(len(subset)),
                    "metrics":         metrics_detail,
                    "histogram":       [int(v) for v in hist_vals],
                    "sub_breakdown":   sub_breakdown,
                    "sub_col":         sub_cats[0] if sub_cats else None,
                    "sub_display":     dname(sub_cats[0]) if sub_cats else None,
                }

            if all_categories:
                results.append({
                    "dimension":         cat_col,
                    "display_dimension": dname(cat_col),
                    "categories":        list(all_categories.keys()),
                    "detail":            all_categories,
                    "primary_metric":    num_ordered[0] if num_ordered else None,
                    "display_metric":    dname(num_ordered[0]) if num_ordered else None,
                })
        except Exception:
            continue
    return results


def _safe_compute(fn, *args, **kwargs) -> List:
    """Call a compute function and return [] on any exception, with JSON-safe output."""
    try:
        import json
        result = fn(*args, **kwargs)
        # Verify JSON-serializable — catches numpy types, defaultdict, etc.
        json.dumps(result)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return []


def generate_interactive_analytics(
    df: pd.DataFrame, data_context: Dict, stats: Dict, profile: Dict
) -> Dict:
    try:
        return {
            "success": True,
            "kpis": compute_kpis(df, data_context),
            "time_series": compute_time_series(df, data_context),
            "distributions": compute_distributions(df),
            "segments": compute_segments(df, data_context),
            "correlation_matrix": compute_correlation_matrix(df),
            "percentage_changes": compute_percentage_changes(df, data_context),
            "boxplots": compute_boxplot_data(df),
            "composition": compute_composition(df),
            "scatter": compute_scatter_data(df),
            "growth_rates": compute_growth_rates(df, data_context),
            "ranking": compute_ranking(df, data_context),
            "outlier_detail": compute_outlier_detail(df, data_context),
            "cohort": compute_cohort(df, data_context),
            "multi_metric": compute_multi_metric(df, data_context),
            "percentile_bands": compute_percentile_bands(df),
            "running_total": compute_running_total(df, data_context),
            "value_at_risk": compute_value_at_risk(df, data_context),
            "moving_statistics": compute_moving_statistics(df, data_context),
            "concentration": compute_concentration(df, data_context),
            "benchmark_comparison": compute_benchmark_comparison(df, data_context, stats),
            "data_quality_detail": compute_data_quality_detail(df, profile),
            "summary_stats": compute_summary_stats(df, data_context),
            "frequency_analysis": compute_frequency_analysis(df),
            "time_decomposition": compute_time_decomposition(df, data_context),
            "gauge": compute_gauge_data(df, data_context, stats),
            "slope_chart": compute_slope_chart(df, data_context),
            "error_bars": compute_error_bars(df, data_context),
            "marimekko": compute_marimekko(df, data_context),
            "gantt": _safe_compute(compute_gantt, df, data_context),
            "sankey": _safe_compute(compute_sankey, df, data_context),
            "drill_through": _safe_compute(compute_drill_through, df, data_context),
            "meta": {
                "total_rows": len(df),
                "total_cols": len(df.columns),
                "numeric_cols": df.select_dtypes(include=["number"]).columns.tolist(),
                "categorical_cols": df.select_dtypes(
                    include=["object", "category"]
                ).columns.tolist(),
                "has_datetime": len(detect_datetime_columns(df)) > 0,
                "domain": data_context.get("business_domain", "General"),
                "quality_score": profile.get("quality_score", 100),
                "completeness": profile.get("completeness", 100),
            },
        }
    except Exception as e:
        import traceback

        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "kpis": [],
            "time_series": [],
            "distributions": [],
            "segments": [],
            "correlation_matrix": {},
            "percentage_changes": [],
            "boxplots": [],
            "composition": [],
            "scatter": [],
            "growth_rates": [],
            "ranking": [],
            "outlier_detail": [],
            "cohort": [],
            "multi_metric": [],
            "percentile_bands": [],
            "running_total": [],
            "value_at_risk": [],
            "moving_statistics": [],
            "concentration": [],
            "benchmark_comparison": [],
            "data_quality_detail": [],
            "summary_stats": [],
            "frequency_analysis": [],
            "time_decomposition": [],
            "gauge": [],
            "slope_chart": [],
            "error_bars": [],
            "marimekko": [],
            "gantt": [],
            "sankey": [],
            "drill_through": [],
            "meta": {},
        }
