"""Bộ nạp và tái cấu trúc Episode hoàn chỉnh từ cơ sở dữ liệu SQLite của persona-runner.

Mô tả:
Mô-đun này cung cấp các hàm chuyên dụng để truy vấn toàn bộ dữ liệu của một Episode
dựa trên `episode_id`, phân giải và bóc tách các trường JSON lồng nhau, ánh xạ các
chiều căn cứ nhận thức (Persona Grounding), trích xuất các chỉ số cử chỉ tương tác
vật lý (gesture metrics) và đóng gói vào cấu trúc `FullEpisodeSchema` (Pydantic v2).

Đường dẫn mặc định:
- D:\\source_code\\agent_in_works\\claw-master\\data\\persona-runner.sqlite
- Hoặc cấu hình qua biến môi trường: SQLITE_PATH

Các hàm chính:
- `get_sqlite_path(...)`: Lấy đường dẫn DB ưu tiên từ tham số -> biến môi trường -> mặc định.
- `list_episodes(...)`: Liệt kê tất cả các episode có trong database kèm thống kê tóm lược.
- `load_episode(episode_id, ...)`: Tải toàn bộ dữ liệu của 1 episode và trả về đối tượng `FullEpisodeSchema`.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sqlite3
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Import các Schema Pydantic
try:
    from loaders.schemas.runner_episode import (
        ActivityWindowSchema,
        ActiveEntitySchema,
        ActiveThreadSchema,
        BehavioralContractSchema,
        BotContextSchema,
        DecisionEvidenceItemSchema,
        DecisionEvidenceRecordSchema,
        EpisodeEventSchema,
        EpisodeMetadataSchema,
        EpisodeStepSchema,
        FullEpisodeSchema,
        HabitFactSchema,
        LiveRunSchema,
        MemoryConsolidationSchema,
        MemoryDeltaSchema,
        SearchHistorySchema,
        StepDecisionContextSchema,
        WorkingMemorySnapshotSchema,
    )
except ImportError:
    # Hỗ trợ khi import trực tiếp file trong folder
    from schemas.runner_episode import (
        ActivityWindowSchema,
        ActiveEntitySchema,
        ActiveThreadSchema,
        BehavioralContractSchema,
        BotContextSchema,
        DecisionEvidenceItemSchema,
        DecisionEvidenceRecordSchema,
        EpisodeEventSchema,
        EpisodeMetadataSchema,
        EpisodeStepSchema,
        FullEpisodeSchema,
        HabitFactSchema,
        LiveRunSchema,
        MemoryConsolidationSchema,
        MemoryDeltaSchema,
        SearchHistorySchema,
        StepDecisionContextSchema,
        WorkingMemorySnapshotSchema,
    )

# Đường dẫn mặc định tới SQLite của claw-master
DEFAULT_SQLITE_PATH = r"/data/projects/web-apps/agent_in_works/claw-master/data/persona-runner.sqlite"

try:
    from dotenv import load_dotenv
    # Tìm file .env ở thư mục hiện tại hoặc cấp trên
    load_dotenv(override=False)
except ImportError:
    pass


def get_sqlite_path(custom_path: Optional[str] = None) -> str:
    """Xác định đường dẫn file SQLite từ tham số, biến môi trường SQLITE_PATH hoặc mặc định."""
    if custom_path and str(custom_path).strip():
        return str(custom_path).strip()
    env_path = os.getenv("SQLITE_PATH")
    if env_path and env_path.strip():
        return env_path.strip()
    return DEFAULT_SQLITE_PATH


def _safe_json_loads(val: Any) -> Any:
    """Hàm phụ trợ phân giải JSON an toàn."""
    if val is None:
        return None
    if isinstance(val, (dict, list)):
        return val
    if isinstance(val, (int, float, bool)):
        return val
    if not isinstance(val, str) or not val.strip():
        return None
    try:
        return json.loads(val)
    except Exception:
        return val


def _parse_gesture_and_evidence(evidence_text: Optional[str]) -> Dict[str, Any]:
    """Bóc tách các chỉ số vật lý, cử chỉ cuộn chuột và URL từ chuỗi evidence."""
    res: Dict[str, Any] = {
        "gesture_pace": None,
        "gesture_total_px": None,
        "gesture_ms": None,
        "gesture_direction": None,
        "landing_correction_px": None,
        "action_url": None,
        "url_type": None,
        "execution_mode": None,
    }
    if not evidence_text or not isinstance(evidence_text, str):
        return res

    m_p = re.search(r'pace=(\w+)', evidence_text)
    m_t = re.search(r'total=(\d+)px', evidence_text)
    m_g = re.search(r'gesture_ms=(\d+)', evidence_text)
    m_d = re.search(r'direction=(\w+)', evidence_text)
    m_l = re.search(r'landing_correction=(-?\d+)px', evidence_text)
    m_u = re.search(r'(https?://[^\s;,\)]+)', evidence_text)

    if m_p:
        res["gesture_pace"] = m_p.group(1)
    if m_t:
        res["gesture_total_px"] = int(m_t.group(1))
    if m_g:
        res["gesture_ms"] = int(m_g.group(1))
    if m_d:
        res["gesture_direction"] = m_d.group(1)
    if m_l:
        res["landing_correction_px"] = int(m_l.group(1))

    if m_u:
        url = m_u.group(1)
        res["action_url"] = url
        if "/groups/" in url:
            res["url_type"] = "group"
        elif "/posts/" in url or "/photo/" in url:
            res["url_type"] = "post"
        elif "/search/" in url:
            res["url_type"] = "search"
        elif "/reel/" in url:
            res["url_type"] = "reel"
        else:
            res["url_type"] = "page_or_profile"

    if "CDP fallback" in evidence_text:
        res["execution_mode"] = "cdp_fallback"
    elif "native Cloak click" in evidence_text:
        res["execution_mode"] = "native_click"
    elif "native Cloak smooth wheel" in evidence_text:
        res["execution_mode"] = "smooth_wheel"
    elif "native Enter" in evidence_text or "search entered" in evidence_text:
        res["execution_mode"] = "native_search"
    elif "read visible post" in evidence_text:
        res["execution_mode"] = "read_post"
    else:
        res["execution_mode"] = "other"

    return res


def list_episodes(sqlite_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Liệt kê danh sách toàn bộ các episode có trong database kèm các chỉ số tóm tắt."""
    db_file = get_sqlite_path(sqlite_path)
    if not os.path.exists(db_file):
        raise FileNotFoundError(f"Không tìm thấy file SQLite tại: {db_file}")

    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = """
        SELECT 
            e.id,
            e.bot_id,
            b.persona_id,
            e.status,
            e.started_at,
            e.ended_at,
            e.terminal_reason,
            (SELECT COUNT(*) FROM agent_live_steps s WHERE s.episode_id = e.id) as step_count,
            (SELECT COUNT(*) FROM decision_evidence d WHERE d.episode_id = e.id) as evidence_count,
            (SELECT COUNT(*) FROM episode_events ev WHERE ev.episode_id = e.id) as event_count,
            (SELECT COUNT(*) FROM search_history sh WHERE sh.episode_id = e.id) as search_count,
            (SELECT COUNT(*) FROM memory_delta_ledger md WHERE md.episode_id = e.id) as memory_delta_count,
            e.video_path
        FROM episodes e
        LEFT JOIN bots b ON b.id = e.bot_id
        ORDER BY e.started_at DESC
    """
    cur.execute(query)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    # Tính thêm duration nếu có
    for r in rows:
        if r.get("started_at") and r.get("ended_at"):
            try:
                t0 = datetime.fromisoformat(r["started_at"].replace("Z", "+00:00"))
                t1 = datetime.fromisoformat(r["ended_at"].replace("Z", "+00:00"))
                r["duration_seconds"] = round((t1 - t0).total_seconds(), 2)
            except Exception:
                r["duration_seconds"] = None
        else:
            r["duration_seconds"] = None

    return rows


