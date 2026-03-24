import pandas as pd
from typing import Any
from src.models.types import CleaningAction, NearDuplicateConfig


class DataCleanerAgent:
    def __init__(self):
        self.near_dup_config = NearDuplicateConfig()

    async def clean(
        self,
        file_path: str,
    ) -> tuple[pd.DataFrame, list[CleaningAction]]:
        df = pd.read_csv(file_path)
        actions = []

        null_counts = df.isnull().sum()
        for col, null_count in null_counts[null_counts > 0].items():
            if pd.api.types.is_numeric_dtype(df[col]):
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)
                actions.append(
                    CleaningAction(
                        action_type="fill_null",
                        column=col,
                        new_value=median_val,
                        rows_affected=null_count,
                    )
                )
            else:
                mode_val = (
                    df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown"
                )
                df[col].fillna(mode_val, inplace=True)
                actions.append(
                    CleaningAction(
                        action_type="fill_null",
                        column=col,
                        new_value=mode_val,
                        rows_affected=null_count,
                    )
                )

        dup_count = df.duplicated().sum()
        if dup_count > 0:
            df.drop_duplicates(inplace=True)
            actions.append(
                CleaningAction(
                    action_type="remove_duplicates",
                    rows_affected=dup_count,
                )
            )

        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].str.strip().str.lower()

        near_dups = self.detect_near_duplicates(df)
        dup_indices = near_dups[near_dups].index.tolist()
        actions.append(
            CleaningAction(
                action_type="remove_duplicates",
                rows_affected=len(dup_indices),
            )
        )

        return df, actions

    def detect_near_duplicates(self, df: pd.DataFrame) -> pd.Series:
        config = self.near_dup_config
        compare_cols = [c for c in df.columns if c not in config.exclude_columns]

        if len(compare_cols) < config.min_comparison_columns:
            return pd.Series([False] * len(df))

        def row_similarity(row1, row2) -> float:
            matches = sum(
                1
                for a, b in zip(row1, row2)
                if str(a).strip().lower() == str(b).strip().lower()
            )
            return matches / len(compare_cols)

        n = len(df)
        threshold = int(config.threshold_pct * len(compare_cols))
        near_dup = [False] * n

        sample_size = min(1000, n)
        sample_indices = list(range(sample_size))

        for i in sample_indices:
            for j in range(i + 1, sample_size):
                if (
                    row_similarity(df.iloc[i][compare_cols], df.iloc[j][compare_cols])
                    >= config.threshold_pct
                ):
                    near_dup[j] = True
                    if sum(near_dup) > n * 0.1:
                        return pd.Series(near_dup)

        return pd.Series(near_dup)
