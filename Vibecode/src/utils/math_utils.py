from typing import Optional, Tuple, Union

import numpy as np
import pandas as pd


def safe_histogram_range(
    data: Union[list, np.ndarray, pd.Series],
) -> Optional[Tuple[float, float]]:
    """
    Calculate a safe range for matplotlib/numpy histograms to prevent the
    "Too many bins for data range" ValueError. Returns None if the data
    is safe to use without a custom range.
    """
    try:
        if isinstance(data, pd.Series):
            clean_data = data.dropna().values
        else:
            clean_data = np.array(data)
            # Remove NaNs if present and float type
            if np.issubdtype(clean_data.dtype, np.floating):
                clean_data = clean_data[~np.isnan(clean_data)]

        if len(clean_data) == 0:
            return (0.0, 1.0)

        d_min = float(np.min(clean_data))
        d_max = float(np.max(clean_data))

        if not np.isfinite(d_min) or not np.isfinite(d_max):
            # If data has infs, we better bound it
            clean_finite = clean_data[np.isfinite(clean_data)]
            if len(clean_finite) == 0:
                return (0.0, 1.0)
            d_min = float(np.min(clean_finite))
            d_max = float(np.max(clean_finite))

        # Exact same min and max
        if d_min == d_max:
            if d_min == 0:
                return (-1.0, 1.0)
            elif d_min > 0:
                return (d_min * 0.9, d_min * 1.1)
            else:
                return (d_min * 1.1, d_min * 0.9)

        # Handle cases where the difference is smaller than float precision relative to magnitude
        magnitude = max(abs(d_min), abs(d_max))
        if magnitude > 0 and (d_max - d_min) / magnitude < 1e-12:
            padding = magnitude * 1e-5
            return (d_min - padding, d_max + padding)

        # It's safe, let numpy/matplotlib handle the range
        return None
    except Exception:
        return (0.0, 1.0)


def get_safe_bins(data: Union[list, np.ndarray, pd.Series], max_bins: int = 30) -> int:
    """
    Calculate an appropriate number of bins for a histogram based on data size and uniqueness.
    """
    try:
        if isinstance(data, pd.Series):
            clean_data = data.dropna().values
        else:
            clean_data = np.array(data)
            if np.issubdtype(clean_data.dtype, np.floating):
                clean_data = clean_data[~np.isnan(clean_data)]

        if len(clean_data) == 0:
            return 1

        n_unique = len(np.unique(clean_data))
        if n_unique < 2:
            return 1
        elif n_unique < 10:
            return n_unique
        else:
            return min(max_bins, max(5, int(np.sqrt(len(clean_data)))))
    except Exception:
        return min(max_bins, 10)
