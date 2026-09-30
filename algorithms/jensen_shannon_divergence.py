"""Jensen-Shannon Divergence (JSD).

Đo lường mức độ sai khác (divergence) đối xứng giữa hai phân phối xác suất p và q.
JSD dựa trên Kullback-Leibler Divergence, có giá trị bị chặn trong [0, 1] khi dùng log cơ số 2.
Thường dùng để đo lường độ lệch phân phối điều kiện P(Y|X=v) so với phân phối biên P(Y).
"""

from __future__ import annotations

import numpy as np


def jensen_shannon_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """Tính Jensen-Shannon Divergence (JSD) giữa hai phân phối xác suất p và q.

    Parameters
    ----------
    p : np.ndarray
        Mảng xác suất hoặc trọng số của phân phối thứ nhất (sẽ được chuẩn hóa sum=1).
    q : np.ndarray
        Mảng xác suất hoặc trọng số của phân phối thứ hai (sẽ được chuẩn hóa sum=1).

    Returns
    -------
    float
        Khoảng cách JSD (theo log2, giá trị từ 0.0 đến 1.0).
    """
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)

    sum_p = np.sum(p)
    sum_q = np.sum(q)

    if sum_p <= 0 or sum_q <= 0:
        return 0.0

    p = p / sum_p
    q = q / sum_q
    m = 0.5 * (p + q)

    def _kl(a: np.ndarray, b: np.ndarray) -> float:
        mask = (a > 0) & (b > 0)
        return float(np.sum(a[mask] * np.log2(a[mask] / b[mask])))

    jsd = 0.5 * _kl(p, m) + 0.5 * _kl(q, m)
    return float(max(0.0, jsd))


if __name__ == "__main__":
    p = np.array([0.2, 0.5, 0.3])
    q = np.array([0.1, 0.4, 0.5])
    print(f"JSD: {jensen_shannon_divergence(p, q):.4f}")
