"""
AI-Powered Chart System with Dynamic Visualizations
===================================================

Uses AI for:
1. Data understanding
2. Chart type selection
3. Title generation
4. Summary generation

Focuses on the most impactful charts for decision making
"""

import pandas as pd
from src.utils.math_utils import safe_histogram_range
import numpy as np
from typing import Dict, List, Optional, Any
import warnings
import io
import base64
import json
import requests

warnings.filterwarnings("ignore")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Professional color scheme
GOLD = "#D4AF37"
TEAL = "#00CED1"
CORAL = "#FF6B6B"
PURPLE = "#9B59B6"
EMERALD = "#2ECC71"
ORANGE = "#E67E22"
BLUE = "#3498DB"
SLATE = "#64748B"
MIDNIGHT = "#1a1a2e"
OBSIDIAN = "#0a0a0f"
FROST = "#ecf0f1"
CHARCOAL = "#888888"

COLOR_LIST = [GOLD, TEAL, CORAL, PURPLE, EMERALD, ORANGE, BLUE, "#1ABC9C"]

# OpenAI API configuration
OPENAI_API_KEY = "sk-f616wEWWXQftbJmE5UWc3EcRx29UcIPR08LrRcvLxhgD8k5I572dkAmhBtQwtEdA"
OPENAI_BASE_URL = "https://api.openai.com/v1"


def get_ai_insights(data_summary: str) -> Dict:
    """Get AI insights for data understanding"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        prompt = f"""Analyze this data and provide insights in JSON format:

{data_summary}

Return ONLY valid JSON with this structure:
{{
    "business_domain": "detected domain",
    "key_metrics": ["metric1", "metric2", "metric3"],
    "data_quality_notes": "quality assessment",
    "recommended_charts": [
        {{"type": "trend", "metric": "metric_name", "reason": "why this chart is important"}},
        {{"type": "ranking", "category": "cat_col", "metric": "num_col", "reason": "why"}},
        {{"type": "correlation", "col1": "metric1", "col2": "metric2", "reason": "why"}}
    ],
    "business_insights": [
        "insight 1 about the data",
        "insight 2 about the data",
        "insight 3 about the data"
    ]
}}"""

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a Senior Data Analyst. Analyze data and provide actionable business insights. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1500,
            "temperature": 0.3,
        }

        response = requests.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            # Extract JSON from response
            if "{" in content and "}" in content:
                json_str = content[content.find("{") : content.rfind("}") + 1]
                return json.loads(json_str)
    except Exception as e:
        print(f"AI insights error: {e}")

    return {}


def get_ai_chart_title(chart_type: str, data_context: str) -> Dict:
    """Get AI-generated chart title and summary"""
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }

        prompt = f"""Generate a compelling title and summary for a {chart_type} chart based on this context:

{data_context}

