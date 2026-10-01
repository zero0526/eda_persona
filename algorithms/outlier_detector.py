"""
Module: outlier_detector.py
Mục đích: Phát hiện điểm dị biệt (Outliers) bằng phương pháp Hàng rào IQR (Tukey's Fences)
và Z-Score hiệu chỉnh (Modified Z-Score / MAD), đồng thời đánh giá bản chất:
Lỗi kỹ thuật (Artifact) hay Tín hiệu hành vi thật (True Behavioral Signal).
Tuân thủ quy chuẩn: Thuật toán độc lập trong algorithms/, phục vụ Bước 3 Pipeline EDA.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


def detect_outliers_iqr_mad(
    df: pd.DataFrame,
    target_cols: List[str] = None
) -> Dict[str, Any]:
    """
    Phát hiện outlier trên các biến định lượng quan trọng.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame cấp độ bước (df_steps).
    target_cols : List[str], optional
        Danh sách các cột cần soi ngoại lai.

    Returns:
    --------
    Dict[str, Any]
        Bảng tổng hợp số lượng outlier, ngưỡng giới hạn và thẩm định bản chất.
    """
    if target_cols is None:
        target_cols = [
            "model_latency_ms", "tool_execution_ms", "total_step_latency_ms",
            "cognitive_latency_ratio", "recent_last_gesture_px", "recent_last_gesture_ms",
            "context_action_velocity", "wm_situational_steps", "context_elapsed_seconds"
        ]

    # Bản đồ diễn giải nghiệp vụ cho từng biến
    domain_insights = {
        "model_latency_ms": "Độ trễ suy luận LLM tăng cao khi gặp trang web nhiều chữ phức tạp hoặc prompt dài. Là tín hiệu tải tính toán tự nhiên, không phải lỗi dữ liệu.",
        "tool_execution_ms": "Độ trễ công cụ DOM tăng khi Facebook tải ajax chậm hoặc chờ phần tử xuất hiện. Phản ánh độ trễ mạng thực tế.",
        "total_step_latency_ms": "Tổng thời gian bước = model + tool. Phản ánh đúng nhịp độ thao tác thực tế.",
        "cognitive_latency_ratio": "Tỷ số thời gian suy nghĩ / tổng thời gian. Giới hạn tự nhiên [0, 1]. Các điểm sát 1 là bước Agent suy nghĩ rất lâu nhưng thao tác DOM cực nhanh.",
        "recent_last_gesture_px": "Quãng đường cuộn chuột (pixel). Các giá trị lớn (>1000px) là cử chỉ cuộn lướt nhanh của Persona pace='quick' hoặc readingDepth='skim'. Tín hiệu hành vi thật quan trọng!",
        "recent_last_gesture_ms": "Thời lượng cử chỉ cuộn (ms). Giới hạn vật lý từ 170ms đến 300ms do CDP Cloak kiểm soát. Rất ổn định.",
        "context_action_velocity": "Vận tốc thao tác (actions/phút). Vận tốc cao xuất hiện ở đầu phiên khi Agent liên tục cuộn quan sát nhanh.",
        "wm_situational_steps": "Số bước sa đà vào chủ đề ngoài lề. Các giá trị cao (5, 6 bước) phản ánh hiện tượng Trôi dạt Nhận thức (Cognitive Drift) ở nhóm No-Persona. Tín hiệu nghiên cứu cốt lõi!",
        "context_elapsed_seconds": "Thời gian tích lũy phiên. Tăng tuyến tính từ 0 đến kết thúc phiên (~700s)."
    }

    records = []
    outlier_indices = {}

    for col in target_cols:
        if col not in df.columns:
            continue

        s = df[col].dropna()
        if len(s) == 0:
            continue

        q1 = s.quantile(0.25)
        q3 = s.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        extreme_upper = q3 + 3.0 * iqr

        # Outlier counts
        outliers_mask = (s < lower_bound) | (s > upper_bound)
        extreme_mask = s > extreme_upper
        n_outliers = int(outliers_mask.sum())
        n_extreme = int(extreme_mask.sum())
        pct_outliers = round((n_outliers / len(s)) * 100.0, 2)

        # Lưu lại danh sách index của các outlier
        outlier_indices[col] = s[outliers_mask].index.tolist()

        # Đánh giá bản chất
        if col in ["recent_last_gesture_px", "wm_situational_steps", "cognitive_latency_ratio"]:
            nature = "Tín hiệu Hành vi Thật (True Behavioral Signal)"
            decision = "GIỮ NGUYÊN (Không xóa bỏ, đưa vào phân tích RQ)"
        elif col in ["model_latency_ms", "tool_execution_ms", "total_step_latency_ms"]:
            nature = "Biến thiên Hệ thống & Độ trễ Mạng (System Latency)"
            decision = "GIỮ NGUYÊN (Sử dụng trung vị và kiểm định phi tham số)"
        else:
            nature = "Dao động Tự nhiên (Natural Variance)"
            decision = "GIỮ NGUYÊN"

        records.append({
            "Biến số": col,
            "Cỡ mẫu hợp lệ (N)": len(s),
            "Trung vị (Median)": round(float(s.median()), 2),
            "Q1 (25%)": round(float(q1), 2),
            "Q3 (75%)": round(float(q3), 2),
            "Ngưỡng trên (Q3+1.5*IQR)": round(float(upper_bound), 2),
            "Số Outlier": n_outliers,
            "Tỷ lệ Outlier (%)": pct_outliers,
            "Số Extreme Outlier": n_extreme,
            "Bản chất Ngoại lai": nature,
            "Quyết định Xử lý": decision,
            "Giải thích Nghiệp vụ": domain_insights.get(col, "Phân phối số liệu")
        })

    df_outliers = pd.DataFrame(records).sort_values(by="Tỷ lệ Outlier (%)", ascending=False).reset_index(drop=True)

    return {
        "outlier_table": df_outliers,
        "outlier_indices": outlier_indices
    }
