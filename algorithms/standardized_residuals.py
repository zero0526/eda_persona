"""Haberman's Adjusted Standardized Residuals for Contingency Tables.

Tính phần dư chuẩn hóa đã hiệu chỉnh (Haberman's Adjusted Standardized Residuals - z_vc)
cho từng ô trong bảng tần số liên kết (contingency table).

Công thức:
    z_vc = (O_vc - E_vc) / sqrt(E_vc * (1 - n_v / N) * (1 - n_c / N))

Trong đó:
    - O_vc: Tần số quan sát thực tế (Observed count)
    - E_vc: Tần số kỳ vọng theo giả thuyết độc lập: E_vc = (n_v * n_c) / N
    - n_v: Tổng hàng (tổng số quan sát tại mức thuộc tính v)
    - n_c: Tổng cột (tổng số quan sát tại phân loại mục tiêu c)
    - N: Tổng số quan sát toàn bảng

Quy tắc diễn giải:
    - |z_vc| > 1.96: Sai lệch có ý nghĩa thống kê ở mức alpha = 0.05.
    - z_vc > +1.96: Xuất hiện nhiều hơn kỳ vọng đáng kể (Over-represented).
    - z_vc < -1.96: Xuất hiện ít hơn kỳ vọng đáng kể (Under-represented).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_standardized_residuals(contingency_table: pd.DataFrame) -> pd.DataFrame:
    """Tính Adjusted Standardized Residuals (z_vc) cho bảng contingency table.

    Parameters
    ----------
    contingency_table : pd.DataFrame
        Bảng tần số liên kết với index là các mức của biến X và columns là các mức của biến Y.

    Returns
    -------
    pd.DataFrame
        Bảng z-scores phần dư chuẩn hóa cùng kích thước và nhãn với contingency_table.
    """
    n_total = float(contingency_table.sum().sum())
    row_totals = contingency_table.sum(axis=1)
    col_totals = contingency_table.sum(axis=0)

    z_residuals = pd.DataFrame(
        index=contingency_table.index,
        columns=contingency_table.columns,
        dtype=float,
    )

    if n_total <= 0:
        return z_residuals.fillna(0.0)

    for v in contingency_table.index:
        n_v = float(row_totals[v])
        for c in contingency_table.columns:
            n_c = float(col_totals[c])
            o_vc = float(contingency_table.loc[v, c])
            e_vc = (n_v * n_c) / n_total

            denom = np.sqrt(e_vc * (1.0 - n_v / n_total) * (1.0 - n_c / n_total))
            if denom > 0:
                z_residuals.loc[v, c] = (o_vc - e_vc) / denom
            else:
                z_residuals.loc[v, c] = 0.0

    return z_residuals


if __name__ == "__main__":
    ct = pd.DataFrame(
        {"Option_A": [30, 10], "Option_B": [10, 40]},
        index=["Group_1", "Group_2"]
    )
    res = compute_standardized_residuals(ct)
    print("Standardized Residuals:")
    print(res.round(2))
