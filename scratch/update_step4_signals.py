import pandas as pd
from pathlib import Path

signals_data = [
    {
        "Giả thuyết": "H1: Định hướng tìm kiếm nội dung (Target Selection)",
        "Nhóm biến số cốt lõi": "has_target_candidate, target_candidate_kind, intent, wm_cumulative_reads",
        "Tín hiệu Đơn biến Khảo sát": "Persona thực hiện 80 lượt đọc/tương tác sâu (read: 14.6%, react: 8.6%) và mở 2-4 nguồn thực thể Page/Group; No-Persona chỉ đọc 1 bài (0.5 bài/phiên) và 0 trang mở.",
        "Gợi ý Hướng Kiểm định": "Phân phối mục tiêu phân hóa rõ rệt. Cần kiểm định Chi-square & Delta-P ở Bước 5 để đo lường xác suất click và tương tác đúng nội dung quan tâm của Persona so với Baseline."
    },
    {
        "Giả thuyết": "H2: Thao tác cuộn chuột và nhịp độ tương tác (Biomechanical Pacing)",
        "Nhóm biến số cốt lõi": "recent_last_gesture_px, recent_last_gesture_ms, gesture_pace, step_delta_sec",
        "Tín hiệu Đơn biến Khảo sát": "Persona duy trì 104 thao tác cuộn chuẩn con người (Trung vị = 463px, nhịp 8.91s); No-Persona cuộn tuột quá đà 684–1200px chỉ 7 lần (nhịp giật cục 4.07s hoặc đơ 24-63s).",
        "Gợi ý Hướng Kiểm định": "Sự khác biệt về biên độ cuộn đạt ý nghĩa thống kê (Mann-Whitney U, p = 0.0135). Cần kiểm định phân phối cự ly thời gian (Inter-action latency) và nhịp độ cuộn ở Bước 5."
    },
    {
        "Giả thuyết": "H3: Khả năng tập trung và tránh phân tâm (Anti-Drift & Guardrail)",
        "Nhóm biến số cốt lõi": "wm_has_novelty_warning, wm_situational_steps, warning_steps_count",
        "Tín hiệu Đơn biến Khảo sát": "Persona đạt tỷ lệ cảnh báo 0.0% (0/349 bước, max sa đà = 0); No-Persona bị cảnh báo nhắc nhở 30.68% số bước (27/88 bước, max sa đà = 6 bước, p < 0.0001).",
        "Gợi ý Hướng Kiểm định": "Persona tự duy trì mục tiêu mà không cần nhắc nhở, trong khi No-Persona thường xuyên bị phân tâm. Cần kiểm định tỷ lệ cảnh báo ở Bước 5."
    },
    {
        "Giả thuyết": "H4: Ký ức dài hạn và quản lý thời gian phiên (Memory & Session Management)",
        "Nhóm biến số cốt lõi": "termination_cause, reads_at_exit, searches_at_exit, opened_at_exit, recent_queries_from_memory",
        "Tín hiệu Đơn biến Khảo sát": "Persona có 50% số phiên tự dừng chủ động khi thỏa mãn mục tiêu (đọc 3.67 bài, search 3.33 chủ đề); No-Persona 100% kết thúc do bế tắc UI Deadlock (50%) hoặc Timeout 600s.",
        "Gợi ý Hướng Kiểm định": "Chỉ số hoàn thành và năng suất thu nhận của Persona cao vượt trội. Cần kiểm định tương quan giữa việc sử dụng ký ức với mức độ chủ động kết thúc phiên ở Bước 5."
    }
]

df_sig = pd.DataFrame(signals_data)
out_path = Path("output/tables/step4_hypotheses_preliminary_signals.csv")
df_sig.to_csv(out_path, index=False, encoding="utf-8-sig")
print("Updated hypotheses signals mapping table successfully!")
