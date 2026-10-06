"""Các Pydantic Models đại diện cho toàn bộ 31 bảng trong cơ sở dữ liệu SQLite persona-runner.

Mỗi bảng trong SQLite tương ứng với 1 Model Pydantic độc lập trong DUY NHẤT file này.
Mọi trường JSON (content_json, contract_json, payload_json, snapshot_json...) đều được bóc tách
thành các Sub-Schema con có định kiểu chặt chẽ (Strongly-typed Pydantic Models),
tuyệt đối KHÔNG để ở dạng Dict[str, Any] chung chung.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ==============================================================================
# HÀM PHỤ TRỢ PHÂN GIẢI JSON CHO PYDANTIC VALIDATORS
# ==============================================================================
def _parse_json_field(v: object) -> object:
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        try:
            return json.loads(s)
        except Exception:
            return None
    return v


# ==============================================================================
# I. CÁC SUB-SCHEMAS CON CHO CÁC TRƯỜNG JSON
# ==============================================================================

# --- 1. Surface Bias Sub-Schema ---
class SurfaceBiasSchema(BaseModel):
    """Tỷ trọng thiên hướng các bề mặt điều hướng."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    feed: Optional[float] = Field(None, description="Tỷ trọng bề mặt Newsfeed.")
    reels: Optional[float] = Field(None, description="Tỷ trọng bề mặt Reels.")
    search: Optional[float] = Field(None, description="Tỷ trọng bề mặt Search.")
    groups: Optional[float] = Field(None, description="Tỷ trọng bề mặt Groups.")
    stories: Optional[float] = Field(None, description="Tỷ trọng bề mặt Stories.")


# --- 2. Live Run State Sub-Schema ---
class LiveRunStateSchema(BaseModel):
    """Trạng thái nội bộ của lần chạy live trong `agent_live_runs`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    episodeId: Optional[str] = Field(None, description="ID của episode.")
    status: Optional[str] = Field(None, description="Trạng thái thực thi (running, completed, error).")
    startedAt: Optional[str] = Field(None, description="Thời điểm bắt đầu ISO 8601.")
    updatedAt: Optional[str] = Field(None, description="Thời điểm cập nhật ISO 8601.")
    error: Optional[str] = Field(None, description="Thông điệp lỗi nếu có.")


# --- 3. Decision Evidence Item Sub-Schema ---
class DecisionEvidenceItemSchema(BaseModel):
    """Từng căn cứ thuộc tính persona trong `decision_evidence`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    dimension: str = Field(..., description="Tên chiều thuộc tính persona.")
    role: Optional[str] = Field("primary", description="Vai trò của căn cứ (primary, supporting).")
    source: Optional[str] = Field("persona", description="Nguồn gốc căn cứ (persona, context).")
    value: Optional[Union[str, int, float, bool]] = Field(None, description="Giá trị thuộc tính.")
    weight: Optional[float] = Field(0.0, description="Trọng số ảnh hưởng nhận thức.")
    reference_id: Optional[str] = Field(None, description="ID tham chiếu.")


# --- 4. Agent Live Step Payload Sub-Schemas ---
class StepDecisionContextSchema(BaseModel):
    """Ngữ cảnh nhận thức của quyết định trong bước hành động."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    topic: Optional[str] = Field(None, description="Chủ đề đang tương tác.")
    purpose: Optional[str] = Field(None, description="Mục đích nhận thức.")
    state: Optional[str] = Field(None, description="Trạng thái hành vi (exploring, evaluating).")
    continuation: Optional[str] = Field(None, description="Tiếp tục hay dừng luồng.")
    interest_relation: Optional[str] = Field(None, description="Mức độ liên quan sở thích.")
    open_question: Optional[str] = Field(None, description="Câu hỏi mở tác tử tò mò.")
    thread_id: Optional[str] = Field(None, description="ID luồng quan tâm.")


class StepDecisionArgsSchema(BaseModel):
    """Tham số chi tiết của quyết định hành động."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    intent: Optional[str] = Field(None, description="Ý định hành vi (scroll, read, react, comment...).")
    target_id: Optional[str] = Field(None, description="ID phần tử giao diện mục tiêu.")
    reason: Optional[str] = Field(None, description="Lý do hành động.")
    decision_context: Optional[StepDecisionContextSchema] = Field(None, description="Ngữ cảnh nhận thức.")
    dimension_evidence: Optional[List[DecisionEvidenceItemSchema]] = Field(default_factory=list, description="Căn cứ persona gắn kèm.")
    comment_text: Optional[str] = Field(None, description="Nội dung bình luận nếu có.")
    reaction_type: Optional[str] = Field(None, description="Loại cảm xúc thả tim/like.")


class StepDecisionSchema(BaseModel):
    """Quyết định hành động được sinh ra từ mô hình nhận thức."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    tool: Optional[str] = Field(None, description="Công cụ thực thi (navigate_feed, scroll_feed, interact...).")
    args: Optional[StepDecisionArgsSchema] = Field(None, description="Bộ tham số chi tiết của quyết định.")


class StepOutcomeRawSchema(BaseModel):
    """Kết quả thô trả về từ browser/tool."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    success: Optional[bool] = Field(True, description="Thực thi thành công.")
    scrolled_pixels: Optional[int] = Field(None, description="Khoảng cách đã cuộn (px).")
    current_url: Optional[str] = Field(None, description="URL hiện tại của trình duyệt.")
    error_message: Optional[str] = Field(None, description="Thông điệp lỗi nếu thất bại.")
    action_type: Optional[str] = Field(None, description="Loại hành động hoàn thành.")


class StepOutcomeSchema(BaseModel):
    """Kết quả phản hồi của môi trường sau khi thực hiện quyết định."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    status: Optional[str] = Field("success", description="Trạng thái kết quả (success, error, timeout).")
    raw: Optional[StepOutcomeRawSchema] = Field(None, description="Dữ liệu thô từ môi trường.")


class StepContextBudgetSchema(BaseModel):
    """Ngân sách token và ngữ cảnh cho bước này."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    max_tokens: Optional[int] = Field(None, description="Giới hạn token tối đa.")
    used_tokens: Optional[int] = Field(None, description="Token đã dùng.")
    available_tokens: Optional[int] = Field(None, description="Token còn khả dụng.")


class StepLlmUsageSchema(BaseModel):
    """Mức tiêu thụ tài nguyên LLM trong bước."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    prompt_tokens: Optional[int] = Field(0, description="Số token prompt.")
    completion_tokens: Optional[int] = Field(0, description="Số token hoàn thành.")
    total_tokens: Optional[int] = Field(0, description="Tổng số token.")


class StepDebugSchema(BaseModel):
    """Thông tin gỡ lỗi chi tiết cho bước."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    prompt: Optional[str] = Field(None, description="Nội dung prompt gửi tới LLM.")
    perception: Optional[str] = Field(None, description="Nhận thức văn bản/DOM trên màn hình.")
    contextBudget: Optional[StepContextBudgetSchema] = Field(None, description="Ngân sách context.")
    llmUsage: Optional[StepLlmUsageSchema] = Field(None, description="Sử dụng LLM.")


class StepPayloadSchema(BaseModel):
    """Toàn bộ nội dung JSON trong trường `payload_json` của bảng `agent_live_steps`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    decision: Optional[StepDecisionSchema] = Field(None, description="Quyết định bước hành động.")
    outcome: Optional[StepOutcomeSchema] = Field(None, description="Kết quả thực thi bước.")
    debug: Optional[StepDebugSchema] = Field(None, description="Thông tin debug chi tiết.")


# --- 5. Behavioral Contract Content Sub-Schemas ---
class ContractCircadianSchema(BaseModel):
    """Cấu hình nhịp sinh học và khung giờ hoạt động."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    active_hours: Optional[List[int]] = Field(default_factory=list, description="Các giờ hoạt động trong ngày.")
    peak_hours: Optional[List[int]] = Field(default_factory=list, description="Khung giờ hoạt động cao điểm.")
    timezone: Optional[str] = Field("Asia/Ho_Chi_Minh", description="Múi giờ sinh hoạt.")


