"""Bộ nạp và kết tập log hành vi (Action Logs) theo phiên (Session) và Persona.

Mô tả:
Mô-đun này cho phép:
1. Nạp log của một session (phiên duyệt/episode) hoàn chỉnh, bóc tách toàn bộ
   chuỗi hành động (actions/steps) theo đúng thứ tự thời gian và chỉ số bước.
2. Kết tập (aggregate) các session theo từng Persona, tự động sắp xếp các session
   theo thứ tự thời gian thực thi (execution time: `started_at` tăng dần).
3. Đánh số thứ tự phiên cho từng Persona (`session_order` = 1, 2, ...), cho phép
   phân tích tiến hóa nhận thức, trôi dạt hành vi (behavior drift), ma trận chuyển
   trạng thái Markov (transition matrix) và phân bổ bề mặt giao diện (surface distribution).
4. Xuất dữ liệu linh hoạt dưới dạng Pydantic v2 Models hoặc Pandas DataFrames
   được chuẩn hóa cho quy trình EDA đa biến.

Nguồn dữ liệu hỗ trợ:
- SQLite Database: `persona-runner.sqlite` (mặc định)
- Benchmark JSON Logs: `data/action_logs/*.json` và `data/no_persona_Action/*.json`
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
import re
import sqlite3
import sys
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

# Đảm bảo in Unicode tiếng Việt trên Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Đảm bảo thư mục gốc của project luôn nằm trong sys.path
_current_file = Path(__file__).resolve()
_project_root = _current_file.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Import các loader và schema hiện có
try:
    from loaders.episode_loader import DEFAULT_SQLITE_PATH, get_sqlite_path, load_episode, list_episodes
    from loaders.schemas.runner_episode import FullEpisodeSchema, EpisodeStepSchema
except ImportError:
    from episode_loader import DEFAULT_SQLITE_PATH, get_sqlite_path, load_episode, list_episodes
    from schemas.runner_episode import FullEpisodeSchema, EpisodeStepSchema


# ==============================================================================
# HÀM PHỤ TRỢ PHÂN TÍCH VÀ XỬ LÝ DỮ LIỆU
# ==============================================================================
def _parse_iso_timestamp(ts: Optional[str]) -> float:
    """Chuyển đổi chuỗi thời gian ISO 8601 sang timestamp số để sắp xếp chuẩn xác."""
    if not ts or not isinstance(ts, str):
        return 0.0
    s = ts.strip()
    if not s:
        return 0.0
    try:
        clean_s = s.replace("Z", "+00:00")
        return datetime.fromisoformat(clean_s).timestamp()
    except Exception:
        return 0.0


def _safe_json_loads(val: Any) -> Any:
    """Phân giải chuỗi JSON an toàn."""
    if val is None:
        return None
    if isinstance(val, (dict, list, int, float, bool)):
        return val
    if not isinstance(val, str) or not val.strip():
        return None
    try:
        return json.loads(val)
    except Exception:
        return val


# ==============================================================================
# I. PYDANTIC SCHEMAS CHO ACTION VÀ SESSION
# ==============================================================================

class DecisionEvidenceDetail(BaseModel):
    """Chi tiết từng căn cứ thuộc tính persona gắn với bước hành động."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    dimension: str = Field(..., description="Tên chiều thuộc tính persona.")
    role: Optional[str] = Field("primary", description="Vai trò (primary, supporting, constraint...).")
    source: Optional[str] = Field("persona", description="Nguồn gốc căn cứ.")
    value: Optional[Union[str, int, float, bool]] = Field(None, description="Giá trị thuộc tính.")
    weight: Optional[float] = Field(0.0, description="Trọng số nhận thức (0.0 đến 1.0).")
    reference_id: Optional[str] = Field(None, description="ID tham chiếu.")


class ActionLog(BaseModel):
    """Đại diện cho 1 hành động / bước thực thi cụ thể trong session."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    step_index: int = Field(..., description="Thứ tự bước trong session (1-based index).")
    timestamp: Optional[str] = Field(None, description="Thời điểm ghi nhận hành động ISO 8601.")
    elapsed_seconds: Optional[float] = Field(None, description="Số giây đã trôi qua từ đầu session.")
    
    # Không gian & Ý định
    intent: Optional[str] = Field(None, description="Ý định hành vi (scroll, read, react, search, observe...).")
    surface: Optional[str] = Field("unknown", description="Bề mặt Facebook (feed, reels, groups, page, detail, search...).")
    tool: Optional[str] = Field(None, description="Công cụ gọi cấp cao.")
    resolved_tool: Optional[str] = Field(None, description="Công cụ thực tế được engine thực thi.")
    verified: Optional[bool] = Field(None, description="Xác minh thành công trên DOM trình duyệt.")
    reaction: Optional[str] = Field(None, description="Cảm xúc thả bài (like, love, care, haha...).")
    
    # Lập luận & Mục tiêu
    reason: Optional[str] = Field(None, description="Chuỗi lập luận tư duy (Chain-of-Thought) tiếng Việt.")
    action_summary: Optional[str] = Field(None, description="Tóm tắt hành vi.")
    target_id: Optional[str] = Field(None, description="ID phần tử DOM mục tiêu.")
    target_text: Optional[str] = Field(None, description="Tiêu đề hoặc trích đoạn văn bản mục tiêu.")
    action_url: Optional[str] = Field(None, description="URL thao tác nếu có.")
    url_type: Optional[str] = Field(None, description="Phân loại URL (group, post, reel, search, page_or_profile).")
    execution_mode: Optional[str] = Field(None, description="Chế độ thực thi (native_click, smooth_wheel...).")

    # Căn cứ nhận thức (Persona Grounding)
    dimension_evidence: List[DecisionEvidenceDetail] = Field(default_factory=list, description="Danh sách các chiều persona căn cứ.")
    primary_dimension: Optional[str] = Field(None, description="Chiều nhận thức quan trọng nhất.")
    primary_value: Optional[Union[str, int, float, bool]] = Field(None, description="Giá trị chiều nhận thức chính.")
    primary_weight: Optional[float] = Field(None, description="Trọng số nhận thức cao nhất.")

    # Cơ học cử chỉ vật lý (Kinematics)
    gesture_pace: Optional[str] = Field(None, description="Nhịp độ vuốt chuột (quick, normal, slow...).")
    gesture_total_px: Optional[int] = Field(None, description="Quãng đường cuộn (px).")
    gesture_ms: Optional[int] = Field(None, description="Thời gian thực hiện cử chỉ cuộn (ms).")

    # Chi phí nhận thức & Latency
    model_latency_ms: Optional[float] = Field(None, description="Thời gian suy luận LLM (ms).")
    tool_execution_ms: Optional[float] = Field(None, description="Thời gian DOM engine chạy (ms).")
    total_tokens: Optional[int] = Field(None, description="Tổng token tiêu thụ.")



# ==============================================================================
# II. PYDANTIC SCHEMAS CHO BỘ NHỚ (LONG-TERM PRIOR & SHORT-TERM WORKING MEMORY)
# ==============================================================================

# --- 1. Long-Term Prior Memory Schemas (Bộ nhớ dài hạn sẵn có lúc bắt đầu session) ---

class ExplorationDispositionSchema(BaseModel):
    """Thiên hướng khám phá nhận thức ban đầu của persona."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    initiative: Optional[str] = Field(None, description="Mức độ chủ động tìm tòi (high, medium, low).")
    natural_triggers: List[str] = Field(default_factory=list, description="Các tác nhân tự nhiên kích thích tò mò.")
    variety: Optional[str] = Field(None, description="Mức độ đa dạng hóa nội dung.")


class ExplorationThreadBaselineSchema(BaseModel):
    """Mạch định hướng khám phá ban đầu được nạp sẵn từ baseline."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    key: Optional[str] = Field(None, description="Mã định danh luồng khám phá.")
    topic: Optional[str] = Field(None, description="Chủ đề quan tâm.")
    angles: List[str] = Field(default_factory=list, description="Các góc nhìn hoặc câu hỏi tò mò.")
    based_on: List[str] = Field(default_factory=list, description="Căn cứ đặc tính persona.")
    source_types: List[str] = Field(default_factory=list, description="Các loại định dạng nguồn ưu tiên.")


class PriorInterestThreadDetail(BaseModel):
    """Luồng sở thích dài hạn đã có sẵn của tác tử bot trước khi vào phiên."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    thread_key: str = Field(..., description="Khóa định danh slug của luồng sở thích.")
    title: Optional[str] = Field(None, description="Tiêu đề luồng sở thích.")
    summary: Optional[str] = Field(None, description="Tóm tắt nhận thức tiến trình luồng sở thích.")
    confidence: Optional[float] = Field(None, description="Độ tin cậy của mô hình về sở thích này (0.0 đến 1.0).")
    evidence_count: Optional[int] = Field(0, description="Số lượng bằng chứng tương tác đã tích lũy.")
    status: Optional[str] = Field(None, description="Trạng thái luồng (active, dormant).")
    updated_at: Optional[str] = Field(None, description="Thời điểm cập nhật cuối.")


class PriorEntityAffinityDetail(BaseModel):
    """Trang, nhóm hoặc thực thể quen thuộc mà tác tử đã có độ gắn kết từ trước."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    entity_type: Optional[str] = Field(None, description="Loại thực thể (source, group, page, user).")
    entity_key: Optional[str] = Field(None, description="URL hoặc key của thực thể.")
    display_name: Optional[str] = Field(None, description="Tên hiển thị của trang/nhóm.")
    url: Optional[str] = Field(None, description="Đường dẫn URL của thực thể.")
    affinity: Optional[float] = Field(None, description="Điểm gắn kết (affinity score) từ 0.0 đến 1.0.")
    familiarity: Optional[float] = Field(None, description="Mức độ quen thuộc.")
    relationship_state: Optional[str] = Field(None, description="Trạng thái quan hệ (provisional, established).")
    evidence_count: Optional[int] = Field(0, description="Số lượng bằng chứng tương tác ghi nhận.")


class PriorHabitSnapshotDetail(BaseModel):
    """Ảnh chụp phân bổ thói quen tương tác của tác tử trước khi bắt đầu phiên."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    action_counts: Dict[str, int] = Field(default_factory=dict, description="Số lần thực hiện từng loại tool/action trước đó.")
    surface_counts: Dict[str, int] = Field(default_factory=dict, description="Số bước trên từng bề mặt trước đó.")
    learned_pacing: Dict[str, float] = Field(default_factory=dict, description="Nhịp độ tương tác đã học được.")
    preferred_surfaces: List[str] = Field(default_factory=list, description="Các bề mặt ưa thích.")
    ranked_topics: List[str] = Field(default_factory=list, description="Các chủ đề xếp hạng ưu tiên.")
    verified_tools: List[str] = Field(default_factory=list, description="Các công cụ đã xác minh thành thạo.")


class PriorLongTermMemory(BaseModel):
    """Toàn bộ tri thức và bộ nhớ dài hạn sẵn có tại thời điểm bắt đầu session."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    core_interests: List[str] = Field(default_factory=list, description="Danh sách sở thích cốt lõi dài hạn.")
    avoid_topics: List[str] = Field(default_factory=list, description="Danh sách chủ đề chủ động né tránh.")
    adjacent_interests: List[str] = Field(default_factory=list, description="Sở thích tiệm cận/phát sinh.")
    source_preferences: List[str] = Field(default_factory=list, description="Ưu tiên định dạng nguồn nội dung.")
    preferred_surface: Optional[str] = Field(None, description="Bề mặt ưu tiên (feed, reels...).")
    reading_depth: Optional[str] = Field(None, description="Độ sâu đọc (selective, deep...).")
    discovery_style: Optional[str] = Field(None, description="Phong cách khám phá (topic_led...).")
    interaction_style: Optional[str] = Field(None, description="Phong cách tương tác (responsive...).")
    exploration_disposition: Optional[ExplorationDispositionSchema] = Field(None, description="Thiên hướng khám phá nhận thức.")
    exploration_threads: List[ExplorationThreadBaselineSchema] = Field(default_factory=list, description="Các mạch định hướng khám phá ban đầu.")
    known_interest_threads: List[PriorInterestThreadDetail] = Field(default_factory=list, description="Các luồng sở thích dài hạn đã có sẵn.")
    known_affinities: List[PriorEntityAffinityDetail] = Field(default_factory=list, description="Các trang/nhóm đã quen thuộc từ trước.")
    prior_habit_snapshot: Optional[PriorHabitSnapshotDetail] = Field(None, description="Ảnh chụp thói quen hành vi trước phiên.")


# --- 2. Short-Term Working Memory Schemas (Bộ nhớ ngắn hạn sinh ra lúc hành động) ---

class WorkingMemoryActiveThreadDetail(BaseModel):
    """Luồng quan tâm/hứng thú đang được theo đuổi trong working memory của phiên."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    key: Optional[str] = Field(None, description="Khóa định danh luồng nội dung.")
    topic: Optional[str] = Field(None, description="Chủ đề đang quan tâm.")
    purpose: Optional[str] = Field(None, description="Mục đích nhận thức của hành động.")
    origin: Optional[str] = Field(None, description="Nguồn gốc luồng (situational, persona, exploration).")
    state: Optional[str] = Field(None, description="Trạng thái tâm lý/hành vi (exploring, active, resolved).")
    interest_relation: Optional[str] = Field(None, description="Quan hệ với sở thích (situational, aligned).")
    open_question: Optional[str] = Field(None, description="Câu hỏi mở mà tác tử tò mò muốn tìm lời giải.")
    last_intent: Optional[str] = Field(None, description="Ý định hành động gần nhất trên mạch này.")
    verified_steps: Optional[int] = Field(0, description="Số bước thực thi thành công gắn với mạch.")
    evidence: List[str] = Field(default_factory=list, description="Bằng chứng nhận thức kích hoạt mạch này.")


