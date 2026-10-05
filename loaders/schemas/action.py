"""Schema định nghĩa các trường dữ liệu được kiểm định thống kê trong EDA Action Logs.

Tài liệu tham chiếu:
- Notebook phân tích chính: notebooks/eda_action_logs.ipynb
- Báo cáo Bước 5: output/step5_bivariate_multivariate_report.md
- Bảng sàng lọc định lượng: output/tables/step4_all_numeric_significance_screening.csv
- Bảng kiểm định đa biến: output/tables/step5_driver_proxy_classification.csv

Toàn bộ các trường trong schema này đều đã được kiểm định thống kê nghiêm ngặt
(Mann-Whitney U, Benjamini-Hochberg FDR, Chi-Square, Random Forest Permutation
Importance, Fisher's Exact Test, Kruskal-Wallis H-test). Các trường metadata kỹ
thuật (UUID, timestamp, URLs, DOM target IDs) đã được loại bỏ hoàn toàn.
"""

from __future__ import annotations

import sys
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")



# ==============================================================================
# 1. TRỤ CỘT I: KHÔNG GIAN & Ý ĐỊNH HÀNH VI (ACTION SPACE & SPATIAL DECISIONS)
# ==============================================================================
class ActionSpatialDecisionSchema(BaseModel):
    """Trụ cột 1: Ý định hành vi và không gian điều hướng trên giao diện Facebook."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    intent: Literal["observe", "scroll", "read", "react", "share", "search", "open"] = Field(
        ...,
        description=(
            "Ý định hành vi của tác tử tại bước này (read, scroll, search, react, share, observe). "
            "Đây là Confirmed Driver số 1 trong mô hình Random Forest (Multi-Importance = 0.0626, "
            "Cramér's V̂ = 0.316, p < 0.001)."
        ),
    )
    surface: Literal["feed", "search", "group", "page", "detail", "reels", "unknown"] = Field(
        ...,
        description=(
            "Bề mặt giao diện nơi phát lệnh hành vi (feed, search, group, page, detail). "
            "Confirmed Driver số 2 và là biến gây nhiễu chính (Confounder) tạo nên Nghịch lý Simpson: "
            "No-Persona bị sa lầy 35.2% thời lượng ở surface 'unknown', trong khi Persona mở rộng sang "
            "group (14.6%) và page (10.3%)."
        ),
    )
    verified: bool = Field(
        ...,
        description=(
            "Trạng thái xác minh thành công trên DOM trình duyệt (True: thành công, False: lỗi/timeout). "
            "Ở cấp gộp: Persona đạt 77.65% vs No-Persona 61.36% (Chi2 = 9.78, p = 0.0018). "
            "Khi kiểm soát theo Surface, tỷ lệ trên feed và detail của hai nhóm là tương đương nhau."
        ),
    )
    reaction: Optional[Literal["like", "love", "care", "haha", "wow", "sad", "angry"]] = Field(
        None,
        description=(
            "Cảm xúc phản hồi tương tác bài viết (like, love, care, haha...). "
            "Đo lường thiên hướng tương tác xã hội. Cụm 1 (Daily/Sharer) có tỷ lệ reaction áp đảo "
            "so với Cụm 3 (Rarely/Reader) chỉ đạt 4.03% (p < 0.001)."
        ),
    )
    resolved_tool: Optional[str] = Field(
        None,
        description=(
            "Công cụ kỹ thuật thực tế được Browser Engine thực thi (scroll_feed, observe_viewport...). "
            "Mô hình Random Forest đã chứng minh đây là Likely Proxy ăn theo intent và surface "
            "(Unique Multi-Importance chỉ 0.0065)."
        ),
    )
    tool: Optional[str] = Field(
        None,
        description=(
            "Tên công cụ cấp cao được tác tử gọi. "
            "Phân loại là Likely Proxy (Multi-Importance = 0.0000), phụ thuộc hoàn toàn vào intent."
        ),
    )
    action_summary_verb: Optional[str] = Field(
        None,
        description=(
            "Động từ hành động trích xuất từ chuỗi summary (scroll, read, observe, react, search, open). "
            "Phản ánh trực tiếp hành động cấp micro-action của tác tử."
        ),
    )
    target_candidate_kind: Optional[str] = Field(
        None,
        description=(
            "Phân loại thực thể Facebook được tác tử nhắm tới (post, search_group, search_page, search_query). "
            "Phản ánh đối tượng tương tác cụ thể trong không gian mạng xã hội."
        ),
    )
    target_candidate_text: Optional[str] = Field(
        None,
        description=(
            "Tiêu đề hoặc trích đoạn văn bản thực thể được chọn để tương tác. "
            "Dùng cho phân tích NLP và đối chiếu độ phủ sở thích mạnh (interests.strong)."
        ),
    )


# ==============================================================================
# 2. TRỤ CỘT II: CHI PHÍ NHẬN THỨC & ĐỘ TRỄ (LATENCY & COGNITIVE EFFORT)
# ==============================================================================
class CognitiveLatencySchema(BaseModel):
    """Trụ cột 2: Chi phí tính toán nhận thức LLM và độ trễ thực thi giao diện."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    model_latency_ms: float = Field(
        ...,
        description=(
            "Thời gian mô hình LLM suy luận ra quyết định (ms). "
            "Persona tiêu tốn nhiều thời gian suy nghĩ hơn đáng kể: Median = 3314 ms vs 2082.5 ms "
            "(chênh lệch +1231.5 ms, Mann-Whitney U = 5162.0, Cliff's Delta = +0.644, p = 9.54e-21, Effect Size Rất lớn)."
        ),
    )
    tool_execution_ms: Optional[float] = Field(
        None,
        description=(
            "Thời gian trình duyệt thực thi công cụ DOM (ms). "
            "No-Persona có biến thiên rất lớn (IQR lên tới 21,848 ms so với 8,050 ms của Persona) "
            "do thường xuyên gặp lỗi nghẽn giao diện hoặc quan sát thất bại."
        ),
    )
    total_step_latency_ms: Optional[float] = Field(
        None,
        description=(
            "Tổng thời gian hoàn thành bước chu kỳ = model_latency_ms + tool_execution_ms. "
            "Đo lường tổng thời lượng của một chu trình nhận thức - hành động (Mann-Whitney p = 0.0183)."
        ),
    )
    cognitive_latency_ratio: Optional[float] = Field(
        None,
        description=(
            "Tỷ số nỗ lực nhận thức: model_latency_ms / total_step_latency_ms (0.0 đến 1.0). "
            "Đo lường tỷ trọng thời gian suy nghĩ trong tổng chu kỳ thao tác."
        ),
    )
    llm_request_index: Optional[int] = Field(
        None,
        description=(
            "Thứ tự yêu cầu gọi API LLM tích lũy trong phiên (1-based counter). "
            "Đo lường tiến trình gọi mô hình nhận thức (Cliff's Delta = +0.240, p = 4.95e-04)."
        ),
    )


