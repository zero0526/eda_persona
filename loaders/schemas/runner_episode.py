"""Schema Pydantic định nghĩa toàn diện cấu trúc một Episode từ SQLite persona-runner.

Tài nguyên cơ sở dữ liệu:
- Database: persona-runner.sqlite (từ hệ thống runner Facebook autonomous agent)
- Định dạng: Chuẩn hóa toàn bộ quan hệ 1-1, 1-n, và các trường JSON payloads lồng nhau
  thành cấu trúc Pydantic v2 có kiểm kiểu nghiêm ngặt (Strict/Optional Typing).

Các thành phần chính của một Full Episode:
1. EpisodeMetadataSchema: Thông tin hành chính, trạng thái, thời gian chạy, video recording.
2. BotContextSchema: Danh tính bot, cấu hình persona nguyên bản & compiled JSON.
3. BehavioralContractSchema: Hợp đồng hành vi, ràng buộc nhịp độ (pacing), pacing rules.
4. ActivityWindowSchema: Cửa sổ hoạt động được lập lịch, surface bias, budget hành động.
5. LiveRunSchema: Trạng thái runtime thực thi live của tác tử.
6. WorkingMemorySnapshotSchema: Ảnh chụp bộ nhớ làm việc (elapsed, remaining, recent actions).
7. DecisionEvidenceItemSchema: Căn cứ quyết định dựa trên các chiều Persona (grounding).
8. EpisodeStepSchema: Chi tiết từng bước thực thi (Perception, Decision, Outcome, Latency, Gestures).
9. EpisodeEventSchema: Dòng sự kiện thời gian thực (start, observation, tool_result, stop).
10. SearchHistorySchema: Lịch sử các truy vấn tìm kiếm Facebook trong episode.
11. MemoryConsolidationSchema & MemoryDeltaSchema: Tiến hóa bộ nhớ dài hạn sau episode.
12. HabitFactSchema: Các sự kiện thói quen được ghi nhận.
13. ActiveEntitySchema & ActiveThreadSchema: Thực thể và luồng sở thích liên quan episode.
14. FullEpisodeSchema: Thực thể đóng gói tối cao, tích hợp các phương thức xuất DataFrame phục vụ EDA.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, ConfigDict
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# ==============================================================================
# 1. EPISODE METADATA & ADMINISTRATIVE CONTEXT
# ==============================================================================
class EpisodeMetadataSchema(BaseModel):
    """Thông tin metadata định danh và hành chính của một Episode từ bảng `episodes`."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="UUID định danh duy nhất của episode.")
    window_id: Optional[str] = Field(None, description="UUID liên kết tới bảng `activity_windows`.")
    bot_id: Optional[str] = Field(None, description="UUID của tác tử bot thực hiện episode.")
    profile_id: Optional[str] = Field(None, description="UUID của profile trình duyệt chống phát hiện (anti-detect browser).")
    contract_id: Optional[str] = Field(None, description="UUID của hợp đồng hành vi (`behavioral_contracts`).")
    runtime_provider: Optional[str] = Field(None, description="Tên runtime provider (ví dụ: 'operator-run-now', 'scheduler').")
    status: str = Field(..., description="Trạng thái hoàn thành của episode (done, failed, running, stopped).")
    started_at: Optional[str] = Field(None, description="Thời điểm bắt đầu phiên dạng ISO 8601 UTC.")
    ended_at: Optional[str] = Field(None, description="Thời điểm kết thúc phiên dạng ISO 8601 UTC.")
    lease_until: Optional[str] = Field(None, description="Thời hạn khóa giữ quyền thực thi tài nguyên.")
    summary: Optional[str] = Field(None, description="Tóm tắt tổng quan phiên chạy do hệ thống hoặc LLM tạo ra.")
    terminal_reason: Optional[str] = Field(None, description="Lý do kết thúc phiên (ví dụ: 'agent_stop', 'episode_error', 'timeout').")
    video_path: Optional[str] = Field(None, description="Đường dẫn tệp video màn hình ghi lại toàn bộ phiên (.webm).")
    duration_seconds: Optional[float] = Field(None, description="Tổng thời lượng thực thi tính bằng giây.")