class ContractLimitsSchema(BaseModel):
    """Giới hạn số lượng hành động và thời lượng để giữ an toàn tài khoản."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    max_actions_per_session: Optional[int] = Field(None, description="Số hành động tối đa mỗi phiên.")
    max_duration_minutes: Optional[int] = Field(None, description="Thời lượng tối đa mỗi phiên (phút).")
    min_cooldown_seconds: Optional[int] = Field(None, description="Thời gian nghỉ tối thiểu giữa các phiên.")


class ContractNavigationSchema(BaseModel):
    """Thiên hướng phân bổ bề mặt mạng xã hội theo hợp đồng."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    surface_bias: Optional[SurfaceBiasSchema] = Field(None, description="Trọng số các bề mặt.")
    scroll_depth_preference: Optional[str] = Field(None, description="Độ sâu cuộn trang (shallow, moderate, deep).")


class ContractSocialSchema(BaseModel):
    """Quy chuẩn tương tác xã hội (like, comment, share)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    interaction_rate: Optional[float] = Field(None, description="Tỷ lệ tương tác trên bài viết lướt qua.")
    comment_probability: Optional[float] = Field(None, description="Xác suất để lại bình luận.")
    like_probability: Optional[float] = Field(None, description="Xác suất thả reaction.")


class ContractTasteSchema(BaseModel):
    """Gu nội dung và chủ đề quan tâm yêu thích / cấm kỵ."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    topics_interested: Optional[List[str]] = Field(default_factory=list, description="Chủ đề quan tâm cao.")
    topics_avoided: Optional[List[str]] = Field(default_factory=list, description="Chủ đề tránh tương tác.")


class ContractWritingSchema(BaseModel):
    """Văn phong, tông giọng và phong cách viết bình luận."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    tone: Optional[str] = Field(None, description="Tông giọng (vui vẻ, trang trọng, tò mò...).")
    emoji_density: Optional[str] = Field(None, description="Mức độ dùng emoji (low, medium, high).")
    language: Optional[str] = Field("vi", description="Ngôn ngữ chính.")


class BehavioralContractContentSchema(BaseModel):
    """Nội dung hợp đồng hành vi trong `contract_json` của `behavioral_contracts`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    schemaVersion: Optional[int] = Field(1, description="Phiên bản schema hợp đồng.")
    circadian: Optional[ContractCircadianSchema] = Field(None, description="Nhịp sinh học thời gian.")
    limits: Optional[ContractLimitsSchema] = Field(None, description="Giới hạn an toàn.")
    navigation: Optional[ContractNavigationSchema] = Field(None, description="Thiên hướng điều hướng.")
    social: Optional[ContractSocialSchema] = Field(None, description="Tương tác xã hội.")
    taste: Optional[ContractTasteSchema] = Field(None, description="Gu nội dung.")
    writing: Optional[ContractWritingSchema] = Field(None, description="Phong cách viết.")


class CompilerTraceSchema(BaseModel):
    """Dấu vết quá trình biên dịch hợp đồng từ persona nguyên bản."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    compiler_version: Optional[str] = Field(None, description="Phiên bản trình biên dịch.")
    source_persona_id: Optional[str] = Field(None, description="ID persona nguồn.")
    compiled_at: Optional[str] = Field(None, description="Thời điểm biên dịch.")
    applied_rules: Optional[List[str]] = Field(default_factory=list, description="Danh sách các quy tắc đã áp dụng.")


# --- 6. Working Memory Snapshot Sub-Schemas ---
class WorkingMemoryPlannedSessionSchema(BaseModel):
    """Kế hoạch thời lượng phiên chạy (phút)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    min: Optional[int] = Field(None, description="Thời lượng tối thiểu.")
    max: Optional[int] = Field(None, description="Thời lượng tối đa.")


class WorkingMemoryRestSchema(BaseModel):
    """Trạng thái nghỉ ngơi trong phiên."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    accumulated_seconds: Optional[int] = Field(0, description="Tổng số giây đã nghỉ.")
    count: Optional[int] = Field(0, description="Số lần nghỉ ngơi.")


class WorkingMemoryRecentActionSchema(BaseModel):
    """Lịch sử hành động gần nhất lưu trong working memory."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    sequence: Optional[int] = Field(None, description="Thứ tự hành động.")
    intent: Optional[str] = Field(None, description="Ý định hành động.")
    origin: Optional[str] = Field(None, description="Nguồn gốc hành động.")
    resolved_tool: Optional[str] = Field(None, description="Công cụ giải quyết.")
    elapsed_seconds: Optional[int] = Field(None, description="Số giây đã trôi qua khi thực hiện.")
    summary: Optional[str] = Field(None, description="Tóm tắt ngắn hành động.")


class WorkingMemorySearchContextSchema(BaseModel):
    """Ngữ cảnh tìm kiếm trong working memory."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    queries_this_session: Optional[List[str]] = Field(default_factory=list, description="Từ khóa đã tra cứu phiên này.")
    recent_queries_from_memory: Optional[List[str]] = Field(default_factory=list, description="Từ khóa từ bộ nhớ trước.")
    rule: Optional[str] = Field(None, description="Quy tắc điều phối tìm kiếm.")


class WorkingMemoryActiveThreadSchema(BaseModel):
    """Luồng suy nghĩ / chủ đề đang kích hoạt trong working memory."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    key: Optional[str] = Field(None, description="Khóa của luồng.")
    id: Optional[str] = Field(None, description="ID của luồng.")
    interest_relation: Optional[str] = Field(None, description="Mức liên quan sở thích.")
    last_intent: Optional[str] = Field(None, description="Ý định gần nhất.")
    evidence: Optional[List[str]] = Field(default_factory=list, description="Bằng chứng kích hoạt luồng.")


class WorkingMemoryNoveltySchema(BaseModel):
    """Đánh giá tính mới lạ và sự tò mò trong working memory."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    explored_thread_count: Optional[int] = Field(0, description="Số luồng đã khám phá.")
    explored_evidence_share: Optional[float] = Field(0.0, description="Tỷ lệ bằng chứng đã khai thác.")
    guidance: Optional[str] = Field(None, description="Chỉ dẫn khám phá tiếp theo.")


class WorkingMemoryPostSchema(BaseModel):
    """Thông tin bài viết đã đọc trong phiên."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    content_stage: Optional[str] = Field(None, description="Giai đoạn đọc nội dung.")
    duration_measurement: Optional[str] = Field(None, description="Phương thức đo thời gian đọc.")
    dwell_seconds: Optional[float] = Field(None, description="Số giây dừng lại xem.")
    read_at_elapsed: Optional[int] = Field(None, description="Thời điểm đọc tính từ đầu phiên.")
    snippet: Optional[str] = Field(None, description="Trích đoạn bài viết.")


class WorkingMemoryOpenedSourceSchema(BaseModel):
    """Thông tin nguồn hoặc trang được mở trong phiên."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    at_elapsed: Optional[int] = Field(None, description="Thời điểm mở (giây từ đầu phiên).")
    target: Optional[str] = Field(None, description="Mục tiêu hoặc tên trang/nguồn.")
    type: Optional[str] = Field(None, description="Loại nguồn (page, group...).")


class WorkingMemorySearchedTopicSchema(BaseModel):
    """Chủ đề tra cứu tìm kiếm trong working memory."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    at_elapsed: Optional[int] = Field(None, description="Thời điểm tìm kiếm (giây từ đầu phiên).")
    open_question: Optional[str] = Field(None, description="Câu hỏi mở tò mò.")
    outcome: Optional[str] = Field(None, description="Kết quả tra cứu.")
    purpose: Optional[str] = Field(None, description="Mục đích tra cứu.")
    query: Optional[str] = Field(None, description="Từ khóa truy vấn.")
    thread_id: Optional[str] = Field(None, description="ID luồng chủ đề.")


class SubjectCapabilitiesSchema(BaseModel):
    """Khả năng tương tác trên đối tượng bài viết."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    canComment: Optional[bool] = Field(None, description="Có thể bình luận hay không.")
    canReact: Optional[bool] = Field(None, description="Có thể thả cảm xúc hay không.")
    canShare: Optional[bool] = Field(None, description="Có thể chia sẻ hay không.")
    canExpand: Optional[bool] = Field(None, description="Có thể mở rộng bài viết.")


class WritingSubjectSchema(BaseModel):
    """Chủ thể / đối tượng của nội dung do bot tự viết."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Optional[str] = Field(None, description="ID bài viết/đối tượng.")
    kind: Optional[str] = Field(None, description="Loại đối tượng.")
    text: Optional[str] = Field(None, description="Nội dung văn bản đối tượng.")
    url: Optional[str] = Field(None, description="Đường dẫn.")
    attention: Optional[str] = Field(None, description="Mức độ chú ý/tập trung.")
    capabilities: Optional[Union[SubjectCapabilitiesSchema, Dict[str, bool], List[str]]] = Field(None, description="Khả năng tương tác.")