def load_episode(
    episode_id: str,
    sqlite_path: Optional[str] = None
) -> FullEpisodeSchema:
    """Tải và cấu trúc hóa toàn bộ một Episode từ SQLite theo episode_id.

    Args:
        episode_id: UUID định danh episode cần tải.
        sqlite_path: Đường dẫn file SQLite (tùy chọn, ưu tiên hơn biến môi trường).

    Returns:
        FullEpisodeSchema: Thực thể Pydantic v2 chứa toàn bộ metadata, bot context,
        hợp đồng, snapshot bộ nhớ, từng bước live steps kèm chỉ số cử chỉ,
        căn cứ persona, timeline sự kiện, tìm kiếm và tiến hóa bộ nhớ.

    Raises:
        FileNotFoundError: Nếu file database không tồn tại.
        ValueError: Nếu không tìm thấy episode_id trong cơ sở dữ liệu.
    """
    db_file = get_sqlite_path(sqlite_path)
    if not os.path.exists(db_file):
        raise FileNotFoundError(f"Không tìm thấy database SQLite tại: {db_file}")

    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # ==========================================================================
    # 1. Truy vấn bảng `episodes`
    # ==========================================================================
    cur.execute("SELECT * FROM episodes WHERE id = ?", (episode_id,))
    ep_row = cur.fetchone()
    if not ep_row:
        conn.close()
        raise ValueError(f"Không tìm thấy Episode với ID '{episode_id}' trong {db_file}")

    ep_data = dict(ep_row)

    # Tính thời lượng phiên
    duration_sec = None
    if ep_data.get("started_at") and ep_data.get("ended_at"):
        try:
            t0 = datetime.fromisoformat(ep_data["started_at"].replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(ep_data["ended_at"].replace("Z", "+00:00"))
            duration_sec = round((t1 - t0).total_seconds(), 2)
        except Exception:
            pass

    metadata = EpisodeMetadataSchema(
        id=ep_data["id"],
        window_id=ep_data.get("window_id"),
        bot_id=ep_data.get("bot_id"),
        profile_id=ep_data.get("profile_id"),
        contract_id=ep_data.get("contract_id"),
        runtime_provider=ep_data.get("runtime_provider"),
        status=ep_data["status"],
        started_at=ep_data.get("started_at"),
        ended_at=ep_data.get("ended_at"),
        lease_until=ep_data.get("lease_until"),
        summary=ep_data.get("summary"),
        terminal_reason=ep_data.get("terminal_reason"),
        video_path=ep_data.get("video_path"),
        duration_seconds=duration_sec,
    )

    # ==========================================================================
    # 2. Truy vấn `bots` & `persona_versions`
    # ==========================================================================
    bot_context: Optional[BotContextSchema] = None
    if ep_data.get("bot_id"):
        cur.execute("SELECT * FROM bots WHERE id = ?", (ep_data["bot_id"],))
        b_row = cur.fetchone()
        if b_row:
            b_dict = dict(b_row)
            # Lấy bản ghi persona_versions mới nhất của bot
            cur.execute(
                "SELECT * FROM persona_versions WHERE bot_id = ? ORDER BY version DESC LIMIT 1",
                (b_dict["id"],)
            )
            pv_row = cur.fetchone()
            pv_dict = dict(pv_row) if pv_row else {}
            content_json = _safe_json_loads(pv_dict.get("content_json")) or {}

            # Trích xuất các phân nhóm thuộc tính persona
            p_attrs = content_json.get("attributes", {})
            demographics = {}
            traits = {}
            interests = {}

            if isinstance(p_attrs, dict):
                for k, v in p_attrs.items():
                    k_lower = k.lower()
                    if any(sub in k_lower for sub in ["age", "gender", "occupation", "tuoi", "gioi_tinh", "nghe_nghiep", "education"]):
                        demographics[k] = v
                    elif any(sub in k_lower for sub in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism", "curiosity"]):
                        traits[k] = v
                    elif "interest" in k_lower or "topic" in k_lower or "cuisine" in k_lower or "sport" in k_lower:
                        interests[k] = v

            bot_context = BotContextSchema(
                bot_id=b_dict["id"],
                persona_id=b_dict.get("persona_id") or content_json.get("persona_id"),
                bot_status=b_dict.get("status"),
                bot_created_at=b_dict.get("created_at"),
                persona_version_id=pv_dict.get("id"),
                persona_version=pv_dict.get("version"),
                persona_content_hash=pv_dict.get("content_hash"),
                persona_name=content_json.get("persona_name") or content_json.get("name") or b_dict.get("persona_id"),
                persona_demographics=demographics,
                persona_traits=traits,
                persona_interests=interests,
                full_persona_json=content_json,
            )

    # ==========================================================================
    # 3. Truy vấn `behavioral_contracts`
    # ==========================================================================
    contract: Optional[BehavioralContractSchema] = None
    if ep_data.get("contract_id"):
        cur.execute("SELECT * FROM behavioral_contracts WHERE id = ?", (ep_data["contract_id"],))
        c_row = cur.fetchone()
        if c_row:
            c_dict = dict(c_row)
            contract = BehavioralContractSchema(
                id=c_dict["id"],
                schema_version=c_dict.get("schema_version"),
                source_hash=c_dict.get("source_hash"),
                contract_rules=_safe_json_loads(c_dict.get("contract_json")) or {},
                compiler_trace=_safe_json_loads(c_dict.get("compiler_trace_json")) or {},
                created_at=c_dict.get("created_at"),
            )

    # ==========================================================================
    # 4. Truy vấn `activity_windows`
    # ==========================================================================
    window: Optional[ActivityWindowSchema] = None
    if ep_data.get("window_id"):
        cur.execute("SELECT * FROM activity_windows WHERE id = ?", (ep_data["window_id"],))
        w_row = cur.fetchone()
        if w_row:
            w_dict = dict(w_row)
            window = ActivityWindowSchema(
                id=w_dict["id"],
                local_date=w_dict.get("local_date"),
                start_at=w_dict.get("start_at"),
                end_at=w_dict.get("end_at"),
                max_actions=w_dict.get("max_actions"),
                seed=w_dict.get("seed"),
                surface_bias=w_dict.get("surface_bias"),
                state=w_dict.get("state"),
                claimed_by=w_dict.get("claimed_by"),
                terminal_reason=w_dict.get("terminal_reason"),
            )

    # ==========================================================================
    # 5. Truy vấn `agent_live_runs`
    # ==========================================================================
    run: Optional[LiveRunSchema] = None
    cur.execute("SELECT * FROM agent_live_runs WHERE episode_id = ?", (episode_id,))
    r_row = cur.fetchone()
    if r_row:
        r_dict = dict(r_row)
        run = LiveRunSchema(
            status=r_dict.get("status"),
            started_at=r_dict.get("started_at"),
            updated_at=r_dict.get("updated_at"),
            error=r_dict.get("error"),
            state_json=_safe_json_loads(r_dict.get("state_json")) or {},
        )

    # ==========================================================================
    # 6. Truy vấn `episode_working_memory`
    # ==========================================================================
    working_memory: Optional[WorkingMemorySnapshotSchema] = None
    cur.execute("SELECT * FROM episode_working_memory WHERE episode_id = ?", (episode_id,))
    wm_row = cur.fetchone()
    if wm_row:
        wm_dict = dict(wm_row)
        snap = _safe_json_loads(wm_dict.get("snapshot_json")) or {}
        working_memory = WorkingMemorySnapshotSchema(
            snapshot_updated_at=wm_dict.get("updated_at"),
            completed_actions=snap.get("completed_actions"),
            current_surface=snap.get("current_surface"),
            elapsed_seconds=snap.get("elapsed_seconds"),
            planned_active_seconds=snap.get("planned_active_seconds"),
            planned_session_minutes=snap.get("planned_session_minutes") if isinstance(snap.get("planned_session_minutes"), dict) else {},
            remaining_seconds=snap.get("remaining_seconds"),
            recent_actions=snap.get("recent_actions") if isinstance(snap.get("recent_actions"), list) else [],
            search_context=snap.get("search_context") if isinstance(snap.get("search_context"), dict) else {},
            raw_snapshot=snap,
        )

    # ==========================================================================
    # 7. Truy vấn `decision_evidence` (Persona Grounding Items)
    # ==========================================================================
    cur.execute("SELECT * FROM decision_evidence WHERE episode_id = ? ORDER BY step_index", (episode_id,))
    de_rows = [dict(r) for r in cur.fetchall()]

    step_evidence_map: Dict[int, List[DecisionEvidenceItemSchema]] = {}
    decision_evidences: List[DecisionEvidenceRecordSchema] = []

    for de in de_rows:
        raw_items = _safe_json_loads(de.get("evidence_json")) or []
        items_list: List[DecisionEvidenceItemSchema] = []
        if isinstance(raw_items, list):
            for itm in raw_items:
                if isinstance(itm, dict) and "dimension" in itm:
                    items_list.append(DecisionEvidenceItemSchema(
                        dimension=str(itm.get("dimension")),
                        role=itm.get("role") or "primary",
                        source=itm.get("source") or "persona",
                        value=itm.get("value"),
                        weight=float(itm.get("weight") or 0.0),
                        reference_id=itm.get("reference_id"),
                    ))

        record = DecisionEvidenceRecordSchema(
            id=de.get("id"),
            step_index=de["step_index"],
            action=de.get("action", ""),
            items=items_list,
            created_at=de.get("created_at"),
        )
        decision_evidences.append(record)

        s_idx = de["step_index"]
        if s_idx not in step_evidence_map:
            step_evidence_map[s_idx] = []
        step_evidence_map[s_idx].extend(items_list)

    # ==========================================================================
    # 8. Truy vấn `agent_live_steps` & Bóc tách cử chỉ / quyết định
    # ==========================================================================
    cur.execute("SELECT * FROM agent_live_steps WHERE episode_id = ? ORDER BY step_index", (episode_id,))
    step_rows = [dict(r) for r in cur.fetchall()]

    steps: List[EpisodeStepSchema] = []
    for sr in step_rows:
        payload = _safe_json_loads(sr.get("payload_json")) or {}
        decision = payload.get("decision", {})
        outcome = payload.get("outcome", {})
        debug = payload.get("debug", {})
        perception_data = payload.get("perception")

        # Chuẩn hóa perception thành chuỗi
        perception_str = None
        if isinstance(perception_data, str):
            perception_str = perception_data
        elif isinstance(perception_data, dict):
            perception_str = json.dumps(perception_data, ensure_ascii=False)

        tool = decision.get("tool", "unknown")
        args = decision.get("args") if isinstance(decision.get("args"), dict) else {}
        action_summary = decision.get("actionSummary")
        reason = decision.get("reason") or args.get("reason")
        target_id = args.get("target_id")

        # Ý định (Intent)
        intent = args.get("intent")
        if not intent:
            if tool == "observe_viewport":
                intent = "observe"
            elif tool == "end_episode":
                intent = "end"
            elif tool == "session_status":
                intent = "status"
            else:
                intent = tool

        # Decision context
        dec_ctx_data = args.get("decision_context")
        decision_context = None
        if isinstance(dec_ctx_data, dict):
            decision_context = StepDecisionContextSchema(
                topic=dec_ctx_data.get("topic"),
                purpose=dec_ctx_data.get("purpose"),
                state=dec_ctx_data.get("state"),
                continuation=dec_ctx_data.get("continuation"),
                interest_relation=dec_ctx_data.get("interest_relation"),
                open_question=dec_ctx_data.get("open_question"),
                thread_id=dec_ctx_data.get("thread_id"),
            )

        # Outcome
        verified = outcome.get("verified")
        ended = outcome.get("ended", False)
        raw_outcome = outcome.get("raw") if isinstance(outcome.get("raw"), dict) else {}
        error = raw_outcome.get("error") if isinstance(raw_outcome, dict) else None

        # Bằng chứng kết quả (Evidence text)
        evidence_text = None
        if outcome.get("evidence"):
            ev_val = outcome.get("evidence")
            evidence_text = ev_val if isinstance(ev_val, str) else json.dumps(ev_val, ensure_ascii=False)
        elif raw_outcome.get("evidence"):
            ev_val = raw_outcome.get("evidence")
            evidence_text = ev_val if isinstance(ev_val, str) else json.dumps(ev_val, ensure_ascii=False)

        # Trích xuất surface & resolved tool
        surface = raw_outcome.get("surface")
        resolved_tool = raw_outcome.get("resolved_tool") or raw_outcome.get("tool")
        exec_duration_ms = raw_outcome.get("execution_duration_ms")

        # Bóc tách các chỉ số cử chỉ (Gesture Metrics) từ evidence_text
        gesture_info = _parse_gesture_and_evidence(evidence_text)

        # Nếu surface chưa có, đoán từ actionSummary hoặc url
        if not surface:
            if gesture_info.get("url_type"):
                surface = gesture_info["url_type"]
            elif "feed" in tool or (action_summary and "feed" in action_summary):
                surface = "feed"

        # LLM Latency & Token Usage
        model_latency_ms = debug.get("modelLatencyMs")
        tool_execution_ms = debug.get("toolExecutionMs")
        llm_usage = debug.get("llmUsage", {})
        prompt_tokens = llm_usage.get("prompt_tokens") or llm_usage.get("input_tokens")
        completion_tokens = llm_usage.get("completion_tokens") or llm_usage.get("output_tokens")
        total_tokens = llm_usage.get("total_tokens")
        if total_tokens is None and prompt_tokens is not None and completion_tokens is not None:
            total_tokens = prompt_tokens + completion_tokens

        # Lấy persona dimension groundings
        s_idx = sr["step_index"]
        dim_evidence = step_evidence_map.get(s_idx, [])
        # Nếu trong step payload args có sẵn dimension_evidence thì bổ sung nếu map rỗng
        if not dim_evidence and isinstance(args.get("dimension_evidence"), list):
            for itm in args["dimension_evidence"]:
                if isinstance(itm, dict) and "dimension" in itm:
                    dim_evidence.append(DecisionEvidenceItemSchema(
                        dimension=str(itm.get("dimension")),
                        role=itm.get("role") or "primary",
                        source=itm.get("source") or "persona",
                        value=itm.get("value"),
                        weight=float(itm.get("weight") or 0.0),
                        reference_id=itm.get("reference_id"),
                    ))

        step_obj = EpisodeStepSchema(
            step_index=s_idx,
            created_at=sr.get("created_at"),
            timestamp=payload.get("timestamp"),
            tool=tool,
            intent=intent,
            target_id=target_id,
            action_summary=action_summary,
            reason=reason,
            args=args,
            decision_context=decision_context,
            verified=verified,
            ended=ended,
            evidence_text=evidence_text,
            surface=surface,
            resolved_tool=resolved_tool,
            execution_duration_ms=exec_duration_ms,
            error=error,
            gesture_pace=gesture_info["gesture_pace"],
            gesture_total_px=gesture_info["gesture_total_px"],
            gesture_ms=gesture_info["gesture_ms"],
            gesture_direction=gesture_info["gesture_direction"],
            landing_correction_px=gesture_info["landing_correction_px"],
            action_url=gesture_info["action_url"],
            url_type=gesture_info["url_type"],
            execution_mode=gesture_info["execution_mode"],
            perception=perception_str,
            model_latency_ms=model_latency_ms,
            tool_execution_ms=tool_execution_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            dimension_evidence=dim_evidence,
        )
        steps.append(step_obj)

    # ==========================================================================
    # 9. Truy vấn `episode_events`
    # ==========================================================================
    cur.execute("SELECT * FROM episode_events WHERE episode_id = ? ORDER BY created_at", (episode_id,))
    ev_rows = [dict(r) for r in cur.fetchall()]
    events: List[EpisodeEventSchema] = []
    for er in ev_rows:
        events.append(EpisodeEventSchema(
            id=er["id"],
            kind=er["kind"],
            payload=_safe_json_loads(er.get("payload_json")) or {},
            created_at=er.get("created_at"),
        ))

    # ==========================================================================
    # 10. Truy vấn `search_history`
    # ==========================================================================
    cur.execute("SELECT * FROM search_history WHERE episode_id = ? ORDER BY step_index", (episode_id,))
    sh_rows = [dict(r) for r in cur.fetchall()]
    searches: List[SearchHistorySchema] = []
    for sh in sh_rows:
        searches.append(SearchHistorySchema(
            id=sh["id"],
            step_index=sh.get("step_index"),
            platform=sh.get("platform") or "facebook",
            query=sh.get("query", ""),
            purpose=sh.get("purpose"),
            verified=bool(sh.get("verified")) if sh.get("verified") is not None else None,
            outcome=sh.get("outcome"),
            created_at=sh.get("created_at"),
        ))

    # ==========================================================================
    # 11. Truy vấn `memory_consolidation_runs` & `memory_delta_ledger`
    # ==========================================================================
    consolidation: Optional[MemoryConsolidationSchema] = None
    cur.execute("SELECT * FROM memory_consolidation_runs WHERE episode_id = ? ORDER BY created_at DESC LIMIT 1", (episode_id,))
    cr_row = cur.fetchone()
    if cr_row:
        cr_dict = dict(cr_row)
        res_json = _safe_json_loads(cr_dict.get("result_json")) or {}
        consolidation = MemoryConsolidationSchema(
            id=cr_dict["id"],
            status=cr_dict.get("status"),
            input_event_count=cr_dict.get("input_event_count"),
            learned_count=res_json.get("learned") if isinstance(res_json, dict) else None,
            error=cr_dict.get("error"),
            result_json=res_json,
            created_at=cr_dict.get("created_at"),
        )

    cur.execute("SELECT * FROM memory_delta_ledger WHERE episode_id = ? ORDER BY created_at", (episode_id,))
    dl_rows = [dict(r) for r in cur.fetchall()]
    deltas: List[MemoryDeltaSchema] = []
    for dl in dl_rows:
        deltas.append(MemoryDeltaSchema(
            id=dl.get("id"),
            record_type=dl.get("record_type", ""),
            record_key=dl.get("record_key", ""),
            operation=dl.get("operation", ""),
            before=_safe_json_loads(dl.get("before_json")),
            after=_safe_json_loads(dl.get("after_json")),
            evidence=_safe_json_loads(dl.get("evidence_json")),
            created_at=dl.get("created_at"),
        ))

    # ==========================================================================
    # 12. Truy vấn `habit_facts`
    # ==========================================================================
    cur.execute("SELECT * FROM habit_facts WHERE episode_id = ? ORDER BY created_at", (episode_id,))
    hf_rows = [dict(r) for r in cur.fetchall()]
    habits: List[HabitFactSchema] = []
    for hf in hf_rows:
        habits.append(HabitFactSchema(
            id=hf["id"],
            kind=hf["kind"],
            value=_safe_json_loads(hf.get("value_json")) or {},
            created_at=hf.get("created_at"),
        ))

    # ==========================================================================
    # 13. Truy vấn `entity_affinities` & `interest_threads` liên kết episode
    # ==========================================================================
    active_entities: List[ActiveEntitySchema] = []
    cur.execute("SELECT * FROM entity_affinities WHERE episode_ids_json LIKE ?", (f"%{episode_id}%",))
    for ea in cur.fetchall():
        ea_dict = dict(ea)
        active_entities.append(ActiveEntitySchema(
            id=ea_dict["id"],
            entity_type=ea_dict.get("entity_type"),
            entity_key=ea_dict.get("entity_key"),
            display_name=ea_dict.get("display_name"),
            affinity=float(ea_dict["affinity"]) if ea_dict.get("affinity") is not None else None,
            familiarity=float(ea_dict["familiarity"]) if ea_dict.get("familiarity") is not None else None,
            evidence_count=ea_dict.get("evidence_count"),
            relationship_state=ea_dict.get("relationship_state"),
            updated_at=ea_dict.get("updated_at"),
        ))

    active_threads: List[ActiveThreadSchema] = []
    cur.execute("SELECT * FROM interest_threads WHERE episode_ids_json LIKE ?", (f"%{episode_id}%",))
    for it in cur.fetchall():
        it_dict = dict(it)
        active_threads.append(ActiveThreadSchema(
            id=it_dict["id"],
            thread_key=it_dict.get("thread_key", ""),
            title=it_dict.get("title"),
            summary=it_dict.get("summary"),
            confidence=float(it_dict["confidence"]) if it_dict.get("confidence") is not None else None,
            evidence_count=it_dict.get("evidence_count"),
            status=it_dict.get("status"),
            updated_at=it_dict.get("updated_at"),
        ))

    conn.close()

    # ==========================================================================
    # 14. Đóng gói vào FullEpisodeSchema
    # ==========================================================================
    full_episode = FullEpisodeSchema(
        metadata=metadata,
        bot=bot_context,
        contract=contract,
        window=window,
        run=run,
        working_memory=working_memory,
        steps=steps,
        decision_evidences=decision_evidences,
        events=events,
        searches=searches,
        consolidation=consolidation,
        deltas=deltas,
        habits=habits,
        active_entities=active_entities,
        active_threads=active_threads,
    )

    return full_episode
