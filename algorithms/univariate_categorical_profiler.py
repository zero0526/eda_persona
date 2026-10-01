"""
Module: univariate_categorical_profiler.py
Mục đích: Phân tích đơn biến cho các biến phân loại (Categorical Variables):
Tần suất, Tỷ lệ phần trăm, Cardinality (số nhóm duy nhất), Shannon Entropy (đo mức độ đa dạng),
phát hiện hiện tượng Mất cân bằng lớp (Class Imbalance) và Đuôi dài (Long-tail rare categories).
Tuân thủ quy chuẩn: Thuật toán độc lập trong algorithms/, phục vụ Bước 4 Pipeline EDA.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


def profile_categorical_variables(
    df: pd.DataFrame,
    target_cols: List[str] = None
) -> Dict[str, Any]:
    """
    Phân tích đơn biến danh mục và bóc tách cấu trúc tần suất / long-tail.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame chứa dữ liệu (df_steps).
    target_cols : List[str], optional
        Danh sách các biến phân loại cần khảo sát.

    Returns:
    --------
    Dict[str, Any]
        Bảng tổng hợp hồ sơ từng biến và chi tiết phân bổ tần suất.
    """
    if target_cols is None:
        target_cols = [
            "dataset_type", "intent", "resolved_tool", "surface", "reaction",
            "recent_last_gesture_pace", "wm_current_thread_origin", "wm_current_thread_state",
            "target_candidate_kind", "has_target_candidate", "context_has_memory_queries",
            "wm_has_novelty_warning", "context_is_overtime"
        ]

    summary_records = []
    frequency_breakdown = {}

    for col in target_cols:
        if col not in df.columns:
            continue

        s = df[col].dropna()
        n_valid = len(s)
        if n_valid == 0:
            continue

        val_counts = s.value_counts()
        val_pcts = s.value_counts(normalize=True) * 100.0

        cardinality = len(val_counts)
        top_cat = val_counts.index[0]
        top_freq = int(val_counts.iloc[0])
        top_pct = float(val_pcts.iloc[0])

        # Tính Shannon Entropy (đo mức độ đa dạng / đồng đều của category)
        probs = s.value_counts(normalize=True).values
        entropy_val = float(-np.sum(probs * np.log2(probs + 1e-12)))

        # Nhận diện Long-tail (các category hiếm < 5%)
        rare_cats = val_pcts[val_pcts < 5.0].to_dict()
        rare_cats_str = ", ".join([f"{k} ({v:.1f}%)" for k, v in rare_cats.items()]) if rare_cats else "Không có"

        # Đánh giá mức độ cân bằng
        if cardinality == 2:
            balance_desc = "Cân bằng tốt" if top_pct < 65.0 else f"Mất cân bằng ({top_pct:.1f}% vs {100-top_pct:.1f}%)"
        else:
            if top_pct > 75.0:
                balance_desc = f"Bị thống trị bởi '{top_cat}' ({top_pct:.1f}%)"
            elif entropy_val > 2.0:
                balance_desc = "Đa dạng phong phú cao (High Entropy)"
            else:
                balance_desc = "Phân bổ tập trung vừa phải"

        summary_records.append({
            "Biến số": col,
            "Cỡ mẫu hợp lệ (N)": n_valid,
            "Tỷ lệ khuyết (%)": round(float(df[col].isna().sum() / len(df) * 100), 1),
            "Số Category (Cardinality)": cardinality,
            "Nhóm chiếm ưu thế (Top 1)": f"{top_cat} ({top_pct:.1f}%)",
            "Shannon Entropy (bits)": round(entropy_val, 2),
            "Trạng thái phân bổ": balance_desc,
            "Danh mục hiếm Long-tail (<5%)": rare_cats_str
        })

        # Lưu lại bảng phân bổ chi tiết
        frequency_breakdown[col] = pd.DataFrame({
            "Category": val_counts.index,
            "Frequency": val_counts.values,
            "Percentage (%)": np.round(val_pcts.values, 2)
        })

    df_summary = pd.DataFrame(summary_records)
    return {
        "summary_table": df_summary,
        "frequency_breakdown": frequency_breakdown
    }
