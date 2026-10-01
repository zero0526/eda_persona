"""Fast Vectorized Chi-Square Test of Independence.

Kiểm định tính độc lập Chi-square (Pearson's Chi-squared test of independence)
được tối ưu hóa bằng vector hóa numpy (np.bincount và outer product)
để thực hiện hàng nghìn phép kiểm định đồng thời (e.g. 1,290 dimensions x all questions)
với tốc độ cao cho dữ liệu lớn.
"""

from __future__ import annotations

from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
import scipy.stats as stats


def fast_chi2_from_codes(
    x_codes: np.ndarray,
    y_codes: np.ndarray,
    n_x: int,
    n_y: int,
    n: int,
) -> Tuple[float, int, float]:
    """Tính nhanh kiểm định Chi-square từ các mảng integer codes.

    Parameters
    ----------
    x_codes : np.ndarray
        Mảng integer codes của biến X.
    y_codes : np.ndarray
        Mảng integer codes của biến Y.
    n_x : int
        Số mức phân loại của X.
    n_y : int
        Số mức phân loại của Y.
    n : int
        Tổng số quan sát.

    Returns
    -------
    Tuple[float, int, float]
        (chi2_stat, dof, p_value)
    """
    if n_x < 2 or n_y < 2 or n < 2:
        return 0.0, 0, 1.0

    x_arr = np.asarray(x_codes, dtype=np.int64)
    y_arr = np.asarray(y_codes, dtype=np.int64)
    counts = np.bincount(x_arr * n_y + y_arr, minlength=n_x * n_y).reshape(n_x, n_y)
    r = counts.sum(axis=1)
    k = counts.sum(axis=0)

    expected = np.outer(r, k) / n
    mask = expected > 0

    chi2 = float(np.sum((counts[mask] - expected[mask]) ** 2 / expected[mask]))
    dof = int((n_x - 1) * (n_y - 1))
    if dof <= 0:
        return 0.0, 0, 1.0

    p_val = float(1.0 - stats.chi2.cdf(chi2, dof))
    return chi2, dof, p_val


def fast_chi2_independence_test(s1: pd.Series, s2: pd.Series) -> Dict[str, Any]:
    """Kiểm định tính độc lập Chi-square giữa hai pandas Series (loại bỏ giá trị missing).

    Parameters
    ----------
    s1 : pd.Series
        Series thứ nhất.
    s2 : pd.Series
        Series thứ hai.

    Returns
    -------
    Dict[str, Any]
        Dictionary chứa 'chi2_stat', 'dof', 'p_value'.
    """
    valid = pd.DataFrame({"x": s1, "y": s2}).dropna()
    if len(valid) < 2:
        return {"chi2_stat": 0.0, "dof": 0, "p_value": 1.0}

    x_cats, x_codes = np.unique(valid["x"].astype(str), return_inverse=True)
    y_cats, y_codes = np.unique(valid["y"].astype(str), return_inverse=True)

    n_x = len(x_cats)
    n_y = len(y_cats)
    n = len(valid)

    chi2, dof, p_val = fast_chi2_from_codes(x_codes, y_codes, n_x, n_y, n)
    return {
        "chi2_stat": round(chi2, 4),
        "dof": dof,
        "p_value": float(p_val),
    }


if __name__ == "__main__":
    s1 = pd.Series(["A", "A", "B", "B", "C", "C"])
    s2 = pd.Series(["1", "1", "2", "2", "1", "2"])
    res = fast_chi2_independence_test(s1, s2)
    print("Chi2 test:", res)