class WorkingMemoryRecentWritingSchema(BaseModel):
    """Nội dung bình luận hoặc bài viết gần đây do tác tử viết."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    content: Optional[str] = Field(None, description="Nội dung đã viết.")
    kind: Optional[str] = Field(None, description="Loại bài viết/bình luận.")
    provenance: Optional[str] = Field(None, description="Nguồn gốc phát sinh.")
    subject: Optional[Union[str, WritingSubjectSchema]] = Field(None, description="Chủ thể tương tác.")
    voice_id: Optional[str] = Field(None, description="ID giọng điệu / voice persona.")


class WorkingMemoryStateSchema(BaseModel):
    """Trạng thái chi tiết của bộ nhớ tác vụ làm việc."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    version: Optional[str] = Field(None, description="Phiên bản working memory.")
    summary: Optional[str] = Field(None, description="Tóm tắt phiên hiện tại.")
    episode_id: Optional[str] = Field(None, description="ID episode.")
    observation_id: Optional[str] = Field(None, description="ID quan sát hiện tại.")
    persona_source_hash: Optional[str] = Field(None, description="Mã băm nguồn persona.")
    planner_rule: Optional[str] = Field(None, description="Quy tắc điều phối của Planner.")
    active_threads: Optional[List[WorkingMemoryActiveThreadSchema]] = Field(default_factory=list, description="Các luồng đang mở.")
    current_thread: Optional[WorkingMemoryActiveThreadSchema] = Field(None, description="Luồng trọng tâm hiện tại.")
    novelty: Optional[WorkingMemoryNoveltySchema] = Field(None, description="Tính mới lạ.")
    read_posts: Optional[List[WorkingMemoryPostSchema]] = Field(default_factory=list, description="Danh sách bài đã đọc.")
    opened_sources: Optional[List[Union[str, WorkingMemoryOpenedSourceSchema]]] = Field(default_factory=list, description="Các nguồn bài viết đã mở.")
    searched_topics: Optional[List[Union[str, WorkingMemorySearchedTopicSchema]]] = Field(default_factory=list, description="Chủ đề đã tìm kiếm.")
    recent_own_writing: Optional[List[Union[str, WorkingMemoryRecentWritingSchema]]] = Field(default_factory=list, description="Bình luận/bài viết vừa tạo.")


class WorkingMemorySnapshotContentSchema(BaseModel):
    """Toàn bộ cấu trúc `snapshot_json` trong `episode_working_memory`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    current_surface: Optional[str] = Field(None, description="Bề mặt đang duyệt (feed, reels, detail...).")
    elapsed_seconds: Optional[int] = Field(0, description="Số giây đã trôi qua kể từ lúc bắt đầu.")
    remaining_seconds: Optional[int] = Field(None, description="Số giây còn lại ước tính.")
    completed_actions: Optional[int] = Field(0, description="Số hành động đã thực hiện.")
    planned_active_seconds: Optional[int] = Field(None, description="Tổng số giây dự kiến chạy.")
    planned_session_minutes: Optional[WorkingMemoryPlannedSessionSchema] = Field(None, description="Thời lượng dự kiến.")
    rest: Optional[WorkingMemoryRestSchema] = Field(None, description="Trạng thái nghỉ ngơi.")
    recent_actions: Optional[List[WorkingMemoryRecentActionSchema]] = Field(default_factory=list, description="Lịch sử các bước gần đây.")
    search_context: Optional[WorkingMemorySearchContextSchema] = Field(None, description="Ngữ cảnh tìm kiếm.")
    working_memory: Optional[WorkingMemoryStateSchema] = Field(None, description="Khối bộ nhớ tác vụ làm việc.")


# --- 7. Habit Facts & Snapshots Sub-Schemas ---
class HabitFactValueSchema(BaseModel):
    """Cấu trúc trường `value_json` trong bảng `habit_facts`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    intent: Optional[str] = Field(None, description="Ý định hành động thói quen hình thành.")
    resolver: Optional[str] = Field(None, description="Trình giải quyết hành động.")
    tool: Optional[str] = Field(None, description="Công cụ thực thi tương ứng.")
    verified: Optional[bool] = Field(True, description="Thói quen đã được kiểm chứng.")
    surface: Optional[str] = Field(None, description="Bề mặt xảy ra thói quen.")
    dwell_ms: Optional[int] = Field(None, description="Thời gian dừng mắt.")


class HabitLearningSchema(BaseModel):
    """Thông tin học tập tích lũy thói quen."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    source: Optional[str] = Field(None, description="Nguồn học tập thói quen.")
    verified_episode_count: Optional[int] = Field(0, description="Số episode đã xác minh.")


class BehaviorFieldEvidenceItemSchema(BaseModel):
    """Chi tiết bằng chứng cho từng trường hành vi."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    confidence: Optional[str] = Field("medium", description="Độ tin cậy của bằng chứng.")
    source: Optional[str] = Field("llm_field_refs", description="Nguồn trích xuất.")
    evidenceIds: Optional[List[str]] = Field(default_factory=list, description="Danh sách ID các trường persona căn cứ.")


class FacebookBehaviorSchema(BaseModel):
    """Đặc tính hành vi mạng xã hội Facebook của Persona."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    schemaVersion: Optional[int] = Field(1, description="Phiên bản schema hành vi.")
    discoveryStyle: Optional[str] = Field(None, description="Phong cách khám phá nội dung (topic_led, serendipitous...).")
    interactionStyle: Optional[str] = Field(None, description="Phong cách tương tác (responsive, passive...).")
    pace: Optional[str] = Field(None, description="Tốc độ lướt mạng xã hội (quick, moderate, slow).")
    preferredSurface: Optional[str] = Field(None, description="Bề mặt ưu tiên (feed, reels, mixed...).")
    readingDepth: Optional[str] = Field(None, description="Độ sâu khi đọc bài (selective, skimming, deep).")
    restStyle: Optional[str] = Field(None, description="Thói quen nghỉ ngơi giữa các phiên (occasional, frequent...).")
    evidenceIds: Optional[List[str]] = Field(default_factory=list, description="Các thuộc tính persona làm căn cứ.")
    fieldEvidence: Optional[Dict[str, BehaviorFieldEvidenceItemSchema]] = Field(default_factory=dict, description="Chi tiết bằng chứng theo từng trường.")


class HabitSnapshotContentSchema(BaseModel):
    """Toàn bộ cấu trúc `snapshot_json` trong bảng `habit_snapshots`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    baseline: Optional[FacebookBehaviorSchema] = Field(None, description="Hành vi baseline mạng xã hội.")
    learning: Optional[HabitLearningSchema] = Field(None, description="Tiến độ học thói quen.")
    action_counts: Optional[Dict[str, int]] = Field(default_factory=dict, description="Thống kê số lần thực hiện từng công cụ.")
    surface_counts: Optional[Dict[str, int]] = Field(default_factory=dict, description="Thống kê số lần ghé thăm từng bề mặt.")
    learned_pacing: Optional[Dict[str, float]] = Field(default_factory=dict, description="Nhịp độ tương tác đã học được.")
    preferred_surfaces: Optional[List[str]] = Field(default_factory=list, description="Danh sách các bề mặt ưa chuộng.")
    ranked_topics: Optional[List[str]] = Field(default_factory=list, description="Danh sách các chủ đề xếp hạng ưu tiên.")
    verified_tools: Optional[List[str]] = Field(default_factory=list, description="Các công cụ đã kiểm chứng.")


# --- 8. Memory Delta Ledger Sub-Schemas ---
class MemoryDeltaRecordDetailSchema(BaseModel):
    """Chi tiết trạng thái bản ghi bộ nhớ trước hoặc sau biến đổi."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    statement: Optional[str] = Field(None, description="Phát biểu tri thức ghi nhớ.")
    confidence: Optional[float] = Field(None, description="Độ tin cậy của tri thức.")
    evidence_count: Optional[int] = Field(0, description="Số lượng bằng chứng củng cố.")


class MemoryDeltaEvidenceSchema(BaseModel):
    """Bằng chứng dẫn đến biến đổi bộ nhớ."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    source_events: Optional[List[str]] = Field(default_factory=list, description="Danh sách ID sự kiện nguồn.")
    rationale: Optional[str] = Field(None, description="Lý do củng cố hoặc thay đổi trí nhớ.")


