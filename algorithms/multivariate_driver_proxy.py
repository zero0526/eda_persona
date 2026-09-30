"""Multivariate Permutation Importance & Driver vs Proxy Disambiguation.

Tách biệt các yếu tố tác động thực sự độc lập (Confirmed Drivers) khỏi các biến gây nhiễu
hoặc ăn theo (Likely Proxies / Spurious Correlations do đa cộng tuyến và số chiều lớn D >> N).

Thuật toán kết hợp:
    1. Huấn luyện mô hình đa biến Multivariate (Random Forest Classifier).
    2. Đo lường Permutation Importance thực tế cho từng thuộc tính sau khi đã gộp one-hot.
    3. So sánh thứ hạng Đơn biến (Univariate Cramér's V̂) vs Đa biến (Multivariate Unique Importance).
    4. Kiểm tra ma trận tương quan giữa các biến để phân loại:
       - Confirmed Driver: Độc lập tạo ra giá trị dự báo cao cả ở đơn biến và đa biến.
       - Likely Proxy: Tương quan đơn biến cao nhưng biến mất trong đa biến do bị biến khác giải thích (Confounded).
       - Low Impact: Ít ảnh hưởng.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance


def classify_driver_vs_proxy(
    df: pd.DataFrame,
    candidate_attributes: List[str],
    target_col: str,
    univariate_df: pd.DataFrame,
    corr_matrix: Optional[pd.DataFrame] = None,
    proxy_registry: Optional[List[Dict[str, Any]]] = None,
    n_estimators: int = 200,
    max_depth: int = 5,
    random_state: int = 42,
) -> pd.DataFrame:
    """Xác nhận Unique Effect và phân loại Confirmed Driver vs Likely Proxy.

    Parameters
    ----------
    df : pd.DataFrame
        Dữ liệu chứa các trường candidate_attributes và target_col.
    candidate_attributes : List[str]
        Danh sách các thuộc tính Persona ứng viên hàng đầu.
    target_col : str
        Cột biến mục tiêu cần dự đoán.
    univariate_df : pd.DataFrame
        Bảng kết quả đơn biến chứa tối thiểu các cột: ['attribute', 'v_tilde'].
    corr_matrix : Optional[pd.DataFrame], optional
        Ma trận tương quan giữa các thuộc tính (đo bằng Cramér's V).
    proxy_registry : Optional[List[Dict[str, Any]]], optional
        Danh sách các biến ngoài top có tương quan cao với candidate.
    n_estimators : int, default=200
        Số cây trong Random Forest.
    max_depth : int, default=5
        Độ sâu tối đa của cây (chống overfitting cho mẫu nhỏ N=128).
    random_state : int, default=42
        Seed ngẫu nhiên.

    Returns
    -------
    pd.DataFrame
        Bảng tổng hợp xếp hạng đơn biến vs đa biến kèm trạng thái driver_status:
        ['attribute', 'v_tilde', 'rank_univariate', 'multivariate_importance',
         'rank_multivariate', 'driver_status', 'analysis_note']
    """
    valid_cols = [a for a in candidate_attributes if a in df.columns and df[a].dropna().nunique() > 1]
    data = df[valid_cols + [target_col]].dropna()

    def _fallback_df(base: pd.DataFrame, msg: str) -> pd.DataFrame:
        out = base.copy()
        if "v_tilde" in out.columns:
            out["rank_univariate"] = out["v_tilde"].rank(ascending=False, method="min").astype(int)
        else:
            out["rank_univariate"] = 1
        out["multivariate_importance"] = 0.0
        out["rank_multivariate"] = out["rank_univariate"]
        out["driver_status"] = "Low Impact"
        out["analysis_note"] = msg
        return out

    if len(data) < 5 or len(valid_cols) == 0:
        return _fallback_df(univariate_df, "Dữ liệu không đủ mẫu quan sát.")

    X_raw = data[valid_cols]
    y_raw = data[target_col]

    if y_raw.nunique() < 2:
        return _fallback_df(univariate_df, "Biến mục tiêu không có đủ biến thiên.")

    X_encoded = pd.get_dummies(X_raw, drop_first=True)
    if X_encoded.shape[1] < 1:
        # Trong trường hợp drop_first làm rỗng (biến hằng số), không drop_first
        X_encoded = pd.get_dummies(X_raw, drop_first=False)
    if X_encoded.shape[1] < 1:
        return _fallback_df(univariate_df, "Không đủ biến độc lập có biến thiên.")

    rf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
    )
    rf.fit(X_encoded, y_raw)

    perm_res = permutation_importance(
        rf, X_encoded, y_raw, n_repeats=20, random_state=random_state
    )
    col_importances = pd.Series(perm_res.importances_mean, index=X_encoded.columns)

    # Gộp importance theo biến gốc
    attr_imp: Dict[str, float] = {}
    for attr in valid_cols:
        matched_cols = [c for c in X_encoded.columns if c == attr or c.startswith(f"{attr}_")]
        val = float(col_importances[matched_cols].sum()) if matched_cols else 0.0
        attr_imp[attr] = max(0.0, val)

    multi_df = pd.DataFrame(list(attr_imp.items()), columns=["attribute", "multivariate_importance"])

    merged = pd.merge(
        univariate_df[univariate_df["attribute"].isin(valid_cols)],
        multi_df,
        on="attribute",
        how="left",
    ).fillna(0.0)

    merged["rank_univariate"] = merged["v_tilde"].rank(ascending=False, method="min").astype(int)
    merged["rank_multivariate"] = merged["multivariate_importance"].rank(ascending=False, method="min").astype(int)

    proxy_dict = {}
    if proxy_registry:
        proxy_dict = {item.get("attribute"): item.get("external_proxies", []) for item in proxy_registry}

    status_list: List[str] = []
    notes_list: List[str] = []

    for _, row in merged.iterrows():
        r_uni = row["rank_univariate"]
        r_mul = row["rank_multivariate"]
        attr = row["attribute"]

        if r_uni <= 5 and r_mul <= 6 and row["multivariate_importance"] > 0.01:
            status_list.append("Confirmed Driver")
            notes_list.append("Unique contributor manh doc lap")
        elif r_uni <= 6 and (r_mul > 8 or row["multivariate_importance"] <= 0.01):
            cand_corrs = []
            if corr_matrix is not None and attr in corr_matrix.index:
                high_corrs = corr_matrix.loc[attr][corr_matrix.loc[attr] > 0.3].drop(attr, errors="ignore")
                cand_corrs = list(high_corrs.index)
            ext_corrs = proxy_dict.get(attr, [])
            all_reasons = cand_corrs + ext_corrs
            status_list.append("Likely Proxy")
            notes_list.append(f"Proxy cua: {', '.join(all_reasons[:2]) if all_reasons else 'nhieu da chieu'}")
        else:
            status_list.append("Low Impact")
            notes_list.append("Tac dong yeu khi kiem soat da bien")

    merged["driver_status"] = status_list
    merged["analysis_note"] = notes_list
    merged = merged.sort_values(
        by=["driver_status", "multivariate_importance"],
        ascending=[True, False],
    ).reset_index(drop=True)

    return merged


if __name__ == "__main__":
    df_dummy = pd.DataFrame({
        "attr1": ["A", "A", "B", "B", "A", "B"] * 10,
        "attr2": ["X", "X", "Y", "Y", "X", "Y"] * 10,
        "target": ["1", "1", "2", "2", "1", "2"] * 10,
    })
    uni = pd.DataFrame([
        {"attribute": "attr1", "v_tilde": 0.8},
        {"attribute": "attr2", "v_tilde": 0.79},
    ])
    res = classify_driver_vs_proxy(df_dummy, ["attr1", "attr2"], "target", uni)
    print(res[["attribute", "driver_status", "multivariate_importance"]])
