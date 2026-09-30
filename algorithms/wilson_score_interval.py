"""Wilson Score Interval algorithm.

Tính khoảng tin cậy Wilson Score Interval (thường là 95%) cho tỷ lệ nhị thức (binomial proportion),
đặc biệt hiệu quả và chuẩn xác cho cỡ mẫu nhỏ hoặc tỷ lệ gần 0 hoặc 1 (khắc phục nhược điểm của Wald interval).
"""

from __future__ import annotations

from typing import Tuple
import numpy as np
import scipy.stats as stats


def wilson_score_interval(
    count: int,
    nobs: int,
    alpha: float = 0.05,
) -> Tuple[float, float]:
    """Tính khoảng tin cậy Wilson Score Interval cho tỷ lệ mẫu.

    Parameters
    ----------
    count : int
        Số lượng quan sát thành công / thỏa điều kiện.
    nobs : int
        Tổng số quan sát trong nhóm (sample size / support).
    alpha : float, default=0.05
        Mức ý nghĩa thống kê (mặc định 0.05 tương ứng khoảng tin cậy 95%).

    Returns
    -------
    Tuple[float, float]
        (ci_low, ci_high) nằm trong đoạn [0.0, 1.0].
    """
    if nobs <= 0:
        return 0.0, 0.0

    p = count / nobs
    z = stats.norm.ppf(1.0 - alpha / 2.0)
    denom = 1.0 + (z ** 2) / nobs
    center = (p + (z ** 2) / (2.0 * nobs)) / denom
    half_width = (z * np.sqrt((p * (1.0 - p) / nobs) + ((z ** 2) / (4.0 * (nobs ** 2))))) / denom

    ci_low = max(0.0, float(center - half_width))
    ci_high = min(1.0, float(center + half_width))
    return ci_low, ci_high


if __name__ == "__main__":
    low, high = wilson_score_interval(count=15, nobs=30)
    print(f"Wilson 95% CI for 15/30: [{low:.4f}, {high:.4f}]")
