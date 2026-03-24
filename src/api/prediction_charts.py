"""
Prediction & Projection Charts
================================
Generates matplotlib-based forecast / projection charts when the data supports it.
Uses simple polynomial regression + linear trend for projection.
No external ML dependencies — pure numpy/scipy.
"""
import base64
import io
import warnings
from typing import List, Dict, Any, Optional

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

from src.utils.math_utils import safe_histogram_range

warnings.filterwarnings("ignore")

# ─── Palette ──────────────────────────────────────────────────────────────────
GOLD    = "#D4AF37"
TEAL    = "#00CED1"
CORAL   = "#FF6B6B"
PURPLE  = "#9B59B6"
EMERALD = "#2ECC71"
AMBER   = "#F39C12"
BG      = "#0a0a0f"
SURFACE = "#0f0f1a"


def _encode(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, facecolor=BG, bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    plt.close(fig)
    return b64


def _style_ax(ax):
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors="gray", labelsize=9)
    ax.grid(True, alpha=0.12, color="white", linestyle="--")
    for spine in ax.spines.values():
        spine.set_edgecolor("rgba(255,255,255,0.06)")


def _detect_datetime(df: pd.DataFrame) -> Optional[str]:
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
        try:
            parsed = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
            if parsed.notna().sum() > len(df) * 0.7:
                return col
        except Exception:
            pass
    return None


