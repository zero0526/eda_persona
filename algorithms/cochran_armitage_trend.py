"""Cochran-Armitage Trend Test.

Kiểm định xu hướng đơn điệu (monotonic trend test) giữa biến độc lập thứ bậc (ordinal attribute)
và biến phụ thuộc nhị phân (binary outcome) trên bảng ngẫu nhiên 2 x K (hoặc bảng K x 2).
"""

from __future__ import annotations

from typing import Any, List, Optional, Tuple
import numpy as np
import pandas as pd
import scipy.stats as stats


def cochran_armitage_trend_test(
    contingency_table: pd.DataFrame,
    focal_col: Any,
    scores: Optional[List[float]] = None,
) -> Tuple[float, float, float]:
    """Thực hiện kiểm định xu hướng Cochran-Armitage.

    Parameters
    ----------
    contingency_table : pd.DataFrame
        Bảng tần số liên kết (contingency table) kích thước K x C,
        với các hàng (index) là các mức của biến thứ bậc theo đúng thứ tự (được xếp hạng),
        và các cột là các phân loại của biến mục tiêu (outcome categories).
    focal_col : Any
        Tên cột mục tiêu được quan tâm kiểm định (focal category, e.g. "Yes", "High", "Buy").
    scores : Optional[List[float]], optional
        Điểm số gán cho các mức thứ bậc (mặc định là [1, 2, ..., K]).

    Returns
    -------
    Tuple[float, float, float]
        - z_stat (float): Thống kê Z-score.
        - p_val (float): P-value 2 phía tương ứng với Z-score.
        - slope (float): Hệ số góc xu hướng tuyến tính (slope).
    """
    if focal_col not in contingency_table.columns:
        return 0.0, 1.0, 0.0

    k = contingency_table.shape[0]
    if k < 2:
        return 0.0, 1.0, 0.0

    s = np.array(scores if scores is not None else list(range(1, k + 1)), dtype=float)
    row_totals = contingency_table.sum(axis=1).values.astype(float)
    focal_counts = contingency_table[focal_col].values.astype(float)

    n_total = row_totals.sum()
    r_total = focal_counts.sum()
    if n_total <= 0 or r_total <= 0 or r_total == n_total:
        return 0.0, 1.0, 0.0

    p_bar = r_total / n_total
    q_bar = 1.0 - p_bar

    s_bar = np.sum(row_totals * s) / n_total
    t_stat = np.sum(focal_counts * (s - s_bar))

    var_t = p_bar * q_bar * (np.sum(row_totals * (s ** 2)) - (n_total * (s_bar ** 2)))
    if var_t <= 0:
        return 0.0, 1.0, 0.0

    z_stat = t_stat / np.sqrt(var_t)
    p_val = 2.0 * (1.0 - stats.norm.cdf(abs(z_stat)))

    denom_slope = np.sum(row_totals * (s - s_bar) ** 2)
    slope = (t_stat / denom_slope) if denom_slope > 0 else 0.0

    return float(z_stat), float(p_val), float(slope)


if __name__ == "__main__":
    # Test mẫu: Khảo sát thu nhập (Low, Med, High) vs Lựa chọn sản phẩm (Yes/No)
    df_ct = pd.DataFrame(
        {"Yes": [5, 15, 25], "No": [20, 15, 5]},
        index=["Low", "Medium", "High"]
    )
    z, p, slope = cochran_armitage_trend_test(df_ct, focal_col="Yes")
    print(f"Cochran-Armitage Test: z={z:.3f}, p={p:.4f}, slope={slope:.4f}")