# ==============================================================================
# 2. BOT & PERSONA CONTEXT
# ==============================================================================
class BotContextSchema(BaseModel):
    """Bối cảnh bot và persona thực thi phiên từ bảng `bots` và `persona_versions`."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    bot_id: str = Field(..., description="UUID của bot.")
    persona_id: Optional[str] = Field(None, description="Mã định danh persona (ví dụ: 'vn_fb_003', 'vn_fb_001').")
    bot_status: Optional[str] = Field(None, description="Trạng thái của bot (active, paused, retired).")
    bot_created_at: Optional[str] = Field(None, description="Thời điểm tạo bot.")
    persona_version_id: Optional[str] = Field(None, description="UUID phiên bản persona trong `persona_versions`.")
    persona_version: Optional[int] = Field(None, description="Số thứ tự phiên bản persona (version).")
    persona_content_hash: Optional[str] = Field(None, description="Mã băm SHA-256 nội dung persona.")
    persona_name: Optional[str] = Field(None, description="Tên persona (nếu có trong content_json).")
    persona_demographics: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Thông tin nhân khẩu học (tuổi, giới tính, nghề nghiệp).")
    persona_traits: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Các đặc tính tâm lý, tính cách Big Five.")
    persona_interests: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Ma trận sở thích và xu hướng nội dung.")
    full_persona_json: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Toàn bộ JSON cấu hình persona nguyên bản.")


# ==============================================================================
# 3. BEHAVIORAL CONTRACT & ACTIVITY WINDOW
# ==============================================================================
class BehavioralContractSchema(BaseModel):
    """Hợp đồng ràng buộc hành vi từ bảng `behavioral_contracts`."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="UUID định danh hợp đồng hành vi.")
    schema_version: Optional[Union[str, int]] = Field(None, description="Phiên bản schema hợp đồng.")
    source_hash: Optional[str] = Field(None, description="Mã băm nguồn của hợp đồng.")
    contract_rules: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Các điều khoản hành vi, pacing, giới hạn tương tác.")
    compiler_trace: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Trace quá trình biên dịch hợp đồng.")
    created_at: Optional[str] = Field(None, description="Thời điểm tạo hợp đồng.")


class ActivityWindowSchema(BaseModel):
    """Cửa sổ hoạt động được lập lịch từ bảng `activity_windows`."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: str = Field(..., description="UUID của activity window.")
    local_date: Optional[str] = Field(None, description="Ngày chạy theo giờ địa phương (YYYY-MM-DD).")
    start_at: Optional[str] = Field(None, description="Thời điểm bắt đầu cửa sổ hoạt động.")
    end_at: Optional[str] = Field(None, description="Thời điểm kết thúc cửa sổ hoạt động.")
    max_actions: Optional[int] = Field(None, description="Số lượng hành động tối đa cho phép trong cửa sổ.")
    seed: Optional[Union[str, int]] = Field(None, description="Seed ngẫu nhiên hóa hành vi.")
    surface_bias: Optional[str] = Field(None, description="Định hướng bề mặt ưu tiên (feed, group, search, ...).")
    state: Optional[str] = Field(None, description="Trạng thái cửa sổ (completed, claimed, expired).")
    terminal_reason: Optional[str] = Field(None, description="Lý do hoàn tất cửa sổ.")


# ==============================================================================
# 4. RUNTIME STATE & WORKING MEMORY
# ==============================================================================
class LiveRunSchema(BaseModel):
    """Trạng thái thực thi live từ bảng `agent_live_runs`."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    status: Optional[str] = Field(None, description="Trạng thái thực thi hiện tại.")
    started_at: Optional[str] = Field(None, description="Thời điểm bắt đầu chạy.")
    updated_at: Optional[str] = Field(None, description="Thời điểm cập nhật cuối.")
    error: Optional[str] = Field(None, description="Chi tiết lỗi nếu phiên thất bại.")
    state_json: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dữ liệu trạng thái nội bộ của runner.")


