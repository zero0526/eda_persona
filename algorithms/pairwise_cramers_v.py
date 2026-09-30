"""Bias-corrected Cramér's V (Bergsma 2013 / Cramér's V-tilde).

Tính độ đo liên kết phi tuyến giữa hai biến định danh (categorical variables)
với hiệu chỉnh bias của Bergsma (2013) nhằm triệt tiêu hiện tượng thổi phồng effect size
khi kích thước mẫu nhỏ hoặc số mức phân loại (cardinality) lớn.
"""

from __future__ import annotations

from typing import Tuple, Union
import numpy as np
import pandas as pd


def fast_bias_corrected_cramers_v_from_codes(
    x_codes: np.ndarray,
    y_codes: np.ndarray,
    n_x: int,
    n_y: int,
    n: int,
) -> float:
    """Phiên bản tính nhanh Bergsma's V-tilde (2013) từ mảng integer codes thông qua np.bincount.

    Parameters
    ----------
    x_codes : np.ndarray
        Mảng integer codes của biến X (0 <= code < n_x).
    y_codes : np.ndarray
        Mảng integer codes của biến Y (0 <= code < n_y).
    n_x : int
        Số giá trị duy nhất (cardinality) của biến X.
    n_y : int
        Số giá trị duy nhất (cardinality) của biến Y.
    n : int
        Tổng số quan sát hợp lệ.

    Returns
    -------
    float
        Giá trị Bergsma's V-tilde trong khoảng [0.0, 1.0].
    """
    counts = np.bincount(x_codes * n_y + y_codes, minlength=n_x * n_y).reshape(n_x, n_y)
    row_sums = counts.sum(axis=1)
    col_sums = counts.sum(axis=0)
    r_nonzero = np.count_nonzero(row_sums)
    k_nonzero = np.count_nonzero(col_sums)
    if r_nonzero <= 1 or k_nonzero <= 1 or n <= 1:
        return 0.0

    expected = np.outer(row_sums, col_sums) / n
    mask = expected > 0
    chi2 = np.sum((counts[mask] - expected[mask]) ** 2 / expected[mask])
    phi2 = chi2 / n
    phi2_tilde = max(0.0, phi2 - ((k_nonzero - 1) * (r_nonzero - 1)) / (n - 1))
    r_tilde = r_nonzero - ((r_nonzero - 1) ** 2) / (n - 1)
    k_tilde = k_nonzero - ((k_nonzero - 1) ** 2) / (n - 1)
    denom = min(r_tilde - 1, k_tilde - 1)

    if denom <= 0:
        return 0.0
    return float(np.sqrt(phi2_tilde / denom))


def compute_pairwise_cramers_v(s1: pd.Series, s2: pd.Series) -> float:
    """Tính Bergsma's V-tilde giữa hai pandas Series bất kỳ (tự động loại bỏ NaN).

    Parameters
    ----------
    s1 : pd.Series
        Series thứ nhất.
    s2 : pd.Series
        Series thứ hai.

    Returns
    -------
    float
        Hệ số tương quan Bergsma's V-tilde trong khoảng [0.0, 1.0].
    """
    valid = pd.DataFrame({"x": s1, "y": s2}).dropna()
    if len(valid) < 2:
        return 0.0
    x_cats, x_codes = np.unique(valid["x"].astype(str), return_inverse=True)
    y_cats, y_codes = np.unique(valid["y"].astype(str), return_inverse=True)
    n_x, n_y, n = len(x_cats), len(y_cats), len(valid)
    if n_x <= 1 or n_y <= 1:
        return 0.0
    return fast_bias_corrected_cramers_v_from_codes(x_codes, y_codes, n_x, n_y, n)


if __name__ == "__main__":
    s1 = pd.Series(["A", "A", "B", "B", "C", "C"])
    s2 = pd.Series(["X", "X", "Y", "Y", "Z", "Z"])
    v = compute_pairwise_cramers_v(s1, s2)
    print(f"Cramér's V (bias-corrected): {v:.4f}")