# --- 9. Memory Consolidation Result Sub-Schema ---
class MemoryConsolidationResultSchema(BaseModel):
    """Kết quả đợt hợp nhất bộ nhớ trong `memory_consolidation_runs`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    consolidated_facts_count: Optional[int] = Field(0, description="Số sự kiện đã hợp nhất.")
    updated_records_count: Optional[int] = Field(0, description="Số bản ghi tri thức đã cập nhật.")
    new_records_count: Optional[int] = Field(0, description="Số bản ghi tri thức tạo mới.")
    summary: Optional[str] = Field(None, description="Tóm tắt đợt học tập và củng cố tri thức.")


# --- 10. Persona Projections & Baselines Sub-Schemas ---
class BehaviorIdentityProjectionSchema(BaseModel):
    """Danh tính nhân khẩu học được ánh xạ sang mạng xã hội."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    age: Optional[int] = Field(None, description="Độ tuổi.")
    gender: Optional[str] = Field(None, description="Giới tính.")
    occupation: Optional[str] = Field(None, description="Nghề nghiệp.")
    location: Optional[str] = Field(None, description="Địa bàn sinh sống.")
    education: Optional[str] = Field(None, description="Trình độ học vấn.")
    income: Optional[str] = Field(None, description="Mức thu nhập.")
    maritalStatus: Optional[str] = Field(None, description="Tình trạng hôn nhân.")
    livingSituation: Optional[str] = Field(None, description="Điều kiện sinh hoạt.")
    archetype: Optional[str] = Field(None, description="Hình mẫu nhân cách.")


class BehaviorInterestsProjectionSchema(BaseModel):
    """Phân vùng sở thích được ánh xạ từ 194 thuộc tính persona."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    strong: Optional[List[str]] = Field(default_factory=list, description="Sở thích đậm nét và ưu tiên cao.")
    avoid: Optional[List[str]] = Field(default_factory=list, description="Chủ đề bài xích hoặc không quan tâm.")
    signals: Optional[List[str]] = Field(default_factory=list, description="Dấu hiệu thói quen và nhận thức.")


class BehaviorCommunicationProjectionSchema(BaseModel):
    """Đặc tính giao tiếp của persona khi tương tác trực tuyến."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    tone: Optional[str] = Field(None, description="Tông giọng chủ đạo.")
    language: Optional[str] = Field("vi", description="Ngôn ngữ sử dụng.")
    register_: Optional[str] = Field(None, alias="register", description="Phong cách ngữ dụng (trang trọng, thân mật...).")
    emojiUse: Optional[str] = Field(None, description="Tần suất và thói quen dùng biểu tượng cảm xúc.")
    directness: Optional[str] = Field(None, description="Mức độ thẳng thắn trong lời nói.")


class PersonaProjectionContentSchema(BaseModel):
    """Toàn bộ cấu trúc `projection_json` trong bảng `persona_projections`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    identity: Optional[BehaviorIdentityProjectionSchema] = Field(None, description="Danh tính căn bản.")
    interests: Optional[BehaviorInterestsProjectionSchema] = Field(None, description="Các phân vùng sở thích.")
    communication: Optional[BehaviorCommunicationProjectionSchema] = Field(None, description="Phong cách giao tiếp.")
    facebookBehavior: Optional[FacebookBehaviorSchema] = Field(None, description="Đặc tính hành vi Facebook.")


class PersonaProjectionTraceSchema(BaseModel):
    """Trace chi tiết quá trình chiếu chiếu persona sang profile tương tác."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    extractor: Optional[str] = Field(None, description="Công cụ trích xuất.")
    source_version: Optional[str] = Field(None, description="Phiên bản persona nguồn.")
    extracted_at: Optional[str] = Field(None, description="Thời điểm trích xuất.")


class PersonaMemoryBaselineContentSchema(BaseModel):
    """Cấu trúc `baseline_json` trong `persona_memory_baselines`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    identity: Optional[BehaviorIdentityProjectionSchema] = Field(None, description="Hồ sơ danh tính tĩnh.")
    facebookBehavior: Optional[FacebookBehaviorSchema] = Field(None, description="Hành vi Facebook khởi tạo.")
    core_beliefs: Optional[List[str]] = Field(default_factory=list, description="Niềm tin cốt lõi.")
    seeded_facts: Optional[List[str]] = Field(default_factory=list, description="Sự kiện bộ nhớ cấy sẵn.")


# --- 11. Persona Version Content Sub-Schema (194 thuộc tính) ---
class PersonaVersionContentSchema(BaseModel):
    """Toàn bộ nội dung hồ sơ Persona 194 trường trong `persona_versions.content_json`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Optional[str] = Field(None, description="Mã định danh persona (ví dụ: 'vn_fb_003').")
    name: Optional[str] = Field(None, description="Tên đại diện của persona.")
    description_vi: Optional[str] = Field(None, description="Mô tả tóm tắt bằng tiếng Việt.")
    attributes: Dict[str, str] = Field(
        default_factory=dict,
        description="Toàn bộ 194 thuộc tính nhận thức & hành vi (dạng key: value rõ ràng)."
    )
    rendered_dimensions: Optional[List[str]] = Field(
        default_factory=list,
        description="Danh sách mô tả các thuộc tính đã qua định dạng hiển thị."
    )


# --- 12. Benchmark Suites & Trials Sub-Schemas ---
class BenchmarkConfigSchema(BaseModel):
    """Cấu hình chạy bài kiểm tra benchmark trong `benchmark_suites`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    benchmark_type: Optional[str] = Field(None, description="Loại benchmark.")
    target_personas: Optional[List[str]] = Field(default_factory=list, description="Danh sách persona được kiểm thử.")
    trials_per_persona: Optional[int] = Field(1, description="Số lần lặp kiểm thử cho mỗi persona.")
    max_duration_seconds: Optional[int] = Field(None, description="Thời lượng tối đa.")


class BenchmarkSuiteSummarySchema(BaseModel):
    """Tóm tắt kết quả kiểm thử trong `benchmark_suites`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    total_trials: Optional[int] = Field(0, description="Tổng số lượt chạy.")
    successful_trials: Optional[int] = Field(0, description="Số lượt thành công.")
    failed_trials: Optional[int] = Field(0, description="Số lượt thất bại.")
    average_score: Optional[float] = Field(None, description="Điểm trung bình đạt được.")


class BenchmarkTrialReportSchema(BaseModel):
    """Báo cáo kết quả của từng trial trong `benchmark_trials`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    score: Optional[float] = Field(None, description="Điểm số đánh giá độ khớp persona.")
    passed: Optional[bool] = Field(True, description="Đạt yêu cầu benchmark.")
    metrics: Optional[Dict[str, float]] = Field(default_factory=dict, description="Các chỉ số định lượng đo lường.")
    notes: Optional[str] = Field(None, description="Ghi chú đánh giá.")


# --- 13. Planning Attempts Sub-Schemas ---
class PlanningDaySpecSchema(BaseModel):
    """Thông số cấu hình một ngày trong yêu cầu lập lịch."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    local_date: Optional[str] = Field(None, description="Ngày lập lịch YYYY-MM-DD.")
    min_minutes: Optional[int] = Field(None, description="Thời lượng phiên tối thiểu (phút).")
    max_minutes: Optional[int] = Field(None, description="Thời lượng phiên tối đa (phút).")
    active_day_parts: Optional[List[str]] = Field(default_factory=list, description="Các buổi trong ngày hoạt động.")
    quiet_day_rate: Optional[float] = Field(0.0, description="Tỷ lệ ngày yên tĩnh không hoạt động.")


class PlanningInferredHabitSchema(BaseModel):
    """Thói quen đã suy luận của bot đưa vào kế hoạch."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Optional[str] = Field(None, description="Mã định danh thói quen.")
    claim: Optional[str] = Field(None, description="Khẳng định thói quen.")


class PlanningAttemptRequestSchema(BaseModel):
    """Yêu cầu gửi tới bộ lập lịch tuần trong `planning_attempts`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    days: Optional[Union[int, List[PlanningDaySpecSchema]]] = Field(default_factory=list, description="Kế hoạch ngày cần lập lịch.")
    timezone: Optional[str] = Field("Asia/Ho_Chi_Minh", description="Múi giờ.")
    locale: Optional[str] = Field("vi_VN", description="Ngôn ngữ địa phương.")
    identity: Optional[BehaviorIdentityProjectionSchema] = Field(None, description="Danh tính người dùng.")
    persona: Optional[FacebookBehaviorSchema] = Field(None, description="Đặc tính hành vi Facebook.")
    inferred_habits: Optional[List[Union[str, PlanningInferredHabitSchema]]] = Field(default_factory=list, description="Thói quen đã suy luận.")
    memory: Optional[List[str]] = Field(default_factory=list, description="Bộ nhớ liên quan.")