class WorkingMemorySnapshotSchema(BaseModel):
    """Ảnh chụp bộ nhớ làm việc ngắn hạn từ bảng `episode_working_memory`."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    snapshot_updated_at: Optional[str] = Field(None, description="Thời điểm lưu snapshot.")
    completed_actions: Optional[int] = Field(None, description="Số hành động đã hoàn tất trong phiên.")
    current_surface: Optional[str] = Field(None, description="Bề mặt giao diện hiện tại của tác tử.")
    elapsed_seconds: Optional[float] = Field(None, description="Thời gian đã chạy (giây).")
    planned_active_seconds: Optional[float] = Field(None, description="Thời lượng mục tiêu của phiên (giây).")
    planned_session_minutes: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Khoảng thời lượng dự kiến min/max (phút).")
    remaining_seconds: Optional[float] = Field(None, description="Thời gian ngân sách còn lại (giây).")
    recent_actions: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Danh sách các hành động gần nhất lưu trong working memory.")
    search_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Ngữ cảnh tìm kiếm hiện tại nếu có.")
    raw_snapshot: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Toàn bộ JSON snapshot bộ nhớ gốc.")


# ==============================================================================
# 5. DECISION EVIDENCE (PERSONA GROUNDING)
# ==============================================================================
class DecisionEvidenceItemSchema(BaseModel):
    """Một căn cứ thuộc tính persona giải trình cho hành động (Grounding Attribution)."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    dimension: str = Field(..., description="Tên chiều đặc tính persona (ví dụ: 'interest_film', 'curiosity').")
    role: str = Field(
        "primary",
        description="Vai trò căn cứ trong việc dẫn dắt hành động (primary, supporting, situational, opposing, v.v.)."
    )
    source: str = Field("persona", description="Nguồn gốc căn cứ (persona, neutral_control, session_memory, v.v.).")
    value: Any = Field(..., description="Giá trị thuộc tính persona (ví dụ: 'Rất đam mê', 'Cao', 0.8).")
    weight: float = Field(0.0, description="Trọng số ảnh hưởng của chiều đặc tính này (0.0 đến 1.0).")
    reference_id: Optional[str] = Field(None, description="Mã tham chiếu hoặc chú thích bổ sung.")


class DecisionEvidenceRecordSchema(BaseModel):
    """Bản ghi căn cứ quyết định từ bảng `decision_evidence`."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Optional[Union[str, int]] = Field(None, description="ID của bản ghi evidence.")
    step_index: int = Field(..., description="Số thứ tự bước hành động.")
    action: str = Field(..., description="Tên hành động tương ứng (ví dụ: 'scroll_feed', 'read_visible_post').")
    items: List[DecisionEvidenceItemSchema] = Field(default_factory=list, description="Danh sách các chiều persona giải trình.")
    created_at: Optional[str] = Field(None, description="Thời điểm ghi nhận căn cứ.")


# ==============================================================================
# 6. STEP EXECUTION DETAIL (AGENT LIVE STEPS)
# ==============================================================================
class StepDecisionContextSchema(BaseModel):
    """Ngữ cảnh mục tiêu và luồng tương tác của quyết định hành động."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    topic: Optional[str] = Field(None, description="Chủ đề nội dung đang tương tác.")
    purpose: Optional[str] = Field(None, description="Mục đích nhận thức của hành động.")
    state: Optional[str] = Field(None, description="Trạng thái tâm lý/hành vi (ví dụ: 'exploring', 'active').")
    continuation: Optional[str] = Field(None, description="Chỉ định tiếp tục hay chuyển mạch ('continue', 'finish').")
    interest_relation: Optional[str] = Field(None, description="Quan hệ với luồng sở thích ('situational', 'aligned').")
    open_question: Optional[str] = Field(None, description="Câu hỏi mở mà tác tử tò mò muốn tìm lời giải.")
    thread_id: Optional[str] = Field(None, description="ID luồng quan tâm liên kết.")


