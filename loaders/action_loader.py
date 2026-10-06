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
        """Trả về từ điển tóm tắt các chỉ số chính của session."""
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
        }

    @classmethod
    def from_full_episode(
        cls,
        ep: FullEpisodeSchema,
        session_order: Optional[int] = None
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


# ==============================================================================
# II. LỚP ĐIỀU PHỐI ACTION LOADER
# ==============================================================================

class ActionLoader:
    """Bộ nạp chuyên sâu quản lý Action Logs và kết tập Sessions theo Persona.
    
    Cung cấp các API thuận tiện để tải session đơn lẻ hoặc tải toàn bộ session
    kết tập theo Persona có sắp xếp theo thời gian thực thi.
    """

    def __init__(
        self,
        sqlite_path: Optional[str] = None,
        action_logs_dir: Optional[str] = None
    ) -> None:
        self.sqlite_path = get_sqlite_path(sqlite_path)
        self.action_logs_dir = Path(action_logs_dir) if action_logs_dir else Path("./data/action_logs")
        self._persona_histories_cache: Optional[Dict[str, PersonaActionHistory]] = None

    def load_session(
        self,
        session_id: str,
        source: Literal["auto", "sqlite", "json"] = "auto"
    ) -> SessionLog:
        """Nạp log của 1 session (episode) theo session_id.

        Args:
            session_id: UUID định danh episode / session.
            source: Nguồn dữ liệu ('auto', 'sqlite', 'json').

        Returns:
            SessionLog: Đối tượng chứa toàn bộ actions sắp xếp theo thứ tự thời gian.
        """
        # 1. Thử từ SQLite
        if source in ("auto", "sqlite") and os.path.exists(self.sqlite_path):
            try:
                full_ep = load_episode(session_id, sqlite_path=self.sqlite_path)
                return SessionLog.from_full_episode(full_ep)
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
            Mỗi PersonaActionHistory chứa các session đã được sắp xếp tăng dần theo `started_at`.
        """
        if self._persona_histories_cache is not None and not refresh:
            return self._persona_histories_cache

        all_sessions: List[SessionLog] = []

        # 1. Nạp từ SQLite nếu có
        if source in ("auto", "sqlite") and os.path.exists(self.sqlite_path):
            try:
                episodes_meta = list_episodes(sqlite_path=self.sqlite_path)
                for ep_m in episodes_meta:
                    ep_id = ep_m["id"]
                    try:
                        full_ep = load_episode(ep_id, sqlite_path=self.sqlite_path)
                        sess = SessionLog.from_full_episode(full_ep)
                        all_sessions.append(sess)
                    except Exception as err:
                        print(f"[!] Bỏ qua episode {ep_id}: {err}")
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


# ==============================================================================
# III. CÁC HÀM TIỆN ÍCH DỄ SỬ DỤNG TRỰC TIẾP (CONVENIENCE APIS)
# ==============================================================================

def load_session_log(
    session_id: str,
    sqlite_path: Optional[str] = None
) -> SessionLog:
    """Nạp log đầy đủ của 1 session cụ thể theo session_id."""
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
    """Nạp và kết tập toàn bộ session theo từng Persona theo thứ tự thời gian thực thi."""
    loader = ActionLoader(sqlite_path=sqlite_path)
    return loader.load_all_personas()


if __name__ == "__main__":
    print("=" * 70)
    print("KIỂM THỬ LOAD ACTION LOGS VÀ KẾT TẬP THEO PERSONA")
    print("=" * 70)

    loader = ActionLoader()
    histories = loader.load_all_personas()
    print(f"\n Đã kết tập được {len(histories)} Persona:")

    for pid, hist in histories.items():
        print(f"\n Persona: {pid:<12} | Tên: {hist.persona_name:<15} | Tổng session: {hist.total_sessions} | Tổng action: {hist.total_actions}")
        for s in hist.sessions:
            print(f"   - Phiên #{s.session_order}: ID={s.session_id[:8]}... | Bắt đầu={s.started_at} | Số bước={s.total_actions} | Surface={s.surface_distribution}")

    # Xuất thử DataFrame tổng hợp
    df_actions = loader.to_unified_actions_dataframe(histories)
    print(f"\n DataFrame Unified Actions: {df_actions.shape[0]} dòng, {df_actions.shape[1]} cột.")
    print("Các cột chính:", list(df_actions.columns[:10]))
