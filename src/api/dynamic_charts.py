"""
Dynamic Chart System - FIXED VERSION
====================================

Creates diverse charts with proper fallback handling
"""

import pandas as pd
from src.utils.math_utils import safe_histogram_range
import numpy as np
from typing import Dict, List, Optional, Any
import warnings
import io
import base64

warnings.filterwarnings("ignore")

# Try Plotly first, fallback to matplotlib
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Color scheme
COLORS = {
    "primary": "#D4AF37",
    "secondary": "#00CED1",
    "accent1": "#FF6B6B",
    "accent2": "#9B59B6",
    "accent3": "#2ECC71",
    "accent4": "#E67E22",
    "accent5": "#3498DB",
    "bg_dark": "#0a0a0f",
    "bg_card": "#1a1a2e",
    "text": "#ecf0f1",
    "text_muted": "#888888",
}

COLOR_LIST = [
    "#D4AF37",
    "#00CED1",
    "#FF6B6B",
    "#9B59B6",
    "#2ECC71",
    "#E67E22",
    "#3498DB",
]


class DynamicChartGenerator:
    """Generates diverse charts with fallback support"""

    def __init__(self, df: pd.DataFrame, data_context: Dict = None):
        self.df = df.copy()
        self.data_context = data_context or {}
        self.numeric_cols = []
        self.categorical_cols = []
        self.datetime_cols = []
        self._identify_columns()

    def _identify_columns(self):
        """Identify column types"""
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            col_lower = col.lower()

            # Check for datetime
            if "datetime" in dtype or any(
                kw in col_lower for kw in ["date", "time", "timestamp"]
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

    def generate_all_charts(self) -> List[Dict]:
        """Generate diverse charts based on data"""
        charts = []

        # 1. Executive Dashboard
        charts.append(self._create_executive_dashboard())

        # 2. Trend Analysis (if datetime exists)
        if self.datetime_cols and self.numeric_cols:
            charts.append(self._create_trend_chart())

        # 3. Period Changes
        if self.datetime_cols and self.numeric_cols:
            charts.append(self._create_period_changes_chart())

        # 4. Distribution Analysis
        if self.numeric_cols:
            charts.append(self._create_distribution_chart())

        # 5. Correlation Heatmap
        if len(self.numeric_cols) >= 3:
            charts.append(self._create_correlation_heatmap())

        # 6. Ranking Chart
        if self.categorical_cols and self.numeric_cols:
            charts.append(self._create_ranking_chart())

        # 7. Composition Chart
        if self.categorical_cols and self.numeric_cols:
            charts.append(self._create_composition_chart())

        # 8. Scatter Analysis
        if len(self.numeric_cols) >= 2:
            charts.append(self._create_scatter_chart())

        # 9. Box Plot Analysis
        if self.numeric_cols:
            charts.append(self._create_box_plot())

        # 10. Data Quality
        charts.append(self._create_data_quality_chart())

        return [c for c in charts if c is not None]

    def _fig_to_base64(self, fig, is_plotly=False) -> str:
        """Convert figure to base64"""
        try:
            if is_plotly and PLOTLY_AVAILABLE:
                # Try Plotly export
                try:
                    img_bytes = fig.to_image(
                        format="png", width=1200, height=700, engine="kaleido"
                    )
                    return base64.b64encode(img_bytes).decode()
                except:
                    # Fallback to HTML
                    html = fig.to_html(include_plotlyjs=False, full_html=False)
                    return base64.b64encode(html.encode()).decode()
            else:
                # Matplotlib
                buf = io.BytesIO()
                fig.savefig(
                    buf,
                    format="png",
                    dpi=120,
                    facecolor=COLORS["bg_dark"],
                    bbox_inches="tight",
                )
                buf.seek(0)
                return base64.b64encode(buf.read()).decode()
        except Exception as e:
            print(f"Error converting figure: {e}")
            return ""
        finally:
            if not is_plotly:
                plt.close(fig)

    def _create_executive_dashboard(self) -> Dict:
        """Create executive dashboard with KPI cards"""
        fig, axes = plt.subplots(2, 3, figsize=(16, 10), facecolor=COLORS["bg_dark"])
        fig.suptitle(
            "Executive Overview",
            fontsize=20,
            color=COLORS["primary"],
            fontweight="bold",
            y=0.98,
        )

        for i, col in enumerate(self.numeric_cols[:6]):
            ax = axes[i // 3, i % 3]
            ax.set_facecolor(COLORS["bg_card"])

            data = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(data) > 0:
                # Create histogram
                ax.hist(
                    data,
                    range=safe_histogram_range(data),
                    bins=30,
                    color=COLOR_LIST[i % len(COLOR_LIST)],
                    alpha=0.8,
                    edgecolor="white",
                )

                # Add mean line
                mean_val = data.mean()
                ax.axvline(
                    mean_val, color=COLORS["accent1"], linestyle="--", linewidth=2
                )

                # Add stats text
                ax.text(
                    0.02,
                    0.95,
                    f"Mean: {mean_val:.1f}\nMedian: {data.median():.1f}\nStd: {data.std():.1f}",
                    transform=ax.transAxes,
                    fontsize=9,
                    color=COLORS["text"],
                    verticalalignment="top",
                    bbox=dict(boxstyle="round", facecolor=COLORS["bg_dark"], alpha=0.8),
                )

                ax.set_title(
                    self._format_name(col),
                    color=COLORS["text"],
                    fontsize=12,
                    fontweight="bold",
                )
                ax.tick_params(colors=COLORS["text_muted"])
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        img = self._fig_to_base64(fig)

        # KPI summary
        kpi_summary = []
        for col in self.numeric_cols[:4]:
            data = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(data) > 0:
                kpi_summary.append(
                    {
                        "name": self._format_name(col),
                        "total": f"{data.sum():,.0f}",
                        "avg": f"{data.mean():,.1f}",
                        "min": f"{data.min():,.1f}",
                        "max": f"{data.max():,.1f}",
                    }
                )

        return {
            "type": "executive_dashboard",
            "title": "Executive Overview",
            "subtitle": f"{len(self.df):,} records across {len(self.df.columns)} dimensions",
            "image_base64": img,
            "summary": f"Key metrics: {', '.join([k['name'] for k in kpi_summary[:3]])}",
            "business_insight": "Dashboard shows distribution patterns for all key metrics",
            "severity": "info",
            "data": {"kpis": kpi_summary},
        }

    def _create_trend_chart(self) -> Dict:
        """Create trend chart with moving average"""
        date_col = self.datetime_cols[0]
        metric_col = self.numeric_cols[0]

        df_sorted = self.df.sort_values(date_col).dropna(subset=[date_col])
        df_sorted[metric_col] = pd.to_numeric(df_sorted[metric_col], errors="coerce")
        df_sorted = df_sorted.dropna(subset=[metric_col])

        if len(df_sorted) < 5:
            return None

        # Aggregate by date
        daily = df_sorted.groupby(date_col)[metric_col].mean().reset_index()

        fig, ax = plt.subplots(figsize=(14, 7), facecolor=COLORS["bg_dark"])
        ax.set_facecolor(COLORS["bg_card"])

        # Plot actual values
        ax.plot(
            daily[date_col],
            daily[metric_col],
            color=COLORS["primary"],
            linewidth=2,
            marker="o",
            markersize=4,
            label="Actual",
        )

        # Moving average
        window = min(7, len(daily) // 3)
        if window >= 2:
            ma = daily[metric_col].rolling(window=window, center=True).mean()
            ax.plot(
                daily[date_col],
                ma,
                color=COLORS["secondary"],
                linewidth=3,
                linestyle="--",
                label=f"{window}-period MA",
            )

        # Calculate change
        first_val = daily[metric_col].iloc[0]
        last_val = daily[metric_col].iloc[-1]
        if first_val != 0:
            change_pct = ((last_val - first_val) / abs(first_val)) * 100
            direction = "upward" if change_pct > 0 else "downward"

            # Add annotation
            color = COLORS["accent3"] if change_pct > 0 else COLORS["accent1"]
            ax.annotate(
                f"Trend: {direction} ({change_pct:+.1f}%)",
                xy=(0.02, 0.95),
                xycoords="axes fraction",
                fontsize=14,
                color=color,
                fontweight="bold",
                bbox=dict(
                    boxstyle="round",
                    facecolor=COLORS["bg_dark"],
                    edgecolor=COLORS["primary"],
                ),
            )

        ax.set_title(
            f"{self._format_name(metric_col)} Trend Analysis",
            color=COLORS["primary"],
            fontsize=16,
            fontweight="bold",
            pad=15,
        )
        ax.set_xlabel("Date", color=COLORS["text_muted"])
        ax.set_ylabel(self._format_name(metric_col), color=COLORS["text_muted"])
        ax.legend(
            facecolor=COLORS["bg_card"],
            edgecolor=COLORS["text_muted"],
            labelcolor=COLORS["text"],
        )
        ax.tick_params(colors=COLORS["text_muted"])
        ax.grid(True, alpha=0.2)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        img = self._fig_to_base64(fig)

        return {
            "type": "trend_analysis",
            "title": f"{self._format_name(metric_col)} Trend Analysis",
            "subtitle": f"Period-over-period analysis with {window}-period moving average",
            "image_base64": img,
            "summary": f"{self._format_name(metric_col)} shows {direction} trend of {abs(change_pct):.1f}%",
            "business_insight": f"Monitor this {'growth' if change_pct > 0 else 'decline'} for strategic planning",
            "severity": "info",
            "data": {"change_pct": change_pct, "direction": direction},
        }

    def _create_period_changes_chart(self) -> Dict:
        """Create period-over-period changes chart"""
        date_col = self.datetime_cols[0]
        metric_col = self.numeric_cols[0]

        df_sorted = self.df.sort_values(date_col).dropna(subset=[date_col])
        df_sorted[metric_col] = pd.to_numeric(df_sorted[metric_col], errors="coerce")
        df_sorted = df_sorted.dropna(subset=[metric_col])

        if len(df_sorted) < 3:
            return None

        # Calculate period changes
        values = df_sorted[metric_col].values
        pct_changes = (
            np.diff(values) / np.where(values[:-1] == 0, 1, np.abs(values[:-1])) * 100
        )

        # Cap extreme values for visualization
        pct_changes = np.clip(pct_changes, -100, 100)

        fig, ax = plt.subplots(figsize=(14, 7), facecolor=COLORS["bg_dark"])
        ax.set_facecolor(COLORS["bg_card"])

        # Create bar chart
        colors = [
            COLORS["accent3"] if x >= 0 else COLORS["accent1"] for x in pct_changes
        ]
        bars = ax.bar(
            range(len(pct_changes)),
            pct_changes,
            color=colors,
            edgecolor="white",
            alpha=0.8,
        )

        # Add value labels
        for bar, val in zip(bars, pct_changes):
            y_pos = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                y_pos + (2 if y_pos >= 0 else -5),
                f"{val:+.1f}%",
                ha="center",
                va="bottom" if y_pos >= 0 else "top",
                fontsize=9,
                color=COLORS["text"],
            )

        # Add zero line
        ax.axhline(y=0, color=COLORS["text_muted"], linestyle="--", linewidth=1)

        # Cumulative change
        cumulative = np.sum(pct_changes)
        ax.annotate(
            f"Cumulative: {cumulative:+.1f}%",
            xy=(0.98, 0.95),
            xycoords="axes fraction",
            fontsize=14,
            color=COLORS["primary"],
            fontweight="bold",
            ha="right",
            bbox=dict(
                boxstyle="round",
                facecolor=COLORS["bg_dark"],
                edgecolor=COLORS["primary"],
            ),
        )

        ax.set_title(
            f"{self._format_name(metric_col)} Period Changes",
            color=COLORS["primary"],
            fontsize=16,
            fontweight="bold",
            pad=15,
        )
        ax.set_xlabel("Period", color=COLORS["text_muted"])
        ax.set_ylabel("Change (%)", color=COLORS["text_muted"])
        ax.tick_params(colors=COLORS["text_muted"])
        ax.grid(True, alpha=0.2, axis="y")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        img = self._fig_to_base64(fig)

        positive_periods = int(np.sum(pct_changes > 0))
        negative_periods = int(np.sum(pct_changes < 0))

        return {
            "type": "period_comparison",
            "title": f"{self._format_name(metric_col)} Period Changes",
            "subtitle": f"{positive_periods} positive periods, {negative_periods} negative periods",
            "image_base64": img,
            "summary": f"Average change: {np.mean(pct_changes):+.1f}% per period",
            "business_insight": f"{'More periods showing growth' if positive_periods > negative_periods else 'More periods showing decline'}",
            "severity": "info",
            "data": {
                "avg_change": float(np.mean(pct_changes)),
                "positive_periods": positive_periods,
                "negative_periods": negative_periods,
                "cumulative": float(cumulative),
            },
        }

    def _create_distribution_chart(self) -> Dict:
        """Create distribution analysis chart"""
        cols_to_plot = self.numeric_cols[:4]

        fig, axes = plt.subplots(2, 2, figsize=(14, 10), facecolor=COLORS["bg_dark"])
        fig.suptitle(
            "Distribution Analysis",
            fontsize=18,
            color=COLORS["primary"],
            fontweight="bold",
            y=0.98,
        )

        for i, col in enumerate(cols_to_plot[:4]):
            ax = axes[i // 2, i % 2]
            ax.set_facecolor(COLORS["bg_card"])

            data = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(data) > 0:
                # Histogram with KDE-like appearance
                n, bins, patches = ax.hist(
                    data,
                    range=safe_histogram_range(data),
                    bins=40,
                    color=COLOR_LIST[i % len(COLOR_LIST)],
                    alpha=0.7,
                    edgecolor="white",
                    density=True,
                )

                # Add mean and median lines
                mean_val = data.mean()
                median_val = data.median()
                ax.axvline(
                    mean_val,
                    color=COLORS["accent1"],
                    linestyle="--",
                    linewidth=2,
                    label=f"Mean: {mean_val:.1f}",
                )
                ax.axvline(
                    median_val,
                    color=COLORS["accent3"],
                    linestyle="-",
                    linewidth=2,
                    label=f"Median: {median_val:.1f}",
                )

                # Skewness info
                skew = data.skew()
                skew_text = (
                    "Right-skewed"
                    if skew > 0.5
                    else "Left-skewed"
                    if skew < -0.5
                    else "Normal"
                )
                ax.text(
                    0.98,
                    0.95,
                    f"Skewness: {skew:.2f}\n{skew_text}",
                    transform=ax.transAxes,
                    fontsize=10,
                    color=COLORS["text"],
                    verticalalignment="top",
                    ha="right",
                    bbox=dict(boxstyle="round", facecolor=COLORS["bg_dark"], alpha=0.8),
                )

                ax.set_title(
                    self._format_name(col),
                    color=COLORS["text"],
                    fontsize=12,
                    fontweight="bold",
                )
                ax.legend(
                    fontsize=8, facecolor=COLORS["bg_card"], labelcolor=COLORS["text"]
                )
                ax.tick_params(colors=COLORS["text_muted"])
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        img = self._fig_to_base64(fig)

        return {
            "type": "distribution_analysis",
            "title": "Distribution Analysis",
            "subtitle": f"Histogram analysis for {len(cols_to_plot)} key metrics",
            "image_base64": img,
            "summary": "Shows distribution shape, central tendency, and spread",
            "business_insight": "Use median for skewed distributions, mean for normal distributions",
            "severity": "info",
        }

    def _create_correlation_heatmap(self) -> Dict:
        """Create correlation heatmap"""
        cols_to_plot = self.numeric_cols[:8]

        corr_matrix = self.df[cols_to_plot].corr()

        fig, ax = plt.subplots(figsize=(12, 10), facecolor=COLORS["bg_dark"])
        ax.set_facecolor(COLORS["bg_card"])

        # Create custom colormap
        from matplotlib.colors import LinearSegmentedColormap

        cmap = LinearSegmentedColormap.from_list(
            "custom", [COLORS["accent1"], COLORS["bg_card"], COLORS["primary"]]
        )

        im = ax.imshow(corr_matrix.values, cmap=cmap, vmin=-1, vmax=1, aspect="auto")

        # Add labels
        labels = [self._format_name(c) for c in cols_to_plot]
        ax.set_xticks(range(len(cols_to_plot)))
        ax.set_yticks(range(len(cols_to_plot)))
        ax.set_xticklabels(
            labels, color=COLORS["text"], fontsize=10, rotation=45, ha="right"
        )
        ax.set_yticklabels(labels, color=COLORS["text"], fontsize=10)

        # Add correlation values
        for i in range(len(cols_to_plot)):
            for j in range(len(cols_to_plot)):
                val = corr_matrix.iloc[i, j]
                color = COLORS["bg_dark"] if abs(val) > 0.5 else COLORS["text"]
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

        # Colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.ax.tick_params(colors=COLORS["text_muted"])
        cbar.set_label("Correlation", color=COLORS["text_muted"])

        ax.set_title(
            "Correlation Heatmap",
            color=COLORS["primary"],
            fontsize=16,
            fontweight="bold",
            pad=15,
        )

        plt.tight_layout()
        img = self._fig_to_base64(fig)

        # Find strongest correlations
        strong_corrs = []
        for i, col1 in enumerate(cols_to_plot):
            for j, col2 in enumerate(cols_to_plot):
                if i < j:
                    r = corr_matrix.loc[col1, col2]
                    if abs(r) >= 0.5:
                        strong_corrs.append(
                            {
                                "col1": self._format_name(col1),
                                "col2": self._format_name(col2),
                                "r": r,
                            }
                        )

        strong_corrs.sort(key=lambda x: abs(x["r"]), reverse=True)

        return {
            "type": "correlation_heatmap",
            "title": "Correlation Heatmap",
            "subtitle": f"{len(cols_to_plot)} metrics analyzed | {len(strong_corrs)} strong correlations",
            "image_base64": img,
            "summary": f"Strongest: {strong_corrs[0]['col1']} & {strong_corrs[0]['col2']} (r={strong_corrs[0]['r']:.2f})"
            if strong_corrs
            else "No strong correlations",
            "business_insight": "Red indicates negative correlation, Gold indicates positive",
            "severity": "info",
            "data": {"strong_correlations": strong_corrs[:5]},
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

        fig, ax = plt.subplots(figsize=(14, 8), facecolor=COLORS["bg_dark"])
        ax.set_facecolor(COLORS["bg_card"])

        colors = [COLORS["primary"]] + [COLORS["text_muted"]] * (len(agg) - 1)
        bars = ax.barh(
            range(len(agg)), agg.values, color=colors, edgecolor="white", height=0.7
        )

        ax.set_yticks(range(len(agg)))
        ax.set_yticklabels(
            [self._format_name(str(x)) for x in agg.index],
            color=COLORS["text"],
            fontsize=11,
        )
        ax.invert_yaxis()

        # Add value labels with percentage
        for bar, val in zip(bars, agg.values):
            pct = val / total * 100
            ax.text(
                val + agg.max() * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{val:,.0f} ({pct:.1f}%)",
                va="center",
                fontsize=10,
                color=COLORS["text"],
            )

        # Top item annotation
        top_item = agg.index[0]
        top_share = agg.iloc[0] / total * 100
        ax.annotate(
            f"TOP: {self._format_name(str(top_item))}: {top_share:.1f}%",
            xy=(agg.max() * 0.7, 0),
            fontsize=12,
            color=COLORS["primary"],
            fontweight="bold",
            bbox=dict(
                boxstyle="round",
                facecolor=COLORS["bg_dark"],
                edgecolor=COLORS["primary"],
            ),
        )

        ax.set_xlim(0, agg.max() * 1.5)
        ax.set_title(
            f"Top {self._format_name(cat_col)} by {self._format_name(metric_col)}",
            color=COLORS["primary"],
            fontsize=16,
            fontweight="bold",
            pad=15,
        )
        ax.set_xlabel(self._format_name(metric_col), color=COLORS["text_muted"])
        ax.tick_params(colors=COLORS["text_muted"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(True, alpha=0.2, axis="x")

        plt.tight_layout()
        img = self._fig_to_base64(fig)

        return {
            "type": "ranking_chart",
            "title": f"{self._format_name(cat_col)} Ranking",
            "subtitle": f"Top {len(agg)} segments by {self._format_name(metric_col)}",
            "image_base64": img,
            "summary": f"{self._format_name(str(top_item))} leads with {top_share:.1f}% share",
            "business_insight": f"Concentration: {'High' if top_share > 30 else 'Moderate' if top_share > 20 else 'Low'}",
            "severity": "info",
            "data": {"top_item": str(top_item), "top_share": top_share},
        }

    def _create_composition_chart(self) -> Dict:
        """Create composition/pie chart"""
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

        fig, ax = plt.subplots(figsize=(12, 10), facecolor=COLORS["bg_dark"])
        ax.set_facecolor(COLORS["bg_card"])

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
            autotext.set_color(COLORS["bg_dark"])
            autotext.set_fontweight("bold")
            autotext.set_fontsize(10)

        # Center text
        ax.text(
            0,
            0,
            f"Total\n{total:,.0f}",
            ha="center",
            va="center",
            fontsize=16,
            color=COLORS["text"],
            fontweight="bold",
        )

        # Legend
        legend_labels = [
            f"{self._format_name(str(label))}: {val / total * 100:.1f}%"
            for label, val in zip(agg.index, agg.values)
        ]
        ax.legend(
            wedges,
            legend_labels,
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            facecolor=COLORS["bg_card"],
            edgecolor=COLORS["text_muted"],
            labelcolor=COLORS["text"],
            fontsize=10,
        )

        ax.set_title(
            f"{self._format_name(metric_col)} by {self._format_name(cat_col)}",
            color=COLORS["primary"],
            fontsize=16,
            fontweight="bold",
            pad=15,
        )

        plt.tight_layout()
        img = self._fig_to_base64(fig)

        top_pct = agg.iloc[0] / total * 100

        return {
            "type": "composition_chart",
            "title": f"{self._format_name(cat_col)} Composition",
            "subtitle": f"Distribution of {self._format_name(metric_col)} across {len(agg)} segments",
            "image_base64": img,
            "summary": f"{self._format_name(str(agg.index[0]))} dominates with {top_pct:.1f}%",
            "business_insight": "Larger segments represent higher contribution to total",
            "severity": "info",
            "data": {"top_segment": str(agg.index[0]), "top_share": top_pct},
        }

    def _create_scatter_chart(self) -> Dict:
        """Create scatter plot with correlation"""
        col1 = self.numeric_cols[0]
        col2 = (
            self.numeric_cols[1] if len(self.numeric_cols) > 1 else self.numeric_cols[0]
        )

        data1 = pd.to_numeric(self.df[col1], errors="coerce")
        data2 = pd.to_numeric(self.df[col2], errors="coerce")
        valid = ~(data1.isna() | data2.isna())

        if valid.sum() < 10:
            return None

        # Sample if too large
        if valid.sum() > 1500:
            sample_idx = np.random.choice(valid[valid].index, 1500, replace=False)
        else:
            sample_idx = valid[valid].index

        fig, ax = plt.subplots(figsize=(14, 10), facecolor=COLORS["bg_dark"])
        ax.set_facecolor(COLORS["bg_card"])

        ax.scatter(
            data1[sample_idx],
            data2[sample_idx],
            c=COLORS["primary"],
            alpha=0.6,
            s=50,
            edgecolors=COLORS["bg_dark"],
        )

        # Trend line
        z = np.polyfit(data1[sample_idx], data2[sample_idx], 1)
        p = np.poly1d(z)
        x_line = np.linspace(data1[sample_idx].min(), data1[sample_idx].max(), 100)
        ax.plot(
            x_line,
            p(x_line),
            color=COLORS["accent1"],
            linewidth=2,
            linestyle="--",
            label="Trend",
        )

        # Correlation
        r = data1[valid].corr(data2[valid])
        strength = (
            "Strong" if abs(r) >= 0.7 else "Moderate" if abs(r) >= 0.5 else "Weak"
        )
        direction = "positive" if r > 0 else "negative"

        ax.annotate(
            f"r = {r:.3f}\n{strength} {direction}",
            xy=(0.05, 0.95),
            xycoords="axes fraction",
            fontsize=14,
            color=COLORS["primary"],
            fontweight="bold",
            bbox=dict(
                boxstyle="round",
                facecolor=COLORS["bg_dark"],
                edgecolor=COLORS["primary"],
            ),
            verticalalignment="top",
        )

        ax.set_title(
            f"{self._format_name(col1)} vs {self._format_name(col2)}",
            color=COLORS["primary"],
            fontsize=16,
            fontweight="bold",
            pad=15,
        )
        ax.set_xlabel(self._format_name(col1), color=COLORS["text_muted"])
        ax.set_ylabel(self._format_name(col2), color=COLORS["text_muted"])
        ax.legend(
            facecolor=COLORS["bg_card"],
            edgecolor=COLORS["text_muted"],
            labelcolor=COLORS["text"],
        )
        ax.tick_params(colors=COLORS["text_muted"])
        ax.grid(True, alpha=0.2)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        plt.tight_layout()
        img = self._fig_to_base64(fig)

        return {
            "type": "scatter_analysis",
            "title": f"{self._format_name(col1)} vs {self._format_name(col2)}",
            "subtitle": f"{strength} {direction} correlation (r={r:.2f})",
            "image_base64": img,
            "summary": f"{strength} relationship detected between metrics",
            "business_insight": "Optimize both metrics together for compound effect",
            "severity": "info",
            "data": {"r": r, "strength": strength},
        }

    def _create_box_plot(self) -> Dict:
        """Create box plot for outlier analysis"""
        cols_to_plot = self.numeric_cols[:6]

        fig, ax = plt.subplots(figsize=(14, 8), facecolor=COLORS["bg_dark"])
        ax.set_facecolor(COLORS["bg_card"])

        # Normalize data for comparison
        data_list = []
        labels = []
        for col in cols_to_plot:
            data = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(data) > 0:
                # Normalize to 0-100 range for comparison
                min_val, max_val = data.min(), data.max()
                if max_val > min_val:
                    normalized = (data - min_val) / (max_val - min_val) * 100
                    data_list.append(normalized)
                    labels.append(self._format_name(col))

        if data_list:
            bp = ax.boxplot(
                data_list, labels=labels, patch_artist=True, showfliers=True
            )

            for i, patch in enumerate(bp["boxes"]):
                patch.set_facecolor(COLOR_LIST[i % len(COLOR_LIST)])
                patch.set_alpha(0.7)

            for element in ["whiskers", "fliers", "means", "medians", "caps"]:
                plt.setp(bp[element], color=COLORS["text"])

        ax.set_title(
            "Outlier Analysis (Normalized)",
            color=COLORS["primary"],
            fontsize=16,
            fontweight="bold",
            pad=15,
        )
        ax.set_ylabel("Normalized Value (0-100)", color=COLORS["text_muted"])
        ax.tick_params(colors=COLORS["text_muted"])
        ax.set_xticklabels(labels, rotation=30, ha="right")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(True, alpha=0.2, axis="y")

        plt.tight_layout()
        img = self._fig_to_base64(fig)

        return {
            "type": "box_plot",
            "title": "Outlier Analysis",
            "subtitle": f"Box plots showing distribution and outliers for {len(cols_to_plot)} metrics",
            "image_base64": img,
            "summary": "Points outside boxes indicate outliers",
            "business_insight": "Investigate outliers for data quality or genuine anomalies",
            "severity": "info",
        }

    def _create_data_quality_chart(self) -> Dict:
        """Create data quality chart"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=COLORS["bg_dark"])

        # Missing data
        ax1 = axes[0]
        ax1.set_facecolor(COLORS["bg_card"])

        missing = self.df.isnull().sum()
        missing = missing[missing > 0].sort_values(ascending=False).head(10)

        if len(missing) > 0:
            ax1.barh(
                range(len(missing)),
                missing.values,
                color=COLORS["accent1"],
                edgecolor="white",
            )
            ax1.set_yticks(range(len(missing)))
            ax1.set_yticklabels(
                [self._format_name(c) for c in missing.index],
                color=COLORS["text"],
                fontsize=10,
            )
            ax1.invert_yaxis()

            for i, val in enumerate(missing.values):
                ax1.text(
                    val + 0.5,
                    i,
                    f"{val}",
                    va="center",
                    fontsize=10,
                    color=COLORS["text"],
                )

        ax1.set_title(
            "Missing Data", color=COLORS["text"], fontsize=14, fontweight="bold"
        )
        ax1.tick_params(colors=COLORS["text_muted"])
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)

        # Completeness gauge
        ax2 = axes[1]
        ax2.set_facecolor(COLORS["bg_card"])

        total_cells = len(self.df) * len(self.df.columns)
        missing_cells = self.df.isnull().sum().sum()
        completeness = (total_cells - missing_cells) / total_cells * 100

        # Create gauge
        theta = np.linspace(0, np.pi, 100)
        r = 1
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        ax2.plot(x, y, color=COLORS["text_muted"], linewidth=20, solid_capstyle="round")

        # Fill based on completeness
        fill_theta = np.linspace(0, np.pi * completeness / 100, 100)
        fill_x = r * np.cos(fill_theta)
        fill_y = r * np.sin(fill_theta)

        color = (
            COLORS["accent3"]
            if completeness >= 90
            else COLORS["accent4"]
            if completeness >= 70
            else COLORS["accent1"]
        )
        ax2.plot(fill_x, fill_y, color=color, linewidth=20, solid_capstyle="round")

        # Center text
        ax2.text(
            0,
            0.3,
            f"{completeness:.1f}%",
            ha="center",
            va="center",
            fontsize=32,
            color=COLORS["text"],
            fontweight="bold",
        )
        ax2.text(
            0,
            0,
            "Completeness",
            ha="center",
            va="center",
            fontsize=14,
            color=COLORS["text_muted"],
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
            -0.3,
            f"Grade: {grade}",
            ha="center",
            va="center",
            fontsize=16,
            color=color,
            fontweight="bold",
        )

        ax2.set_xlim(-1.5, 1.5)
        ax2.set_ylim(-0.5, 1.5)
        ax2.set_title(
            "Data Quality", color=COLORS["text"], fontsize=14, fontweight="bold"
        )
        ax2.axis("off")

        plt.tight_layout()
        img = self._fig_to_base64(fig)

        return {
            "type": "data_quality",
            "title": "Data Quality Dashboard",
            "subtitle": f"Overall quality: {completeness:.1f}% (Grade: {grade})",
            "image_base64": img,
            "summary": f"{missing_cells:,} missing values out of {total_cells:,} total cells",
            "business_insight": "High quality data enables more reliable analysis",
            "severity": "info" if completeness >= 90 else "warning",
            "data": {"completeness": completeness, "grade": grade},
        }

    def _format_name(self, name: str) -> str:
        """Format column name"""
        return str(name).replace("_", " ").replace("-", " ").title()


def generate_dynamic_charts(df: pd.DataFrame, data_context: Dict = None) -> List[Dict]:
    """Generate dynamic charts"""
    generator = DynamicChartGenerator(df, data_context)
    return generator.generate_all_charts()