class EpisodeStepSchema(BaseModel):
    """Chi tiết thực thi đầy đủ của một bước (Step) từ bảng `agent_live_steps`."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    step_index: int = Field(..., description="Chỉ số bước thực thi (1, 2, 3...).")
    created_at: Optional[str] = Field(None, description="Thời điểm ghi nhận bước trong database.")
    timestamp: Optional[str] = Field(None, description="Thời điểm bước được sinh ra từ LLM runner.")

    # 1. Quyết định (Decision)
    tool: str = Field(..., description="Tool cấp cao mà LLM gọi ('act', 'end_episode', 'observe_viewport', 'session_status').")
    intent: Optional[str] = Field(None, description="Ý định hành vi được giải mã ('scroll', 'read', 'react', 'comment', 'search', 'open', 'observe').")
    target_id: Optional[str] = Field(None, description="ID phần tử giao diện mục tiêu trên màn hình (ví dụ: 'visible-200', 'feed:scroll').")
    action_summary: Optional[str] = Field(None, description="Tóm tắt hành động do LLM sinh ra.")
    reason: Optional[str] = Field(None, description="Lý do và chuỗi suy luận (chain-of-thought) của tác tử cho quyết định này.")
    args: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Tham số chi tiết truyền vào tool.")
    decision_context: Optional[StepDecisionContextSchema] = Field(None, description="Ngữ cảnh nhận thức của quyết định.")

    # 2. Kết quả (Outcome)
    verified: Optional[bool] = Field(None, description="Trạng thái xác minh thành công trên DOM trình duyệt (True = thành công, False = lỗi).")
    ended: Optional[bool] = Field(False, description="Cờ đánh dấu bước này có kết thúc toàn bộ episode hay không.")
    evidence_text: Optional[str] = Field(None, description="Chuỗi bằng chứng vật lý hoặc mô tả kết quả trả về từ trình duyệt.")
    surface: Optional[str] = Field(None, description="Bề mặt giao diện nơi thực hiện hành vi ('feed', 'detail', 'group', 'search', 'unknown').")
    resolved_tool: Optional[str] = Field(None, description="Tool hạ tầng cấp thấp được thực thi ('scroll_feed', 'read_visible_post', ...).")
    execution_duration_ms: Optional[int] = Field(None, description="Thời gian thực thi thao tác trên trình duyệt tính bằng mili-giây.")
    error: Optional[str] = Field(None, description="Thông báo lỗi nếu bước thực thi thất bại.")

    # 3. Các chỉ số cử chỉ vật lý (Physical Gesture Metrics - trích xuất từ evidence)
    gesture_pace: Optional[str] = Field(None, description="Nhịp độ cuộn/thao tác vật lý ('fast', 'careful', 'moderate').")
    gesture_total_px: Optional[int] = Field(None, description="Quãng đường cuộn vật lý tính bằng pixel (px).")
    gesture_ms: Optional[int] = Field(None, description="Thời gian thực hiện cử chỉ cuộn bánh xe chuột (ms).")
    gesture_direction: Optional[str] = Field(None, description="Hướng cuộn ('down', 'up').")
    landing_correction_px: Optional[int] = Field(None, description="Độ bù hiệu chỉnh hạ cánh (landing correction) pixel sau khi cuộn.")
    action_url: Optional[str] = Field(None, description="URL Facebook được tương tác trong bước nếu có.")
    url_type: Optional[str] = Field(None, description="Loại liên kết URL ('feed', 'group', 'post', 'search', 'reel').")
    execution_mode: Optional[str] = Field(None, description="Cơ chế thực thi ('smooth_wheel', 'native_click', 'native_search', 'read_post', 'cdp_fallback').")

    # 4. Nhận thức & DOM (Perception)
    perception: Optional[str] = Field(None, description="Tóm tắt nhận thức của tác tử về các phần tử và affordance khả dụng trên viewport.")

    # 5. Hiệu năng & LLM Usage (Debug)
    model_latency_ms: Optional[int] = Field(None, description="Độ trễ phản hồi từ API mô hình ngôn ngữ (ms).")
    tool_execution_ms: Optional[int] = Field(None, description="Độ trễ thực thi tool và thao tác browser (ms).")
    prompt_tokens: Optional[int] = Field(None, description="Số lượng token đầu vào (prompt tokens).")
    completion_tokens: Optional[int] = Field(None, description="Số lượng token đầu ra (completion tokens).")
    total_tokens: Optional[int] = Field(None, description="Tổng token tiêu thụ cho bước này.")

    # 6. Căn cứ Persona (Grounding Attributions)
    dimension_evidence: List[DecisionEvidenceItemSchema] = Field(
        default_factory=list,
        description="Danh sách các chiều thuộc tính Persona giải trình cho bước này."
    )


# ==============================================================================
# 7. EVENT TIMELINE & AUDIT LOGS
# ==============================================================================
class EpisodeEventSchema(BaseModel):
    """Một sự kiện trong dòng thời gian của episode từ bảng `episode_events`."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Union[str, int] = Field(..., description="ID của sự kiện (UUID hoặc integer auto-increment).")
    kind: str = Field(..., description="Loại sự kiện (episode_start, observation, tool_result, agent_stop, video_recording_saved, ...).")
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Payload chi tiết của sự kiện.")
    created_at: Optional[str] = Field(None, description="Thời điểm ghi nhận sự kiện dạng ISO 8601 UTC.")