# ==============================================================================
# 3. TRỤ CỘT III: BỘ NHỚ LÀM VIỆC & KIỂM SOÁT SA ĐÀ (WORKING MEMORY & DRIFT)
# ==============================================================================
class WorkingMemoryDriftSchema(BaseModel):
    """Trụ cột 3: Cấu trúc bộ nhớ làm việc, sa đà nhận thức và cơ chế tự tiết chế."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    wm_num_active_threads: int = Field(
        ...,
        description=(
            "Tổng số mạch chủ đề đang hoạt động đồng thời trong bộ nhớ làm việc. "
            "Đây là biến phân tách mạnh mẽ nhất toàn bộ tập dữ liệu: Persona duy trì Median = 8 threads "
            "so với 2 threads ở No-Persona (Cliff's Delta = +0.709, p = 9.03e-32, Mutual Information = 0.347)."
        ),
    )
    wm_cumulative_opened: int = Field(
        ...,
        description=(
            "Số trang/nhóm bài viết đã đào sâu mở ra tích luỹ trong Working Memory. "
            "Persona đạt Median = 2 so với 0 ở No-Persona (Cliff's Delta = +0.711, p = 3.20e-27, Rất lớn)."
        ),
    )
    wm_cumulative_searches: int = Field(
        ...,
        description=(
            "Số lần chủ động tìm kiếm từ khóa tích luỹ ghi nhận trong Working Memory "
            "(Cliff's Delta = +0.536, p = 1.35e-15, Rất lớn)."
        ),
    )
    wm_cumulative_reads: int = Field(
        ...,
        description=(
            "Số bài viết đã đọc tích luỹ ghi nhận trong Working Memory "
            "(Cliff's Delta = +0.357, p = 2.54e-08, Trung bình)."
        ),
    )
    wm_persona_threads_count: int = Field(
        ...,
        description=(
            "Số lượng mạch chủ đề bắt nguồn từ hồ sơ Persona trong bộ nhớ "
            "(Persona = 8.0 vs No-Persona = 0.0, Cliff's Delta = +0.822, p = 9.19e-44, Rất lớn)."
        ),
    )
    wm_situational_threads_count: int = Field(
        ...,
        description=(
            "Số lượng mạch chủ đề phát sinh từ kích thích tình huống ngoài lề "
            "(No-Persona chiếm ưu thế tương đối khi không có định hướng, Cliff's Delta = -0.636, p = 6.39e-57)."
        ),
    )
    wm_situational_steps: int = Field(
        ...,
        description=(
            "Số bước liên tiếp bị cuốn theo chủ đề tình huống ngoài lề. "
            "Thước đo định lượng trực tiếp về mức độ Sa đà Nhận thức (Cognitive Drift) (Cliff's Delta = -0.636, p = 6.50e-57)."
        ),
    )
    wm_explored_thread_count: int = Field(
        ...,
        description=(
            "Số lượng mạch chủ đề đã được khám phá trọn vẹn trong phiên "
            "(Cliff's Delta = -0.636, p = 6.39e-57)."
        ),
    )
    wm_explored_evidence_share: float = Field(
        ...,
        description=(
            "Tỷ lệ bằng chứng đã khám phá so với tổng kế hoạch phiên (0.00 đến 1.00) "
            "(Cliff's Delta = -0.636, p = 6.63e-57)."
        ),
    )
    wm_current_thread_verified_steps: Optional[float] = Field(
        None,
        description=(
            "Số bước xác minh thành công của mạch nhận thức hiện tại (Cliff's Delta = +0.133, p = 0.0204)."
        ),
    )
    wm_has_novelty_warning: Optional[bool] = Field(
        False,
        description=(
            "Cờ cảnh báo tiết chế khi Agent sa đà quá lâu vào nội dung ngoài lề. "
            "Khi cờ này bật, Persona hồi phục 100% về quỹ đạo sở thích cốt lõi (Guardrail Recovery Rate = 100%)."
        ),
    )
    wm_novelty_guidance: Optional[str] = Field(
        None,
        description=(
            "Chỉ dẫn tiết chế/khám phá từ cơ chế Working Memory (ví dụ: 'CẢNH BÁO TIẾT CHẾ: Bạn đang sa đà...')."
        ),
    )


# ==============================================================================
# 4. TRỤ CỘT IV: TÓM TẮT PHIÊN TRONG WORKING MEMORY (WM SESSION SUMMARIES)
# ==============================================================================
class WMSessionSummarySchema(BaseModel):
    """Trụ cột 4: Các chỉ số tóm tắt phiên tích hợp trong Working Memory."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    wm_summary_opened_sources: Optional[float] = Field(
        None,
        description=(
            "Số nguồn/trang đã mở ghi nhận trong bản tóm tắt phiên "
            "(Persona Median = 2.0 vs No-Persona = 0.0, Cliff's Delta = +0.864, p = 2.36e-27, Rất lớn)."
        ),
    )
    wm_summary_searched_topics: Optional[float] = Field(
        None,
        description=(
            "Số chủ đề đã tìm kiếm trong tóm tắt phiên "
            "(Cliff's Delta = +0.696, p = 1.14e-18, Rất lớn)."
        ),
    )
    wm_summary_read_posts: Optional[float] = Field(
        None,
        description=(
            "Số bài viết đã đọc ghi nhận trong tóm tắt phiên "
            "(Cliff's Delta = +0.431, p = 4.24e-08, Trung bình)."
        ),
    )
    wm_summary_run_minutes: Optional[float] = Field(
        None,
        description=(
            "Thời gian chạy thực tế ghi nhận trong bản tóm tắt phiên (phút) "
            "(Cliff's Delta = +0.086, p = 0.289, biến kiểm soát)."
        ),
    )
    wm_summary_planned_minutes: Optional[float] = Field(
        None,
        description=(
            "Thời gian kế hoạch phiên ghi trong WM (phút, 10.0 đến 15.0 phút) "
            "(Phân bổ đồng đều giữa các nhóm, p = 1.00)."
        ),
    )


