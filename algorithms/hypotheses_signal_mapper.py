"""
Module: hypotheses_signal_mapper.py
Mục đích: Tổng hợp các đặc trưng đơn biến (Univariate Signals) theo 5 nhóm biến số trọng yếu,
thiết lập các chỉ số chỉ báo sơ khởi (Preliminary Indicator Signals) gợi hướng kiểm định
cho 5 Giả thuyết thực nghiệm (H1 -> H5) đã xác lập ở Bước 1.
Tuân thủ quy chuẩn: Thuật toán độc lập trong algorithms/, phục vụ Bước 4 Pipeline EDA.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


def map_preliminary_hypothesis_signals(df_steps: pd.DataFrame) -> pd.DataFrame:
    """
    Ánh xạ các phân phối đơn biến vào 5 Giả thuyết kỳ vọng H1 -> H5.
    """
    total_steps = len(df_steps)
    
    # 1. Tín hiệu H1: Lựa chọn nội dung mục tiêu (Target Selection)
    tc_count = df_steps["has_target_candidate"].sum()
    tc_pct = round((tc_count / total_steps) * 100, 1)
    read_react_count = df_steps["intent"].isin(["read", "react", "like_page"]).sum()
    read_react_pct = round((read_react_count / total_steps) * 100, 1)

    # 2. Tín hiệu H2: Nhất quán cơ học cuộn chuột (Biomechanical Pacing)
    s_px = df_steps["recent_last_gesture_px"].dropna()
    px_median = round(float(s_px.median()), 1) if len(s_px) > 0 else 0
    px_iqr = round(float(s_px.quantile(0.75) - s_px.quantile(0.25)), 1) if len(s_px) > 0 else 0
    fast_count = (df_steps["recent_last_gesture_pace"] == "fast").sum()
    careful_count = (df_steps["recent_last_gesture_pace"] == "careful").sum()
    total_gestures = fast_count + careful_count
    fast_pct = round((fast_count / total_gestures) * 100, 1) if total_gestures > 0 else 0

    # 3. Tín hiệu H3: Kháng trôi dạt nhận thức (Anti-Drift)
    sit_steps_nonzero = (df_steps["wm_situational_steps"] > 0).sum()
    sit_steps_nonzero_pct = round((sit_steps_nonzero / total_steps) * 100, 1)
    sit_max = int(df_steps["wm_situational_steps"].max())
    warning_count = df_steps["wm_has_novelty_warning"].sum()

    # 4. Tín hiệu H4: Không gian & Vận tốc thao tác (Spatial & Velocity)
    surface_entropy = float(-np.sum(
        df_steps["surface"].value_counts(normalize=True).values * 
        np.log2(df_steps["surface"].value_counts(normalize=True).values + 1e-12)
    ))
    vel_s = df_steps["context_action_velocity"].dropna()
    vel_median = round(float(vel_s.median()), 2) if len(vel_s) > 0 else 0
    vel_p90 = round(float(vel_s.quantile(0.90)), 2) if len(vel_s) > 0 else 0

    # 5. Tín hiệu H5: Ký ức đa phiên & Ngân sách thời gian (Memory & Budget)
    mem_steps = df_steps["context_has_memory_queries"].sum()
    mem_pct = round((mem_steps / total_steps) * 100, 1)
    overtime_steps = df_steps["context_is_overtime"].sum()
    overtime_pct = round((overtime_steps / total_steps) * 100, 1)

    signals = [
        {
            "Giả thuyết": "H1: Lựa chọn nội dung mục tiêu (Target Selection)",
            "Nhóm biến số cốt lõi": "has_target_candidate, target_candidate_kind, intent",
            "Tín hiệu Đơn biến Khảo sát": f"Có {tc_count} bước nhắm thực thể cụ thể ({tc_pct}%); {read_react_count} bước tương tác sâu read/react ({read_react_pct}%).",
            "Gợi ý Hướng Kiểm định": "Phân phối intent và target_candidate cho thấy sự phân hóa mục tiêu rõ rệt. Cần kiểm định Chi-square & Delta-P ở Bước 5 để đo mức độ lái nội dung của Persona."
        },
        {
            "Giả thuyết": "H2: Nhất quán cơ học cuộn chuột (Biomechanical Pacing)",
            "Nhóm biến số cốt lõi": "recent_last_gesture_px, recent_last_gesture_ms, gesture_pace",
            "Tín hiệu Đơn biến Khảo sát": f"Quãng cuộn trải rộng (Median = {px_median}px, IQR = {px_iqr}px, Min=181px, Max=1418px); Tỷ lệ fast = {fast_pct}%, careful = {100-fast_pct}%.",
            "Gợi ý Hướng Kiểm định": "Phân phối quãng cuộn có tính đa đỉnh (bimodal) và lệch phải. Gợi ý kiểm định Mann-Whitney U test giữa nhóm pace='quick' vs pace='slow' ở Bước 5."
        },
        {
            "Giả thuyết": "H3: Kháng trôi dạt nhận thức (Anti-Drift)",
            "Nhóm biến số cốt lõi": "wm_situational_steps, wm_has_novelty_warning, thread_origin",
            "Tín hiệu Đơn biến Khảo sát": f"Có {sit_steps_nonzero} bước xuất hiện sa đà tình huống ({sit_steps_nonzero_pct}%), mức sa đà cực đại lên tới {sit_max} bước; {warning_count} cảnh báo tiết chế.",
            "Gợi ý Hướng Kiểm định": "Biến situational_steps phân bố zero-inflated lệch phải nặng (chủ yếu là 0). Cần kiểm định tỷ lệ sa đà giữa Persona vs No-Persona ở Bước 5."
        },
        {
            "Giả thuyết": "H4: Đa dạng không gian & Vận tốc (Spatial & Velocity)",
            "Nhóm biến số cốt lõi": "surface, context_action_velocity",
            "Tín hiệu Đơn biến Khảo sát": f"Độ đa dạng bề mặt (Entropy = {surface_entropy:.2f} bits, 6 bề mặt khác nhau); Vận tốc thao tác Median = {vel_median}, P90 = {vel_p90} actions/phút.",
            "Gợi ý Hướng Kiểm định": "Phân phối bề mặt có độ phân tán cao. Cần xây dựng ma trận chuyển dịch bề mặt (Markov Transition Matrix) ở Bước 6 để so sánh hành trình không gian."
        },
        {
            "Giả thuyết": "H5: Ký ức đa phiên & Ngân sách thời gian (Memory & Budget)",
            "Nhóm biến số cốt lõi": "context_has_memory_queries, context_is_overtime, remaining_seconds",
            "Tín hiệu Đơn biến Khảo sát": f"Có {mem_steps} bước nạp lại truy vấn từ phiên trước ({mem_pct}%); {overtime_steps} bước diễn ra ở trạng thái quá giờ ({overtime_pct}%).",
            "Gợi ý Hướng Kiểm định": "Khả năng duy trì ký ức đa phiên xuất hiện cục bộ. Cần đối chiếu xem nhóm có Persona có khả năng điều tiết dừng phiên trước ngưỡng overtime tốt hơn không."
        }
    ]

    return pd.DataFrame(signals)