# ==============================================================================
# 8. SEARCH HISTORY
# ==============================================================================
class SearchHistorySchema(BaseModel):
    """Bản ghi truy vấn tìm kiếm từ bảng `search_history`."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Union[str, int] = Field(..., description="ID bản ghi tìm kiếm (UUID hoặc integer).")
    step_index: Optional[int] = Field(None, description="Bước thực hiện tìm kiếm.")
    platform: Optional[str] = Field("facebook", description="Nền tảng tìm kiếm.")
    query: str = Field(..., description="Từ khóa tìm kiếm đã nhập.")
    purpose: Optional[str] = Field(None, description="Mục đích nhận thức của truy vấn tìm kiếm.")
    verified: Optional[bool] = Field(None, description="Trạng thái thực thi trang tìm kiếm thành công.")
    outcome: Optional[str] = Field(None, description="URL hoặc kết quả trả về sau tìm kiếm.")
    created_at: Optional[str] = Field(None, description="Thời điểm tìm kiếm.")


# ==============================================================================
# 9. LONG-TERM MEMORY EVOLUTION (CONSOLIDATION & DELTAS)
# ==============================================================================
class MemoryDeltaSchema(BaseModel):
    """Một biến đổi bộ nhớ dài hạn phát sinh từ episode trong bảng `memory_delta_ledger`."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Optional[Union[str, int]] = Field(None, description="ID bản ghi delta.")
    record_type: str = Field(..., description="Loại thực thể bộ nhớ được cập nhật ('thread', 'entity', 'affinity').")
    record_key: str = Field(..., description="Khóa định danh của đối tượng bộ nhớ (ví dụ slug luồng quan tâm, url trang).")
    operation: str = Field(..., description="Thao tác biến đổi ('upsert', 'create', 'update', 'decay').")
    before: Optional[Any] = Field(None, description="Trạng thái trước khi hợp nhất.")
    after: Optional[Any] = Field(None, description="Trạng thái mới sau khi hợp nhất.")
    evidence: Optional[Any] = Field(None, description="Bằng chứng từ các bước hành động chứng minh cho việc học.")
    created_at: Optional[str] = Field(None, description="Thời điểm ghi nhận delta.")


