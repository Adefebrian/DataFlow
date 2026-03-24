"""
Animated Dynamic Charts with Plotly
===================================

Creates interactive, animated charts that adapt to data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import json
import base64
import io
import warnings

warnings.filterwarnings("ignore")

# Import plotly
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

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

COLOR_SEQUENCE = [
    "#D4AF37",
    "#00CED1",
    "#FF6B6B",
    "#9B59B6",
    "#2ECC71",
    "#E67E22",
    "#3498DB",
    "#1ABC9C",
]


class AnimatedChartGenerator:
    """Creates animated, interactive charts with Plotly"""

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
        """Generate all animated charts"""
        charts = []

        # 1. Animated Executive Dashboard
        charts.append(self._create_animated_dashboard())

        # 2. Animated Trend with Slider
        if self.datetime_cols and self.numeric_cols:
            charts.append(self._create_animated_trend())

        # 3. Animated Bar Race
        if self.categorical_cols and self.numeric_cols:
            charts.append(self._create_animated_bar_race())

        # 4. Animated Scatter with Animation Frame
        if len(self.numeric_cols) >= 2:
            charts.append(self._create_animated_scatter())

        # 5. Animated Distribution
        if self.numeric_cols:
            charts.append(self._create_animated_distribution())

        # 6. Animated Heatmap
        if len(self.numeric_cols) >= 3:
            charts.append(self._create_animated_heatmap())

        # 7. Animated Treemap
        if self.categorical_cols and self.numeric_cols:
            charts.append(self._create_animated_treemap())

        # 8. Animated Sunburst
        if len(self.categorical_cols) >= 2 and self.numeric_cols:
            charts.append(self._create_animated_sunburst())

        # 9. Animated Waterfall
        if self.categorical_cols and self.numeric_cols:
            charts.append(self._create_animated_waterfall())

        # 10. Data Quality Animated
        charts.append(self._create_animated_quality())

        return [c for c in charts if c is not None]

    def _create_animated_dashboard(self) -> Dict:
        """Create animated executive dashboard"""
        if not PLOTLY_AVAILABLE:
            return None

        fig = make_subplots(
            rows=2,
            cols=3,
            subplot_titles=[self._format_name(c) for c in self.numeric_cols[:6]],
            vertical_spacing=0.12,
            horizontal_spacing=0.08,
        )

        for i, col in enumerate(self.numeric_cols[:6]):
            row = (i // 3) + 1
            col_pos = (i % 3) + 1

            data = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(data) > 0:
                # Animated histogram with frames
                fig.add_trace(
                    go.Histogram(
                        x=data,
                        name=self._format_name(col),
                        marker_color=COLOR_SEQUENCE[i % len(COLOR_SEQUENCE)],
                        opacity=0.8,
                        showlegend=False,
                        nbinsx=30,
                    ),
                    row=row,
                    col=col_pos,
                )

                # Add mean line with animation
                mean_val = data.mean()
                fig.add_vline(
                    x=mean_val,
                    line_dash="dash",
                    line_color=COLORS["accent1"],
                    line_width=2,
                    row=row,
                    col=col_pos,
                )

        fig.update_layout(
            title=dict(
                text="Executive Overview - Key Metrics",
                font=dict(size=24, color=COLORS["primary"]),
                x=0.5,
            ),
            paper_bgcolor=COLORS["bg_dark"],
            plot_bgcolor=COLORS["bg_card"],
            font=dict(color=COLORS["text"], size=12),
            height=700,
            showlegend=False,
            hovermode="closest",
        )

        # Add animation config
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    buttons=[
                        dict(
                            label="Play",
                            method="animate",
                            args=[
                                None,
                                {
                                    "frame": {"duration": 500, "redraw": True},
                                    "fromcurrent": True,
                                },
                            ],
                        ),
                        dict(
                            label="Pause",
                            method="animate",
                            args=[
                                [None],
                                {
                                    "frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                },
                            ],
                        ),
                    ],
                    x=0.1,
                    y=1.15,
                )
            ]
        )

        html = fig.to_html(include_plotlyjs="cdn", full_html=False)

        # KPI summary
        kpis = []
        for col in self.numeric_cols[:4]:
            data = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(data) > 0:
                kpis.append(
                    {
                        "name": self._format_name(col),
                        "total": f"{data.sum():,.0f}",
                        "avg": f"{data.mean():,.1f}",
                        "trend": "up" if data.iloc[-1] > data.iloc[0] else "down",
                    }
                )

        return {
            "type": "animated_dashboard",
            "title": "Executive Dashboard",
            "subtitle": f"{len(self.df):,} records analyzed",
            "html_content": html,
            "summary": f"Interactive dashboard with {len(self.numeric_cols[:6])} key metrics",
            "business_insight": "Click and drag to zoom, hover for details",
            "severity": "info",
            "data": {"kpis": kpis},
            "is_interactive": True,
        }

    def _create_animated_trend(self) -> Dict:
        """Create animated trend chart with slider"""
        if not PLOTLY_AVAILABLE or not self.datetime_cols:
            return None

        date_col = self.datetime_cols[0]
        metric_col = self.numeric_cols[0]

        df_sorted = self.df.sort_values(date_col).dropna(subset=[date_col])
        df_sorted[metric_col] = pd.to_numeric(df_sorted[metric_col], errors="coerce")
        df_sorted = df_sorted.dropna(subset=[metric_col])

        if len(df_sorted) < 5:
            return None

        # Aggregate by date
        daily = (
            df_sorted.groupby(date_col)[metric_col]
            .agg(["mean", "sum", "count"])
            .reset_index()
        )

        fig = go.Figure()

        # Main line with animation
        fig.add_trace(
            go.Scatter(
                x=daily[date_col],
                y=daily["mean"],
                mode="lines+markers",
                name="Average",
                line=dict(color=COLORS["primary"], width=3),
                marker=dict(size=8, color=COLORS["primary"]),
                hovertemplate="<b>%{x}</b><br>Value: %{y:,.2f}<br>Count: %{customdata}<extra></extra>",
                customdata=daily["count"],
            )
        )

        # Add range slider
        fig.update_xaxes(
            rangeslider=dict(visible=True, bgcolor=COLORS["bg_card"]),
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=7, label="1W", step="day", stepmode="backward"),
                        dict(count=1, label="1M", step="month", stepmode="backward"),
                        dict(count=3, label="3M", step="month", stepmode="backward"),
                        dict(count=6, label="6M", step="month", stepmode="backward"),
                        dict(step="all", label="All"),
                    ]
                ),
                bgcolor=COLORS["bg_card"],
                font=dict(color=COLORS["text"]),
            ),
        )

        # Calculate trend
        first_val = daily["mean"].iloc[0]
        last_val = daily["mean"].iloc[-1]
        change_pct = (
            ((last_val - first_val) / abs(first_val)) * 100 if first_val != 0 else 0
        )

        fig.update_layout(
            title=dict(
                text=f"{self._format_name(metric_col)} Trend Analysis",
                font=dict(size=20, color=COLORS["primary"]),
                x=0.5,
            ),
            paper_bgcolor=COLORS["bg_dark"],
            plot_bgcolor=COLORS["bg_card"],
            font=dict(color=COLORS["text"]),
            xaxis=dict(gridcolor=COLORS["text_muted"]),
            yaxis=dict(gridcolor=COLORS["text_muted"]),
            height=600,
            hovermode="x unified",
            annotations=[
                dict(
                    text=f"Overall Change: {change_pct:+.1f}%",
                    xref="paper",
                    yref="paper",
                    x=0.02,
                    y=0.98,
                    showarrow=False,
                    font=dict(
                        size=16,
                        color=COLORS["accent3"]
                        if change_pct > 0
                        else COLORS["accent1"],
                    ),
                    bgcolor=COLORS["bg_card"],
                    bordercolor=COLORS["primary"],
                    borderwidth=1,
                )
            ],
        )

        html = fig.to_html(include_plotlyjs="cdn", full_html=False)

        return {
            "type": "animated_trend",
            "title": f"{self._format_name(metric_col)} Trend",
            "subtitle": f"Interactive trend with range slider | Change: {change_pct:+.1f}%",
            "html_content": html,
            "summary": f"Trend shows {change_pct:+.1f}% change over the period",
            "business_insight": "Use the range slider to zoom into specific periods",
            "severity": "info",
            "data": {"change_pct": change_pct},
            "is_interactive": True,
        }

    def _create_animated_bar_race(self) -> Dict:
        """Create animated bar race chart"""
        if not PLOTLY_AVAILABLE or not self.categorical_cols:
            return None

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

        fig = go.Figure()

        # Create bars with animation
        for i, (cat, val) in enumerate(agg.items()):
            fig.add_trace(
                go.Bar(
                    x=[val],
                    y=[self._format_name(str(cat))],
                    orientation="h",
                    name=self._format_name(str(cat)),
                    marker_color=COLOR_SEQUENCE[i % len(COLOR_SEQUENCE)],
                    text=[f"{val:,.0f}"],
                    textposition="outside",
                    hovertemplate=f"<b>{self._format_name(str(cat))}</b><br>Value: {val:,.0f}<extra></extra>",
                )
            )

        # Sort by value
        fig.update_layout(
            title=dict(
                text=f"Top {len(agg)} {self._format_name(cat_col)} by {self._format_name(metric_col)}",
                font=dict(size=20, color=COLORS["primary"]),
                x=0.5,
            ),
            paper_bgcolor=COLORS["bg_dark"],
            plot_bgcolor=COLORS["bg_card"],
            font=dict(color=COLORS["text"]),
            xaxis=dict(gridcolor=COLORS["text_muted"]),
            yaxis=dict(autorange="reversed"),
            height=600,
            showlegend=False,
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    buttons=[
                        dict(
                            label="Play",
                            method="animate",
                            args=[
                                None,
                                {
                                    "frame": {"duration": 1000, "redraw": True},
                                    "fromcurrent": True,
                                },
                            ],
                        ),
                        dict(
                            label="Pause",
                            method="animate",
                            args=[
                                [None],
                                {
                                    "frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                },
                            ],
                        ),
                    ],
                )
            ],
        )

        html = fig.to_html(include_plotlyjs="cdn", full_html=False)

        return {
            "type": "animated_bar_race",
            "title": f"{self._format_name(cat_col)} Ranking",
            "subtitle": f"Animated ranking by {self._format_name(metric_col)}",
            "html_content": html,
            "summary": f"{self._format_name(str(agg.index[0]))} leads the ranking",
            "business_insight": "Click Play to animate the ranking",
            "severity": "info",
            "is_interactive": True,
        }

    def _create_animated_scatter(self) -> Dict:
        """Create animated scatter plot"""
        if not PLOTLY_AVAILABLE or len(self.numeric_cols) < 2:
            return None

        col1 = self.numeric_cols[0]
        col2 = self.numeric_cols[1]

        # Sample data
        df_sample = self.df[[col1, col2]].dropna()
        if len(df_sample) > 1500:
            df_sample = df_sample.sample(1500, random_state=42)

        # Add color dimension if available
        color_col = self.categorical_cols[0] if self.categorical_cols else None
        if color_col and color_col in self.df.columns:
            df_sample[color_col] = self.df.loc[df_sample.index, color_col]

        fig = go.Figure()

        if color_col:
            for i, cat in enumerate(df_sample[color_col].unique()[:8]):
                mask = df_sample[color_col] == cat
                fig.add_trace(
                    go.Scatter(
                        x=df_sample.loc[mask, col1],
                        y=df_sample.loc[mask, col2],
                        mode="markers",
                        name=self._format_name(str(cat)),
                        marker=dict(
                            size=10,
                            color=COLOR_SEQUENCE[i % len(COLOR_SEQUENCE)],
                            opacity=0.7,
                            line=dict(width=1, color=COLORS["bg_dark"]),
                        ),
                        hovertemplate=f"<b>{self._format_name(str(cat))}</b><br>{col1}: %{{x:,.2f}}<br>{col2}: %{{y:,.2f}}<extra></extra>",
                    )
                )
        else:
            fig.add_trace(
                go.Scatter(
                    x=df_sample[col1],
                    y=df_sample[col2],
                    mode="markers",
                    marker=dict(
                        size=10,
                        color=COLORS["primary"],
                        opacity=0.7,
                        line=dict(width=1, color=COLORS["bg_dark"]),
                    ),
                    hovertemplate=f"{col1}: %{{x:,.2f}}<br>{col2}: %{{y:,.2f}}<extra></extra>",
                )
            )

        # Add trend line
        z = np.polyfit(df_sample[col1], df_sample[col2], 1)
        p = np.poly1d(z)
        x_line = np.linspace(df_sample[col1].min(), df_sample[col1].max(), 100)

        fig.add_trace(
            go.Scatter(
                x=x_line,
                y=p(x_line),
                mode="lines",
                name="Trend",
                line=dict(color=COLORS["accent1"], width=3, dash="dash"),
            )
        )

        # Correlation
        r = df_sample[col1].corr(df_sample[col2])

        fig.update_layout(
            title=dict(
                text=f"{self._format_name(col1)} vs {self._format_name(col2)}",
                font=dict(size=20, color=COLORS["primary"]),
                x=0.5,
            ),
            paper_bgcolor=COLORS["bg_dark"],
            plot_bgcolor=COLORS["bg_card"],
            font=dict(color=COLORS["text"]),
            xaxis=dict(gridcolor=COLORS["text_muted"], title=self._format_name(col1)),
            yaxis=dict(gridcolor=COLORS["text_muted"], title=self._format_name(col2)),
            height=600,
            annotations=[
                dict(
                    text=f"Correlation: r = {r:.3f}",
                    xref="paper",
                    yref="paper",
                    x=0.02,
                    y=0.98,
                    showarrow=False,
                    font=dict(size=16, color=COLORS["primary"]),
                    bgcolor=COLORS["bg_card"],
                    bordercolor=COLORS["primary"],
                )
            ],
        )

        html = fig.to_html(include_plotlyjs="cdn", full_html=False)

        return {
            "type": "animated_scatter",
            "title": f"{self._format_name(col1)} vs {self._format_name(col2)}",
            "subtitle": f"Interactive scatter plot | Correlation: {r:.3f}",
            "html_content": html,
            "summary": f"{'Strong' if abs(r) > 0.7 else 'Moderate' if abs(r) > 0.5 else 'Weak'} correlation detected",
            "business_insight": "Click and drag to zoom, double-click to reset",
            "severity": "info",
            "data": {"r": r},
            "is_interactive": True,
        }

    def _create_animated_distribution(self) -> Dict:
        """Create animated distribution chart"""
        if not PLOTLY_AVAILABLE:
            return None

        cols_to_plot = self.numeric_cols[:4]

        fig = go.Figure()

        for i, col in enumerate(cols_to_plot):
            data = pd.to_numeric(self.df[col], errors="coerce").dropna()
            if len(data) > 0:
                fig.add_trace(
                    go.Violin(
                        y=data,
                        name=self._format_name(col),
                        box_visible=True,
                        meanline_visible=True,
                        fillcolor=COLOR_SEQUENCE[i % len(COLOR_SEQUENCE)],
                        opacity=0.7,
                        line_color=COLORS["text"],
                        hoverinfo="y+name",
                    )
                )

        fig.update_layout(
            title=dict(
                text="Distribution Analysis",
                font=dict(size=20, color=COLORS["primary"]),
                x=0.5,
            ),
            paper_bgcolor=COLORS["bg_dark"],
            plot_bgcolor=COLORS["bg_card"],
            font=dict(color=COLORS["text"]),
            yaxis=dict(gridcolor=COLORS["text_muted"]),
            height=600,
            showlegend=True,
            legend=dict(bgcolor=COLORS["bg_card"]),
        )

        html = fig.to_html(include_plotlyjs="cdn", full_html=False)

        return {
            "type": "animated_distribution",
            "title": "Distribution Analysis",
            "subtitle": f"Violin plots for {len(cols_to_plot)} metrics",
            "html_content": html,
            "summary": "Shows distribution shape, median, and quartiles",
            "business_insight": "Hover over violins to see distribution details",
            "severity": "info",
            "is_interactive": True,
        }

    def _create_animated_heatmap(self) -> Dict:
        """Create animated correlation heatmap"""
        if not PLOTLY_AVAILABLE or len(self.numeric_cols) < 3:
            return None

        cols_to_plot = self.numeric_cols[:8]
        corr_matrix = self.df[cols_to_plot].corr()

        fig = go.Figure(
            data=go.Heatmap(
                z=corr_matrix.values,
                x=[self._format_name(c) for c in cols_to_plot],
                y=[self._format_name(c) for c in cols_to_plot],
                colorscale=[
                    [0, COLORS["accent1"]],
                    [0.5, COLORS["bg_card"]],
                    [1, COLORS["primary"]],
                ],
                zmin=-1,
                zmax=1,
                text=np.round(corr_matrix.values, 2),
                texttemplate="%{text}",
                textfont=dict(size=12),
                hoverongaps=False,
                hovertemplate="<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.3f}<extra></extra>",
            )
        )

        fig.update_layout(
            title=dict(
                text="Correlation Heatmap",
                font=dict(size=20, color=COLORS["primary"]),
                x=0.5,
            ),
            paper_bgcolor=COLORS["bg_dark"],
            font=dict(color=COLORS["text"]),
            height=600,
            xaxis=dict(tickangle=45),
            yaxis=dict(autorange="reversed"),
        )

        html = fig.to_html(include_plotlyjs="cdn", full_html=False)

        return {
            "type": "animated_heatmap",
            "title": "Correlation Heatmap",
            "subtitle": f"{len(cols_to_plot)} metrics analyzed",
            "html_content": html,
            "summary": "Interactive correlation matrix",
            "business_insight": "Hover to see exact correlation values",
            "severity": "info",
            "is_interactive": True,
        }

    def _create_animated_treemap(self) -> Dict:
        """Create animated treemap"""
        if not PLOTLY_AVAILABLE or not self.categorical_cols:
            return None

        cat_col = self.categorical_cols[0]
        metric_col = self.numeric_cols[0]

        agg = (
            self.df.groupby(cat_col)[metric_col]
            .sum()
            .sort_values(ascending=False)
            .head(12)
        )

        if len(agg) < 2:
            return None

        fig = go.Figure(
            go.Treemap(
                labels=[self._format_name(str(x)) for x in agg.index],
                parents=[""] * len(agg),
                values=agg.values,
                textinfo="label+value+percent parent",
                marker=dict(colors=COLOR_SEQUENCE[: len(agg)], colorscale="Viridis"),
                textfont=dict(size=14),
                hovertemplate="<b>%{label}</b><br>Value: %{value:,.0f}<br>Share: %{percentParent:.1%}<extra></extra>",
            )
        )

        fig.update_layout(
            title=dict(
                text=f"{self._format_name(metric_col)} by {self._format_name(cat_col)}",
                font=dict(size=20, color=COLORS["primary"]),
                x=0.5,
            ),
            paper_bgcolor=COLORS["bg_dark"],
            font=dict(color=COLORS["text"]),
            height=600,
        )

        html = fig.to_html(include_plotlyjs="cdn", full_html=False)

        return {
            "type": "animated_treemap",
            "title": f"{self._format_name(cat_col)} Composition",
            "subtitle": f"Treemap of {self._format_name(metric_col)}",
            "html_content": html,
            "summary": "Interactive treemap showing segment composition",
            "business_insight": "Click to drill down into segments",
            "severity": "info",
            "is_interactive": True,
        }

    def _create_animated_sunburst(self) -> Dict:
        """Create animated sunburst chart"""
        if not PLOTLY_AVAILABLE or len(self.categorical_cols) < 2:
            return None

        cat1 = self.categorical_cols[0]
        cat2 = self.categorical_cols[1]
        metric_col = self.numeric_cols[0]

        # Aggregate data
        agg = self.df.groupby([cat1, cat2])[metric_col].sum().reset_index()
        agg = agg.head(30)  # Limit for readability

        fig = go.Figure(
            go.Sunburst(
                labels=[
                    f"{self._format_name(str(row[cat2]))}" for _, row in agg.iterrows()
                ],
                parents=[
                    self._format_name(str(row[cat1])) for _, row in agg.iterrows()
                ],
                values=agg[metric_col].values,
                branchvalues="total",
                marker=dict(colors=COLOR_SEQUENCE[: len(agg)]),
                hovertemplate="<b>%{label}</b><br>Value: %{value:,.0f}<extra></extra>",
            )
        )

        # Add parent labels
        parent_labels = agg[cat1].unique()
        for parent in parent_labels:
            fig.add_trace(
                go.Sunburst(
                    labels=[self._format_name(str(parent))],
                    parents=[""],
                    values=[0],
                    branchvalues="total",
                    marker=dict(colors=[COLORS["bg_card"]]),
                    hoverinfo="skip",
                )
            )

        fig.update_layout(
            title=dict(
                text=f"{self._format_name(metric_col)} by {self._format_name(cat1)} and {self._format_name(cat2)}",
                font=dict(size=20, color=COLORS["primary"]),
                x=0.5,
            ),
            paper_bgcolor=COLORS["bg_dark"],
            font=dict(color=COLORS["text"]),
            height=600,
        )

        html = fig.to_html(include_plotlyjs="cdn", full_html=False)

        return {
            "type": "animated_sunburst",
            "title": "Hierarchical Analysis",
            "subtitle": f"{self._format_name(cat1)} and {self._format_name(cat2)} breakdown",
            "html_content": html,
            "summary": "Interactive sunburst showing hierarchical relationships",
            "business_insight": "Click segments to zoom in",
            "severity": "info",
            "is_interactive": True,
        }

    def _create_animated_waterfall(self) -> Dict:
        """Create animated waterfall chart"""
        if not PLOTLY_AVAILABLE or not self.categorical_cols:
            return None

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

        fig = go.Figure(
            go.Waterfall(
                x=[self._format_name(str(x)) for x in agg.index],
                y=agg.values,
                measure=["relative"] * len(agg),
                text=[f"{v / total * 100:.1f}%" for v in agg.values],
                textposition="outside",
                connector=dict(line=dict(color=COLORS["text_muted"])),
                decreasing=dict(marker=dict(color=COLORS["accent1"])),
                increasing=dict(marker=dict(color=COLORS["accent3"])),
                totals=dict(marker=dict(color=COLORS["primary"])),
                hovertemplate="<b>%{x}</b><br>Value: %{y:,.0f}<extra></extra>",
            )
        )

        fig.update_layout(
            title=dict(
                text=f"{self._format_name(metric_col)} by {self._format_name(cat_col)}",
                font=dict(size=20, color=COLORS["primary"]),
                x=0.5,
            ),
            paper_bgcolor=COLORS["bg_dark"],
            plot_bgcolor=COLORS["bg_card"],
            font=dict(color=COLORS["text"]),
            xaxis=dict(gridcolor=COLORS["text_muted"]),
            yaxis=dict(gridcolor=COLORS["text_muted"]),
            height=600,
        )

        html = fig.to_html(include_plotlyjs="cdn", full_html=False)

        return {
            "type": "animated_waterfall",
            "title": f"{self._format_name(cat_col)} Waterfall",
            "subtitle": f"Contribution analysis of {self._format_name(metric_col)}",
            "html_content": html,
            "summary": f"Shows contribution of each {self._format_name(cat_col).lower()}",
            "business_insight": "Larger bars represent higher contribution",
            "severity": "info",
            "is_interactive": True,
        }

    def _create_animated_quality(self) -> Dict:
        """Create animated data quality dashboard"""
        if not PLOTLY_AVAILABLE:
            return None

        # Calculate quality metrics
        total_cells = len(self.df) * len(self.df.columns)
        missing_cells = self.df.isnull().sum().sum()
        completeness = (total_cells - missing_cells) / total_cells * 100

        missing = self.df.isnull().sum()
        missing = missing[missing > 0].sort_values(ascending=False).head(10)

        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=["Missing Data by Column", "Data Completeness"],
            specs=[[{"type": "bar"}, {"type": "indicator"}]],
        )

        if len(missing) > 0:
            fig.add_trace(
                go.Bar(
                    x=[self._format_name(c) for c in missing.index],
                    y=missing.values,
                    marker_color=COLORS["accent1"],
                    name="Missing",
                    hovertemplate="<b>%{x}</b><br>Missing: %{y}<extra></extra>",
                ),
                row=1,
                col=1,
            )

        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=completeness,
                title={"text": "Completeness %", "font": {"color": COLORS["text"]}},
                delta={"reference": 90, "increasing": {"color": COLORS["accent3"]}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": COLORS["text"]},
                    "bar": {"color": COLORS["primary"]},
                    "bgcolor": COLORS["bg_card"],
                    "steps": [
                        {"range": [0, 70], "color": COLORS["accent1"]},
                        {"range": [70, 90], "color": COLORS["accent4"]},
                        {"range": [90, 100], "color": COLORS["accent3"]},
                    ],
                    "threshold": {
                        "line": {"color": COLORS["text"], "width": 4},
                        "thickness": 0.75,
                        "value": 90,
                    },
                },
            ),
            row=1,
            col=2,
        )

        fig.update_layout(
            title=dict(
                text="Data Quality Dashboard",
                font=dict(size=20, color=COLORS["primary"]),
                x=0.5,
            ),
            paper_bgcolor=COLORS["bg_dark"],
            plot_bgcolor=COLORS["bg_card"],
            font=dict(color=COLORS["text"]),
            height=500,
            showlegend=False,
        )

        html = fig.to_html(include_plotlyjs="cdn", full_html=False)

        grade = (
            "A"
            if completeness >= 90
            else "B"
            if completeness >= 80
            else "C"
            if completeness >= 70
            else "D"
        )

        return {
            "type": "animated_quality",
            "title": "Data Quality Dashboard",
            "subtitle": f"Overall quality: {completeness:.1f}% (Grade: {grade})",
            "html_content": html,
            "summary": f"{missing_cells:,} missing values out of {total_cells:,} total cells",
            "business_insight": "Hover for detailed quality metrics",
            "severity": "info" if completeness >= 90 else "warning",
            "data": {"completeness": completeness, "grade": grade},
            "is_interactive": True,
        }

    def _format_name(self, name: str) -> str:
        """Format column name"""
        return str(name).replace("_", " ").replace("-", " ").title()


def generate_animated_charts(df: pd.DataFrame, data_context: Dict = None) -> List[Dict]:
    """Generate animated charts"""
    generator = AnimatedChartGenerator(df, data_context)
    return generator.generate_all_charts()