class PlanningAttemptResponseItemSchema(BaseModel):
    """Từng cửa sổ hoạt động được bộ lập lịch đề xuất."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    localDate: Optional[str] = Field(None, alias="local_date", description="Ngày dự kiến phiên chạy YYYY-MM-DD.")
    startAt: Optional[str] = Field(None, alias="start_at", description="Thời điểm bắt đầu phiên ISO 8601.")
    endAt: Optional[str] = Field(None, alias="end_at", description="Thời điểm kết thúc phiên ISO 8601.")
    surfaceBias: Optional[SurfaceBiasSchema] = Field(None, alias="surface_bias", description="Thiên hướng bề mặt đề xuất.")
    seed: Optional[str] = Field(None, description="Hạt giống ngẫu nhiên của phiên.")
    reason: Optional[str] = Field(None, description="Lý do phân bổ cửa sổ thời gian.")

    @field_validator("surfaceBias", mode="before")
    @classmethod
    def parse_item_surface_bias(cls, v: object) -> object:
        return _parse_json_field(v)


# --- 14. Episode Event Payload Sub-Schema ---
class EpisodeEventPayloadSchema(BaseModel):
    """Chi tiết payload của sự kiện trong bảng `episode_events`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    fps: Optional[int] = Field(None, description="Khung hình mỗi giây.")
    preset: Optional[str] = Field(None, description="Cấu hình preset quay video.")
    profile_id: Optional[str] = Field(None, description="ID profile trình duyệt.")
    resolution: Optional[str] = Field(None, description="Độ phân giải màn hình.")
    video_path: Optional[str] = Field(None, description="Đường dẫn file video.")
    viewport_candidates: Optional[int] = Field(None, description="Số lượng viewport ứng viên.")
    summary: Optional[str] = Field(None, description="Tóm tắt sự kiện.")
    resolved_tool: Optional[str] = Field(None, description="Công cụ thực thi tương ứng.")
    terminal: Optional[bool] = Field(None, description="Sự kiện kết thúc phiên.")
    surface: Optional[str] = Field(None, description="Bề mặt tương tác.")
    scroll_px: Optional[Union[int, List[int]]] = Field(None, description="Khoảng cách cuộn trang (px).")
    tool: Optional[str] = Field(None, description="Tên công cụ gọi.")
    duration_seconds: Optional[float] = Field(None, description="Thời lượng sự kiện.")
    execution_duration_ms: Optional[int] = Field(None, description="Thời gian thực thi mili-giây.")
    status: Optional[str] = Field(None, description="Trạng thái thực hiện.")
    reason: Optional[str] = Field(None, description="Lý do hành động.")
    error: Optional[str] = Field(None, description="Thông điệp lỗi nếu có.")
    args: Optional[StepDecisionArgsSchema] = Field(None, description="Tham số công cụ.")
    evidence: Optional[List[str]] = Field(default_factory=list, description="Bằng chứng căn cứ.")


# --- 15. Account Relationship Evidence Sub-Schema ---
class AccountRelationshipEvidenceSchema(BaseModel):
    """Bằng chứng quan hệ tài khoản trong `account_relationships`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    interaction_count: Optional[int] = Field(0, description="Số lần tương tác qua lại.")
    last_interaction_at: Optional[str] = Field(None, description="Thời điểm tương tác gần nhất.")
    signals: Optional[List[str]] = Field(default_factory=list, description="Các tín hiệu thân thiết.")
    notes: Optional[str] = Field(None, description="Ghi chú về thực thể quan hệ.")


# --- 16. Entity Affinity Payload Sub-Schema ---
class EntityAffinityPayloadSchema(BaseModel):
    """Payload chi tiết của độ gắn kết thực thể trong `entity_affinities`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    interaction_types: Optional[Dict[str, int]] = Field(default_factory=dict, description="Số lần tương tác theo loại.")
    sentiment_score: Optional[float] = Field(0.0, description="Điểm đánh giá cảm xúc tương tác.")
    topics_in_common: Optional[List[str]] = Field(default_factory=list, description="Các chủ đề quan tâm chung.")
    last_action: Optional[str] = Field(None, description="Hành động gần nhất đối với thực thể.")


# --- 17. Interest Thread Payload Sub-Schema ---
class InterestThreadPayloadSchema(BaseModel):
    """Payload chi tiết của luồng quan tâm trong `interest_threads`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    keywords: Optional[List[str]] = Field(default_factory=list, description="Từ khóa chủ đề liên quan.")
    salience_score: Optional[float] = Field(1.0, description="Độ nổi bật của luồng quan tâm.")
    interaction_count: Optional[int] = Field(0, description="Số lần tác tử tương tác với luồng.")
    notes: Optional[str] = Field(None, description="Ghi chú diễn biến luồng quan tâm.")


# --- 18. Memory Record Payload Sub-Schema ---
class MemoryRecordPayloadSchema(BaseModel):
    """Payload chi tiết của bản ghi tri thức bộ nhớ trong `memory_records`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    topic: Optional[str] = Field(None, description="Chủ đề của tri thức.")
    subject: Optional[str] = Field(None, description="Chủ thể trong mệnh đề tri thức.")
    predicate: Optional[str] = Field(None, description="Vị từ quan hệ.")
    object: Optional[str] = Field(None, description="Đối tượng quan hệ.")
    source_episode_id: Optional[str] = Field(None, description="ID episode phát sinh tri thức.")
    keywords: Optional[List[str]] = Field(default_factory=list, description="Từ khóa ngữ nghĩa.")


# ==============================================================================
# II. CÁC MODEL CHÍNH ĐẠI DIỆN CHO 31 BẢNG SQLITE
# ==============================================================================

class AccountRelationshipModel(BaseModel):
    """1. Bảng `account_relationships` (Mối quan hệ bạn bè, theo dõi trên nền tảng)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID UUID.")
    bot_id: str = Field(..., description="ID của bot.")
    platform: str = Field(..., description="Nền tảng mạng xã hội (facebook, tiktok...).")
    profile_id: str = Field(..., description="ID profile trình duyệt anti-detect.")
    entity_key: str = Field(..., description="Khóa thực thể quan hệ.")
    state: str = Field(..., description="Trạng thái quan hệ (friend, following, stranger...).")
    episode_id: Optional[str] = Field(None, description="ID episode nếu có.")
    evidence_json: Optional[AccountRelationshipEvidenceSchema] = Field(None, description="Bằng chứng quan hệ có định kiểu.")
    updated_at: str = Field(..., description="Thời điểm cập nhật ISO 8601.")

    @field_validator("evidence_json", mode="before")
    @classmethod
    def parse_evidence(cls, v: object) -> object:
        return _parse_json_field(v)


class ActivityWindowModel(BaseModel):
    """2. Bảng `activity_windows` (Cửa sổ hoạt động được lập lịch)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID UUID.")
    bot_id: str = Field(..., description="ID của bot.")
    profile_id: str = Field(..., description="ID profile trình duyệt.")
    contract_id: str = Field(..., description="ID hợp đồng behavioral contract.")
    local_date: str = Field(..., description="Ngày chạy YYYY-MM-DD.")
    start_at: str = Field(..., description="Thời điểm bắt đầu phiên.")
    end_at: str = Field(..., description="Thời điểm kết thúc phiên.")
    max_actions: int = Field(..., description="Số hành động tối đa cho phép.")
    seed: str = Field(..., description="Hạt giống ngẫu nhiên.")
    surface_bias: Optional[SurfaceBiasSchema] = Field(None, description="Phân bổ bề mặt dự kiến có định kiểu.")
    state: str = Field(..., description="Trạng thái cửa sổ (ready, active, completed, skipped).")
    claimed_by: Optional[str] = Field(None, description="Worker hoặc Runner đang giữ cửa sổ.")
    lease_until: Optional[str] = Field(None, description="Thời hạn khóa giữ cửa sổ.")
    terminal_reason: Optional[str] = Field(None, description="Lý do kết thúc cửa sổ.")
    reason: Optional[str] = Field(None, description="Lý do phân bổ cửa sổ hoạt động.")
    created_at: str = Field(..., description="Thời điểm tạo.")
    updated_at: str = Field(..., description="Thời điểm cập nhật.")

    @field_validator("surface_bias", mode="before")
    @classmethod
    def parse_surface_bias(cls, v: object) -> object:
        return _parse_json_field(v)