# ==============================================================================
# 5. TRỤ CỘT V: MA TRẬN DẪN CHỨNG NHẬN THỨC & NLP (COGNITIVE MATRIX & NLP)
# ==============================================================================
class CognitiveEvidenceSchema(BaseModel):
    """Trụ cột 5: Ma trận viện dẫn chiều kích tâm lý và chuỗi lập luận tư duy tiếng Việt."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    num_dimension_evidence: int = Field(
        ...,
        description=(
            "Số lượng chiều tâm lý Persona được viện dẫn làm căn cứ cho hành động này (0 đến 5). "
            "Tương quan Spearman dương với model_latency_ms (r = +0.515, p < 1e-15, Cliff's Delta = +0.387, p = 3.80e-10)."
        ),
    )
    num_dim_primary: int = Field(
        ...,
        description=(
            "Số lượng chiều giữ vai trò quyết định chính (role=primary) "
            "(Cliff's Delta = +0.510, p = 2.70e-17, Rất lớn)."
        ),
    )
    num_dim_supporting: int = Field(
        ...,
        description=(
            "Số lượng chiều giữ vai trò bổ trợ (role=supporting) "
            "(Cliff's Delta = +0.436, p = 1.98e-14, Trung bình)."
        ),
    )
    num_dim_constraint: int = Field(
        0,
        description=(
            "Số lượng chiều giữ vai trò ràng buộc/tiết chế (role=constraint) "
            "(Cliff's Delta = +0.138, p = 2.33e-04)."
        ),
    )
    num_dim_situational: int = Field(
        0,
        description=(
            "Số lượng chiều nhận thức giữ vai trò tình huống ngoại cảnh "
            "(Cliff's Delta = -0.061, p = 0.216)."
        ),
    )
    dim_evidence_max_weight: Optional[float] = Field(
        None,
        description=(
            "Trọng số nhận thức cao nhất trong các chiều được viện dẫn (0.40 đến 1.00) "
            "(Cliff's Delta = +0.619, p = 2.25e-06, Rất lớn)."
        ),
    )
    dim_evidence_avg_weight: Optional[float] = Field(
        None,
        description=(
            "Trọng số nhận thức trung bình của các chiều viện dẫn (0.00 đến 1.00) "
            "(Cliff's Delta = +0.382, p = 4.93e-03, Trung bình)."
        ),
    )
    reason: Optional[str] = Field(
        None,
        description=(
            "Đoạn văn bản lập luận suy nghĩ tiếng Việt của Agent (Chain-of-Thought reasoning). "
            "Được phân tích NLP bằng underthesea và tính Log-Odds Ratio (LOR): "
            "Persona áp đảo ở các từ 'mục_tiêu', 'sở_thích', 'nhóm', No-Persona áp đảo ở 'quan_sát', 'thử_lại'."
        ),
    )
    reason_length: Optional[int] = Field(
        None,
        description=(
            "Độ dài ký tự của đoạn văn lập luận suy nghĩ. "
            "No-Persona có tương quan âm rất mạnh giữa model_latency_ms và reason_length (r = -0.770), "
            "trong khi Persona duy trì chiều dài lập luận ổn định (Cliff's Delta = +0.299, p = 5.22e-06)."
        ),
    )


# ==============================================================================
# 6. TRỤ CỘT VI: TIẾN TRÌNH THỜI GIAN & NHỊP NGHỈ (TEMPORAL & REST DYNAMICS)
# ==============================================================================
class TemporalDynamicsSchema(BaseModel):
    """Trụ cột 6: Vận tốc tương tác tức thời, tiến trình phiên và nhịp dừng nghỉ."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    context_action_velocity: float = Field(
        ...,
        description=(
            "Vận tốc tương tác tức thời (hành động/phút). "
            "Persona đạt Median = 3.00 hành động/phút, cao gấp 3.3 lần mức 0.91 của No-Persona "
            "(Cliff's Delta = +0.462, p = 1.62e-11, Trung bình)."
        ),
    )
    context_completed_actions: Optional[float] = Field(
        None,
        description=(
            "Số hành động đã hoàn thành ghi nhận tích lũy trong context "
            "(Cliff's Delta = +0.625, p = 1.56e-14, Rất lớn)."
        ),
    )
    context_elapsed_seconds: Optional[float] = Field(
        None,
        description=(
            "Thời gian tích luỹ đã trôi qua kể từ đầu phiên (giây) "
            "(Cliff's Delta = +0.089, p = 0.276, biến kiểm soát tiến trình)."
        ),
    )
    context_remaining_seconds: Optional[float] = Field(
        None,
        description=(
            "Thời gian còn lại của phiên theo kế hoạch (giây) "
            "(Cliff's Delta = -0.087, p = 0.286)."
        ),
    )
    context_is_overtime: Optional[bool] = Field(
        False,
        description=(
            "Đánh dấu phiên chạy đã vượt quá thời lượng kế hoạch ban đầu (True/False)."
        ),
    )
    context_rest_accumulated_seconds: Optional[int] = Field(
        0,
        description=(
            "Thời gian dừng nghỉ tích luỹ của Agent (giây). "
            "Trong 6 Persona, duy nhất vn_000081 (energy: Low, restStyle: periodic) kích hoạt nghỉ "
            "giữa phiên 120s; toàn bộ 5 Persona còn lại có thời gian nghỉ = 0s (Fisher's exact p < 0.001)."
        ),
    )
    context_rest_count: Optional[int] = Field(
        0,
        description=(
            "Số lần thực hiện hành vi dừng nghỉ xả hơi (0, 1, 2 lần)."
        ),
    )