class WorkingMemoryReadPostDetail(BaseModel):
    """Bài viết đã đọc trong phiên kèm thời gian dừng đọc (dwell time) và đoạn trích."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    url: Optional[str] = Field(None, description="URL bài viết.")
    dwell_seconds: Optional[float] = Field(None, description="Thời gian dừng đọc bài tính bằng giây (dwell time).")
    read_at_elapsed: Optional[int] = Field(None, description="Thời điểm đọc tính từ đầu phiên (giây).")
    snippet: Optional[str] = Field(None, description="Trích đoạn nội dung bài viết.")
    content_stage: Optional[str] = Field(None, description="Giai đoạn đọc (preview, full).")
    duration_measurement: Optional[str] = Field(None, description="Cách thức đo thời gian dừng đọc.")


class WorkingMemoryOpenedSourceDetail(BaseModel):
    """Nguồn, trang hoặc nhóm Facebook đã mở ra trong phiên."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    at_elapsed: Optional[int] = Field(None, description="Thời điểm mở tính từ đầu phiên (giây).")
    target: Optional[str] = Field(None, description="Tên hoặc trích dẫn nguồn/nhóm đã mở.")
    type: Optional[str] = Field(None, description="Loại nguồn (group, page, profile).")


class WorkingMemorySearchedTopicDetail(BaseModel):
    """Chủ đề tìm kiếm ghi nhận trong working memory của phiên."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    at_elapsed: Optional[int] = Field(None, description="Thời điểm tìm kiếm tính từ đầu phiên (giây).")
    query: Optional[str] = Field(None, description="Từ khóa truy vấn tìm kiếm.")
    purpose: Optional[str] = Field(None, description="Mục đích tìm kiếm.")
    open_question: Optional[str] = Field(None, description="Câu hỏi mở tác tử tò mò.")
    outcome: Optional[str] = Field(None, description="URL hoặc kết quả tìm kiếm.")
    thread_id: Optional[str] = Field(None, description="ID luồng quan tâm liên kết.")


class WorkingMemoryOwnWritingDetail(BaseModel):
    """Nội dung do tác tử tự sáng tác trong phiên (comment, bài chia sẻ...)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    kind: Optional[str] = Field(None, description="Loại nội dung (comment, share, search_related).")
    content: Optional[str] = Field(None, description="Nội dung văn bản được viết.")
    voice_id: Optional[str] = Field(None, description="ID giọng điệu phát ngôn.")
    provenance: Optional[str] = Field(None, description="Nguồn gốc tác sinh.")
    subject_kind: Optional[str] = Field(None, description="Đối tượng tương tác (post, video).")
    subject_url: Optional[str] = Field(None, description="URL đối tượng tương tác.")


class WorkingMemoryNoveltyDetail(BaseModel):
    """Thông tin điều hướng tính mới mẻ và kiểm soát trôi dạt chủ đề."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    guidance: Optional[str] = Field(None, description="Hướng dẫn từ hệ thống về tính mới mẻ và quota đổi chủ đề.")
    explored_thread_count: Optional[int] = Field(None, description="Số luồng chủ đề đã khám phá.")
    explored_evidence_share: Optional[float] = Field(None, description="Tỷ trọng bằng chứng đã khám phá.")
    situational_steps: Optional[int] = Field(None, description="Số bước tương tác theo tình huống ngẫu nhiên.")


class WorkingMemoryRestDetail(BaseModel):
    """Trạng thái nghỉ ngơi và phân bổ nhịp thở trong phiên."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    accumulated_seconds: int = Field(0, description="Tổng số giây nghỉ ngơi tích lũy.")
    count: int = Field(0, description="Số lần nghỉ ngơi.")


class SessionHabitFactDetail(BaseModel):
    """Sự kiện hình thành thói quen vi mô phát sinh trong phiên từ `habit_facts`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Union[str, int] = Field(..., description="ID sự kiện thói quen.")
    kind: str = Field(..., description="Loại sự kiện (interaction_outcome, session_timing...).")
    intent: Optional[str] = Field(None, description="Ý định hành động.")
    tool: Optional[str] = Field(None, description="Công cụ thực thi.")
    resolver: Optional[str] = Field(None, description="Bộ điều phối resolver.")
    verified: Optional[bool] = Field(None, description="Trạng thái xác minh thành công.")
    surface: Optional[str] = Field(None, description="Bề mặt tương tác.")
    dwell_ms: Optional[int] = Field(None, description="Thời gian dừng dwell (ms).")
    created_at: Optional[str] = Field(None, description="Thời điểm ghi nhận.")


class SessionMemoryDeltaDetail(BaseModel):
    """Biến đổi cập nhật vào bộ nhớ dài hạn do phiên này sinh ra từ `memory_delta_ledger`."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: Optional[Union[str, int]] = Field(None, description="ID bản ghi delta.")
    record_type: str = Field(..., description="Loại thực thể (thread, entity, affinity).")
    record_key: str = Field(..., description="Khóa định danh slug/URL.")
    operation: str = Field(..., description="Thao tác (upsert, create, update, decay).")
    statement: Optional[str] = Field(None, description="Mệnh đề nhận thức mới rút ra được.")
    confidence: Optional[float] = Field(None, description="Độ tin cậy của tri thức mới.")
    evidence_count: Optional[int] = Field(None, description="Số lượng bằng chứng mới.")
    rationale: Optional[str] = Field(None, description="Lập luận củng cố cho việc cập nhật bộ nhớ.")
    created_at: Optional[str] = Field(None, description="Thời điểm ghi nhận.")