Return ONLY valid JSON:
{{
    "title": "Action-oriented title for the chart",
    "subtitle": "Brief context about what the chart shows",
    "summary": "1-2 sentence summary explaining the chart's key insight",
    "business_insight": "What business decision this chart supports",
    "severity": "info/warning/critical"
}}"""

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a Business Intelligence expert. Generate compelling chart titles and summaries. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 500,
            "temperature": 0.5,
        }

        response = requests.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            if "{" in content and "}" in content:
                json_str = content[content.find("{") : content.rfind("}") + 1]
                return json.loads(json_str)
    except Exception as e:
        print(f"AI title error: {e}")

    return {}


class AIChartGenerator:
    """
    AI-Powered Chart Generator
    Creates impactful charts with AI-generated titles and summaries
    """

    def __init__(self, df: pd.DataFrame, data_context: Dict = None):
        self.df = df.copy()
        self.data_context = data_context or {}
        self.numeric_cols = []
        self.categorical_cols = []
        self.datetime_cols = []
        self.ai_insights = {}
        self._identify_columns()
        self._get_ai_understanding()

    def _identify_columns(self):
        """Identify column types"""
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            col_lower = col.lower()

            # Check for datetime
            if "datetime" in dtype or any(
                kw in col_lower for kw in ["date", "time", "timestamp", "created"]
            ):
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors="coerce")
                    if self.df[col].notna().sum() > 0:
                        self.datetime_cols.append(col)
                        continue
                except:
                    pass

            # Check for numeric
            if any(x in dtype for x in ["int", "float", "number"]):
                self.numeric_cols.append(col)
            else:
                try:
                    numeric_count = (
                        pd.to_numeric(self.df[col], errors="coerce").notna().sum()
                    )
                    if numeric_count / len(self.df) > 0.8:
                        self.numeric_cols.append(col)
                    else:
                        self.categorical_cols.append(col)
                except:
                    self.categorical_cols.append(col)

    def _get_ai_understanding(self):
        """Get AI understanding of the data"""
        # Create data summary for AI
        summary = (
            f"Dataset has {len(self.df)} rows and {len(self.df.columns)} columns.\n"
        )
        summary += f"Numeric columns: {', '.join(self.numeric_cols[:10])}\n"
        summary += f"Categorical columns: {', '.join(self.categorical_cols[:10])}\n"
        summary += f"Datetime columns: {', '.join(self.datetime_cols[:5])}\n"

        # Add sample stats
        for col in self.numeric_cols[:5]:
            data = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(data) > 0:
                summary += f"\n{col}: total={data.sum():,.0f}, avg={data.mean():,.1f}, min={data.min():,.1f}, max={data.max():,.1f}"

        self.ai_insights = get_ai_insights(summary)

    def generate_charts(self) -> List[Dict]:
        """Generate AI-powered charts"""
        charts = []

        # 1. KPI Dashboard (always)
        charts.append(self._create_kpi_dashboard())

        # 2. Trend Chart (if datetime exists)
        if self.datetime_cols and self.numeric_cols:
            charts.append(self._create_trend_chart())

        # 3. Period Changes (if datetime exists)
        if self.datetime_cols and self.numeric_cols:
            charts.append(self._create_period_changes_chart())

        # 4. Ranking Chart (if categorical exists)
        if self.categorical_cols and self.numeric_cols:
            charts.append(self._create_ranking_chart())

        # 5. Correlation Chart (if multiple numeric)
        if len(self.numeric_cols) >= 2:
            charts.append(self._create_correlation_chart())

        # 6. Distribution Chart
        if self.numeric_cols:
            charts.append(self._create_distribution_chart())

        # 7. Composition Chart
        if self.categorical_cols and self.numeric_cols:
            charts.append(self._create_composition_chart())

        # 8. Data Quality
        charts.append(self._create_quality_chart())

        # Add AI insights to charts
        if self.ai_insights.get("business_insights"):
            for i, insight in enumerate(self.ai_insights["business_insights"][:3]):
                if i < len(charts):
                    charts[i]["ai_insight"] = insight

        return [c for c in charts if c is not None]

    def _create_kpi_dashboard(self) -> Dict:
        """Create KPI dashboard with AI insights"""
        num_cols = min(6, len(self.numeric_cols))
        if num_cols == 0:
            return None

        fig, axes = plt.subplots(2, 3, figsize=(16, 10), facecolor=OBSIDIAN)

        # AI-generated title
        ai_title = self.ai_insights.get("business_domain", "Key Performance Indicators")
        fig.suptitle(
            f"EXECUTIVE DASHBOARD - {ai_title.upper()}",
            fontsize=18,
            color=GOLD,
            fontweight="bold",
            y=0.98,
        )

        for i, col in enumerate(self.numeric_cols[:6]):
            row, col_pos = i // 3, i % 3
            ax = axes[row, col_pos]
            ax.set_facecolor(MIDNIGHT)

            data = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(data) > 0:
                # Calculate appropriate number of bins based on data
                n_unique = data.nunique()
                if n_unique < 2:
                    n_bins = 1
                elif n_unique < 10:
                    n_bins = n_unique
                else:
                    n_bins = min(30, max(5, int(np.sqrt(len(data)))))

                ax.hist(
                    data,
                    range=safe_histogram_range(data),
                    bins=n_bins,
                    color=COLOR_LIST[i % len(COLOR_LIST)],
                    alpha=0.8,
                    edgecolor="white",
                )

                mean_val = data.mean()
                median_val = data.median()
                ax.axvline(
                    mean_val,
                    color=CORAL,
                    linestyle="--",
                    linewidth=2,
                    label=f"Mean: {mean_val:,.1f}",
                )
                ax.axvline(
                    median_val,
                    color=EMERALD,
                    linestyle="-",
                    linewidth=2,
                    label=f"Median: {median_val:,.1f}",
                )

                col_name = col.replace("_", " ").title()
                ax.set_title(
                    f"{col_name}\nTotal: {data.sum():,.0f} | Avg: {mean_val:,.1f}",
                    color=FROST,
                    fontsize=11,
                    fontweight="bold",
                )
                ax.legend(
                    fontsize=8, facecolor=MIDNIGHT, edgecolor=CHARCOAL, labelcolor=FROST
                )
                ax.tick_params(colors=CHARCOAL)
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)

        plt.tight_layout(rect=[0, 0, 1, 0.95])

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        # Generate KPI summary
        kpis = []
        for col in self.numeric_cols[:4]:
            data = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(data) > 0:
                kpis.append(
                    {
                        "name": col.replace("_", " ").title(),
                        "total": f"{data.sum():,.0f}",
                        "avg": f"{data.mean():,.1f}",
                    }
                )

        # AI-generated summary
        summary = f"Analysis of {len(self.df):,} records across {len(self.numeric_cols)} key metrics. "
        summary += f"Key metrics: {', '.join([k['name'] for k in kpis[:3]])}."

        return {
            "type": "kpi_dashboard",
            "title": f"Executive Dashboard - {ai_title}",
            "subtitle": f"{len(self.df):,} records analyzed | {len(self.numeric_cols)} metrics",
            "image_base64": img,
            "summary": summary,
            "business_insight": "Monitor these KPIs to identify trends and areas for improvement",
            "severity": "info",
            "data": {"kpis": kpis},
        }

    def _create_trend_chart(self) -> Dict:
        """Create trend chart with AI insights"""
        date_col = self.datetime_cols[0]
        metric_col = self.numeric_cols[0]

        df_sorted = self.df.sort_values(date_col).dropna(subset=[date_col])
        df_sorted[metric_col] = pd.to_numeric(df_sorted[metric_col], errors="coerce")
        df_sorted = df_sorted.dropna(subset=[metric_col])

        if len(df_sorted) < 5:
            return None

        daily = df_sorted.groupby(date_col)[metric_col].mean().reset_index()

        fig, ax = plt.subplots(figsize=(14, 7), facecolor=OBSIDIAN)
        ax.set_facecolor(MIDNIGHT)

        ax.fill_between(daily[date_col], daily[metric_col], alpha=0.3, color=GOLD)
        ax.plot(
            daily[date_col],
            daily[metric_col],
            color=GOLD,
            linewidth=2.5,
            marker="o",
            markersize=6,
        )

        window = min(7, len(daily) // 3)
        if window >= 2:
            ma = daily[metric_col].rolling(window=window, center=True).mean()
            ax.plot(
                daily[date_col],
                ma,
                color=TEAL,
                linewidth=3,
                linestyle="--",
                label=f"{window}-period MA",
            )

        first_val = daily[metric_col].iloc[0]
        last_val = daily[metric_col].iloc[-1]
        change_pct = (
            ((last_val - first_val) / abs(first_val)) * 100 if first_val != 0 else 0
        )
        direction = "UPWARD" if change_pct > 0 else "DOWNWARD"
        color = EMERALD if change_pct > 0 else CORAL

        ax.annotate(
            f"TREND: {direction}\nChange: {change_pct:+.1f}%",
            xy=(0.02, 0.95),
            xycoords="axes fraction",
            fontsize=14,
            color=color,
            fontweight="bold",
            bbox=dict(boxstyle="round", facecolor=MIDNIGHT, edgecolor=color),
            verticalalignment="top",
        )

        col_name = metric_col.replace("_", " ").title()
        ax.set_title(
            f"{col_name} TREND ANALYSIS",
            color=GOLD,
            fontsize=18,
            fontweight="bold",
            pad=15,
        )
        ax.set_xlabel("Date", color=CHARCOAL)
        ax.set_ylabel(col_name, color=CHARCOAL)
        ax.legend(facecolor=MIDNIGHT, edgecolor=CHARCOAL, labelcolor=FROST)
        ax.tick_params(colors=CHARCOAL)
        ax.grid(True, alpha=0.2)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        # Get AI title
        context = f"{col_name} shows {direction.lower()} trend with {change_pct:+.1f}% change over the analysis period"
        ai_content = get_ai_chart_title("trend", context)

        title = ai_content.get("title", f"{col_name} Trend Analysis")
        subtitle = ai_content.get(
            "subtitle", f"{direction} trend with {change_pct:+.1f}% change"
        )
        summary = ai_content.get(
            "summary", f"Overall {direction.lower()} movement of {abs(change_pct):.1f}%"
        )
        business_insight = ai_content.get(
            "business_insight",
            f"{'Continue current strategy to maintain growth' if change_pct > 0 else 'Investigate causes of decline'}",
        )

        return {
            "type": "trend_analysis",
            "title": title,
            "subtitle": subtitle,
            "image_base64": img,
            "summary": summary,
            "business_insight": business_insight,
            "severity": "healthy" if change_pct > 0 else "warning",
            "data": {"change_pct": change_pct, "direction": direction},
        }

    def _create_period_changes_chart(self) -> Dict:
        """Create period changes chart"""
        date_col = self.datetime_cols[0]
        metric_col = self.numeric_cols[0]

        df_sorted = self.df.sort_values(date_col).dropna(subset=[date_col])
        df_sorted[metric_col] = pd.to_numeric(df_sorted[metric_col], errors="coerce")
        df_sorted = df_sorted.dropna(subset=[metric_col])

        if len(df_sorted) < 3:
            return None

        values = df_sorted[metric_col].values
        pct_changes = (
            np.diff(values) / np.where(values[:-1] == 0, 1, np.abs(values[:-1])) * 100
        )
        pct_changes = np.clip(pct_changes, -100, 100)

        fig, ax = plt.subplots(figsize=(14, 7), facecolor=OBSIDIAN)
        ax.set_facecolor(MIDNIGHT)

        colors = [EMERALD if x >= 0 else CORAL for x in pct_changes]
        bars = ax.bar(
            range(len(pct_changes)),
            pct_changes,
            color=colors,
            edgecolor="white",
            alpha=0.8,
            width=0.7,
        )

        for bar, val in zip(bars, pct_changes):
            y_pos = bar.get_height()
            label = f"+{val:.1f}%" if val >= 0 else f"{val:.1f}%"
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                y_pos + (2 if y_pos >= 0 else -5),
                label,
                ha="center",
                va="bottom" if y_pos >= 0 else "top",
                fontsize=9,
                color=FROST,
                fontweight="bold",
            )

        ax.axhline(y=0, color=CHARCOAL, linestyle="--", linewidth=1)

        positive_periods = int(np.sum(pct_changes > 0))
        negative_periods = int(np.sum(pct_changes < 0))
        avg_change = np.mean(pct_changes)

        col_name = metric_col.replace("_", " ").title()
        ax.set_title(
            f"{col_name} - PERIOD-OVER-PERIOD CHANGES",
            color=GOLD,
            fontsize=18,
            fontweight="bold",
            pad=15,
        )
        ax.set_xlabel("Period Number", color=CHARCOAL)
        ax.set_ylabel("Change (%)", color=CHARCOAL)
        ax.tick_params(colors=CHARCOAL)
        ax.grid(True, alpha=0.2, axis="y")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        # Get AI title
        context = f"{col_name} period changes: {positive_periods} growth periods, {negative_periods} decline periods, average change {avg_change:+.1f}%"
        ai_content = get_ai_chart_title("period_changes", context)

        title = ai_content.get("title", f"{col_name} Period Changes")
        subtitle = ai_content.get(
            "subtitle",
            f"{positive_periods} growth periods, {negative_periods} decline periods",
        )
        summary = ai_content.get(
            "summary", f"Average period change: {avg_change:+.1f}%"
        )
        business_insight = ai_content.get(
            "business_insight",
            f"{'More periods showing growth - positive momentum' if positive_periods > negative_periods else 'More periods showing decline - investigate causes'}",
        )

        return {
            "type": "period_changes",
            "title": title,
            "subtitle": subtitle,
            "image_base64": img,
            "summary": summary,
            "business_insight": business_insight,
            "severity": "info",
            "data": {
                "avg_change": avg_change,
                "positive": positive_periods,
                "negative": negative_periods,
            },
        }

    def _create_ranking_chart(self) -> Dict:
        """Create ranking chart"""
        cat_col = self.categorical_cols[0]
        metric_col = self.numeric_cols[0]

        agg = (
            self.df.groupby(cat_col)[metric_col]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        if len(agg) < 2:
            return None

        total = agg.sum()

        fig, ax = plt.subplots(figsize=(14, 8), facecolor=OBSIDIAN)
        ax.set_facecolor(MIDNIGHT)

        colors = [GOLD] + [SLATE] * (len(agg) - 1)
        bars = ax.barh(
            range(len(agg)), agg.values, color=colors, edgecolor="white", height=0.7
        )

        labels = [str(x).replace("_", " ").title()[:20] for x in agg.index]
        ax.set_yticks(range(len(agg)))
        ax.set_yticklabels(labels, color=FROST, fontsize=11)
        ax.invert_yaxis()

        for bar, val in zip(bars, agg.values):
            pct = val / total * 100
            ax.text(
                val + agg.max() * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{val:,.0f} ({pct:.1f}%)",
                va="center",
                fontsize=10,
                color=FROST,
                fontweight="bold",
            )

        top_item = labels[0]
        top_share = agg.iloc[0] / total * 100

        cat_name = cat_col.replace("_", " ").title()
        metric_name = metric_col.replace("_", " ").title()
        ax.set_title(
            f"TOP {len(agg)} {cat_name.upper()} BY {metric_name.upper()}",
            color=GOLD,
            fontsize=16,
            fontweight="bold",
            pad=15,
        )
        ax.set_xlabel(metric_name, color=CHARCOAL)
        ax.tick_params(colors=CHARCOAL)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(True, alpha=0.2, axis="x")

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        # Get AI title
        context = f"Ranking of {cat_name} by {metric_name}: {top_item} leads with {top_share:.1f}% share"
        ai_content = get_ai_chart_title("ranking", context)

        title = ai_content.get("title", f"{cat_name} Ranking by {metric_name}")
        subtitle = ai_content.get("subtitle", f"Top {len(agg)} performers")
        summary = ai_content.get(
            "summary", f"{top_item} leads with {top_share:.1f}% share"
        )
        business_insight = ai_content.get(
            "business_insight",
            f"{'High concentration - consider diversification' if top_share > 40 else 'Healthy distribution across segments'}",
        )

        return {
            "type": "ranking_chart",
            "title": title,
            "subtitle": subtitle,
            "image_base64": img,
            "summary": summary,
            "business_insight": business_insight,
            "severity": "info",
            "data": {"top_item": top_item, "top_share": top_share},
        }

    def _create_correlation_chart(self) -> Dict:
        """Create correlation chart"""
        col1 = self.numeric_cols[0]
        col2 = (
            self.numeric_cols[1] if len(self.numeric_cols) > 1 else self.numeric_cols[0]
        )

        data1 = pd.to_numeric(self.df[col1], errors="coerce")
        data2 = pd.to_numeric(self.df[col2], errors="coerce")
        valid = ~(data1.isna() | data2.isna())

        if valid.sum() < 10:
            return None

        sample_idx = valid[valid].index
        if len(sample_idx) > 1500:
            sample_idx = np.random.choice(sample_idx, 1500, replace=False)

        fig, ax = plt.subplots(figsize=(14, 10), facecolor=OBSIDIAN)
        ax.set_facecolor(MIDNIGHT)

        ax.scatter(
            data1[sample_idx],
            data2[sample_idx],
            c=GOLD,
            alpha=0.6,
            s=50,
            edgecolors=OBSIDIAN,
        )

        z = np.polyfit(data1[sample_idx], data2[sample_idx], 1)
        p = np.poly1d(z)
        x_line = np.linspace(data1[sample_idx].min(), data1[sample_idx].max(), 100)
        ax.plot(
            x_line,
            p(x_line),
            color=CORAL,
            linewidth=3,
            linestyle="--",
            label="Trend Line",
        )

        r = data1[valid].corr(data2[valid])
        strength = (
            "STRONG" if abs(r) >= 0.7 else "MODERATE" if abs(r) >= 0.5 else "WEAK"
        )
        direction = "POSITIVE" if r > 0 else "NEGATIVE"
        color = EMERALD if abs(r) >= 0.7 else (ORANGE if abs(r) >= 0.5 else CORAL)

        col1_name = col1.replace("_", " ").title()
        col2_name = col2.replace("_", " ").title()

        ax.annotate(
            f"CORRELATION: {strength} {direction}\nr = {r:.3f}",
            xy=(0.02, 0.95),
            xycoords="axes fraction",
            fontsize=14,
            color=color,
            fontweight="bold",
            bbox=dict(boxstyle="round", facecolor=MIDNIGHT, edgecolor=color),
            verticalalignment="top",
        )

        ax.set_title(
            f"{col1_name} vs {col2_name}",
            color=GOLD,
            fontsize=18,
            fontweight="bold",
            pad=15,
        )
        ax.set_xlabel(col1_name, color=CHARCOAL)
        ax.set_ylabel(col2_name, color=CHARCOAL)
        ax.legend(facecolor=MIDNIGHT, edgecolor=CHARCOAL, labelcolor=FROST)
        ax.tick_params(colors=CHARCOAL)
        ax.grid(True, alpha=0.2)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        # Get AI title
        context = f"{col1_name} vs {col2_name}: {strength.lower()} {direction.lower()} correlation (r={r:.3f})"
        ai_content = get_ai_chart_title("correlation", context)

        title = ai_content.get("title", f"{col1_name} vs {col2_name}")
        subtitle = ai_content.get(
            "subtitle", f"{strength} {direction.lower()} correlation (r={r:.3f})"
        )
        summary = ai_content.get("summary", f"{strength.lower()} relationship detected")
        business_insight = ai_content.get(
            "business_insight",
            f"{'Optimize both metrics together for maximum impact' if abs(r) >= 0.5 else 'Metrics may be independent - analyze separately'}",
        )

        return {
            "type": "correlation_chart",
            "title": title,
            "subtitle": subtitle,
            "image_base64": img,
            "summary": summary,
            "business_insight": business_insight,
            "severity": "info",
            "data": {"r": r, "strength": strength},
        }

    def _create_distribution_chart(self) -> Dict:
        """Create distribution chart"""
        cols_to_plot = self.numeric_cols[:4]

        fig, axes = plt.subplots(2, 2, figsize=(14, 10), facecolor=OBSIDIAN)
        fig.suptitle(
            "DISTRIBUTION ANALYSIS", fontsize=18, color=GOLD, fontweight="bold", y=0.98
        )

        for i, col in enumerate(cols_to_plot[:4]):
            ax = axes[i // 2, i % 2]
            ax.set_facecolor(MIDNIGHT)

            data = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(data) > 0:
                # Calculate appropriate number of bins based on data
                n_unique = data.nunique()
                if n_unique < 2:
                    n_bins = 1
                elif n_unique < 10:
                    n_bins = n_unique
                else:
                    n_bins = min(40, max(5, int(np.sqrt(len(data)))))

                ax.hist(
                    data,
                    range=safe_histogram_range(data),
                    bins=n_bins,
                    color=COLOR_LIST[i % len(COLOR_LIST)],
                    alpha=0.7,
                    edgecolor="white",
                )

                mean_val = data.mean()
                median_val = data.median()
                ax.axvline(
                    mean_val,
                    color=CORAL,
                    linestyle="--",
                    linewidth=2,
                    label=f"Mean: {mean_val:,.1f}",
                )
                ax.axvline(
                    median_val,
                    color=EMERALD,
                    linestyle="-",
                    linewidth=2,
                    label=f"Median: {median_val:,.1f}",
                )

                skew = data.skew()
                skew_text = (
                    "Right-Skewed"
                    if skew > 0.5
                    else "Left-Skewed"
                    if skew < -0.5
                    else "Normal"
                )

                col_name = col.replace("_", " ").title()
                ax.set_title(
                    f"{col_name}\n{skew_text} (Skew: {skew:.2f})",
                    color=FROST,
                    fontsize=11,
                    fontweight="bold",
                )
                ax.legend(
                    fontsize=8, facecolor=MIDNIGHT, edgecolor=CHARCOAL, labelcolor=FROST
                )
                ax.tick_params(colors=CHARCOAL)
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        return {
            "type": "distribution_chart",
            "title": "Distribution Analysis",
            "subtitle": f"Analysis of {len(cols_to_plot)} key metrics",
            "image_base64": img,
            "summary": "Shows data distribution patterns and central tendency",
            "business_insight": "Use median for skewed data, mean for normal distributions",
            "severity": "info",
        }

    def _create_composition_chart(self) -> Dict:
        """Create composition chart"""
        cat_col = self.categorical_cols[0]
        metric_col = self.numeric_cols[0]

        agg = (
            self.df.groupby(cat_col)[metric_col]
            .sum()
            .sort_values(ascending=False)
            .head(8)
        )

        if len(agg) < 2:
            return None

        fig, ax = plt.subplots(figsize=(12, 10), facecolor=OBSIDIAN)
        ax.set_facecolor(MIDNIGHT)

        total = agg.sum()
        wedges, texts, autotexts = ax.pie(
            agg.values,
            labels=None,
            colors=COLOR_LIST[: len(agg)],
            autopct=lambda pct: f"{pct:.1f}%" if pct > 3 else "",
            startangle=90,
            pctdistance=0.75,
            wedgeprops=dict(width=0.5, edgecolor="white"),
        )

        for autotext in autotexts:
            autotext.set_color(OBSIDIAN)
            autotext.set_fontweight("bold")
            autotext.set_fontsize(11)

        ax.text(
            0,
            0,
            f"TOTAL\n{total:,.0f}",
            ha="center",
            va="center",
            fontsize=18,
            color=FROST,
            fontweight="bold",
        )

        labels = [
            f"{str(x).replace('_', ' ').title()[:15]}: {val / total * 100:.1f}%"
            for x, val in zip(agg.index, agg.values)
        ]
        ax.legend(
            wedges,
            labels,
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            facecolor=MIDNIGHT,
            edgecolor=CHARCOAL,
            labelcolor=FROST,
            fontsize=10,
        )

        top_pct = agg.iloc[0] / total * 100
        cat_name = cat_col.replace("_", " ").title()
        metric_name = metric_col.replace("_", " ").title()
        ax.set_title(
            f"{metric_name} BY {cat_name.upper()}",
            color=GOLD,
            fontsize=16,
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
            "type": "composition_chart",
            "title": f"{cat_name} Composition",
            "subtitle": f"Distribution of {metric_name}",
            "image_base64": img,
            "summary": f"{str(agg.index[0]).replace('_', ' ').title()} dominates with {top_pct:.1f}%",
            "business_insight": "Larger segments represent higher contribution to total",
            "severity": "info",
            "data": {"top_segment": str(agg.index[0]), "top_share": top_pct},
        }

    def _create_quality_chart(self) -> Dict:
        """Create data quality chart"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=OBSIDIAN)

        ax1 = axes[0]
        ax1.set_facecolor(MIDNIGHT)

        missing = self.df.isnull().sum()
        missing = missing[missing > 0].sort_values(ascending=False).head(8)

        if len(missing) > 0:
            ax1.barh(
                range(len(missing)), missing.values, color=CORAL, edgecolor="white"
            )
            ax1.set_yticks(range(len(missing)))
            ax1.set_yticklabels(
                [str(c).replace("_", " ").title()[:15] for c in missing.index],
                color=FROST,
                fontsize=10,
            )
            ax1.invert_yaxis()

            for i, val in enumerate(missing.values):
                ax1.text(
                    val + 0.5, i, f"{val:,}", va="center", fontsize=10, color=FROST
                )
        else:
            ax1.text(
                0.5,
                0.5,
                "No Missing Data",
                ha="center",
                va="center",
                fontsize=14,
                color=EMERALD,
                transform=ax1.transAxes,
            )

        ax1.set_title(
            "Missing Data by Column", color=FROST, fontsize=14, fontweight="bold"
        )
        ax1.tick_params(colors=CHARCOAL)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)

        ax2 = axes[1]
        ax2.set_facecolor(MIDNIGHT)

        total_cells = len(self.df) * len(self.df.columns)
        missing_cells = self.df.isnull().sum().sum()
        completeness = (total_cells - missing_cells) / total_cells * 100

        theta = np.linspace(0, np.pi, 100)
        ax2.plot(
            np.cos(theta),
            np.sin(theta),
            color=CHARCOAL,
            linewidth=25,
            solid_capstyle="round",
        )

        fill_theta = np.linspace(0, np.pi * completeness / 100, 100)
        color = (
            EMERALD if completeness >= 90 else (ORANGE if completeness >= 70 else CORAL)
        )
        ax2.plot(
            np.cos(fill_theta),
            np.sin(fill_theta),
            color=color,
            linewidth=25,
            solid_capstyle="round",
        )

        ax2.text(
            0,
            0.3,
            f"{completeness:.1f}%",
            ha="center",
            va="center",
            fontsize=36,
            color=FROST,
            fontweight="bold",
        )
        ax2.text(
            0, 0, "DATA QUALITY", ha="center", va="center", fontsize=14, color=CHARCOAL
        )

        grade = (
            "A"
            if completeness >= 90
            else "B"
            if completeness >= 80
            else "C"
            if completeness >= 70
            else "D"
        )
        ax2.text(
            0,
            -0.25,
            f"Grade: {grade}",
            ha="center",
            va="center",
            fontsize=18,
            color=color,
            fontweight="bold",
        )

        ax2.set_xlim(-1.5, 1.5)
        ax2.set_ylim(-0.5, 1.5)
        ax2.set_title(
            "Overall Quality Score", color=FROST, fontsize=14, fontweight="bold"
        )
        ax2.axis("off")

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=OBSIDIAN, bbox_inches="tight")
        buf.seek(0)
        img = base64.b64encode(buf.read()).decode()
        plt.close()

        return {
            "type": "quality_chart",
            "title": "Data Quality Dashboard",
            "subtitle": f"Overall quality: {completeness:.1f}% (Grade: {grade})",
            "image_base64": img,
            "summary": f"{missing_cells:,} missing values out of {total_cells:,} total",
            "business_insight": "High quality data enables more reliable analysis",
            "severity": "info" if completeness >= 90 else "warning",
            "data": {"completeness": completeness, "grade": grade},
        }


def generate_ai_charts(df: pd.DataFrame, data_context: Dict = None) -> List[Dict]:
    """Generate AI-powered charts"""
    generator = AIChartGenerator(df, data_context)
    return generator.generate_charts()