# ─── 1. Linear Trend + Projection ────────────────────────────────────────────
def create_trend_projection_chart(
    df: pd.DataFrame,
    metric_col: str,
    date_col: Optional[str],
    data_context: dict,
    n_periods: int = 6,
) -> Optional[dict]:
    """
    Show historical trend line + n_periods forward projection with confidence band.
    Works with both time-indexed and index-based data.
    """
    try:
        data = pd.to_numeric(df[metric_col], errors="coerce").dropna()
        if len(data) < 6:
            return None

        friendly = data_context.get("friendly_names", {}).get(metric_col,
                                    metric_col.replace("_", " ").title())

        # Build X axis
        if date_col and date_col in df.columns:
            ts = pd.to_datetime(df[date_col], errors="coerce")
            valid = ts.notna() & data.notna()
            x_raw = ts[valid].values
            y = data[valid].values
            x_num = np.arange(len(y))
            labels_hist = [str(pd.Timestamp(t).strftime("%b %d")) for t in x_raw]
        else:
            y = data.values
            x_num = np.arange(len(y))
            labels_hist = [f"T{i+1}" for i in x_num]

        if len(y) < 4:
            return None

        # Fit linear trend
        coeffs = np.polyfit(x_num, y, 1)
        trend_line = np.poly1d(coeffs)
        y_trend = trend_line(x_num)

        # Project forward
        x_future = np.arange(len(y), len(y) + n_periods)
        y_proj = trend_line(x_future)
        labels_proj = [f"+{i+1}" for i in range(n_periods)]

        # Confidence band (±1.5 × residual std)
        residuals = y - y_trend
        res_std = np.std(residuals)
        band_upper = y_proj + 1.5 * res_std
        band_lower = y_proj - 1.5 * res_std

        # Determine trend direction
        slope = coeffs[0]
        trend_pct = (y_proj[-1] - y[-1]) / abs(y[-1]) * 100 if y[-1] != 0 else 0
        trend_color = EMERALD if slope >= 0 else CORAL
        trend_label = f"Trending {'up' if slope >= 0 else 'down'} {abs(trend_pct):.1f}% over {n_periods} periods"

        # Plot
        all_x = np.arange(len(y) + n_periods)
        all_labels = labels_hist + labels_proj
        tick_step = max(1, len(all_labels) // 8)

        fig, ax = plt.subplots(figsize=(14, 6), facecolor=BG)
        _style_ax(ax)

        # Historical data
        ax.plot(x_num, y, color=GOLD, linewidth=2.5, zorder=3, label="Historical")
        ax.scatter(x_num, y, color=GOLD, s=40, zorder=4, edgecolors="white", linewidth=0.5)

        # Trend line
        ax.plot(x_num, y_trend, color=TEAL, linewidth=1.5, linestyle="--",
                alpha=0.7, label="Trend")

        # Projection
        ax.plot(x_future, y_proj, color=trend_color, linewidth=2.5,
                linestyle=":", zorder=3, label=f"Projection ({n_periods}p)")
        ax.fill_between(x_future, band_lower, band_upper,
                        alpha=0.12, color=trend_color, label="Confidence band")

        # Divider
        ax.axvline(x=len(y) - 0.5, color="rgba(255,255,255,0.15)",
                   linestyle="-", linewidth=1.5)
        ax.text(len(y) - 0.3, ax.get_ylim()[1] * 0.97, "Forecast",
                color="rgba(255,255,255,0.3)", fontsize=8, va="top")

        ax.set_xticks(all_x[::tick_step])
        ax.set_xticklabels(all_labels[::tick_step], rotation=35, ha="right",
                           color="gray", fontsize=8)
        ax.set_ylabel(friendly, color="gray", fontsize=10)
        ax.legend(facecolor="#10101c", edgecolor="rgba(212,175,55,0.15)",
                  labelcolor="white", fontsize=9)

        plt.suptitle(f"{friendly.upper()} — TREND & PROJECTION",
                     fontsize=15, fontweight="bold", color=GOLD, y=1.01)
        plt.tight_layout()

        # Summary — no double-dash, plain language
        y_mean = np.mean(y)
        summary = (
            f"TREND PROJECTION: {friendly}\n\n"
            f"Historical average: {y_mean:.2f} | "
            f"Current: {y[-1]:.2f} | "
            f"Projected ({n_periods}p): {y_proj[-1]:.2f}\n\n"
            f"{trend_label}.\n\n"
            f"Confidence band shows expected range (±1.5 std dev).\n"
            f"Shaded area represents uncertainty — actual results may vary."
        )

        return {
            "type": "forecast",
            "title": f"{friendly} — Trend Projection",
            "subtitle": trend_label,
            "image_base64": _encode(fig),
            "summary": summary,
            "business_insight": (
                f"If current trend continues, {friendly} will reach "
                f"{y_proj[-1]:.2f} in {n_periods} periods. "
                f"{'Positive trajectory — continue current strategy.' if slope >= 0 else 'Declining trend — intervention recommended.'}"
            ),
        }
    except Exception:
        import traceback; traceback.print_exc()
        return None


# ─── 2. Moving Average Projection ────────────────────────────────────────────
def create_moving_average_chart(
    df: pd.DataFrame,
    metric_col: str,
    date_col: Optional[str],
    data_context: dict,
) -> Optional[dict]:
    """
    Historical data with 3-period and 7-period moving averages.
    Shows smoothed trend without projection noise.
    """
    try:
        data = pd.to_numeric(df[metric_col], errors="coerce").dropna()
        if len(data) < 8:
            return None

        friendly = data_context.get("friendly_names", {}).get(metric_col,
                                    metric_col.replace("_", " ").title())
        y = data.values
        x = np.arange(len(y))
        labels = [f"T{i+1}" for i in x]
        if date_col and date_col in df.columns:
            ts = pd.to_datetime(df[date_col], errors="coerce")
            if ts.notna().sum() >= len(y) * 0.7:
                labels = [str(pd.Timestamp(t).strftime("%b %d"))
                          for t in ts.dropna().values[:len(y)]]

        ma3 = pd.Series(y).rolling(window=3, min_periods=1).mean().values
        ma7 = pd.Series(y).rolling(window=7, min_periods=1).mean().values

        fig, ax = plt.subplots(figsize=(14, 6), facecolor=BG)
        _style_ax(ax)

        ax.fill_between(x, y, alpha=0.08, color=GOLD)
        ax.plot(x, y, color=GOLD, linewidth=1.5, alpha=0.6, label="Actual")
        ax.plot(x, ma3, color=TEAL, linewidth=2.5, label="3-period avg")
        ax.plot(x, ma7, color=CORAL, linewidth=2.5, linestyle="--", label="7-period avg")

        tick_step = max(1, len(labels) // 8)
        ax.set_xticks(x[::tick_step])
        ax.set_xticklabels(labels[::tick_step], rotation=35, ha="right",
                           color="gray", fontsize=8)
        ax.set_ylabel(friendly, color="gray", fontsize=10)
        ax.legend(facecolor="#10101c", edgecolor="rgba(212,175,55,0.15)",
                  labelcolor="white", fontsize=9)

        # Annotate last values
        ax.annotate(f"{ma3[-1]:.1f}", xy=(x[-1], ma3[-1]),
                    xytext=(5, 0), textcoords="offset points",
                    color=TEAL, fontsize=9, fontweight="bold")
        ax.annotate(f"{ma7[-1]:.1f}", xy=(x[-1], ma7[-1]),
                    xytext=(5, 0), textcoords="offset points",
                    color=CORAL, fontsize=9, fontweight="bold")

        plt.suptitle(f"{friendly.upper()} — MOVING AVERAGE ANALYSIS",
                     fontsize=15, fontweight="bold", color=GOLD, y=1.01)
        plt.tight_layout()

        # Crossover signal
        if ma3[-1] > ma7[-1] and ma3[-3] <= ma7[-3]:
            signal = "Short-term avg crossed above long-term — bullish signal."
        elif ma3[-1] < ma7[-1] and ma3[-3] >= ma7[-3]:
            signal = "Short-term avg crossed below long-term — bearish signal."
        else:
            signal = f"Short-term avg ({ma3[-1]:.1f}) vs long-term avg ({ma7[-1]:.1f})."

        summary = (
            f"MOVING AVERAGE ANALYSIS: {friendly}\n\n"
            f"3-period moving average smooths short-term noise.\n"
            f"7-period moving average shows the broader trend.\n\n"
            f"{signal}\n\n"
            f"Gap between averages: {abs(ma3[-1] - ma7[-1]):.2f} "
            f"({'widening' if abs(ma3[-1]-ma7[-1]) > abs(ma3[-3]-ma7[-3]) else 'narrowing'})"
        )

        return {
            "type": "trend",
            "title": f"{friendly} — Moving Average",
            "subtitle": signal,
            "image_base64": _encode(fig),
            "summary": summary,
            "business_insight": signal,
        }
    except Exception:
        import traceback; traceback.print_exc()
        return None


# ─── 3. Growth Rate Chart ─────────────────────────────────────────────────────
def create_growth_rate_chart(
    df: pd.DataFrame,
    metric_col: str,
    data_context: dict,
) -> Optional[dict]:
    """Period-over-period growth rate with cumulative overlay."""
    try:
        data = pd.to_numeric(df[metric_col], errors="coerce").dropna()
        if len(data) < 5:
            return None

        friendly = data_context.get("friendly_names", {}).get(metric_col,
                                    metric_col.replace("_", " ").title())
        y = data.values
        growth = [(y[i]-y[i-1])/abs(y[i-1])*100 if y[i-1] != 0 else 0
                  for i in range(1, len(y))]
        cumulative = [(y[i]-y[0])/abs(y[0])*100 if y[0] != 0 else 0
                      for i in range(1, len(y))]
        x = np.arange(len(growth))
        labels = [f"P{i+2}" for i in x]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), facecolor=BG)
        _style_ax(ax1)
        _style_ax(ax2)

        # Period growth bars
        colors_bar = [EMERALD if g >= 0 else CORAL for g in growth]
        bars = ax1.bar(x, growth, color=colors_bar, edgecolor="white",
                       alpha=0.8, linewidth=0.5)
        ax1.axhline(0, color="rgba(255,255,255,0.2)", linewidth=1)
        avg_growth = np.mean(growth)
        ax1.axhline(avg_growth, color=AMBER, linestyle="--", linewidth=1.5,
                    label=f"Avg growth: {avg_growth:.1f}%")
        for bar, val in zip(bars, growth):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                     f"{val:.1f}%", ha="center", fontsize=7, color="white")
        ax1.set_xticks(x[::max(1, len(x)//8)])
        ax1.set_xticklabels(labels[::max(1, len(x)//8)], color="gray", fontsize=8)
        ax1.set_ylabel("Period Growth %", color="gray", fontsize=9)
        ax1.set_title("Period-over-Period Growth Rate",
                      color="white", fontsize=11, fontweight="bold")
        ax1.legend(facecolor="#10101c", edgecolor="rgba(212,175,55,0.15)",
                   labelcolor="white", fontsize=8)

        # Cumulative growth line
        cum_color = TEAL if cumulative[-1] >= 0 else CORAL
        ax2.fill_between(x, cumulative, alpha=0.08, color=cum_color)
        ax2.plot(x, cumulative, color=cum_color, linewidth=2.5)
        ax2.scatter(x, cumulative, color=cum_color, s=30, zorder=3)
        ax2.axhline(0, color="rgba(255,255,255,0.2)", linewidth=1)
        ax2.set_xticks(x[::max(1, len(x)//8)])
        ax2.set_xticklabels(labels[::max(1, len(x)//8)], color="gray", fontsize=8)
        ax2.set_ylabel("Cumulative Growth %", color="gray", fontsize=9)
        ax2.set_title("Cumulative Growth from Baseline",
                      color="white", fontsize=11, fontweight="bold")

        plt.suptitle(f"{friendly.upper()} — GROWTH RATE ANALYSIS",
                     fontsize=15, fontweight="bold", color=GOLD, y=1.01)
        plt.tight_layout()

        pos_periods = sum(1 for g in growth if g >= 0)
        neg_periods = len(growth) - pos_periods

        summary = (
            f"GROWTH RATE ANALYSIS: {friendly}\n\n"
            f"Average period growth: {avg_growth:.1f}% | "
            f"Cumulative: {cumulative[-1]:.1f}%\n\n"
            f"Positive periods: {pos_periods} | Negative periods: {neg_periods}\n\n"
            f"{'Growth is predominantly positive — healthy trajectory.' if pos_periods > neg_periods else 'More negative periods than positive — review performance drivers.'}"
        )

        return {
            "type": "trend",
            "title": f"{friendly} — Growth Rate",
            "subtitle": f"Avg: {avg_growth:.1f}%/period | Cumulative: {cumulative[-1]:.1f}%",
            "image_base64": _encode(fig),
            "summary": summary,
            "business_insight": (
                f"{friendly} has grown cumulatively by {cumulative[-1]:.1f}% from baseline. "
                f"Average period growth: {avg_growth:.1f}%."
            ),
        }
    except Exception:
        import traceback; traceback.print_exc()
        return None


# ─── Main orchestrator ────────────────────────────────────────────────────────
def generate_prediction_charts(df: pd.DataFrame, data_context: dict) -> List[dict]:
    """
    Entry point: tries to generate prediction/projection charts based on data shape.
    Returns a list of chart dicts (may be empty if data doesn't support it).
    """
    charts: List[dict] = []
    seen_titles: set = set()

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        return charts

    # Pick the most important numeric columns (top 3 by variance)
    key_cols = sorted(numeric_cols, key=lambda c: df[c].var(), reverse=True)[:3]

    # Override with explicitly identified key metrics
    context_keys = data_context.get("key_metrics", [])
    if context_keys:
        key_cols = [c for c in context_keys if c in numeric_cols][:3] or key_cols

    date_col = None
    # Detect datetime column
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_col = col
            break
    if not date_col:
        for col in df.columns:
            try:
                parsed = pd.to_datetime(df[col], errors="coerce")
                if parsed.notna().sum() > len(df) * 0.7:
                    date_col = col
                    break
            except Exception:
                pass

    has_enough_rows = len(df) >= 8

    for col in key_cols:
        if not has_enough_rows:
            break

        # Trend + projection
        chart = create_trend_projection_chart(df, col, date_col, data_context)
        if chart and chart.get("title") not in seen_titles:
            charts.append(chart)
            seen_titles.add(chart["title"])

        # Moving average
        if len(charts) < 6:
            chart = create_moving_average_chart(df, col, date_col, data_context)
            if chart and chart.get("title") not in seen_titles:
                charts.append(chart)
                seen_titles.add(chart["title"])

        # Growth rate
        if len(charts) < 6:
            chart = create_growth_rate_chart(df, col, data_context)
            if chart and chart.get("title") not in seen_titles:
                charts.append(chart)
                seen_titles.add(chart["title"])

    return charts