# ==============================================================================
# 7. TRỤ CỘT VII: TÌM KIẾM & NGỮ CẢNH BỘ NHỚ (SEARCH & MEMORY CONTEXT)
# ==============================================================================
class SearchMemoryContextSchema(BaseModel):
    """Trụ cột 7: Tần suất tìm kiếm từ khóa và ngữ cảnh bộ nhớ phiên."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    context_num_queries_this_session: Optional[int] = Field(
        0,
        description=(
            "Số lượng truy vấn tìm kiếm đã thực hiện trong phiên hiện tại "
            "(Cliff's Delta = +0.355, p = 1.44e-07, Trung bình)."
        ),
    )
    context_num_memory_queries: Optional[int] = Field(
        0,
        description=(
            "Số lượng từ khóa nạp lại từ bộ nhớ phiên trước (Cliff's Delta = +0.080, p = 6.10e-03)."
        ),
    )
    context_num_recent_actions: Optional[int] = Field(
        0,
        description=(
            "Số lượng hành vi gần nhất được lưu trong cửa sổ trượt context "
            "(Cliff's Delta = +0.357, p = 8.40e-09, Trung bình)."
        ),
    )


# ==============================================================================
# 8. TRỤ CỘT VIII: CƠ HỌC CHUYỂN ĐỘNG CHUỘT VẬT LÝ (PHYSICAL KINEMATICS)
# ==============================================================================
class PhysicalKinematicsSchema(BaseModel):
    """Trụ cột 8: Cơ học cuộn chuột vật lý đo đạc trực tiếp từ Playwright engine."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    scroll_speed_px_s: Optional[float] = Field(
        None,
        description=(
            "Vận tốc cuộn lướt thực tế đo bằng pixels / giây. "
            "Cụm 1 (Quick Pace) đạt vận tốc 5,027.5 px/s, nhanh gấp 2.9 lần Cụm 2 (1,752.1 px/s) "
            "và Cụm 3 (1,800.4 px/s) (Kruskal-Wallis H = 26.28, p = 1.97e-06, Effect Rất lớn)."
        ),
    )
    scroll_pace_mode: Optional[Literal["fast", "careful", "unknown"]] = Field(
        None,
        description=(
            "Chế độ cuộn chuột vật lý đo đạc (fast vs careful). "
            "Phân tách nhị phân tuyệt đối 100%: Nhóm Quick là 100% FAST (12/12 lượt), "
            "Nhóm Slow/Balanced là 100% CAREFUL (59/59 lượt) (Fisher's Exact Test: p = 1.84e-14)."
        ),
    )
    scroll_px: Optional[float] = Field(
        None,
        description=(
            "Biên độ quãng đường cuộn chuột mỗi lần (pixels). "
            "Cụm 1 đạt trung bình 982.3 px (quét toàn bộ chiều cao màn hình) so với ~430 px ở Cụm 2 và 3 "
            "(Kruskal-Wallis H = 25.76, p = 2.55e-06)."
        ),
    )
    gesture_ms: Optional[float] = Field(
        None,
        description=(
            "Thời gian thực hiện cử chỉ cuộn chuột (ms). "
            "Cụm 1 vuốt nhanh dứt khoát trong 180 ms so với 240-290 ms của các cụm đọc chậm."
        ),
    )
    recent_last_gesture_ms: Optional[float] = Field(
        None,
        description=(
            "Thời gian vuốt chuột của hành động gần nhất lưu trong context (ms) "
            "(Cliff's Delta = -0.651, p = 4.10e-03, Rất lớn)."
        ),
    )
    recent_last_gesture_px: Optional[float] = Field(
        None,
        description=(
            "Khoảng cách vuốt chuột của hành động gần nhất lưu trong context (pixels) "
            "(Cliff's Delta = -0.560, p = 1.35e-02, Rất lớn)."
        ),
    )