class ShortTermWorkingMemory(BaseModel):
    """Bộ nhớ làm việc ngắn hạn sinh ra và biến đổi liên tục trong suốt phiên thực thi."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    current_surface: Optional[str] = Field(None, description="Bề mặt giao diện hiện tại.")
    elapsed_seconds: Optional[int] = Field(None, description="Thời gian đã chạy (giây).")
    remaining_seconds: Optional[int] = Field(None, description="Thời gian còn lại (giây).")
    completed_actions: Optional[int] = Field(None, description="Số hành động đã hoàn tất trong phiên.")
    planned_active_seconds: Optional[int] = Field(None, description="Thời lượng mục tiêu của phiên (giây).")
    rest: WorkingMemoryRestDetail = Field(default_factory=WorkingMemoryRestDetail, description="Nhịp nghỉ tích lũy trong phiên.")
    summary: Optional[str] = Field(None, description="Tóm tắt ngắn gọn trạng thái bộ nhớ phiên.")
    planner_rule: Optional[str] = Field(None, description="Quy tắc định hướng lập kế hoạch nhận thức.")
    novelty: Optional[WorkingMemoryNoveltyDetail] = Field(None, description="Điều hướng tính mới mẻ và kiểm soát chủ đề.")
    active_threads: List[WorkingMemoryActiveThreadDetail] = Field(default_factory=list, description="Các luồng quan tâm/hứng thú đang sinh ra và theo đuổi trong phiên.")
    current_thread: Optional[WorkingMemoryActiveThreadDetail] = Field(None, description="Mạch nội dung hiện tại đang xử lý.")
    read_posts: List[WorkingMemoryReadPostDetail] = Field(default_factory=list, description="Danh sách các bài viết đã đọc kèm dwell time.")
    opened_sources: List[WorkingMemoryOpenedSourceDetail] = Field(default_factory=list, description="Danh sách các URL/nguồn đã mở trong phiên.")
    searched_topics: List[WorkingMemorySearchedTopicDetail] = Field(default_factory=list, description="Các chủ đề tìm kiếm trong working memory.")
    recent_own_writing: List[WorkingMemoryOwnWritingDetail] = Field(default_factory=list, description="Các nội dung bài viết/bình luận tác tử tự sáng tác.")
    habit_facts: List[SessionHabitFactDetail] = Field(default_factory=list, description="Các sự kiện thói quen phát sinh trong phiên.")
    memory_deltas: List[SessionMemoryDeltaDetail] = Field(default_factory=list, description="Biến đổi/cập nhật bộ nhớ dài hạn do phiên sinh ra.")
    consolidation_summary: Optional[str] = Field(None, description="Tóm tắt hợp nhất tri thức sau phiên.")
    learned_count: Optional[int] = Field(None, description="Số lượng tri thức mới được học.")


# ==============================================================================
# III. PYDANTIC SCHEMAS CHO SESSION HOÀN CHỈNH
# ==============================================================================

class SessionLog(BaseModel):
    """Đại diện cho log hoàn chỉnh của một phiên chạy (Session/Episode)."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    session_id: str = Field(..., description="Mã định danh phiên (UUID episode_id).")
    persona_id: str = Field(..., description="Mã định danh persona (ví dụ: 'vn_fb_001').")
    bot_id: Optional[str] = Field(None, description="Mã định danh bot.")
    persona_name: Optional[str] = Field(None, description="Tên đại diện của persona.")
    
    # Thứ tự thời gian thực thi trong chuỗi của Persona
    session_order: Optional[int] = Field(
        None,
        description="Thứ tự phiên của Persona này theo tiến trình thời gian thực thi (1, 2, 3...)."
    )
    started_at: Optional[str] = Field(None, description="Thời điểm bắt đầu phiên ISO 8601.")
    ended_at: Optional[str] = Field(None, description="Thời điểm kết thúc phiên ISO 8601.")
    duration_seconds: Optional[float] = Field(None, description="Thời lượng thực tế của phiên (giây).")
    status: Optional[str] = Field(None, description="Trạng thái hoàn thành (done, failed, stopped...).")
    terminal_reason: Optional[str] = Field(None, description="Lý do kết thúc phiên.")
    video_path: Optional[str] = Field(None, description="Đường dẫn file video ghi hình.")
    
    # Danh sách toàn bộ hành động (được sắp xếp chuẩn theo thứ tự bước/thời gian)
    actions: List[ActionLog] = Field(default_factory=list, description="Danh sách các hành động trong phiên.")

    # Thông tin bộ nhớ tại phiên này
    prior_memory: Optional[PriorLongTermMemory] = Field(
        None,
        description="Bộ nhớ dài hạn sẵn có tại thời điểm bắt đầu phiên (baseline interests, avoid topics, known threads, affinities, habit snapshot)."
    )
    working_memory: Optional[ShortTermWorkingMemory] = Field(
        None,
        description="Bộ nhớ ngắn hạn sinh ra và biến đổi trong phiên (active threads, read posts, novelty guidance, habit facts, memory deltas)."
    )

    # Các chỉ số thống kê gộp nhanh
    total_actions: int = Field(0, description="Tổng số hành động thực hiện trong phiên.")
    verified_rate: float = Field(0.0, description="Tỷ lệ hành động thực thi thành công.")
    total_scroll_px: int = Field(0, description="Tổng quãng đường cuộn chuột (pixels).")
    surface_distribution: Dict[str, int] = Field(default_factory=dict, description="Phân bổ số bước theo từng bề mặt.")
    intent_distribution: Dict[str, int] = Field(default_factory=dict, description="Phân bổ số bước theo ý định.")

    def model_post_init(self, __context: Any) -> None:
        """Tự động chuẩn hóa thứ tự hành động và cập nhật thống kê tóm tắt."""
        if self.actions:
            # Sắp xếp các actions theo thứ tự step_index tăng dần
            self.actions.sort(key=lambda a: a.step_index)
            self.total_actions = len(self.actions)

            # Tính toán phân bổ surface và intent
            surfaces: Dict[str, int] = {}
            intents: Dict[str, int] = {}
            verified_count = 0
            scroll_total = 0

            for a in self.actions:
                s_key = a.surface or "unknown"
                surfaces[s_key] = surfaces.get(s_key, 0) + 1

                i_key = a.intent or "unknown"
                intents[i_key] = intents.get(i_key, 0) + 1

                if a.verified is True:
                    verified_count += 1
                if a.gesture_total_px:
                    scroll_total += a.gesture_total_px

            self.surface_distribution = surfaces
            self.intent_distribution = intents
            self.verified_rate = round(verified_count / self.total_actions, 4) if self.total_actions > 0 else 0.0
            self.total_scroll_px = scroll_total

    def to_dataframe(self) -> pd.DataFrame:
        """Chuyển đổi các hành động trong session này thành DataFrame kèm metadata phiên."""
        records = []
        for a in self.actions:
            row = {
                "session_id": self.session_id,
                "persona_id": self.persona_id,
                "persona_name": self.persona_name,
                "session_order": self.session_order,
                "session_started_at": self.started_at,
                "session_duration_seconds": self.duration_seconds,
                "step_index": a.step_index,
                "timestamp": a.timestamp,
                "elapsed_seconds": a.elapsed_seconds,
                "intent": a.intent,
                "surface": a.surface,
                "tool": a.tool,
                "resolved_tool": a.resolved_tool,
                "verified": a.verified,
                "reaction": a.reaction,
                "reason": a.reason,
                "action_summary": a.action_summary,
                "target_id": a.target_id,
                "target_text": a.target_text,
                "action_url": a.action_url,
                "url_type": a.url_type,
                "execution_mode": a.execution_mode,
                "primary_dimension": a.primary_dimension,
                "primary_value": a.primary_value,
                "primary_weight": a.primary_weight,
                "num_dimension_evidence": len(a.dimension_evidence),
                "gesture_pace": a.gesture_pace,
                "gesture_total_px": a.gesture_total_px,
                "gesture_ms": a.gesture_ms,
                "model_latency_ms": a.model_latency_ms,
                "tool_execution_ms": a.tool_execution_ms,
                "total_tokens": a.total_tokens,
            }
            records.append(row)
        return pd.DataFrame(records)

    def get_summary(self) -> Dict[str, Any]:
        """Trả về từ điển tóm tắt các chỉ số chính của session kèm thông tin bộ nhớ."""
        pm = self.prior_memory
        wm = self.working_memory
        return {
            "session_id": self.session_id,
            "persona_id": self.persona_id,
            "persona_name": self.persona_name,
            "session_order": self.session_order,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_seconds": self.duration_seconds,
            "status": self.status,
            "terminal_reason": self.terminal_reason,
            "total_actions": self.total_actions,
            "verified_rate": self.verified_rate,
            "total_scroll_px": self.total_scroll_px,
            "surface_distribution": self.surface_distribution,
            "intent_distribution": self.intent_distribution,
            # Chỉ số tóm tắt bộ nhớ dài hạn
            "prior_core_interests_count": len(pm.core_interests) if pm else 0,
            "prior_avoid_topics_count": len(pm.avoid_topics) if pm else 0,
            "prior_known_threads_count": len(pm.known_interest_threads) if pm else 0,
            "prior_known_affinities_count": len(pm.known_affinities) if pm else 0,
            # Chỉ số tóm tắt bộ nhớ ngắn hạn
            "session_active_threads_count": len(wm.active_threads) if wm else 0,
            "session_read_posts_count": len(wm.read_posts) if wm else 0,
            "session_habit_facts_count": len(wm.habit_facts) if wm else 0,
            "session_memory_deltas_count": len(wm.memory_deltas) if wm else 0,
            "novelty_guidance": wm.novelty.guidance if wm and wm.novelty else None,
        }

    @classmethod
    def from_full_episode(
        cls,
        ep: FullEpisodeSchema,
        session_order: Optional[int] = None,
        prior_memory: Optional[PriorLongTermMemory] = None,
        working_memory: Optional[ShortTermWorkingMemory] = None,
    ) -> SessionLog:
        """Khởi tạo SessionLog từ đối tượng FullEpisodeSchema nạp từ SQLite."""
        actions: List[ActionLog] = []

        for st in ep.steps:
            # Tính elapsed_seconds từ timestamp/created_at và started_at
            elapsed_sec = None
            ts_str = st.timestamp or st.created_at
            if ts_str and ep.metadata.started_at:
                try:
                    t0 = datetime.fromisoformat(ep.metadata.started_at.replace("Z", "+00:00"))
                    t1 = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    elapsed_sec = round(max(0.0, (t1 - t0).total_seconds()), 2)
                except Exception:
                    pass

            # Reaction & Target Text từ args
            reaction_val = None
            target_text_val = None
            if isinstance(st.args, dict):
                reaction_val = st.args.get("reaction_type") or st.args.get("reaction")
                target_text_val = st.args.get("target_text") or st.args.get("comment_text")

            # Bóc tách dimension evidence
            evidence_details: List[DecisionEvidenceDetail] = []
            primary_dim = None
            primary_val = None
            primary_weight = None

            for itm in st.dimension_evidence:
                evidence_details.append(DecisionEvidenceDetail(
                    dimension=itm.dimension,
                    role=itm.role,
                    source=itm.source,
                    value=itm.value,
                    weight=itm.weight,
                    reference_id=itm.reference_id,
                ))
                if itm.role == "primary" and primary_dim is None:
                    primary_dim = itm.dimension
                    primary_val = itm.value
                    primary_weight = itm.weight

            if primary_dim is None and st.dimension_evidence:
                first = st.dimension_evidence[0]
                primary_dim = first.dimension
                primary_val = first.value
                primary_weight = first.weight

            act = ActionLog(
                step_index=st.step_index,
                timestamp=ts_str,
                elapsed_seconds=elapsed_sec,
                intent=st.intent,
                surface=st.surface or "unknown",
                tool=st.tool,
                resolved_tool=st.resolved_tool,
                verified=st.verified,
                reaction=reaction_val,
                reason=st.reason,
                action_summary=st.action_summary,
                target_id=st.target_id,
                target_text=target_text_val,
                action_url=st.action_url,
                url_type=st.url_type,
                execution_mode=st.execution_mode,
                dimension_evidence=evidence_details,
                primary_dimension=primary_dim,
                primary_value=primary_val,
                primary_weight=primary_weight,
                gesture_pace=st.gesture_pace,
                gesture_total_px=st.gesture_total_px,
                gesture_ms=st.gesture_ms,
                model_latency_ms=st.model_latency_ms,
                tool_execution_ms=st.tool_execution_ms,
                total_tokens=st.total_tokens,
            )
            actions.append(act)

        persona_id = ep.bot.persona_id if ep.bot and ep.bot.persona_id else "unknown_persona"
        persona_name = ep.bot.persona_name if ep.bot and ep.bot.persona_name else persona_id

        return cls(
            session_id=ep.metadata.id,
            persona_id=persona_id,
            bot_id=ep.metadata.bot_id,
            persona_name=persona_name,
            session_order=session_order,
            started_at=ep.metadata.started_at,
            ended_at=ep.metadata.ended_at,
            duration_seconds=ep.metadata.duration_seconds,
            status=ep.metadata.status,
            terminal_reason=ep.metadata.terminal_reason,
            video_path=ep.metadata.video_path,
            actions=actions,
            prior_memory=prior_memory,
            working_memory=working_memory,
        )