class MemoryConsolidationSchema(BaseModel):
    """Bản ghi phiên hợp nhất bộ nhớ dài hạn từ bảng `memory_consolidation_runs`."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Optional[Union[str, int]] = Field(None, description="ID phiên hợp nhất.")
    status: Optional[str] = Field(None, description="Trạng thái hợp nhất (success, failed).")
    input_event_count: Optional[int] = Field(None, description="Số lượng sự kiện hành động được đưa vào phân tích.")
    learned_count: Optional[int] = Field(None, description="Số lượng tri thức mới được tác tử học.")
    error: Optional[str] = Field(None, description="Chi tiết lỗi nếu quá trình học thất bại.")
    result_json: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Kết quả chi tiết gồm proposal và learned items.")
    created_at: Optional[str] = Field(None, description="Thời điểm kết thúc hợp nhất.")


# ==============================================================================
# 10. HABIT FACTS & ASSOCIATED ENTITIES / THREADS
# ==============================================================================
class HabitFactSchema(BaseModel):
    """Bản ghi sự kiện hình thành thói quen từ bảng `habit_facts`."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Union[str, int] = Field(..., description="ID sự kiện thói quen.")
    kind: str = Field(..., description="Loại sự kiện thói quen (ví dụ: 'interaction_outcome', 'session_timing').")
    value: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dữ liệu chi tiết về thói quen.")
    created_at: Optional[str] = Field(None, description="Thời điểm ghi nhận.")


class ActiveEntitySchema(BaseModel):
    """Thực thể Facebook mà tác tử phát sinh độ gắn kết (affinity) liên quan tới episode này."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Union[str, int] = Field(..., description="ID thực thể.")
    entity_type: Optional[str] = Field(None, description="Loại thực thể (source, group, page, user).")
    entity_key: Optional[str] = Field(None, description="URL hoặc key của thực thể.")
    display_name: Optional[str] = Field(None, description="Tên hiển thị của trang/nhóm/thực thể.")
    affinity: Optional[float] = Field(None, description="Điểm gắn kết (affinity score) từ 0.0 đến 1.0.")
    familiarity: Optional[float] = Field(None, description="Mức độ quen thuộc.")
    evidence_count: Optional[int] = Field(None, description="Số lượng bằng chứng tương tác ghi nhận.")
    relationship_state: Optional[str] = Field(None, description="Trạng thái quan hệ (provisional, established).")
    updated_at: Optional[str] = Field(None, description="Thời điểm cập nhật cuối.")


class ActiveThreadSchema(BaseModel):
    """Luồng sở thích/chủ đề dài hạn mà episode này tác động hoặc tiếp tục theo đuổi."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Union[str, int] = Field(..., description="ID luồng quan tâm.")
    thread_key: str = Field(..., description="Khóa định danh slug của chủ đề (ví dụ: 'am-thuc-duong-pho-da-nang').")
    title: Optional[str] = Field(None, description="Tiêu đề luồng sở thích.")
    summary: Optional[str] = Field(None, description="Tóm tắt nhận thức tiến trình luồng sở thích.")
    confidence: Optional[float] = Field(None, description="Độ tin cậy của mô hình về sở thích này (0.0 đến 1.0).")
    evidence_count: Optional[int] = Field(None, description="Số lượng bằng chứng tích lũy.")
    status: Optional[str] = Field(None, description="Trạng thái luồng ('active', 'dormant').")
    updated_at: Optional[str] = Field(None, description="Thời điểm cập nhật cuối.")