# ==============================================================================
# UNIFIED SCHEMA: 53 TRƯỜNG ĐƯỢC KIỂM ĐỊNH THỐNG KÊ (STATISTICAL ACTION SCHEMA)
# ==============================================================================
class StatisticalActionSchema(
    ActionSpatialDecisionSchema,
    CognitiveLatencySchema,
    WorkingMemoryDriftSchema,
    WMSessionSummarySchema,
    CognitiveEvidenceSchema,
    TemporalDynamicsSchema,
    SearchMemoryContextSchema,
    PhysicalKinematicsSchema,
):
    """Schema hợp nhất chứa toàn bộ các trường thông tin được kiểm định thống kê trong EDA.

    Đại diện cho một quan sát hoàn chỉnh (Step Action Observation) đã làm sạch metadata.
    Bao gồm 53-56 trường thông tin đặc trưng được phân vào 8 trụ cột chức năng.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


# ==============================================================================
# DANH MỤC TRƯỜNG & HÀM TIỆN ÍCH CHO PHÂN TÍCH & BÁO CÁO
# ==============================================================================

# Danh sách 18 Trường Cốt Lõi dùng cho Báo cáo Executive & Slide PPT
CORE_18_REPORTING_FIELDS: List[str] = [
    # Trụ cột 1: Không gian & Ý định (4 trường)
    "intent",
    "surface",
    "verified",
    "reaction",
    # Trụ cột 2: Chi phí nhận thức (3 trường)
    "model_latency_ms",
    "tool_execution_ms",
    "cognitive_latency_ratio",
    # Trụ cột 3: Bộ nhớ làm việc & Sa đà (5 trường)
    "wm_num_active_threads",
    "wm_cumulative_opened",
    "wm_cumulative_searches",
    "wm_situational_steps",
    "wm_has_novelty_warning",
    # Trụ cột 4: Tiến trình & Nghỉ ngơi (3 trường)
    "context_action_velocity",
    "context_completed_actions",
    "context_rest_accumulated_seconds",
    # Trụ cột 5: Cơ học cuộn chuột vật lý (3 trường)
    "scroll_speed_px_s",
    "scroll_pace_mode",
    "scroll_px",
]

# Toàn bộ danh sách 53 trường được kiểm định thống kê trong EDA
STATISTICAL_53_FIELDS: List[str] = list(StatisticalActionSchema.model_fields.keys())


def get_core_18_fields() -> List[str]:
    """Trả về danh sách 18 trường trọng tâm báo cáo dùng trên Slide PPT."""
    return list(CORE_18_REPORTING_FIELDS)


def get_statistical_53_fields() -> List[str]:
    """Trả về danh sách toàn bộ các trường được kiểm định thống kê trong EDA."""
    return list(STATISTICAL_53_FIELDS)


def export_field_metadata_dataframe() -> pd.DataFrame:
    """Xuất bảng metadata chi tiết của toàn bộ các trường thống kê dưới dạng DataFrame.

    Bao gồm: Tên trường, Kiểu dữ liệu, Bắt buộc/Tùy chọn, Trụ cột phân loại, và Mô tả chi tiết.
    """
    records = []
    pillar_mapping = {
        ActionSpatialDecisionSchema: "I. Không Gian & Ý Định",
        CognitiveLatencySchema: "II. Chi Phí Nhận Thức",
        WorkingMemoryDriftSchema: "III. Bộ Nhớ & Trôi Dạt",
        WMSessionSummarySchema: "IV. Tóm Tắt Phiên WM",
        CognitiveEvidenceSchema: "V. Ma Trận Dẫn Chứng & NLP",
        TemporalDynamicsSchema: "VI. Tiến Trình & Nhịp Nghỉ",
        SearchMemoryContextSchema: "VII. Tìm Kiếm & Ngữ Cảnh",
        PhysicalKinematicsSchema: "VIII. Cơ Học Chuột Vật Lý",
    }

    for sub_cls, pillar_name in pillar_mapping.items():
        for fname, ffield in sub_cls.model_fields.items():
            records.append({
                "Trụ Cột": pillar_name,
                "Tên Trường": fname,
                "Kiểu Dữ Liệu": str(ffield.annotation),
                "Bắt Buộc": ffield.is_required(),
                "Trọng Tâm Slide (Top 18)": fname in CORE_18_REPORTING_FIELDS,
                "Mô Tả & Kết Quả Thống Kê": ffield.description,
            })

    return pd.DataFrame(records)


if __name__ == "__main__":
    df_meta = export_field_metadata_dataframe()
    print(f"Tổng số trường thống kê trong schema: {len(df_meta)}")
    print(f"Số trường cốt lõi Top 18: {df_meta['Trọng Tâm Slide (Top 18)'].sum()}")
    print("\nPhân bổ theo từng Trụ Cột:")
    print(df_meta["Trụ Cột"].value_counts())