class AgentLiveRunModel(BaseModel):
    """3. Bảng `agent_live_runs` (Trạng thái runtime thực thi live của episode)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    episode_id: str = Field(..., description="ID episode (Khóa chính).")
    status: str = Field(..., description="Trạng thái thực thi live.")
    started_at: str = Field(..., description="Thời điểm bắt đầu.")
    updated_at: str = Field(..., description="Thời điểm cập nhật.")
    error: Optional[str] = Field(None, description="Chi tiết lỗi nếu có.")
    state_json: Optional[LiveRunStateSchema] = Field(None, description="Trạng thái runtime có định kiểu.")

    @field_validator("state_json", mode="before")
    @classmethod
    def parse_state_json(cls, v: object) -> object:
        return _parse_json_field(v)


class AgentLiveStepModel(BaseModel):
    """4. Bảng `agent_live_steps` (Chi tiết từng bước hành động thực thi live)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    episode_id: str = Field(..., description="ID episode (Khóa chính composite).")
    step_index: int = Field(..., description="Thứ tự bước (Khóa chính composite).")
    created_at: str = Field(..., description="Thời điểm ghi nhận bước.")
    payload_json: Optional[StepPayloadSchema] = Field(None, description="Toàn bộ payload bước có định kiểu sâu.")

    @field_validator("payload_json", mode="before")
    @classmethod
    def parse_payload_json(cls, v: object) -> object:
        return _parse_json_field(v)


class BehavioralContractModel(BaseModel):
    """5. Bảng `behavioral_contracts` (Hợp đồng ràng buộc hành vi tác tử)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID UUID.")
    persona_version_id: str = Field(..., description="ID phiên bản persona nguồn.")
    schema_version: int = Field(..., description="Phiên bản schema hợp đồng.")
    source_hash: str = Field(..., description="Mã băm nguồn persona.")
    contract_json: Optional[BehavioralContractContentSchema] = Field(None, description="Quy tắc hợp đồng có định kiểu.")
    compiler_trace_json: Optional[CompilerTraceSchema] = Field(None, description="Dấu vết biên dịch hợp đồng.")
    created_at: str = Field(..., description="Thời điểm tạo.")

    @field_validator("contract_json", "compiler_trace_json", mode="before")
    @classmethod
    def parse_contract_jsons(cls, v: object) -> object:
        return _parse_json_field(v)


class BenchmarkSuiteModel(BaseModel):
    """6. Bảng `benchmark_suites` (Bộ kịch bản kiểm thử benchmark)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID.")
    kind: str = Field(..., description="Loại benchmark suite.")
    status: str = Field(..., description="Trạng thái suite (running, completed...).")
    config_json: Optional[BenchmarkConfigSchema] = Field(None, description="Cấu hình suite có định kiểu.")
    started_at: str = Field(..., description="Thời điểm bắt đầu.")
    ended_at: Optional[str] = Field(None, description="Thời điểm kết thúc.")
    summary_json: Optional[BenchmarkSuiteSummarySchema] = Field(None, description="Tóm tắt kết quả suite có định kiểu.")

    @field_validator("config_json", "summary_json", mode="before")
    @classmethod
    def parse_suite_jsons(cls, v: object) -> object:
        return _parse_json_field(v)


class BenchmarkTrialModel(BaseModel):
    """7. Bảng `benchmark_trials` (Lượt chạy thử nghiệm thuộc benchmark suite)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID.")
    suite_id: str = Field(..., description="ID bộ suite chứa trial này.")
    variant: str = Field(..., description="Biến thể kiểm thử.")
    persona_id: Optional[str] = Field(None, description="ID persona kiểm thử.")
    profile_id: str = Field(..., description="ID profile trình duyệt.")
    control_mode: str = Field(..., description="Chế độ kiểm soát.")
    persona_mode: str = Field(..., description="Chế độ persona.")
    episode_id: Optional[str] = Field(None, description="ID episode kiểm thử nếu có.")
    status: str = Field(..., description="Trạng thái trial (completed, error...).")
    started_at: Optional[str] = Field(None, description="Thời điểm bắt đầu.")
    ended_at: Optional[str] = Field(None, description="Thời điểm kết thúc.")
    report_json: Optional[BenchmarkTrialReportSchema] = Field(None, description="Báo cáo kết quả trial có định kiểu.")

    @field_validator("report_json", mode="before")
    @classmethod
    def parse_report_json(cls, v: object) -> object:
        return _parse_json_field(v)


class BotModel(BaseModel):
    """8. Bảng `bots` (Danh tính và trạng thái tác tử bot)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID bot.")
    persona_id: str = Field(..., description="Mã định danh persona (ví dụ: 'vn_fb_003').")
    status: str = Field(..., description="Trạng thái bot (active, retired...).")
    created_at: str = Field(..., description="Thời điểm tạo.")
    updated_at: str = Field(..., description="Thời điểm cập nhật.")


class DecisionEvidenceModel(BaseModel):
    """9. Bảng `decision_evidence` (Căn cứ thuộc tính nhận thức gắn với từng bước)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID.")
    episode_id: str = Field(..., description="ID episode.")
    step_index: Optional[int] = Field(None, description="Chỉ số bước thực thi nếu có.")
    action: str = Field(..., description="Tên hành động tương ứng.")
    evidence_json: Optional[List[DecisionEvidenceItemSchema]] = Field(default_factory=list, description="Danh sách các căn cứ persona có định kiểu.")
    created_at: str = Field(..., description="Thời điểm ghi nhận.")

    @field_validator("evidence_json", mode="before")
    @classmethod
    def parse_evidence_json(cls, v: object) -> object:
        return _parse_json_field(v)


class EntityAffinityModel(BaseModel):
    """10. Bảng `entity_affinities` (Độ gắn kết và quen thuộc của bot với các thực thể)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID.")
    bot_id: str = Field(..., description="ID bot.")
    entity_type: str = Field(..., description="Loại thực thể (page, group, user...).")
    entity_key: str = Field(..., description="Khóa thực thể.")
    display_name: str = Field(..., description="Tên hiển thị.")
    url: Optional[str] = Field(None, description="Đường dẫn tới thực thể.")
    relationship_state: str = Field(..., description="Trạng thái quan hệ.")
    scope: str = Field(..., description="Phạm vi (public, group...).")
    status: str = Field(..., description="Trạng thái bản ghi.")
    affinity: float = Field(..., description="Điểm gắn kết tình cảm (0.0 - 1.0).")
    familiarity: float = Field(..., description="Độ quen thuộc (0.0 - 1.0).")
    evidence_count: int = Field(..., description="Số bằng chứng tương tác.")
    payload_json: Optional[EntityAffinityPayloadSchema] = Field(None, description="Payload chi tiết có định kiểu.")
    first_seen_at: str = Field(..., description="Thời điểm thấy lần đầu.")
    last_seen_at: str = Field(..., description="Thời điểm thấy lần cuối.")
    created_at: str = Field(..., description="Thời điểm tạo.")
    updated_at: str = Field(..., description="Thời điểm cập nhật.")
    episode_ids_json: Optional[List[str]] = Field(default_factory=list, description="Danh sách episode IDs liên quan.")
    memory_scope: str = Field(..., description="Phạm vi bộ nhớ.")
    platform: str = Field(..., description="Nền tảng (facebook).")
    aliases_json: Optional[List[str]] = Field(default_factory=list, description="Danh sách tên bí danh.")

    @field_validator("payload_json", "episode_ids_json", "aliases_json", mode="before")
    @classmethod
    def parse_entity_jsons(cls, v: object) -> object:
        return _parse_json_field(v)