# ==============================================================================
# 11. TOP-LEVEL CONTAINER: FULL EPISODE SCHEMA
# ==============================================================================
class FullEpisodeSchema(BaseModel):
    """Thực thể đóng gói hoàn chỉnh một Episode Facebook Agent sẵn sàng cho phân tích EDA.

    Tích hợp toàn bộ:
    - Metadata hành chính & Video
    - Bối cảnh Bot & Persona
    - Hợp đồng hành vi & Hoạt động
    - Trạng thái live run & Bộ nhớ làm việc
    - Danh sách các bước thực thi Step-by-Step
    - Dòng sự kiện Timeline
    - Lịch sử tìm kiếm
    - Tiến hóa bộ nhớ dài hạn (Consolidation & Deltas)
    - Các thực thể và luồng sở thích liên quan

    Cung cấp các phương thức xuất DataFrame chuyên dụng:
    - `to_steps_dataframe()`: Bảng DataFrame chi tiết từng bước phục vụ kiểm định thống kê.
    - `to_events_dataframe()`: Bảng DataFrame dòng sự kiện.
    - `to_searches_dataframe()`: Bảng DataFrame các từ khóa tìm kiếm.
    - `to_deltas_dataframe()`: Bảng DataFrame các cập nhật bộ nhớ dài hạn.
    - `get_summary()`: Từ điển tóm lược các chỉ số cốt lõi.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    metadata: EpisodeMetadataSchema = Field(..., description="Thông tin hành chính của phiên.")
    bot: Optional[BotContextSchema] = Field(None, description="Bối cảnh bot và persona.")
    contract: Optional[BehavioralContractSchema] = Field(None, description="Hợp đồng hành vi.")
    window: Optional[ActivityWindowSchema] = Field(None, description="Cửa sổ hoạt động.")
    run: Optional[LiveRunSchema] = Field(None, description="Trạng thái thực thi live.")
    working_memory: Optional[WorkingMemorySnapshotSchema] = Field(None, description="Ảnh chụp bộ nhớ ngắn hạn.")
    steps: List[EpisodeStepSchema] = Field(default_factory=list, description="Danh sách các bước thực thi tuần tự của tác tử.")
    decision_evidences: List[DecisionEvidenceRecordSchema] = Field(default_factory=list, description="Toàn bộ bản ghi căn cứ persona theo bước.")
    events: List[EpisodeEventSchema] = Field(default_factory=list, description="Dòng thời gian sự kiện của phiên.")
    searches: List[SearchHistorySchema] = Field(default_factory=list, description="Lịch sử các lượt tìm kiếm Facebook.")
    consolidation: Optional[MemoryConsolidationSchema] = Field(None, description="Phiên hợp nhất bộ nhớ dài hạn sau episode.")
    deltas: List[MemoryDeltaSchema] = Field(default_factory=list, description="Các cập nhật delta vào bộ nhớ dài hạn.")
    habits: List[HabitFactSchema] = Field(default_factory=list, description="Các sự kiện thói quen được lưu lại.")
    active_entities: List[ActiveEntitySchema] = Field(default_factory=list, description="Các thực thể gắn kết liên quan.")
    active_threads: List[ActiveThreadSchema] = Field(default_factory=list, description="Các luồng quan tâm liên quan.")

    def to_steps_dataframe(self) -> pd.DataFrame:
        """Chuyển đổi danh sách steps thành pandas DataFrame chuẩn hóa phục vụ EDA."""
        records = []
        for s in self.steps:
            # Lấy thông tin persona grounding ưu tiên
            primary_dim = None
            primary_val = None
            primary_weight = None
            for d in s.dimension_evidence:
                if d.role == "primary":
                    primary_dim = d.dimension
                    primary_val = str(d.value)
                    primary_weight = d.weight
                    break
            if not primary_dim and s.dimension_evidence:
                primary_dim = s.dimension_evidence[0].dimension
                primary_val = str(s.dimension_evidence[0].value)
                primary_weight = s.dimension_evidence[0].weight

            row = {
                "episode_id": self.metadata.id,
                "persona_id": self.bot.persona_id if self.bot else None,
                "step_index": s.step_index,
                "created_at": s.created_at,
                "timestamp": s.timestamp,
                "tool": s.tool,
                "intent": s.intent,
                "surface": s.surface,
                "resolved_tool": s.resolved_tool,
                "verified": s.verified,
                "ended": s.ended,
                "target_id": s.target_id,
                "action_summary": s.action_summary,
                "reason": s.reason,
                "execution_duration_ms": s.execution_duration_ms,
                "model_latency_ms": s.model_latency_ms,
                "tool_execution_ms": s.tool_execution_ms,
                "prompt_tokens": s.prompt_tokens,
                "completion_tokens": s.completion_tokens,
                "total_tokens": s.total_tokens,
                "gesture_pace": s.gesture_pace,
                "gesture_total_px": s.gesture_total_px,
                "gesture_ms": s.gesture_ms,
                "gesture_direction": s.gesture_direction,
                "landing_correction_px": s.landing_correction_px,
                "action_url": s.action_url,
                "url_type": s.url_type,
                "execution_mode": s.execution_mode,
                "primary_dimension": primary_dim,
                "primary_value": primary_val,
                "primary_weight": primary_weight,
                "evidence_dimension_count": len(s.dimension_evidence),
                "error": s.error,
                "perception": s.perception,
            }
            records.append(row)

        df = pd.DataFrame(records)
        return df

    def to_events_dataframe(self) -> pd.DataFrame:
        """Chuyển đổi toàn bộ events thành pandas DataFrame."""
        records = []
        for ev in self.events:
            records.append({
                "episode_id": self.metadata.id,
                "event_id": ev.id,
                "kind": ev.kind,
                "created_at": ev.created_at,
                "payload_json": json.dumps(ev.payload, ensure_ascii=False) if ev.payload else None,
            })
        return pd.DataFrame(records)

    def to_searches_dataframe(self) -> pd.DataFrame:
        """Chuyển đổi lịch sử tìm kiếm thành DataFrame."""
        records = []
        for sc in self.searches:
            records.append({
                "episode_id": self.metadata.id,
                "search_id": sc.id,
                "step_index": sc.step_index,
                "platform": sc.platform,
                "query": sc.query,
                "purpose": sc.purpose,
                "verified": sc.verified,
                "outcome": sc.outcome,
                "created_at": sc.created_at,
            })
        return pd.DataFrame(records)

    def to_deltas_dataframe(self) -> pd.DataFrame:
        """Chuyển đổi các biến đổi bộ nhớ dài hạn thành DataFrame."""
        records = []
        for dl in self.deltas:
            records.append({
                "episode_id": self.metadata.id,
                "delta_id": dl.id,
                "record_type": dl.record_type,
                "record_key": dl.record_key,
                "operation": dl.operation,
                "evidence": json.dumps(dl.evidence, ensure_ascii=False) if dl.evidence else None,
                "created_at": dl.created_at,
            })
        return pd.DataFrame(records)

    def get_summary(self) -> Dict[str, Any]:
        """Tạo từ điển tổng hợp các chỉ số trọng yếu của episode."""
        step_count = len(self.steps)
        verified_steps = sum(1 for s in self.steps if s.verified is True)
        success_rate = (verified_steps / step_count) if step_count > 0 else 0.0
        total_tokens = sum(s.total_tokens or 0 for s in self.steps)

        # Tính tổng quãng đường cuộn
        total_scroll_px = sum(s.gesture_total_px or 0 for s in self.steps if s.gesture_total_px)

        # Bề mặt xuất hiện
        surfaces = {}
        for s in self.steps:
            sf = s.surface or "unknown"
            surfaces[sf] = surfaces.get(sf, 0) + 1

        # Ý định phân bố
        intents = {}
        for s in self.steps:
            it = s.intent or s.tool
            intents[it] = intents.get(it, 0) + 1

        return {
            "episode_id": self.metadata.id,
            "persona_id": self.bot.persona_id if self.bot else None,
            "status": self.metadata.status,
            "terminal_reason": self.metadata.terminal_reason,
            "started_at": self.metadata.started_at,
            "ended_at": self.metadata.ended_at,
            "duration_seconds": self.metadata.duration_seconds,
            "total_steps": step_count,
            "verified_steps": verified_steps,
            "step_success_rate": round(success_rate, 4),
            "total_tokens_consumed": total_tokens,
            "total_scroll_px": total_scroll_px,
            "searches_count": len(self.searches),
            "memory_deltas_count": len(self.deltas),
            "surface_distribution": surfaces,
            "intent_distribution": intents,
            "video_path": self.metadata.video_path,
        }