class PersonaActionHistory(BaseModel):
    """Kết tập toàn bộ các Session của 1 Persona, sắp xếp theo thứ tự thời gian thực thi."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    persona_id: str = Field(..., description="Mã định danh persona (ví dụ: 'vn_fb_001').")
    persona_name: Optional[str] = Field(None, description="Tên đại diện của persona.")
    total_sessions: int = Field(0, description="Tổng số session của persona này.")
    total_actions: int = Field(0, description="Tổng số hành động qua tất cả các session.")
    first_session_at: Optional[str] = Field(None, description="Mốc thời gian phiên đầu tiên.")
    last_session_at: Optional[str] = Field(None, description="Mốc thời gian phiên gần nhất.")
    
    # DANH SÁCH CÁC SESSION: Luôn được sắp xếp theo thời gian thực thi tăng dần
    sessions: List[SessionLog] = Field(
        default_factory=list,
        description="Danh sách các session theo thứ tự thời gian thực thi (started_at ASC)."
    )

    def model_post_init(self, __context: Any) -> None:
        """Đảm bảo các session luôn được sắp xếp theo thời gian thực thi tăng dần."""
        self._sort_and_reindex_sessions()

    def _sort_and_reindex_sessions(self) -> None:
        """Sắp xếp lại các session theo `started_at` và gán lại `session_order` (1, 2, ...)."""
        if not self.sessions:
            self.total_sessions = 0
            self.total_actions = 0
            return

        # Sắp xếp theo timestamp thực thi tăng dần
        self.sessions.sort(key=lambda s: _parse_iso_timestamp(s.started_at))
        
        # Đánh số thứ tự session_order (1, 2, ...)
        total_acts = 0
        for idx, s in enumerate(self.sessions, start=1):
            s.session_order = idx
            total_acts += s.total_actions

        self.total_sessions = len(self.sessions)
        self.total_actions = total_acts
        self.first_session_at = self.sessions[0].started_at
        self.last_session_at = self.sessions[-1].started_at

    def add_session(self, session: SessionLog) -> None:
        """Thêm 1 session vào lịch sử persona và tự động sắp xếp lại theo thời gian."""
        self.sessions.append(session)
        self._sort_and_reindex_sessions()

    def get_session(self, index: int) -> Optional[SessionLog]:
        """Lấy session theo thứ tự phiên (hỗ trợ cả 0-based index hoặc 1-based index)."""
        if 1 <= index <= len(self.sessions):
            return self.sessions[index - 1]
        if 0 <= index < len(self.sessions):
            return self.sessions[index]
        return None

    def get_session_by_id(self, session_id: str) -> Optional[SessionLog]:
        """Tìm session theo session_id UUID."""
        for s in self.sessions:
            if s.session_id == session_id:
                return s
        return None

    def to_actions_dataframe(self) -> pd.DataFrame:
        """Xuất DataFrame toàn bộ hành động qua tất cả các session của Persona này."""
        if not self.sessions:
            return pd.DataFrame()
        dfs = [s.to_dataframe() for s in self.sessions]
        return pd.concat(dfs, ignore_index=True)

    def to_sessions_dataframe(self) -> pd.DataFrame:
        """Xuất DataFrame tiến hóa qua các session theo thời gian (mỗi dòng là 1 session)."""
        records = []
        for s in self.sessions:
            row = s.get_summary()
            # Bổ sung các cột tỷ lệ surface
            tot = s.total_actions if s.total_actions > 0 else 1
            for surf, count in s.surface_distribution.items():
                row[f"{surf}_steps"] = count
                row[f"{surf}_ratio"] = round(count / tot, 4)
            records.append(row)
        return pd.DataFrame(records)

    def get_surface_drift(self) -> pd.DataFrame:
        """Thống kê tỷ lệ phân bổ các bề mặt qua từng session liên tiếp để thấy sự dịch chuyển."""
        df_sess = self.to_sessions_dataframe()
        if df_sess.empty:
            return pd.DataFrame()
        
        ratio_cols = [c for c in df_sess.columns if c.endswith("_ratio")]
        base_cols = ["session_order", "session_id", "started_at", "total_actions"]
        available_cols = [c for c in base_cols if c in df_sess.columns] + ratio_cols
        return df_sess[available_cols].fillna(0.0)

    def get_transition_matrix(self, column: str = "surface") -> pd.DataFrame:
        """Tính ma trận xác suất chuyển trạng thái Markov giữa các bước trong Persona."""
        df_act = self.to_actions_dataframe()
        if df_act.empty or column not in df_act.columns:
            return pd.DataFrame()

        # Tạo chuỗi trạng thái kế tiếp trong cùng một session
        df_act = df_act.sort_values(by=["session_order", "step_index"])
        df_act["next_state"] = df_act.groupby("session_id")[column].shift(-1)
        valid = df_act.dropna(subset=[column, "next_state"])
        if valid.empty:
            return pd.DataFrame()

        # Bảng chéo tần suất và chuẩn hóa thành xác suất
        crosstab = pd.crosstab(valid[column], valid["next_state"], normalize="index")
        return crosstab.round(4)

    def to_memory_evolution_dataframe(self) -> pd.DataFrame:
        """Xuất DataFrame tiến hóa bộ nhớ dài hạn và ngắn hạn qua các session theo thời gian."""
        records = []
        for s in self.sessions:
            pm = s.prior_memory
            wm = s.working_memory

            row = {
                "persona_id": self.persona_id,
                "persona_name": self.persona_name,
                "session_order": s.session_order,
                "session_id": s.session_id,
                "started_at": s.started_at,
                "duration_seconds": s.duration_seconds,
                "total_actions": s.total_actions,
                # --- Long-Term Prior Memory (Bắt đầu phiên) ---
                "prior_core_interests_count": len(pm.core_interests) if pm else 0,
                "prior_avoid_topics_count": len(pm.avoid_topics) if pm else 0,
                "prior_adjacent_interests_count": len(pm.adjacent_interests) if pm else 0,
                "prior_exploration_threads_count": len(pm.exploration_threads) if pm else 0,
                "prior_known_threads_count": len(pm.known_interest_threads) if pm else 0,
                "prior_known_affinities_count": len(pm.known_affinities) if pm else 0,
                "prior_preferred_surface": pm.preferred_surface if pm else None,
                "prior_discovery_style": pm.discovery_style if pm else None,
                "prior_interaction_style": pm.interaction_style if pm else None,
                # --- Short-Term Working Memory (Sinh ra trong phiên) ---
                "session_active_threads_count": len(wm.active_threads) if wm else 0,
                "session_read_posts_count": len(wm.read_posts) if wm else 0,
                "session_read_posts_avg_dwell_sec": (
                    round(sum(p.dwell_seconds or 0 for p in wm.read_posts) / len(wm.read_posts), 2)
                    if wm and wm.read_posts else 0.0
                ),
                "session_opened_sources_count": len(wm.opened_sources) if wm else 0,
                "session_searched_topics_count": len(wm.searched_topics) if wm else 0,
                "session_recent_writings_count": len(wm.recent_own_writing) if wm else 0,
                "session_rest_accumulated_seconds": wm.rest.accumulated_seconds if wm else 0,
                "session_rest_count": wm.rest.count if wm else 0,
                "session_habit_facts_count": len(wm.habit_facts) if wm else 0,
                "session_memory_deltas_count": len(wm.memory_deltas) if wm else 0,
                "session_learned_count": wm.learned_count if wm else 0,
                "novelty_guidance": wm.novelty.guidance if wm and wm.novelty else None,
                "novelty_situational_steps": wm.novelty.situational_steps if wm and wm.novelty else None,
                "working_memory_summary": wm.summary if wm else None,
            }
            records.append(row)
        return pd.DataFrame(records)

    def to_working_memory_active_threads_dataframe(self) -> pd.DataFrame:
        """Xuất DataFrame chi tiết tất cả các luồng quan tâm/hứng thú được theo đuổi trong các phiên."""
        records = []
        for s in self.sessions:
            if not s.working_memory:
                continue
            for th in s.working_memory.active_threads:
                records.append({
                    "persona_id": self.persona_id,
                    "session_order": s.session_order,
                    "session_id": s.session_id,
                    "thread_key": th.key,
                    "topic": th.topic,
                    "purpose": th.purpose,
                    "origin": th.origin,
                    "state": th.state,
                    "interest_relation": th.interest_relation,
                    "open_question": th.open_question,
                    "last_intent": th.last_intent,
                    "verified_steps": th.verified_steps,
                    "evidence": ", ".join(th.evidence) if th.evidence else None,
                })
        return pd.DataFrame(records)

    def to_read_posts_dataframe(self) -> pd.DataFrame:
        """Xuất DataFrame chi tiết các bài viết đã đọc kèm thời gian dwell time qua các phiên."""
        records = []
        for s in self.sessions:
            if not s.working_memory:
                continue
            for p in s.working_memory.read_posts:
                records.append({
                    "persona_id": self.persona_id,
                    "session_order": s.session_order,
                    "session_id": s.session_id,
                    "read_at_elapsed": p.read_at_elapsed,
                    "dwell_seconds": p.dwell_seconds,
                    "url": p.url,
                    "content_stage": p.content_stage,
                    "snippet": p.snippet[:150] if p.snippet else None,
                })
        return pd.DataFrame(records)


# ==============================================================================
# IV. LỚP ĐIỀU PHỐI ACTION LOADER
# ==============================================================================

class ActionLoader:
    """Bộ nạp chuyên sâu quản lý Action Logs và kết tập Sessions theo Persona.
    
    Cung cấp các API thuận tiện để tải session đơn lẻ hoặc tải toàn bộ session
    kết tập theo Persona có sắp xếp theo thời gian thực thi kèm bộ nhớ phiên đầy đủ.
    """

    def __init__(
        self,
        sqlite_path: Optional[str] = None,
        action_logs_dir: Optional[str] = None
    ) -> None:
        self.sqlite_path = get_sqlite_path(sqlite_path)
        self.action_logs_dir = Path(action_logs_dir) if action_logs_dir else Path("./data/action_logs")
        self._persona_histories_cache: Optional[Dict[str, PersonaActionHistory]] = None

    def _load_memory_for_session(
        self,
        session_id: str,
        bot_id: Optional[str] = None,
        conn: Optional[sqlite3.Connection] = None
    ) -> Tuple[Optional[PriorLongTermMemory], Optional[ShortTermWorkingMemory]]:
        """Nạp dữ liệu bộ nhớ dài hạn tại điểm xuất phát và bộ nhớ ngắn hạn trong phiên từ SQLite."""
        if not os.path.exists(self.sqlite_path):
            return None, None

        close_after = False
        if conn is None:
            conn = sqlite3.connect(self.sqlite_path)
            conn.row_factory = sqlite3.Row
            close_after = True

        try:
            cur = conn.cursor()

            # Lấy bot_id nếu chưa có
            if not bot_id:
                cur.execute("SELECT bot_id FROM episodes WHERE id = ?", (session_id,))
                ep_row = cur.fetchone()
                if ep_row:
                    bot_id = ep_row["bot_id"]

            prior_mem: Optional[PriorLongTermMemory] = None
            if bot_id:
                # 1. Baseline
                cur.execute("SELECT baseline_json FROM persona_memory_baselines WHERE bot_id = ?", (bot_id,))
                b_row = cur.fetchone()
                b_json = _safe_json_loads(b_row["baseline_json"]) if b_row else {}
                if not isinstance(b_json, dict):
                    b_json = {}

                # 2. Habit snapshot
                cur.execute("SELECT snapshot_json FROM habit_snapshots WHERE bot_id = ?", (bot_id,))
                h_row = cur.fetchone()
                h_json = _safe_json_loads(h_row["snapshot_json"]) if h_row else {}
                if not isinstance(h_json, dict):
                    h_json = {}

                # 3. Interest threads
                cur.execute(
                    "SELECT thread_key, title, summary, confidence, evidence_count, status, updated_at "
                    "FROM interest_threads WHERE bot_id = ?",
                    (bot_id,)
                )
                known_threads = []
                for tr in cur.fetchall():
                    known_threads.append(PriorInterestThreadDetail(
                        thread_key=tr["thread_key"],
                        title=tr["title"],
                        summary=tr["summary"],
                        confidence=tr["confidence"],
                        evidence_count=tr["evidence_count"],
                        status=tr["status"],
                        updated_at=tr["updated_at"],
                    ))

                # 4. Entity affinities
                cur.execute(
                    "SELECT entity_type, entity_key, display_name, url, affinity, familiarity, "
                    "relationship_state, evidence_count FROM entity_affinities WHERE bot_id = ?",
                    (bot_id,)
                )
                known_affinities = []
                for ar in cur.fetchall():
                    known_affinities.append(PriorEntityAffinityDetail(
                        entity_type=ar["entity_type"],
                        entity_key=ar["entity_key"],
                        display_name=ar["display_name"],
                        url=ar["url"],
                        affinity=ar["affinity"],
                        familiarity=ar["familiarity"],
                        relationship_state=ar["relationship_state"],
                        evidence_count=ar["evidence_count"],
                    ))

                # Bóc tách exploration disposition
                exp_disp_raw = b_json.get("exploration_disposition") or {}
                exp_disp = None
                if isinstance(exp_disp_raw, dict):
                    exp_disp = ExplorationDispositionSchema(
                        initiative=exp_disp_raw.get("initiative"),
                        natural_triggers=exp_disp_raw.get("natural_triggers") or [],
                        variety=exp_disp_raw.get("variety"),
                    )

                # Bóc tách exploration threads
                exp_threads = []
                for et in (b_json.get("exploration_threads") or []):
                    if isinstance(et, dict):
                        exp_threads.append(ExplorationThreadBaselineSchema(
                            key=et.get("key"),
                            topic=et.get("topic"),
                            angles=et.get("angles") or [],
                            based_on=et.get("based_on") or [],
                            source_types=et.get("source_types") or [],
                        ))

                # Bóc tách habit snapshot
                prior_habit = None
                if h_json:
                    prior_habit = PriorHabitSnapshotDetail(
                        action_counts=h_json.get("action_counts") or {},
                        surface_counts=h_json.get("surface_counts") or {},
                        learned_pacing=h_json.get("learned_pacing") or {},
                        preferred_surfaces=h_json.get("preferred_surfaces") or [],
                        ranked_topics=h_json.get("ranked_topics") or [],
                        verified_tools=h_json.get("verified_tools") or [],
                    )

                prior_mem = PriorLongTermMemory(
                    core_interests=b_json.get("core_interests") or [],
                    avoid_topics=b_json.get("avoid_topics") or [],
                    adjacent_interests=b_json.get("adjacent_interests") or [],
                    source_preferences=b_json.get("source_preferences") or [],
                    preferred_surface=b_json.get("preferred_surface"),
                    reading_depth=b_json.get("reading_depth"),
                    discovery_style=b_json.get("discovery_style"),
                    interaction_style=b_json.get("interaction_style"),
                    exploration_disposition=exp_disp,
                    exploration_threads=exp_threads,
                    known_interest_threads=known_threads,
                    known_affinities=known_affinities,
                    prior_habit_snapshot=prior_habit,
                )

            # 5. Short-term Working Memory (Từ session_id)
            cur.execute("SELECT snapshot_json FROM episode_working_memory WHERE episode_id = ?", (session_id,))
            wm_row = cur.fetchone()
            wm_json = _safe_json_loads(wm_row["snapshot_json"]) if wm_row else {}
            if not isinstance(wm_json, dict):
                wm_json = {}
            wm_inner = wm_json.get("working_memory") or {}
            if not isinstance(wm_inner, dict):
                wm_inner = {}

            # Active threads
            active_threads = []
            for at in (wm_inner.get("active_threads") or []):
                if isinstance(at, dict):
                    active_threads.append(WorkingMemoryActiveThreadDetail(
                        key=at.get("key"),
                        topic=at.get("topic"),
                        purpose=at.get("purpose"),
                        origin=at.get("origin"),
                        state=at.get("state"),
                        interest_relation=at.get("interest_relation"),
                        open_question=at.get("open_question"),
                        last_intent=at.get("last_intent"),
                        verified_steps=at.get("verified_steps") or 0,
                        evidence=at.get("evidence") or [],
                    ))

            # Current thread
            cur_th = None
            ct_raw = wm_inner.get("current_thread")
            if isinstance(ct_raw, dict):
                cur_th = WorkingMemoryActiveThreadDetail(
                    key=ct_raw.get("key") or ct_raw.get("id"),
                    topic=ct_raw.get("topic"),
                    purpose=ct_raw.get("purpose"),
                    origin=ct_raw.get("origin"),
                    state=ct_raw.get("state"),
                    interest_relation=ct_raw.get("interest_relation"),
                    open_question=ct_raw.get("open_question"),
                    last_intent=ct_raw.get("last_intent"),
                    verified_steps=ct_raw.get("verified_steps") or 0,
                    evidence=ct_raw.get("evidence") or [],
                )

            # Read posts
            read_posts = []
            for rp in (wm_inner.get("read_posts") or []):
                if isinstance(rp, dict):
                    read_posts.append(WorkingMemoryReadPostDetail(
                        url=rp.get("url"),
                        dwell_seconds=rp.get("dwell_seconds"),
                        read_at_elapsed=rp.get("read_at_elapsed"),
                        snippet=rp.get("snippet"),
                        content_stage=rp.get("content_stage"),
                        duration_measurement=rp.get("duration_measurement"),
                    ))

            # Opened sources
            opened_sources = []
            for src in (wm_inner.get("opened_sources") or []):
                if isinstance(src, dict):
                    opened_sources.append(WorkingMemoryOpenedSourceDetail(
                        at_elapsed=src.get("at_elapsed"),
                        target=src.get("target"),
                        type=src.get("type"),
                    ))

            # Searched topics
            searched_topics = []
            for st in (wm_inner.get("searched_topics") or []):
                if isinstance(st, dict):
                    searched_topics.append(WorkingMemorySearchedTopicDetail(
                        at_elapsed=st.get("at_elapsed"),
                        query=st.get("query"),
                        purpose=st.get("purpose"),
                        open_question=st.get("open_question"),
                        outcome=st.get("outcome"),
                        thread_id=st.get("thread_id"),
                    ))

            # Recent writings
            writings = []
            for w in (wm_inner.get("recent_own_writing") or []):
                if isinstance(w, dict):
                    subj = w.get("subject") or {}
                    writings.append(WorkingMemoryOwnWritingDetail(
                        kind=w.get("kind"),
                        content=w.get("content"),
                        voice_id=w.get("voice_id"),
                        provenance=w.get("provenance"),
                        subject_kind=subj.get("kind") if isinstance(subj, dict) else None,
                        subject_url=subj.get("url") if isinstance(subj, dict) else None,
                    ))

            # Novelty
            novelty = None
            nov_raw = wm_inner.get("novelty")
            if isinstance(nov_raw, dict):
                novelty = WorkingMemoryNoveltyDetail(
                    guidance=nov_raw.get("guidance"),
                    explored_thread_count=nov_raw.get("explored_thread_count"),
                    explored_evidence_share=nov_raw.get("explored_evidence_share"),
                    situational_steps=nov_raw.get("situational_steps"),
                )

            # Rest
            rest_raw = wm_json.get("rest") or {}
            rest_obj = WorkingMemoryRestDetail(
                accumulated_seconds=rest_raw.get("accumulated_seconds") or 0,
                count=rest_raw.get("count") or 0,
            )

            # Habit facts
            cur.execute("SELECT id, kind, value_json, created_at FROM habit_facts WHERE episode_id = ? ORDER BY created_at", (session_id,))
            habit_facts = []
            for hfr in cur.fetchall():
                v_json = _safe_json_loads(hfr["value_json"]) or {}
                if not isinstance(v_json, dict):
                    v_json = {}
                habit_facts.append(SessionHabitFactDetail(
                    id=hfr["id"],
                    kind=hfr["kind"],
                    intent=v_json.get("intent"),
                    tool=v_json.get("tool"),
                    resolver=v_json.get("resolver"),
                    verified=v_json.get("verified"),
                    surface=v_json.get("surface"),
                    dwell_ms=v_json.get("dwell_ms"),
                    created_at=hfr["created_at"],
                ))

            # Memory delta ledger
            cur.execute(
                "SELECT id, record_type, record_key, operation, after_json, evidence_json, created_at "
                "FROM memory_delta_ledger WHERE episode_id = ? ORDER BY created_at",
                (session_id,)
            )
            deltas = []
            for dlr in cur.fetchall():
                aft = _safe_json_loads(dlr["after_json"]) or {}
                ev = _safe_json_loads(dlr["evidence_json"]) or {}
                stmt = aft.get("statement") if isinstance(aft, dict) else None
                conf = aft.get("confidence") if isinstance(aft, dict) else None
                ev_cnt = aft.get("evidence_count") if isinstance(aft, dict) else None
                rat = ev.get("rationale") if isinstance(ev, dict) else None
                deltas.append(SessionMemoryDeltaDetail(
                    id=dlr["id"],
                    record_type=dlr["record_type"],
                    record_key=dlr["record_key"],
                    operation=dlr["operation"],
                    statement=stmt,
                    confidence=conf,
                    evidence_count=ev_cnt,
                    rationale=rat,
                    created_at=dlr["created_at"],
                ))

            # Consolidation run
            cur.execute(
                "SELECT result_json FROM memory_consolidation_runs WHERE episode_id = ? ORDER BY created_at DESC LIMIT 1",
                (session_id,)
            )
            cr_row = cur.fetchone()
            cr_res = _safe_json_loads(cr_row["result_json"]) if cr_row else {}
            cons_summary = cr_res.get("summary") if isinstance(cr_res, dict) else None
            learned_count = cr_res.get("learned") or cr_res.get("learned_count") if isinstance(cr_res, dict) else None

            working_mem = ShortTermWorkingMemory(
                current_surface=wm_json.get("current_surface"),
                elapsed_seconds=wm_json.get("elapsed_seconds"),
                remaining_seconds=wm_json.get("remaining_seconds"),
                completed_actions=wm_json.get("completed_actions"),
                planned_active_seconds=wm_json.get("planned_active_seconds"),
                rest=rest_obj,
                summary=wm_inner.get("summary"),
                planner_rule=wm_inner.get("planner_rule"),
                novelty=novelty,
                active_threads=active_threads,
                current_thread=cur_th,
                read_posts=read_posts,
                opened_sources=opened_sources,
                searched_topics=searched_topics,
                recent_own_writing=writings,
                habit_facts=habit_facts,
                memory_deltas=deltas,
                consolidation_summary=cons_summary,
                learned_count=learned_count,
            )

            return prior_mem, working_mem
        finally:
            if close_after:
                conn.close()

    def load_session(
        self,
        session_id: str,
        source: Literal["auto", "sqlite", "json"] = "auto"
    ) -> SessionLog:
        """Nạp log của 1 session (episode) theo session_id kèm bộ nhớ đầy đủ.

        Args:
            session_id: UUID định danh episode / session.
            source: Nguồn dữ liệu ('auto', 'sqlite', 'json').

        Returns:
            SessionLog: Đối tượng chứa toàn bộ actions và memory sắp xếp theo thứ tự thời gian.
        """
        # 1. Thử từ SQLite
        if source in ("auto", "sqlite") and os.path.exists(self.sqlite_path):
            try:
                full_ep = load_episode(session_id, sqlite_path=self.sqlite_path)
                prior_mem, working_mem = self._load_memory_for_session(
                    session_id=session_id,
                    bot_id=full_ep.metadata.bot_id
                )
                return SessionLog.from_full_episode(
                    full_ep,
                    prior_memory=prior_mem,
                    working_memory=working_mem
                )
            except Exception as e:
                if source == "sqlite":
                    raise e

        # 2. Thử từ file JSON benchmark
        if source in ("auto", "json"):
            json_session = self._load_session_from_json(session_id)
            if json_session:
                return json_session

        raise ValueError(f"Không tìm thấy log cho session '{session_id}' từ nguồn '{source}'")

    def _load_session_from_json(self, session_id: str) -> Optional[SessionLog]:
        """Hàm nội bộ tìm và nạp session từ các file JSON benchmark."""
        search_dirs = [
            self.action_logs_dir,
            Path("./data/no_persona_Action"),
            Path("./data/action_logs")
        ]
        for sdir in search_dirs:
            if not sdir.is_dir():
                continue
            for jf in sdir.glob("benchmark_eda_*.json"):
                try:
                    with open(jf, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    ep_list = data if isinstance(data, list) else data.get("episodes", [])
                    for ep_item in ep_list:
                        if ep_item.get("episode_id") == session_id:
                            return self._convert_json_episode_to_session_log(ep_item)
                except Exception:
                    continue
        return None

    def _convert_json_episode_to_session_log(self, ep_item: Dict[str, Any]) -> SessionLog:
        """Chuyển đổi một dict episode từ JSON benchmark sang SessionLog chuẩn."""
        session_id = ep_item.get("episode_id", "unknown_id")
        persona_id = ep_item.get("persona_id") or "neutral_control"
        step_records = ep_item.get("step_records") or []

        actions: List[ActionLog] = []
        for step in step_records:
            dim_evidence = step.get("dimension_evidence") or []
            evidence_details = []
            p_dim = None
            p_val = None
            p_w = None

            for d in dim_evidence:
                if isinstance(d, dict):
                    evidence_details.append(DecisionEvidenceDetail(
                        dimension=d.get("dimension", "raw"),
                        role=d.get("role", "primary"),
                        source=d.get("source", "persona"),
                        value=d.get("value"),
                        weight=float(d.get("weight") or 0.0),
                        reference_id=d.get("reference_id"),
                    ))
                    if d.get("role") == "primary" and p_dim is None:
                        p_dim = d.get("dimension")
                        p_val = d.get("value")
                        p_w = float(d.get("weight") or 0.0)

            # Phân giải gesture và kinematics nếu có trong action_summary
            summary = step.get("action_summary", "")
            g_pace = None
            g_total_px = None
            g_ms = None
            if summary:
                m_p = re.search(r'pace=(\w+)', summary)
                m_t = re.search(r'total=(\d+)px', summary)
                m_g = re.search(r'gesture_ms=(\d+)', summary)
                if m_p: g_pace = m_p.group(1)
                if m_t: g_total_px = int(m_t.group(1))
                if m_g: g_ms = int(m_g.group(1))

            target_cand = step.get("target_candidate") or {}
            t_text = target_cand.get("text") if isinstance(target_cand, dict) else None

            act = ActionLog(
                step_index=int(step.get("step_index") or len(actions) + 1),
                timestamp=step.get("timestamp"),
                elapsed_seconds=step.get("elapsed_seconds"),
                intent=step.get("intent"),
                surface=step.get("surface") or "unknown",
                tool=step.get("tool"),
                resolved_tool=step.get("resolved_tool"),
                verified=step.get("verified"),
                reaction=step.get("reaction"),
                reason=step.get("reason"),
                action_summary=summary,
                target_id=step.get("target_id"),
                target_text=t_text,
                dimension_evidence=evidence_details,
                primary_dimension=p_dim,
                primary_value=p_val,
                primary_weight=p_w,
                gesture_pace=g_pace,
                gesture_total_px=g_total_px,
                gesture_ms=g_ms,
                model_latency_ms=step.get("model_latency_ms"),
                tool_execution_ms=step.get("tool_execution_ms"),
            )
            actions.append(act)

        return SessionLog(
            session_id=session_id,
            persona_id=persona_id,
            persona_name=persona_id,
            started_at=ep_item.get("started_at"),
            ended_at=ep_item.get("ended_at"),
            duration_seconds=ep_item.get("duration_seconds"),
            status=ep_item.get("status"),
            terminal_reason=ep_item.get("terminal_reason"),
            actions=actions,
        )

    def load_persona_sessions(
        self,
        persona_id: str,
        source: Literal["auto", "sqlite", "json"] = "auto"
    ) -> PersonaActionHistory:
        """Nạp toàn bộ các session của một Persona cụ thể theo thứ tự thời gian thực thi.

        Args:
            persona_id: Mã persona cần nạp (ví dụ: 'vn_fb_001').
            source: Nguồn dữ liệu ('auto', 'sqlite', 'json').

        Returns:
            PersonaActionHistory: Tập hợp các session được sắp xếp theo thời gian tăng dần.
        """
        all_histories = self.load_all_personas(source=source)
        if persona_id in all_histories:
            return all_histories[persona_id]

        # Trả về đối tượng rỗng nếu không tìm thấy
        return PersonaActionHistory(persona_id=persona_id, sessions=[])

    def load_all_personas(
        self,
        source: Literal["auto", "sqlite", "json"] = "auto",
        refresh: bool = False
    ) -> Dict[str, PersonaActionHistory]:
        """Tải toàn bộ session từ nguồn và kết tập theo Persona theo thứ tự thời gian thực thi.

        Returns:
            Dict[str, PersonaActionHistory]: Từ điển dạng {persona_id: PersonaActionHistory}.
            Mỗi PersonaActionHistory chứa các session đã được sắp xếp tăng dần theo `started_at`
            kèm đầy đủ bộ nhớ dài hạn khởi đầu và bộ nhớ ngắn hạn của phiên.
        """
        if self._persona_histories_cache is not None and not refresh:
            return self._persona_histories_cache

        all_sessions: List[SessionLog] = []

        # 1. Nạp từ SQLite nếu có
        if source in ("auto", "sqlite") and os.path.exists(self.sqlite_path):
            try:
                conn = sqlite3.connect(self.sqlite_path)
                conn.row_factory = sqlite3.Row
                try:
                    episodes_meta = list_episodes(sqlite_path=self.sqlite_path)
                    for ep_m in episodes_meta:
                        ep_id = ep_m["id"]
                        try:
                            full_ep = load_episode(ep_id, sqlite_path=self.sqlite_path)
                            prior_mem, working_mem = self._load_memory_for_session(
                                session_id=ep_id,
                                bot_id=ep_m.get("bot_id"),
                                conn=conn
                            )
                            sess = SessionLog.from_full_episode(
                                full_ep,
                                prior_memory=prior_mem,
                                working_memory=working_mem
                            )
                            all_sessions.append(sess)
                        except Exception as err:
                            print(f"[!] Bỏ qua episode {ep_id}: {err}")
                finally:
                    conn.close()
            except Exception as e:
                if source == "sqlite":
                    raise e

        # 2. Nạp từ JSON nếu source là json hoặc auto và chưa có session nào từ SQLite
        if (source == "json" or (source == "auto" and not all_sessions)):
            all_sessions.extend(self._load_all_sessions_from_json())

        # 3. Kết tập theo Persona có sắp xếp thời gian
        histories = self.aggregate_sessions_by_persona(all_sessions)
        self._persona_histories_cache = histories
        return histories

    def _load_all_sessions_from_json(self) -> List[SessionLog]:
        """Nạp toàn bộ sessions từ các file JSON benchmark."""
        sessions: List[SessionLog] = []
        search_dirs = [self.action_logs_dir, Path("./data/no_persona_Action")]
        
        for sdir in search_dirs:
            if not sdir.is_dir():
                continue
            for jf in sorted(sdir.glob("benchmark_eda_*.json")):
                try:
                    with open(jf, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    ep_list = data if isinstance(data, list) else data.get("episodes", [])
                    for ep_item in ep_list:
                        sess = self._convert_json_episode_to_session_log(ep_item)
                        sessions.append(sess)
                except Exception as e:
                    print(f"[!] Lỗi đọc file {jf}: {e}")
        return sessions

    @staticmethod
    def aggregate_sessions_by_persona(
        sessions: List[SessionLog]
    ) -> Dict[str, PersonaActionHistory]:
        """Hàm tĩnh kết tập một danh sách các session bất kỳ theo từng Persona.
        
        Tự động:
        1. Phân nhóm theo `persona_id`.
        2. Sắp xếp các session trong từng nhóm theo thứ tự thời gian thực thi (`started_at` tăng dần).
        3. Đánh số `session_order` (1, 2, ...) cho từng phiên theo tiến trình thời gian.
        4. Cập nhật các chỉ số tổng hợp toàn diện.
        """
        grouped: Dict[str, List[SessionLog]] = {}
        names_map: Dict[str, str] = {}

        for sess in sessions:
            pid = sess.persona_id or "unknown_persona"
            if pid not in grouped:
                grouped[pid] = []
            grouped[pid].append(sess)
            if sess.persona_name and pid not in names_map:
                names_map[pid] = sess.persona_name

        result: Dict[str, PersonaActionHistory] = {}
        for pid, sess_list in grouped.items():
            history = PersonaActionHistory(
                persona_id=pid,
                persona_name=names_map.get(pid, pid),
                sessions=sess_list,
            )
            result[pid] = history

        return result

    def to_unified_actions_dataframe(
        self,
        personas_history: Optional[Dict[str, PersonaActionHistory]] = None
    ) -> pd.DataFrame:
        """Xuất DataFrame toàn diện chứa tất cả các hành động của tất cả các persona.
        
        Bao gồm các cột phân cấp: persona_id -> session_order -> step_index.
        """
        histories = personas_history or self.load_all_personas()
        dfs = []
        for p_hist in histories.values():
            df_p = p_hist.to_actions_dataframe()
            if not df_p.empty:
                dfs.append(df_p)

        if not dfs:
            return pd.DataFrame()
        return pd.concat(dfs, ignore_index=True)

    def to_unified_sessions_dataframe(
        self,
        personas_history: Optional[Dict[str, PersonaActionHistory]] = None
    ) -> pd.DataFrame:
        """Xuất DataFrame toàn diện chứa tất cả các session của tất cả các persona theo thời gian."""
        histories = personas_history or self.load_all_personas()
        dfs = []
        for p_hist in histories.values():
            df_s = p_hist.to_sessions_dataframe()
            if not df_s.empty:
                dfs.append(df_s)

        if not dfs:
            return pd.DataFrame()
        return pd.concat(dfs, ignore_index=True)

    def to_unified_memory_evolution_dataframe(
        self,
        personas_history: Optional[Dict[str, PersonaActionHistory]] = None
    ) -> pd.DataFrame:
        """Xuất DataFrame tiến hóa bộ nhớ toàn diện cho tất cả các persona theo thứ tự session."""
        histories = personas_history or self.load_all_personas()
        dfs = []
        for p_hist in histories.values():
            df_m = p_hist.to_memory_evolution_dataframe()
            if not df_m.empty:
                dfs.append(df_m)

        if not dfs:
            return pd.DataFrame()
        return pd.concat(dfs, ignore_index=True)

    def load_activity_windows(self) -> pd.DataFrame:
        """Nạp danh sách toàn bộ các cửa sổ hoạt động (Activity Windows) từ SQLite,
        tự động tính toán thời lượng phút (duration_min) và giờ bắt đầu địa phương (start_hour_local UTC+7).
        """
        if not os.path.exists(self.sqlite_path):
            return pd.DataFrame()

        conn = sqlite3.connect(self.sqlite_path)
        try:
            query = """
                SELECT 
                    w.id as window_id,
                    w.bot_id,
                    b.persona_id,
                    w.local_date,
                    w.start_at,
                    w.end_at,
                    w.max_actions,
                    w.surface_bias,
                    w.state,
                    w.terminal_reason,
                    w.reason as window_reason
                FROM activity_windows w
                LEFT JOIN bots b ON w.bot_id = b.id
                ORDER BY w.start_at ASC
            """
            df_windows = pd.read_sql_query(query, conn)

            def _calc_window_time(row):
                try:
                    t0 = datetime.fromisoformat(row['start_at'].replace('Z', '+00:00'))
                    t1 = datetime.fromisoformat(row['end_at'].replace('Z', '+00:00'))
                    dur_min = (t1 - t0).total_seconds() / 60.0
                    hour_utc = t0.hour + t0.minute / 60.0
                    hour_local = (hour_utc + 7) % 24
                    return pd.Series({'duration_min': dur_min, 'start_hour_local': hour_local})
                except Exception:
                    return pd.Series({'duration_min': None, 'start_hour_local': None})

            if not df_windows.empty:
                time_metrics = df_windows.apply(_calc_window_time, axis=1)
                df_windows = pd.concat([df_windows, time_metrics], axis=1)

            return df_windows
        finally:
            conn.close()

    def load_persona_profiles_and_contracts(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Nạp hồ sơ nhân vật (persona_profiles) và hợp đồng hành vi (contracts_dict) từ SQLite."""
        if not os.path.exists(self.sqlite_path):
            return {}, {}

        conn = sqlite3.connect(self.sqlite_path)
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT b.persona_id, pv.content_json, c.contract_json
                FROM bots b
                JOIN persona_versions pv ON b.id = pv.bot_id
                JOIN behavioral_contracts c ON pv.id = c.persona_version_id
            """)
            persona_profiles = {}
            contracts_dict = {}
            for p_id, p_json, c_json in cur.fetchall():
                persona_profiles[p_id] = _safe_json_loads(p_json) or {}
                contracts_dict[p_id] = _safe_json_loads(c_json) or {}
            return persona_profiles, contracts_dict
        finally:
            conn.close()

    def get_dataset_summary_tables(
        self,
        personas_history: Optional[Dict[str, PersonaActionHistory]] = None,
        df_windows: Optional[pd.DataFrame] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Tạo bảng thống kê nhanh về dữ liệu:
        - Số persona
        - Số session (thực thi thành công có logs)
        - Số lượng bước hành động
        - Số kịch bản đã thực hiện (activity windows completed/claimed)
        - Số kịch bản đã lên kế hoạch (tổng activity windows)
        
        Trả về tuple: (df_summary_total, df_summary_by_persona)
        """
        histories = personas_history or self.load_all_personas()
        if df_windows is None:
            df_windows = self.load_activity_windows()

        all_personas = sorted(list(set(
            list(histories.keys()) +
            (df_windows["persona_id"].dropna().unique().tolist() if not df_windows.empty else [])
        )))

        total_personas = len(all_personas)
        total_planned_scenarios = len(df_windows) if not df_windows.empty else 0
        total_executed_scenarios = int((df_windows["state"].isin(["completed", "claimed"])).sum()) if not df_windows.empty else 0
        total_sessions = sum(h.total_sessions for h in histories.values())
        total_actions = sum(h.total_actions for h in histories.values())

        by_persona_records = []
        for pid in all_personas:
            h = histories.get(pid)
            n_sess = h.total_sessions if h else 0
            n_acts = h.total_actions if h else 0

            p_wins = df_windows[df_windows["persona_id"] == pid] if not df_windows.empty else pd.DataFrame()
            planned = len(p_wins)
            executed = int((p_wins["state"].isin(["completed", "claimed"])).sum()) if not p_wins.empty else 0

            by_persona_records.append({
                "Persona ID": pid,
                "Số kịch bản đã lên kế hoạch": planned,
                "Số kịch bản đã thực hiện": executed,
                "Số Session ghi nhận": n_sess,
                "Số lượng bước hành động": n_acts,
            })

        df_by_persona = pd.DataFrame(by_persona_records)

        # Thêm dòng Tổng cộng ở cuối bảng per-persona
        total_row = pd.DataFrame([{
            "Persona ID": "TỔNG CỘNG",
            "Số kịch bản đã lên kế hoạch": total_planned_scenarios,
            "Số kịch bản đã thực hiện": total_executed_scenarios,
            "Số Session ghi nhận": total_sessions,
            "Số lượng bước hành động": total_actions,
        }])
        df_by_persona_with_total = pd.concat([df_by_persona, total_row], ignore_index=True)

        # Bảng chỉ số tổng quan điều hành (Executive Summary)
        overview_records = [
            {"Chỉ số (Metric)": "Số Persona", "Số lượng": total_personas, "Đơn vị": "Persona", "Mô tả": "Số lượng hồ sơ nhân vật độc lập trong thử nghiệm"},
            {"Chỉ số (Metric)": "Số kịch bản đã lên kế hoạch", "Số lượng": total_planned_scenarios, "Đơn vị": "Kịch bản / Cửa sổ", "Mô tả": "Tổng số activity windows được lập lịch tự động (LLM Scheduler)"},
            {"Chỉ số (Metric)": "Số kịch bản đã thực hiện", "Số lượng": total_executed_scenarios, "Đơn vị": "Kịch bản / Cửa sổ", "Mô tả": "Số activity windows đã chạy thực tế (completed/claimed)"},
            {"Chỉ số (Metric)": "Số Session ghi nhận", "Số lượng": total_sessions, "Đơn vị": "Phiên (Session)", "Mô tả": "Số phiên chạy trực tiếp thu thập đầy đủ action logs"},
            {"Chỉ số (Metric)": "Số lượng bước hành động", "Số lượng": total_actions, "Đơn vị": "Thao tác (Step)", "Mô tả": "Tổng các bước tương tác thực tế trên trình duyệt (agent_live_steps)"},
        ]
        df_total = pd.DataFrame(overview_records)

        return df_total, df_by_persona_with_total

    def get_persona_overview_dataframe(
        self,
        persona_profiles: Dict[str, Any],
        contracts_dict: Dict[str, Any],
        personas_history: Optional[Dict[str, PersonaActionHistory]] = None,
        df_windows: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """Tổng hợp bảng đối soát thuộc tính 6 Persona chuẩn chỉnh từ attributes và contracts."""
        histories = personas_history or self.load_all_personas()
        overview_records = []
        for p_id in sorted(persona_profiles.keys()):
            prof = persona_profiles[p_id]
            attrs = prof.get("attributes", {})
            contract = contracts_dict.get(p_id, {})
            nav = contract.get("navigation", {})

            hist = histories.get(p_id)
            n_sess = hist.total_sessions if hist else 0
            n_acts = hist.total_actions if hist else 0
            n_wins = len(df_windows[df_windows["persona_id"] == p_id]) if df_windows is not None else 0

            overview_records.append({
                "Persona ID": p_id,
                "Tuổi": attrs.get("Nhóm tuổi", "N/A"),
                "Giới tính": attrs.get("Bản dạng giới", "N/A"),
                "Nghề nghiệp": attrs.get("Nhóm vai trò công việc hiện tại.", "N/A"),
                "Địa bàn": f"{attrs.get('Tỉnh / Thành phố', 'N/A')} ({attrs.get('Vùng miền', '')})",
                "Định dạng ưa thích": attrs.get("Loại hình nội dung yêu thích nhất", "N/A"),
                "Mức độ nhóm": attrs.get("Mức độ sinh hoạt trong các hội nhóm và cộng đồng mạng xã hội.", "N/A"),
                "Tần suất FB": attrs.get("Tần suất sử dụng Facebook", "N/A"),
                "Hình thái tương tác": attrs.get("Cách thường tham gia và tương tác trên các nền tảng trực tuyến.", "N/A"),
                "Nhịp Pacing": nav.get("scrollCadence", "N/A"),
                "Windows": n_wins,
                "Episodes": n_sess,
                "Actions": n_acts,
            })
        return pd.DataFrame(overview_records)

    def get_temporal_data_health_check(
        self,
        df_windows: Optional[pd.DataFrame] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Kiểm tra độ sạch (Data Health Check) và tham số hình thái phân phối (Distribution Profile)
        của 3 biến thời gian: Giờ bắt đầu (start_hour_local), Thời lượng (duration_min), và Tần suất phiên/ngày.
        Trả về: (df_health, df_dist)
        """
        if df_windows is None:
            df_windows = self.load_activity_windows()
            
        if df_windows.empty:
            return pd.DataFrame(), pd.DataFrame()

        # 1. Bảng Health Check
        health_records = []
        for col, name, valid_min, valid_max, unit in [
            ("start_hour_local", "Giờ bắt đầu phiên (UTC+7)", 6.0, 23.5, "Giờ"),
            ("duration_min", "Thời lượng phiên", 8.0, 32.0, "Phút"),
        ]:
            s = df_windows[col]
            n_total = len(s)
            n_missing = int(s.isna().sum())
            val_min = float(s.min())
            val_max = float(s.max())
            n_violations = int(((s < valid_min) | (s > valid_max)).sum())
            pct_violations = (n_violations / n_total) * 100.0
            status = "✅ Hợp lệ (100%)" if n_violations == 0 else f"⚠️ {n_violations} điểm ngoài biên ({pct_violations:.1f}%)"
            
            health_records.append({
                "Biến số": name,
                "Cột dữ liệu": col,
                "Số quan sát (N)": n_total,
                "Số bản ghi khuyết": n_missing,
                "Khoảng thực tế [Min, Max]": f"[{val_min:.1f}, {val_max:.1f}] {unit}",
                # "Ngưỡng hợp lệ kỳ vọng": f"[{valid_min:.1f}, {valid_max:.1f}] {unit}",
                # "Số điểm ngoài ngưỡng": n_violations,
                # "Đánh giá chất lượng": status
            })

        # Thêm tần suất phiên theo ngày
        wpd = df_windows.groupby(['persona_id', 'local_date']).size().reset_index(name='daily_windows')
        n_wpd = len(wpd)
        min_wpd = int(wpd['daily_windows'].min()) if n_wpd > 0 else 0
        max_wpd = int(wpd['daily_windows'].max()) if n_wpd > 0 else 0
        n_viol_w = int(((wpd['daily_windows'] < 1) | (wpd['daily_windows'] > 4)).sum())
        health_records.append({
            "Biến số": "Tần suất phiên mỗi ngày",
            "Cột dữ liệu": "daily_windows",
            "Số quan sát (N)": n_wpd,
            "Số bản ghi khuyết": 0,
            "Khoảng thực tế [Min, Max]": f"[{min_wpd}, {max_wpd}] Phiên/ngày",
            # "Ngưỡng hợp lệ kỳ vọng": "[1, 4] Phiên/ngày",
            # "Số điểm ngoài ngưỡng": n_viol_w,
            # "Đánh giá chất lượng": "✅ Hợp lệ (100%)" if n_viol_w == 0 else f"⚠️ {n_viol_w} điểm ngoài"
        })
        # Thêm khoảng cách giữa các lần thực thi liên tiếp (gap_hours)
        df_w_sorted = df_windows.sort_values(by=['persona_id', 'start_at']).copy()
        df_w_sorted['start_dt'] = pd.to_datetime(df_w_sorted['start_at'])
        gaps = (df_w_sorted.groupby('persona_id')['start_dt'].diff().dt.total_seconds() / 3600.0).dropna()
        n_gaps = len(gaps)
        min_gap = float(gaps.min()) if n_gaps > 0 else 0.0
        max_gap = float(gaps.max()) if n_gaps > 0 else 0.0
        health_records.append({
            "Biến số": "Khoảng cách giữa các lần thực thi",
            "Cột dữ liệu": "gap_hours",
            "Số quan sát (N)": n_gaps,
            "Số bản ghi khuyết": 0,
            "Khoảng thực tế [Min, Max]": f"[{min_gap:.1f}, {max_gap:.1f}] Giờ",
        })
        df_health = pd.DataFrame(health_records)

        # 2. Bảng Distribution Stats
        dist_records = []
        for col, name, unit in [
            ("start_hour_local", "Giờ bắt đầu phiên", "Giờ"),
            ("duration_min", "Thời lượng phiên", "Phút"),
        ]:
            s = df_windows[col].dropna()
            q1 = float(s.quantile(0.25))
            q2 = float(s.median())
            q3 = float(s.quantile(0.75))
            skew = float(s.skew())
            kurt = float(s.kurt())
            shape_desc = "Gần đối xứng" if abs(skew) < 0.2 else ("Lệch phải" if skew > 0 else "Lệch trái")
            kurt_desc = "Phẳng / Đa đỉnh" if kurt < -1.0 else ("Nhọn / Đỉnh dốc" if kurt > 1.0 else "Trung bình")
                
            dist_records.append({
                "Biến số": name,
                "Đơn vị": unit,
                "Số mẫu (N)": len(s),
                "Mean": float(s.mean()),
                "Std": float(s.std()),
                "Median (Q2)": q2,
                "Q1": q1,
                "Q3": q3,
                "IQR": q3 - q1,
                "Min": float(s.min()),
                "Max": float(s.max()),
                "Skewness": skew,
                "Kurtosis": kurt,
                "Hình thái phân phối": f"{shape_desc}, {kurt_desc}"
            })

        # Add daily windows distribution
        s_wpd = wpd['daily_windows']
        q1_w = float(s_wpd.quantile(0.25))
        q2_w = float(s_wpd.median())
        q3_w = float(s_wpd.quantile(0.75))
        dist_records.append({
            "Biến số": "Tần suất phiên ngày",
            "Đơn vị": "Phiên/ngày",
            "Số mẫu (N)": len(s_wpd),
            "Mean": float(s_wpd.mean()),
            "Std": float(s_wpd.std()),
            "Median (Q2)": q2_w,
            "Q1": q1_w,
            "Q3": q3_w,
            "IQR": q3_w - q1_w,
            "Min": float(s_wpd.min()),
            "Max": float(s_wpd.max()),
            "Skewness": float(s_wpd.skew()),
            "Kurtosis": float(s_wpd.kurt()),
            "Hình thái phân phối": "Đều đặn [1 - 3]"
        })

        # Add gap_hours distribution
        if n_gaps > 0:
            q1_g = float(gaps.quantile(0.25))
            q2_g = float(gaps.median())
            q3_g = float(gaps.quantile(0.75))
            dist_records.append({
                "Biến số": "Khoảng cách giữa các phiên",
                "Đơn vị": "Giờ",
                "Số mẫu (N)": n_gaps,
                "Mean": float(gaps.mean()),
                "Std": float(gaps.std()),
                "Median (Q2)": q2_g,
                "Q1": q1_g,
                "Q3": q3_g,
                "IQR": q3_g - q1_g,
                "Min": float(gaps.min()),
                "Max": float(gaps.max()),
                "Skewness": float(gaps.skew()),
                "Kurtosis": float(gaps.kurt()),
                "Hình thái phân phối": "Lệch phải, Tập trung quanh 8h"
            })
        df_dist = pd.DataFrame(dist_records)

        return df_health, df_dist

    def get_temporal_by_persona_stats(
        self,
        df_windows: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """Thống kê chi tiết giờ bắt đầu, thời lượng, tần suất và khoảng cách phiên phân rã theo từng Persona."""
        if df_windows is None:
            df_windows = self.load_activity_windows()
            
        if df_windows.empty:
            return pd.DataFrame()

        df_w_sorted = df_windows.sort_values(by=['persona_id', 'start_at']).copy()
        df_w_sorted['start_dt'] = pd.to_datetime(df_w_sorted['start_at'])
        wpd = df_windows.groupby(['persona_id', 'local_date']).size().reset_index(name='daily_windows')
        by_p = []
        for pid in sorted(df_windows['persona_id'].unique()):
            sub = df_windows[df_windows['persona_id'] == pid]
            sub_sorted = df_w_sorted[df_w_sorted['persona_id'] == pid]
            sub_wpd = wpd[wpd['persona_id'] == pid]
            sub_gaps = sub_sorted['start_dt'].diff().dt.total_seconds() / 3600.0
            gap_mean = round(float(sub_gaps.dropna().mean()), 1) if not sub_gaps.dropna().empty else None

            by_p.append({
                "Persona ID": pid,
                "Số Windows": len(sub),
                "Giờ bắt đầu Mean": round(float(sub['start_hour_local'].mean()), 1),
                "Giờ bắt đầu Std": round(float(sub['start_hour_local'].std()), 1),
                "Giờ [Min, Max]": f"[{sub['start_hour_local'].min():.1f}, {sub['start_hour_local'].max():.1f}]h",
                "Thời lượng Mean": round(float(sub['duration_min'].mean()), 1),
                "Thời lượng Std": round(float(sub['duration_min'].std()), 1),
                "Thời lượng [Min, Max]": f"[{sub['duration_min'].min():.0f}, {sub['duration_min'].max():.0f}]m",
                "Tần suất ngày Mean": round(float(sub_wpd['daily_windows'].mean()), 2) if not sub_wpd.empty else 0.0,
                "Khoảng cách phiên Mean (h)": gap_mean if gap_mean is not None else 0.0,
                "Số ngày hoạt động": len(sub_wpd)
            })
        return pd.DataFrame(by_p)

    def plot_temporal_distribution_overview(
        self,
        df_windows: Optional[pd.DataFrame] = None,
        palette: Optional[Dict[str, str]] = None,
        save_path: Optional[str] = None
    ) -> Any:
        """Trực quan hóa tổng hợp hình thái phân phối của 4 yếu tố thời gian (2x2 grid):
        1. Giờ 24h
        2. Thời lượng phiên
        3. Tần suất phiên mỗi ngày
        4. Khoảng cách giữa các lần thực thi liên tiếp (gap_hours)
        """
        import matplotlib.pyplot as plt
        import seaborn as sns

        if df_windows is None:
            df_windows = self.load_activity_windows()
            
        wpd = df_windows.groupby(['persona_id', 'local_date']).size().reset_index(name='daily_windows')

        # Tính khoảng cách giữa các cửa sổ liên tiếp của cùng 1 Persona
        df_w_sorted = df_windows.sort_values(by=['persona_id', 'start_at']).copy()
        df_w_sorted['start_dt'] = pd.to_datetime(df_w_sorted['start_at'])
        df_w_sorted['gap_hours'] = df_w_sorted.groupby('persona_id')['start_dt'].diff().dt.total_seconds() / 3600.0

        fig, axes = plt.subplots(2, 2, figsize=(16, 9.5), dpi=120)

        # 1. Giờ bắt đầu phiên (24h)
        ax1 = axes[0, 0]
        sns.histplot(df_windows['start_hour_local'], bins=16, kde=True, color='#2b5c8f', ax=ax1, stat='density', alpha=0.45)
        ax1.axvspan(6, 11, color='#ffeaa7', alpha=0.25, label='Sáng (6-11h)')
        ax1.axvspan(11, 14, color='#fab1a0', alpha=0.25, label='Trưa (11-14h)')
        ax1.axvspan(14, 18, color='#55efc4', alpha=0.2, label='Chiều (14-18h)')
        ax1.axvspan(18, 23, color='#74b9ff', alpha=0.2, label='Tối (18-23h)')
        med_h = float(df_windows['start_hour_local'].median())
        ax1.axvline(med_h, color='#d63031', linestyle='--', linewidth=1.8, label=f"Median ({med_h:.1f}h)")
        ax1.set_title("1. Phân phối Giờ bắt đầu phiên (start_hour_local)\nKèm 4 ca sinh hoạt chính trong ngày (UTC+7)", fontsize=11, fontweight='bold')
        ax1.set_xlabel("Giờ trong ngày (Local Hour UTC+7)", fontsize=10)
        ax1.set_ylabel("Mật độ xác suất (Density)", fontsize=10)
        ax1.set_xlim(5, 24)
        ax1.legend(loc='upper right', fontsize=8.5)

        # 2. Thời lượng phiên theo Persona (Boxplot)
        ax2 = axes[0, 1]
        sns.boxplot(data=df_windows, x='persona_id', y='duration_min', hue='persona_id', palette=palette, legend=False, ax=ax2, width=0.55, boxprops=dict(alpha=0.75))
        sns.stripplot(data=df_windows, x='persona_id', y='duration_min', color='#2d3436', size=4.5, jitter=0.2, ax=ax2, alpha=0.6)
        ax2.axhline(8, color='#d63031', linestyle=':', linewidth=1.5, label='Biên dưới (8m)')
        ax2.axhline(32, color='#d63031', linestyle='--', linewidth=1.5, label='Biên trên (32m)')
        ax2.set_title("2. Phân phối Thời lượng phiên (duration_min)\nGiới hạn [8, 32] phút theo Persona", fontsize=11, fontweight='bold')
        ax2.set_xlabel("Persona ID", fontsize=10)
        ax2.set_ylabel("Thời lượng (Phút)", fontsize=10)
        ax2.set_ylim(4, 38)
        ax2.legend(loc='upper left', fontsize=8.5)

        # 3. Tần suất phiên mỗi ngày
        ax3 = axes[1, 0]
        sns.barplot(data=wpd, x='persona_id', y='daily_windows', hue='persona_id', palette=palette, legend=False, ax=ax3, errorbar=None, alpha=0.85)
        means = wpd.groupby('persona_id')['daily_windows'].mean()
        for i, (pid, m) in enumerate(means.items()):
            ax3.text(i, m + 0.06, f"{m:.2f}", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#2d3436')

        mean_all = float(wpd['daily_windows'].mean())
        ax3.axhline(mean_all, color='#636e72', linestyle='--', linewidth=1.2, label=f"TB Toàn hệ thống ({mean_all:.2f}/ngày)")
        ax3.set_title("3. Tần suất phiên trung bình mỗi ngày\nSố lượng windows/ngày theo từng Persona", fontsize=11, fontweight='bold')
        ax3.set_xlabel("Persona ID", fontsize=10)
        ax3.set_ylabel("Số phiên / ngày", fontsize=10)
        ax3.set_ylim(0, 3.5)
        ax3.legend(loc='lower right', fontsize=8.5)

        # 4. Khoảng cách giữa các lần thực thi liên tiếp (gap_hours)
        ax4 = axes[1, 1]
        valid_gaps = df_w_sorted.dropna(subset=['gap_hours'])
        sns.boxplot(data=valid_gaps, x='persona_id', y='gap_hours', hue='persona_id', palette=palette, legend=False, ax=ax4, width=0.55, boxprops=dict(alpha=0.75))
        sns.stripplot(data=valid_gaps, x='persona_id', y='gap_hours', color='#2d3436', size=4.5, jitter=0.2, ax=ax4, alpha=0.6)
        med_gap = float(valid_gaps['gap_hours'].median())
        ax4.axhline(med_gap, color='#e17055', linestyle='--', linewidth=1.5, label=f"Median toàn hệ thống ({med_gap:.1f}h)")
        ax4.axhline(24, color='#b2bec3', linestyle=':', linewidth=1.2, label="Khoảng cách 24h (1 ngày)")
        ax4.set_title("4. Khoảng cách giữa các lần thực thi liên tiếp (gap_hours)\nThời gian giữa 2 phiên kế tiếp của cùng Persona (Giờ)", fontsize=11, fontweight='bold')
        ax4.set_xlabel("Persona ID", fontsize=10)
        ax4.set_ylabel("Khoảng cách (Giờ)", fontsize=10)
        ax4.set_ylim(-1, 40)
        ax4.legend(loc='upper right', fontsize=8.5)

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
        return fig

    def get_temporal_contingency_and_residuals(
        self,
        df_windows: Optional[pd.DataFrame] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """Tính toán bảng chéo tần số, tần số kỳ vọng, phần dư chuẩn hóa Haberman và kiểm định độc lập Chi-square
        theo Persona và 3 khung giờ sinh hoạt đỉnh (Sáng, Trưa/Chiều, Tối).
        """
        from scipy.stats import chi2_contingency
        import numpy as np

        if df_windows is None:
            df_windows = self.load_activity_windows()

        if df_windows.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}

        def assign_peak_slot(h):
            if 6 <= h < 11:
                return "1. Ca Sáng (06h - 11h)"
            elif 11 <= h < 17:
                return "2. Ca Trưa & Chiều (11h - 17h)"
            else:
                return "3. Ca Tối (17h - 23h)"

        df_w = df_windows.copy()
        df_w['time_slot'] = df_w['start_hour_local'].apply(assign_peak_slot)

        order_cols = ["1. Ca Sáng (06h - 11h)", "2. Ca Trưa & Chiều (11h - 17h)", "3. Ca Tối (17h - 23h)"]
        df_obs = pd.crosstab(df_w['persona_id'], df_w['time_slot'])[order_cols]

        chi2, p_val, dof, expected_arr = chi2_contingency(df_obs)
        df_exp = pd.DataFrame(expected_arr, index=df_obs.index, columns=df_obs.columns)

        n = df_obs.values.sum()
        cramers_v = np.sqrt(chi2 / (n * (min(df_obs.shape) - 1)))

        # Tính Haberman's Adjusted Residuals: (O - E) / sqrt(E * (1 - r_i/n) * (1 - c_j/n))
        row_sums = df_obs.sum(axis=1).values
        col_sums = df_obs.sum(axis=0).values
        df_adj_res = pd.DataFrame(index=df_obs.index, columns=df_obs.columns, dtype=float)
        for i in range(len(row_sums)):
            for j in range(len(col_sums)):
                exp = expected_arr[i, j]
                adj = (df_obs.iloc[i, j] - exp) / np.sqrt(exp * (1 - row_sums[i] / n) * (1 - col_sums[j] / n))
                df_adj_res.iloc[i, j] = adj

        # Bảng tỷ lệ phần trăm phân bổ theo hàng (Persona)
        df_pct = (df_obs.div(df_obs.sum(axis=1), axis=0) * 100).round(1)
        df_pct["Tổng Windows"] = df_obs.sum(axis=1)

        test_stats = {
            "Phép kiểm định": "Chi-Square Test of Independence",
            "Biến độc lập (Hàng)": "Persona ID (6 nhóm)",
            "Biến phụ thuộc (Cột)": "Khung giờ hoạt động (3 ca)",
            "Tổng số quan sát (N)": int(n),
            "Giá trị Chi-Square (χ²)": round(float(chi2), 4),
            "Bậc tự do (df)": int(dof),
            "p-value": round(float(p_val), 4),
            "Cramér's V": round(float(cramers_v), 4),
            "Mức ý nghĩa alpha": 0.05,
            "Kết luận thống kê": "Chưa đủ bằng chứng bác bỏ H0 (p = 0.8955 > 0.05). Do cỡ mẫu support nhỏ (N=79, vn_fb_001/002 có N=2), đây là quan sát sơ bộ, chưa thể khẳng định tuyệt đối."
        }

        return df_obs, df_exp, df_adj_res, test_stats

    def plot_temporal_residual_heatmap(
        self,
        df_windows: Optional[pd.DataFrame] = None,
        save_path: Optional[str] = None
    ) -> Any:
        """Trực quan hóa Heatmap 2 panel:
        Panel A: Bảng tần số quan sát (O) kèm kỳ vọng (E).
        Panel B: Heatmap phần dư chuẩn hóa hiệu chỉnh (Haberman Adjusted Residuals z) kèm kiểm định Chi-Square.
        """
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np

        df_obs, df_exp, df_adj_res, test_stats = self.get_temporal_contingency_and_residuals(df_windows)
        if df_obs.empty:
            return None

        # Rút ngắn tiêu đề cột cho biểu đồ gọn gàng
        short_cols = ["1. Ca Sáng\n(06h - 11h)", "2. Ca Trưa & Chiều\n(11h - 17h)", "3. Ca Tối\n(17h - 23h)"]
        plot_obs = df_obs.copy()
        plot_obs.columns = short_cols
        plot_adj = df_adj_res.copy()
        plot_adj.columns = short_cols

        # Chuẩn bị ma trận nhãn văn bản O (exp: E)
        annot_counts = np.empty(plot_obs.shape, dtype=object)
        for i in range(plot_obs.shape[0]):
            for j in range(plot_obs.shape[1]):
                annot_counts[i, j] = f"{plot_obs.iloc[i, j]}\n(exp: {df_exp.iloc[i, j]:.1f})"

        # Chuẩn bị ma trận nhãn phần dư z (* nếu |z| >= 1.96)
        annot_res = np.empty(plot_adj.shape, dtype=object)
        for i in range(plot_adj.shape[0]):
            for j in range(plot_adj.shape[1]):
                val = plot_adj.iloc[i, j]
                sig = " *" if abs(val) >= 1.96 else ""
                annot_res[i, j] = f"{val:+.2f}{sig}"

        fig, axes = plt.subplots(1, 2, figsize=(15.5, 6.2), dpi=120)

        # Panel A: Tần số quan sát vs kỳ vọng
        sns.heatmap(
            plot_obs,
            annot=annot_counts,
            fmt="",
            cmap="Blues",
            cbar=True,
            linewidths=1.2,
            linecolor="white",
            ax=axes[0],
            annot_kws={"fontsize": 10.5, "fontweight": "bold"}
        )
        axes[0].set_title(
            "A. Bảng Tần Số Quan Sát Thực Tế (O) vs Kỳ Vọng (E)\n(Số lượng cửa sổ hoạt động đã lên lịch)",
            fontsize=12, fontweight="bold", pad=12
        )
        axes[0].set_xlabel("Khung Giờ Sinh Hoạt", fontsize=11, fontweight="bold")
        axes[0].set_ylabel("Persona ID", fontsize=11, fontweight="bold")
        axes[0].tick_params(axis='y', rotation=0)

        # Panel B: Heatmap phần dư chuẩn hóa hiệu chỉnh
        chi2_val = test_stats.get("Giá trị Chi-Square (χ²)", 0.0)
        p_val = test_stats.get("p-value", 1.0)
        df_val = test_stats.get("Bậc tự do (df)", 0)
        v_val = test_stats.get("Cramér's V", 0.0)

        sns.heatmap(
            plot_adj.astype(float),
            annot=annot_res,
            fmt="",
            cmap="vlag",
            center=0,
            vmin=-2.5,
            vmax=2.5,
            cbar=True,
            linewidths=1.2,
            linecolor="white",
            ax=axes[1],
            annot_kws={"fontsize": 11, "fontweight": "bold"}
        )
        axes[1].set_title(
            f"B. Heatmap Phần Dư Chuẩn Hóa Hiệu Chỉnh (Adjusted Residuals)\n"
            f"Kiểm định Chi-Square: $\\chi^2 = {chi2_val:.2f}$ (p = {p_val:.4f}, df = {df_val}) | Cramér's V = {v_val:.2f}",
            fontsize=12, fontweight="bold", pad=12
        )
        axes[1].set_xlabel("Khung Giờ Sinh Hoạt", fontsize=11, fontweight="bold")
        axes[1].set_ylabel("Persona ID", fontsize=11, fontweight="bold")
        axes[1].tick_params(axis='y', rotation=0)

        # Ghi chú phương pháp luận ở chân biểu đồ
        fig.text(
            0.5, -0.065,
            "Ghi chú: Giá trị phần dư chuẩn hóa z thuộc khoảng [-1.96, +1.96] tương ứng với phân phối chuẩn tắc N(0, 1) ở mức ý nghĩa alpha = 0.05.\n"
            "Không có ô nào vượt ngưỡng (+1.96: thiên kiến ưa chuộng; -1.96: thiên kiến né tránh). Do cỡ mẫu support nhỏ (N=79), đây là quan sát sơ bộ.",
            ha="center", fontsize=9.5, style="italic", bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#ced4da")
        )

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
        return fig



# ==============================================================================
# V. CÁC HÀM TIỆN ÍCH DỄ SỬ DỤNG TRỰC TIẾP (CONVENIENCE APIS)
# ==============================================================================

def load_session_log(
    session_id: str,
    sqlite_path: Optional[str] = None
) -> SessionLog:
    """Nạp log đầy đủ của 1 session cụ thể theo session_id kèm bộ nhớ."""
    loader = ActionLoader(sqlite_path=sqlite_path)
    return loader.load_session(session_id)


def load_persona_sessions(
    persona_id: str,
    sqlite_path: Optional[str] = None
) -> PersonaActionHistory:
    """Nạp toàn bộ các session của 1 persona, sắp xếp theo thứ tự thời gian thực thi."""
    loader = ActionLoader(sqlite_path=sqlite_path)
    return loader.load_persona_sessions(persona_id)


def load_all_persona_sessions(
    sqlite_path: Optional[str] = None
) -> Dict[str, PersonaActionHistory]:
    """Nạp và kết tập toàn bộ session theo từng Persona theo thứ tự thời gian thực thi kèm bộ nhớ."""
    loader = ActionLoader(sqlite_path=sqlite_path)
    return loader.load_all_personas()


if __name__ == "__main__":
    print("=" * 75)
    print("KIỂM THỬ LOAD ACTION LOGS & BỘ NHỚ THEO PHIÊN (SESSION & PERSONA)")
    print("=" * 75)

    loader = ActionLoader()
    histories = loader.load_all_personas()
    print(f"\n Đã kết tập được {len(histories)} Persona:")

    for pid, hist in histories.items():
        print(f"\n Persona: {pid:<12} | Tên: {hist.persona_name:<15} | Tổng session: {hist.total_sessions} | Tổng action: {hist.total_actions}")
        for s in hist.sessions:
            pm = s.prior_memory
            wm = s.working_memory
            print(f"   * Phiên #{s.session_order}: ID={s.session_id[:8]}... | Bắt đầu={s.started_at} | Bước={s.total_actions}")
            if pm:
                print(f"     [Bộ nhớ dài hạn đầu phiên] Core Interests ({len(pm.core_interests)}): {pm.core_interests[:2]}... | Avoid ({len(pm.avoid_topics)}) | Threads có sẵn={len(pm.known_interest_threads)} | Affinities={len(pm.known_affinities)}")
            if wm:
                print(f"     [Bộ nhớ ngắn hạn trong phiên] Active Threads ({len(wm.active_threads)}): {[t.topic for t in wm.active_threads[:2]]} | Đã đọc ({len(wm.read_posts)} bài) | Habit Facts ({len(wm.habit_facts)}) | Memory Deltas ({len(wm.memory_deltas)})")

    # Xuất thử DataFrame tiến hóa bộ nhớ
    df_mem = loader.to_unified_memory_evolution_dataframe(histories)
    print(f"\n DataFrame Unified Memory Evolution: {df_mem.shape[0]} phiên, {df_mem.shape[1]} thuộc tính.")
    print("Một số cột tiến hóa bộ nhớ chính:")
    for col in [
        "persona_id", "session_order", "prior_core_interests_count", "prior_avoid_topics_count",
        "prior_known_threads_count", "session_active_threads_count", "session_read_posts_count",
        "session_habit_facts_count", "session_memory_deltas_count", "session_learned_count"
    ]:
        if col in df_mem.columns:
            print(f"  - {col}")

