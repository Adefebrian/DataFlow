import pandas as pd
import json
import numpy as np
from src.models.types import DataProfile, ColumnInfo


def convert_to_native(obj):
    if isinstance(obj, (list, tuple)):
        return [convert_to_native(v) for v in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    return obj


class DataProfilerAgent:
    async def profile(self, file_path: str) -> DataProfile:
        df = pd.read_csv(file_path)

        columns = []
        for col in df.columns:
            dtype = self._classify_dtype(df[col])
            sample_vals = df[col].dropna().head(5).tolist()
            col_info = ColumnInfo(
                name=col,
                dtype=dtype,
                unique_count=int(df[col].nunique()),
                null_count=int(df[col].isna().sum()),
                sample_values=[convert_to_native(v) for v in sample_vals],
            )
            columns.append(col_info)

        correlation_pairs = self._find_high_correlations(df)

        quality_score = self._calculate_quality_score(df)

        return DataProfile(
            row_count=int(len(df)),
            column_count=int(len(df.columns)),
            columns=columns,
            file_path=file_path,
            quality_score=float(quality_score),
            high_correlation_pairs=correlation_pairs,
        )

    def _classify_dtype(self, series: pd.Series) -> str:
        if pd.api.types.is_numeric_dtype(series):
            return "numeric"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        elif series.nunique() <= 15:
            return "categorical"
        return "string"

    def _find_high_correlations(self, df: pd.DataFrame) -> list[dict]:
        numeric_cols = df.select_dtypes(include=["number"]).columns
        pairs = []
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            for i in range(len(numeric_cols)):
                for j in range(i + 1, len(numeric_cols)):
                    corr = float(abs(corr_matrix.iloc[i, j]))
                    if corr > 0.4:
                        pairs.append(
                            {
                                "col_a": str(numeric_cols[i]),
                                "col_b": str(numeric_cols[j]),
                                "correlation": round(corr, 3),
                            }
                        )
        return pairs

    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        total_cells = df.shape[0] * df.shape[1]
        null_cells = int(df.isna().sum().sum())
        duplicate_rows = int(df.duplicated().sum())

        null_penalty = (null_cells / total_cells) * 100 if total_cells > 0 else 0
        duplicate_penalty = (duplicate_rows / len(df)) * 100 if len(df) > 0 else 0

        score = max(0, 100 - null_penalty - duplicate_penalty)
        return round(float(score), 2)
