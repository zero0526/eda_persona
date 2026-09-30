"""Delta P, Lift, Support & Wilson Score Confidence Intervals.

Đo lường mức độ ảnh hưởng thực tế (Substantive Effect Size) của từng mức thuộc tính Persona
lên sự thay đổi xác suất lựa chọn các phương án khảo sát.

Các chỉ số cốt lõi:
    - Support (n_support): Kích thước mẫu của phân nhóm X = v.
    - Conditional Probability: P(Y=c | X=v) = count(X=v, Y=c) / n_v
    - Baseline Marginal Probability: P_base(Y=c) = count(Y=c) / N
    - Delta P (Chênh lệch tỷ lệ): Delta_P = P(Y=c | X=v) - P_base(Y=c)
    - Lift (Hệ số tăng trưởng): Lift = P(Y=c | X=v) / P_base(Y=c)
    - 95% Wilson Score Interval: Khoảng tin cậy chuẩn xác cho P(Y=c | X=v) với cỡ mẫu n_v.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
import pandas as pd
from algorithms.wilson_score_interval import wilson_score_interval


def compute_delta_p_lift_table(
    df: pd.DataFrame,
    attribute: str,
    target_col: str,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Tính bảng thống kê chi tiết Delta P, Lift, Support và Wilson CI 95%.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame chứa dữ liệu đã làm sạch.
    attribute : str
        Tên cột thuộc tính Persona (biến giải thích X).
    target_col : str
        Tên cột câu hỏi khảo sát mục tiêu (biến phản hồi Y).
    alpha : float, default=0.05
        Mức ý nghĩa cho khoảng tin cậy Wilson Score (0.05 tương ứng 95% CI).

    Returns
    -------
    pd.DataFrame
        Bảng chi tiết chứa các cột:
        ['value', 'category', 'n_support', 'count', 'p_cond', 'p_base',
         'ci_low', 'ci_high', '95%_ci', 'delta_p', 'lift']
    """
    valid_df = df[[attribute, target_col]].dropna()
    contingency = pd.crosstab(valid_df[attribute], valid_df[target_col])
    n_total = float(contingency.sum().sum())
    row_totals = contingency.sum(axis=1)
    col_totals = contingency.sum(axis=0)

    records: List[Dict[str, Any]] = []
    for v in contingency.index:
        n_v = int(row_totals[v])
        for c in contingency.columns:
            count = int(contingency.loc[v, c])
            p_cond = (count / n_v) if n_v > 0 else 0.0
            p_base = (col_totals[c] / n_total) if n_total > 0 else 0.0
            delta_p = p_cond - p_base
            lift = (p_cond / p_base) if p_base > 0 else 1.0
            ci_low, ci_high = wilson_score_interval(count, n_v, alpha=alpha)

            records.append({
                "value": v,
                "category": c,
                "n_support": n_v,
                "count": count,
                "p_cond": round(p_cond, 4),
                "p_base": round(p_base, 4),
                "ci_low": round(ci_low, 4),
                "ci_high": round(ci_high, 4),
                "95%_ci": f"[{ci_low:.1%}, {ci_high:.1%}]",
                "delta_p": round(delta_p, 4),
                "lift": round(lift, 3),
            })

    return pd.DataFrame(records)


if __name__ == "__main__":
    df_sample = pd.DataFrame({
        "income": ["High", "High", "Low", "Low", "Low"],
        "buy": ["Yes", "Yes", "No", "No", "Yes"],
    })
    res_table = compute_delta_p_lift_table(df_sample, "income", "buy")
    print(res_table.to_string(index=False))
