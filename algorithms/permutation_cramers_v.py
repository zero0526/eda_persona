"""Vectorized Permutation Test for Cramér's V (Bergsma's V-tilde).

Kiểm định hoán vị (Permutation Test) kiểm soát hiện tượng tương quan ngẫu nhiên
khi số chiều D >> kích cỡ mẫu N (e.g. D = 1,290 >> N = 128).
Thuật toán xây dựng phân phối giả thuyết vô hiệu (Null Distribution) thông qua B lần hoán vị ngẫu nhiên nhãn Y,
từ đó xác định ngưỡng thực nghiệm P95 và tính p-value thực nghiệm chính xác.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from algorithms.pairwise_cramers_v import fast_bias_corrected_cramers_v_from_codes


def permutation_cramers_v_test(
    x_codes: np.ndarray,
    y_codes: np.ndarray,
    n_x: int,
    n_y: int,
    n_samples: int,
    shuffled_ys: Optional[List[np.ndarray]] = None,
    n_permutations: int = 500,
    random_state: int = 42,
) -> Dict[str, Union[float, bool]]:
    """Thực hiện kiểm định hoán vị Cramér's V trên integer codes.

    Parameters
    ----------
    x_codes : np.ndarray
        Mảng integer codes của biến X.
    y_codes : np.ndarray
        Mảng integer codes của biến mục tiêu Y.
    n_x : int
        Số mức giá trị của X.
    n_y : int
        Số mức giá trị của Y.
    n_samples : int
        Tổng số quan sát.
    shuffled_ys : Optional[List[np.ndarray]], optional
        Danh sách các mảng y_codes đã hoán vị trước (giúp tăng tốc khi test hàng loạt thuộc tính).
    n_permutations : int, default=500
        Số lần hoán vị nếu chưa cung cấp shuffled_ys.
    random_state : int, default=42
        Seed ngẫu nhiên.

    Returns
    -------
    Dict[str, Union[float, bool]]
        - 'v_tilde': Bergsma's V-tilde quan sát thực tế.
        - 'p_perm': P-value thực nghiệm từ hoán vị.
        - 'threshold_p95': Ngưỡng phân vị 95% của phân phối Null.
        - 'exceeds_threshold': True nếu v_tilde >= threshold_p95.
    """
    v_obs = fast_bias_corrected_cramers_v_from_codes(x_codes, y_codes, n_x, n_y, n_samples)

    if shuffled_ys is None:
        rng = np.random.default_rng(random_state)
        shuffled_ys = [rng.permutation(y_codes) for _ in range(n_permutations)]
    else:
        n_permutations = len(shuffled_ys)

    null_v = np.empty(n_permutations, dtype=float)
    for i, s_y in enumerate(shuffled_ys):
        null_v[i] = fast_bias_corrected_cramers_v_from_codes(x_codes, s_y, n_x, n_y, n_samples)

    p_perm = float((1.0 + np.sum(null_v >= v_obs)) / (n_permutations + 1.0))
    thresh_95 = float(np.percentile(null_v, 95))

    return {
        "v_tilde": round(v_obs, 4),
        "p_perm": round(p_perm, 5),
        "threshold_p95": round(thresh_95, 4),
        "exceeds_threshold": bool(v_obs >= thresh_95),
    }


def permutation_cramers_v_series(
    s_x: pd.Series,
    s_y: pd.Series,
    n_permutations: int = 500,
    random_state: int = 42,
) -> Dict[str, Union[float, bool]]:
    """Kiểm định hoán vị Cramér's V giữa hai pandas Series bất kỳ.

    Parameters
    ----------
    s_x : pd.Series
        Series biến độc lập.
    s_y : pd.Series
        Series biến mục tiêu.
    n_permutations : int, default=500
        Số lần hoán vị.
    random_state : int, default=42
        Seed ngẫu nhiên.

    Returns
    -------
    Dict[str, Union[float, bool]]
        Kết quả kiểm định hoán vị.
    """
    valid = pd.DataFrame({"x": s_x, "y": s_y}).dropna()
    if len(valid) < 2:
        return {"v_tilde": 0.0, "p_perm": 1.0, "threshold_p95": 0.0, "exceeds_threshold": False}

    x_cats, x_codes = np.unique(valid["x"].astype(str), return_inverse=True)
    y_cats, y_codes = np.unique(valid["y"].astype(str), return_inverse=True)

    n_x, n_y, n = len(x_cats), len(y_cats), len(valid)
    if n_x < 2 or n_y < 2:
        return {"v_tilde": 0.0, "p_perm": 1.0, "threshold_p95": 0.0, "exceeds_threshold": False}

    return permutation_cramers_v_test(
        x_codes, y_codes, n_x, n_y, n,
        n_permutations=n_permutations,
        random_state=random_state,
    )


if __name__ == "__main__":
    x = pd.Series(["A", "A", "B", "B", "C", "C", "A", "B"] * 5)
    y = pd.Series(["1", "1", "2", "2", "1", "2", "1", "2"] * 5)
    res = permutation_cramers_v_series(x, y, n_permutations=200)
    print("Permutation Test Result:", res)
