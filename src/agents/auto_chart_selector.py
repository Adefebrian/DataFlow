from src.models.types import DataProfile, ChartSpec
from typing import Literal


class AutoChartSelectorAgent:
    def select_charts(
        self,
        profile: DataProfile,
        max_count: int = 12,
    ) -> list[ChartSpec]:
        charts: list[ChartSpec] = []
        seen_keys: set[frozenset] = set()

        def add_chart(spec: ChartSpec, key: frozenset) -> None:
            if key not in seen_keys:
                seen_keys.add(key)
                charts.append(spec)

        for col in profile.columns:
            if col.dtype == "datetime":
                numeric_cols = [c for c in profile.columns if c.dtype == "numeric"][:3]
                for num_col in numeric_cols:
                    add_chart(
                        ChartSpec(
                            type="line",
                            x=col.name,
                            y=num_col.name,
                            title=f"{num_col.name} over time",
                        ),
                        frozenset({f"line:{col.name}:{num_col.name}"}),
                    )
            elif col.dtype == "numeric":
                add_chart(
                    ChartSpec(
                        type="histogram",
                        x=col.name,
                        title=f"Distribution of {col.name}",
                        bins=20,
                    ),
                    frozenset({f"hist:{col.name}"}),
                )
            elif col.dtype == "categorical" and col.unique_count <= 15:
                add_chart(
                    ChartSpec(
                        type="bar",
                        x=col.name,
                        y="count",
                        title=f"{col.name} frequency",
                    ),
                    frozenset({f"bar:{col.name}"}),
                )

        numeric_col_names = [c.name for c in profile.columns if c.dtype == "numeric"]
        if len(numeric_col_names) >= 3:
            add_chart(
                ChartSpec(
                    type="heatmap",
                    columns=numeric_col_names,
                    title="Correlation matrix",
                ),
                frozenset({"heatmap:all_numeric"}),
            )

        for pair in profile.high_correlation_pairs:
            key = frozenset(
                {
                    f"scatter:{min(pair['col_a'], pair['col_b'])}:{max(pair['col_a'], pair['col_b'])}"
                }
            )
            add_chart(
                ChartSpec(
                    type="scatter",
                    x=pair["col_a"],
                    y=pair["col_b"],
                    title=f"{pair['col_a']} vs {pair['col_b']} (r={pair['correlation']:.2f})",
                ),
                key,
            )

        return charts[:max_count]
