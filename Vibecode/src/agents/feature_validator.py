import ast
import pandas as pd
from src.models.types import FeatureSuggestion


class ValidationResult:
    def __init__(self, valid: bool, message: str = ""):
        self.valid = valid
        self.message = message

    @staticmethod
    def accept() -> "ValidationResult":
        return ValidationResult(True, "Valid")

    @staticmethod
    def reject(reason: str) -> "ValidationResult":
        return ValidationResult(False, reason)


class FeatureSuggestionValidator:
    def validate(
        self,
        suggestion: FeatureSuggestion,
        df: pd.DataFrame,
    ) -> ValidationResult:
        try:
            ast.parse(suggestion.formula, mode="eval")
        except SyntaxError as e:
            return ValidationResult.reject(f"Formula tidak valid: {e}")

        referenced_cols = self._extract_column_refs(suggestion.formula, df.columns)
        missing = set(referenced_cols) - set(df.columns)
        if missing:
            return ValidationResult.reject(f"Kolom tidak ada: {missing}")

        try:
            sample = df.head(100).copy()
            result = sample.eval(suggestion.formula)
            if result.isna().all():
                return ValidationResult.reject("Formula menghasilkan semua NaN")
        except Exception as e:
            return ValidationResult.reject(f"Formula gagal dieksekusi: {e}")

        for col in df.columns:
            if df[col].dtype == result.dtype:
                try:
                    correlation = df[col].corr(result)
                    if abs(correlation) > 0.999:
                        return ValidationResult.reject(
                            f"Fitur baru identik dengan kolom '{col}' yang sudah ada"
                        )
                except Exception:
                    pass

        return ValidationResult.accept()

    def _extract_column_refs(
        self, formula: str, available_columns: list[str]
    ) -> list[str]:
        referenced = []
        for col in available_columns:
            if (
                f"df['{col}']" in formula
                or f'df["{col}"]' in formula
                or f"`{col}`" in formula
            ):
                referenced.append(col)
        return referenced
