import pandas as pd
import numpy as np
from typing import Any


def convert_to_native(obj):
    if isinstance(obj, dict):
        return {k: convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_native(v) for v in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif pd.isna(obj):
        return None
    return obj


class StatisticsAgent:
    def compute(self, df: pd.DataFrame) -> dict[str, Any]:
        stats = {}

        for col in df.columns:
            col_stats = {}

            if pd.api.types.is_numeric_dtype(df[col]):
                col_stats["mean"] = float(df[col].mean())
                col_stats["median"] = float(df[col].median())
                col_stats["std"] = float(df[col].std())
                col_stats["min"] = float(df[col].min())
                col_stats["max"] = float(df[col].max())
                col_stats["q25"] = float(df[col].quantile(0.25))
                col_stats["q75"] = float(df[col].quantile(0.75))
                col_stats["missing"] = int(df[col].isna().sum())
                col_stats["zeros"] = int((df[col] == 0).sum())

                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                outliers = df[(df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)]
                col_stats["outlier_count"] = int(len(outliers))
                col_stats["outlier_pct"] = round(
                    float(len(outliers)) / len(df) * 100, 2
                )

            elif df[col].dtype == "object" or df[col].dtype.name == "category":
                col_stats["unique"] = int(df[col].nunique())
                top_vals = df[col].value_counts().head(5)
                col_stats["top_values"] = {str(k): int(v) for k, v in top_vals.items()}
                col_stats["missing"] = int(df[col].isna().sum())

            stats[col] = col_stats

        return convert_to_native(stats)

    def detect_anomalies(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        anomalies = []

        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1

                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr

                outlier_mask = (df[col] < lower) | (df[col] > upper)
                outlier_count = int(outlier_mask.sum())

                if outlier_count > 0:
                    anomalies.append(
                        {
                            "column": col,
                            "method": "IQR",
                            "count": outlier_count,
                            "pct": round(outlier_count / len(df) * 100, 2),
                            "sample_values": convert_to_native(
                                df[outlier_mask][col].head(5).tolist()
                            ),
                        }
                    )

        return anomalies
