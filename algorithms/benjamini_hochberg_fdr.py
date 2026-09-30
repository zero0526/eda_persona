"""Benjamini-Hochberg False Discovery Rate (BH-FDR) Procedure.

Thuật toán hiệu chỉnh đa kiểm định (Multiple Testing Correction) theo quy trình Benjamini-Hochberg (1995)
nhằm kiểm soát tỷ lệ phát hiện sai (False Discovery Rate - FDR) khi thực hiện đồng thời hàng trăm
hoặc hàng nghìn phép kiểm định thống kê (e.g. 1,290 dimensions, 5,000+ Chi2 tests).

Quy trình toán học (Step-up procedure):
    1. Sắp xếp m p-values theo thứ tự tăng dần: p_(1) <= p_(2) <= ... <= p_(m)
    2. Với mỗi i = 1, ..., m, tính giá trị ngưỡng: (i / m) * q
    3. Tìm chỉ số lớn nhất k sao cho: p_(k) <= (k / m) * q
    4. Bác bỏ tất cả các giả thuyết H_(1), ..., H_(k)
    5. P-value hiệu chỉnh (Adjusted p-value / q-value):
       p_adj_(i) = min_{k >= i} [ min(1, (m / k) * p_(k)) ]
"""

from __future__ import annotations

from typing import Sequence, Tuple, Union
import numpy as np


def benjamini_hochberg_fdr(
    p_values: Sequence[float] | np.ndarray,
    alpha: float = 0.05,
) -> Tuple[np.ndarray, np.ndarray]:
    """Thực hiện hiệu chỉnh Benjamini-Hochberg FDR trên mảng p-values.

    Parameters
    ----------
    p_values : Sequence[float] | np.ndarray
        Danh sách hoặc mảng 1D các p-values thô (raw p-values).
    alpha : float, default=0.05
        Mức kiểm soát FDR mong muốn (thường là 0.05).

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        - rejected (np.ndarray[bool]): Mảng boolean cùng kích thước, True nếu có ý nghĩa thống kê sau hiệu chỉnh.
        - p_fdr (np.ndarray[float]): Mảng p-values đã được hiệu chỉnh (adjusted p-values).
    """
    p_arr = np.asarray(p_values, dtype=float)
    shape = p_arr.shape
    p_flat = p_arr.ravel()
    m = len(p_flat)

    if m == 0:
        return np.array([], dtype=bool), np.array([], dtype=float)

    # Xử lý các giá trị NaN nếu có
    valid_mask = ~np.isnan(p_flat)
    n_valid = int(np.sum(valid_mask))
    if n_valid == 0:
        return np.zeros(shape, dtype=bool), np.full(shape, np.nan)

    p_valid = p_flat[valid_mask]
    sort_indices = np.argsort(p_valid)
    sorted_p = p_valid[sort_indices]

    # Tính m / k * p_(k)
    k = np.arange(1, n_valid + 1, dtype=float)
    factors = n_valid / k
    p_adj_sorted = sorted_p * factors

    # Đảm bảo tính đơn điệu lùi: p_adj_(i) = min_{k >= i} p_adj_(k)
    p_adj_sorted = np.minimum.accumulate(p_adj_sorted[::-1])[::-1]
    p_adj_sorted = np.clip(p_adj_sorted, 0.0, 1.0)

    # Đưa về vị trí index ban đầu
    p_fdr_valid = np.empty_like(p_adj_sorted)
    p_fdr_valid[sort_indices] = p_adj_sorted

    rejected_valid = p_fdr_valid <= alpha

    # Khôi phục shape và vị trí NaN
    rejected = np.zeros(m, dtype=bool)
    p_fdr = np.full(m, np.nan, dtype=float)

    rejected[valid_mask] = rejected_valid
    p_fdr[valid_mask] = p_fdr_valid

    return rejected.reshape(shape), p_fdr.reshape(shape)


if __name__ == "__main__":
    raw_p = [0.001, 0.008, 0.039, 0.041, 0.045, 0.12, 0.55]
    rej, adj_p = benjamini_hochberg_fdr(raw_p, alpha=0.05)
    print("Raw p:    ", [round(p, 4) for p in raw_p])
    print("Adj p_FDR:", [round(p, 4) for p in adj_p])
    print("Rejected: ", rej.tolist())