class EpisodeEventModel(BaseModel):
    """11. Bảng `episode_events` (Dòng sự kiện thời gian thực trong episode)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int = Field(..., description="Khóa chính ID (Tự tăng).")
    episode_id: str = Field(..., description="ID episode.")
    kind: str = Field(..., description="Loại sự kiện (start, tool_call, tool_result, video_record...).")
    payload_json: Optional[EpisodeEventPayloadSchema] = Field(None, description="Payload sự kiện có định kiểu.")
    created_at: str = Field(..., description="Thời điểm phát sinh sự kiện.")

    @field_validator("payload_json", mode="before")
    @classmethod
    def parse_event_payload(cls, v: object) -> object:
        return _parse_json_field(v)


class EpisodeWorkingMemoryModel(BaseModel):
    """12. Bảng `episode_working_memory` (Ảnh chụp bộ nhớ ngắn hạn working memory)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    episode_id: str = Field(..., description="ID episode (Khóa chính).")
    snapshot_json: Optional[WorkingMemorySnapshotContentSchema] = Field(None, description="Snapshot bộ nhớ có định kiểu.")
    updated_at: str = Field(..., description="Thời điểm cập nhật.")

    @field_validator("snapshot_json", mode="before")
    @classmethod
    def parse_wm_snapshot(cls, v: object) -> object:
        return _parse_json_field(v)


class EpisodeModel(BaseModel):
    """13. Bảng `episodes` (Metadata phiên chạy hoàn chỉnh của tác tử)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID UUID của episode.")
    window_id: str = Field(..., description="ID liên kết tới `activity_windows`.")
    bot_id: str = Field(..., description="ID bot.")
    profile_id: str = Field(..., description="ID profile trình duyệt.")
    contract_id: str = Field(..., description="ID hợp đồng `behavioral_contracts`.")
    runtime_provider: str = Field(..., description="Tên runtime provider.")
    status: str = Field(..., description="Trạng thái hoàn thành (done, failed, stopped...).")
    started_at: str = Field(..., description="Thời điểm bắt đầu ISO 8601.")
    ended_at: Optional[str] = Field(None, description="Thời điểm kết thúc ISO 8601.")
    lease_until: str = Field(..., description="Thời hạn khóa tài nguyên.")
    summary: Optional[str] = Field(None, description="Tóm tắt phiên chạy.")
    terminal_reason: Optional[str] = Field(None, description="Lý do kết thúc (agent_stop, timeout...).")
    video_path: Optional[str] = Field(None, description="Đường dẫn video phiên (.webm).")


class HabitFactModel(BaseModel):
    """14. Bảng `habit_facts` (Các sự kiện thói quen được ghi nhận)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID.")
    bot_id: str = Field(..., description="ID bot.")
    episode_id: str = Field(..., description="ID episode.")
    kind: str = Field(..., description="Loại thói quen.")
    value_json: Optional[HabitFactValueSchema] = Field(None, description="Chi tiết thói quen có định kiểu.")
    created_at: str = Field(..., description="Thời điểm tạo.")

    @field_validator("value_json", mode="before")
    @classmethod
    def parse_habit_value(cls, v: object) -> object:
        return _parse_json_field(v)


class HabitSnapshotModel(BaseModel):
    """15. Bảng `habit_snapshots` (Ảnh chụp thói quen tích lũy của bot)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    bot_id: str = Field(..., description="ID bot (Khóa chính).")
    source_episode_id: Optional[str] = Field(None, description="ID episode phát sinh ảnh chụp gần nhất.")
    snapshot_json: Optional[HabitSnapshotContentSchema] = Field(None, description="Dữ liệu snapshot có định kiểu.")
    updated_at: str = Field(..., description="Thời điểm cập nhật.")

    @field_validator("snapshot_json", mode="before")
    @classmethod
    def parse_habit_snapshot(cls, v: object) -> object:
        return _parse_json_field(v)


class InterestThreadModel(BaseModel):
    """16. Bảng `interest_threads` (Các luồng chủ đề quan tâm của tác tử)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID.")
    bot_id: str = Field(..., description="ID bot.")
    thread_key: str = Field(..., description="Khóa định danh luồng chủ đề.")
    scope: str = Field(..., description="Phạm vi luồng quan tâm.")
    status: str = Field(..., description="Trạng thái luồng (active, retired...).")
    title: str = Field(..., description="Tiêu đề luồng quan tâm.")
    summary: str = Field(..., description="Tóm tắt luồng.")
    payload_json: Optional[InterestThreadPayloadSchema] = Field(None, description="Payload chi tiết có định kiểu.")
    confidence: float = Field(..., description="Độ tin cậy của luồng quan tâm.")
    evidence_count: int = Field(..., description="Số bằng chứng củng cố luồng.")
    first_seen_at: str = Field(..., description="Lần đầu phát hiện.")
    last_seen_at: str = Field(..., description="Lần gần nhất thấy.")
    created_at: str = Field(..., description="Thời điểm tạo.")
    updated_at: str = Field(..., description="Thời điểm cập nhật.")
    episode_ids_json: Optional[List[str]] = Field(default_factory=list, description="Danh sách episodes liên quan.")
    memory_scope: str = Field(..., description="Phạm vi bộ nhớ.")
    platform: str = Field(..., description="Nền tảng (facebook).")
    aliases_json: Optional[List[str]] = Field(default_factory=list, description="Bí danh của chủ đề.")

    @field_validator("payload_json", "episode_ids_json", "aliases_json", mode="before")
    @classmethod
    def parse_thread_jsons(cls, v: object) -> object:
        return _parse_json_field(v)


class MemoryConsolidationRunModel(BaseModel):
    """17. Bảng `memory_consolidation_runs` (Các đợt hợp nhất và học tập bộ nhớ dài hạn)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID.")
    bot_id: str = Field(..., description="ID bot.")
    episode_id: str = Field(..., description="ID episode.")
    status: str = Field(..., description="Trạng thái hợp nhất (completed, error...).")
    input_event_count: int = Field(..., description="Số sự kiện đầu vào được xử lý.")
    result_json: Optional[MemoryConsolidationResultSchema] = Field(None, description="Kết quả hợp nhất có định kiểu.")
    error: Optional[str] = Field(None, description="Chi tiết lỗi nếu có.")
    created_at: str = Field(..., description="Thời điểm tạo.")

    @field_validator("result_json", mode="before")
    @classmethod
    def parse_consolidation_result(cls, v: object) -> object:
        return _parse_json_field(v)


class MemoryDeltaLedgerModel(BaseModel):
    """18. Bảng `memory_delta_ledger` (Sổ cái ghi nhận các biến đổi bộ nhớ)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID.")
    bot_id: str = Field(..., description="ID bot.")
    episode_id: str = Field(..., description="ID episode.")
    record_type: str = Field(..., description="Loại bản ghi bộ nhớ được cập nhật.")
    record_key: str = Field(..., description="Khóa bản ghi.")
    operation: str = Field(..., description="Thao tác (insert, update, delete).")
    before_json: Optional[MemoryDeltaRecordDetailSchema] = Field(None, description="Trạng thái trước cập nhật có định kiểu.")
    after_json: Optional[MemoryDeltaRecordDetailSchema] = Field(None, description="Trạng thái sau cập nhật có định kiểu.")
    evidence_json: Optional[MemoryDeltaEvidenceSchema] = Field(None, description="Bằng chứng dẫn đến biến đổi có định kiểu.")
    created_at: str = Field(..., description="Thời điểm tạo.")

    @field_validator("before_json", "after_json", "evidence_json", mode="before")
    @classmethod
    def parse_delta_jsons(cls, v: object) -> object:
        return _parse_json_field(v)


class MemoryRecordModel(BaseModel):
    """19. Bảng `memory_records` (Các bản ghi tri thức bộ nhớ dài hạn)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID.")
    bot_id: str = Field(..., description="ID bot.")
    kind: str = Field(..., description="Loại tri thức.")
    status: str = Field(..., description="Trạng thái bản ghi.")
    entity_type: Optional[str] = Field(None, description="Loại thực thể.")
    entity_key: Optional[str] = Field(None, description="Khóa thực thể.")
    statement: str = Field(..., description="Phát biểu tri thức đã học được.")
    payload_json: Optional[MemoryRecordPayloadSchema] = Field(None, description="Payload chi tiết của tri thức có định kiểu.")
    confidence: float = Field(1.0, description="Độ tin cậy của tri thức.")
    evidence_count: int = Field(0, description="Số bằng chứng hỗ trợ.")
    first_seen_at: str = Field(..., description="Lần đầu phát hiện.")
    last_seen_at: str = Field(..., description="Lần gần nhất thấy.")
    created_at: str = Field(..., description="Thời điểm tạo.")
    updated_at: str = Field(..., description="Thời điểm cập nhật.")

    @field_validator("payload_json", mode="before")
    @classmethod
    def parse_payload(cls, v: object) -> object:
        return _parse_json_field(v)


class MemorySettingModel(BaseModel):
    """20. Bảng `memory_settings` (Cấu hình cơ chế đọc/học bộ nhớ của bot)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    bot_id: str = Field(..., description="ID bot (Khóa chính).")
    learning_enabled: bool = Field(True, description="Kích hoạt cơ chế học bộ nhớ.")
    updated_at: str = Field(..., description="Thời điểm cập nhật.")
    read_enabled: bool = Field(True, description="Kích hoạt cơ chế đọc bộ nhớ.")


class PersonaMemoryBaselineModel(BaseModel):
    """21. Bảng `persona_memory_baselines` (Bộ nhớ khởi tạo tĩnh cho từng persona)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    bot_id: str = Field(..., description="ID bot (Khóa chính).")
    persona_version_id: str = Field(..., description="ID phiên bản persona.")
    baseline_json: Optional[PersonaMemoryBaselineContentSchema] = Field(None, description="Cấu hình baseline có định kiểu.")
    source: str = Field(..., description="Nguồn baseline.")
    created_at: str = Field(..., description="Thời điểm tạo.")
    updated_at: str = Field(..., description="Thời điểm cập nhật.")

    @field_validator("baseline_json", mode="before")
    @classmethod
    def parse_baseline(cls, v: object) -> object:
        return _parse_json_field(v)


class PersonaProjectionModel(BaseModel):
    """22. Bảng `persona_projections` (Bản chiếu hành vi persona sang mạng xã hội)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID.")
    persona_version_id: str = Field(..., description="ID phiên bản persona.")
    schema_version: int = Field(1, description="Phiên bản schema.")
    source_hash: str = Field(..., description="Mã băm nguồn.")
    projection_json: Optional[PersonaProjectionContentSchema] = Field(None, description="Bản chiếu có định kiểu.")
    extraction_trace_json: Optional[CompilerTraceSchema] = Field(None, description="Trace trích xuất có định kiểu.")
    created_at: str = Field(..., description="Thời điểm tạo.")

    @field_validator("projection_json", "extraction_trace_json", mode="before")
    @classmethod
    def parse_projection_jsons(cls, v: object) -> object:
        return _parse_json_field(v)


class PersonaScheduleSettingModel(BaseModel):
    """23. Bảng `persona_schedule_settings` (Cấu hình chu kỳ lịch chạy persona)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    bot_id: str = Field(..., description="ID bot (Khóa chính).")
    enabled: bool = Field(True, description="Bật lập lịch tự động.")
    horizon_days: int = Field(7, description="Số ngày lập lịch trước.")
    updated_at: str = Field(..., description="Thời điểm cập nhật.")


class PersonaVersionModel(BaseModel):
    """24. Bảng `persona_versions` (Phiên bản hồ sơ Persona gốc — chứa 194 trường)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID.")
    bot_id: str = Field(..., description="ID bot.")
    version: int = Field(1, description="Số thứ tự phiên bản persona.")
    content_hash: str = Field(..., description="Mã băm SHA-256 nội dung persona.")
    content_json: Optional[PersonaVersionContentSchema] = Field(None, description="Toàn bộ 194 thuộc tính có định kiểu.")
    created_at: str = Field(..., description="Thời điểm tạo.")

    @field_validator("content_json", mode="before")
    @classmethod
    def parse_content(cls, v: object) -> object:
        return _parse_json_field(v)


class PlanningAttemptModel(BaseModel):
    """25. Bảng `planning_attempts` (Lịch sử các lần lập kế hoạch tuần của Planner)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID.")
    bot_id: str = Field(..., description="ID bot.")
    local_date: str = Field(..., description="Ngày lập lịch địa phương YYYY-MM-DD.")
    status: str = Field(..., description="Trạng thái (completed, failed).")
    request_json: Optional[PlanningAttemptRequestSchema] = Field(None, description="Yêu cầu lập lịch có định kiểu.")
    response_json: Optional[List[PlanningAttemptResponseItemSchema]] = Field(default_factory=list, description="Kết quả phân bổ lịch có định kiểu.")
    error: Optional[str] = Field(None, description="Chi tiết lỗi nếu thất bại.")
    created_at: str = Field(..., description="Thời điểm tạo.")

    @field_validator("request_json", "response_json", mode="before")
    @classmethod
    def parse_planning_jsons(cls, v: object) -> object:
        return _parse_json_field(v)


class ProfileBindingModel(BaseModel):
    """26. Bảng `profile_bindings` (Ràng buộc profile trình duyệt anti-detect với bot)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID.")
    bot_id: str = Field(..., description="ID bot.")
    manager_id: str = Field(..., description="ID trình quản lý browser (ví dụ: cloak-manager).")
    profile_id: str = Field(..., description="ID hồ sơ browser chống phát hiện.")
    platform: str = Field(..., description="Nền tảng mạng xã hội.")
    active: bool = Field(True, description="Profile đang hoạt động.")
    created_at: str = Field(..., description="Thời điểm tạo.")
    ended_at: Optional[str] = Field(None, description="Thời điểm kết thúc.")


class ResearchArtifactModel(BaseModel):
    """27. Bảng `research_artifacts` (Tài nguyên tra cứu web của tác tử)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID.")
    bot_id: str = Field(..., description="ID bot.")
    episode_id: Optional[str] = Field(None, description="ID episode nếu có.")
    query: str = Field(..., description="Từ khóa tra cứu.")
    url: str = Field(..., description="Đường dẫn nguồn tài liệu.")
    title: str = Field(..., description="Tiêu đề trang.")
    summary: str = Field(..., description="Tóm tắt nội dung thu thập.")
    source_domain: str = Field(..., description="Tên miền gốc.")
    confidence: float = Field(..., description="Độ tin cậy của tài nguyên.")
    verified: bool = Field(..., description="Đã được kiểm chứng.")
    used_in_decision: bool = Field(..., description="Đã được dùng làm căn cứ ra quyết định.")
    created_at: str = Field(..., description="Thời điểm tạo.")
    updated_at: str = Field(..., description="Thời điểm cập nhật.")


class RuntimeStateModel(BaseModel):
    """28. Bảng `runtime_state` (Trạng thái runtime toàn cục của orchestrator)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int = Field(..., description="Khóa chính ID.")
    enabled: bool = Field(..., description="Trạng thái kích hoạt hệ thống.")
    scheduler_lease_owner: Optional[str] = Field(None, description="Người nắm giữ khóa lập lịch.")
    scheduler_lease_until: Optional[str] = Field(None, description="Thời hạn khóa lập lịch.")
    heartbeat_at: Optional[str] = Field(None, description="Nhịp tim hệ thống gần nhất.")
    updated_at: str = Field(..., description="Thời điểm cập nhật.")


class SearchHistoryModel(BaseModel):
    """29. Bảng `search_history` (Lịch sử tìm kiếm Facebook trong episode)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="Khóa chính ID.")
    bot_id: str = Field(..., description="ID bot.")
    episode_id: str = Field(..., description="ID episode.")
    step_index: int = Field(..., description="Chỉ số bước thực hiện tìm kiếm.")
    platform: str = Field(..., description="Nền tảng (facebook).")
    query: str = Field(..., description="Nội dung từ khóa tìm kiếm.")
    purpose: str = Field(..., description="Mục đích tra cứu.")
    verified: bool = Field(..., description="Kết quả tra cứu đã được kiểm chứng.")
    outcome: str = Field(..., description="Kết quả tóm tắt sau khi tìm kiếm.")
    created_at: str = Field(..., description="Thời điểm tạo.")


class SettingModel(BaseModel):
    """30. Bảng `settings` (Cấu hình tham số hệ thống key-value)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    key: str = Field(..., description="Khóa cấu hình.")
    value: str = Field(..., description="Giá trị cấu hình dạng text/json.")


class SqliteSequenceModel(BaseModel):
    """31. Bảng `sqlite_sequence` (Bảng tự tăng nội bộ của SQLite)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    name: Optional[str] = Field(None, description="Tên bảng tự tăng.")
    seq: Optional[int] = Field(None, description="Giá trị tự tăng hiện tại.")
