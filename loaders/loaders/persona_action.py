from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Union, Tuple

# Đảm bảo project root có trong sys.path khi chạy trực tiếp hoặc import
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd

from configs.settings import cfg
from data_loader import PersonaDataLoader

# Đảm bảo in Unicode tiếng Việt trên Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

fb_pf_persona_path = cfg.persona.fb_pf_persona
no_persona_action_path = cfg.fb_action_logs.without_persona
persona_action_path = cfg.fb_action_logs.persona


def parse_wm_summary(summary_text: Optional[str]) -> Dict[str, Optional[int]]:
    """Dùng regex bóc tách các chỉ số nhận thức trong working_memory.summary."""
    res = {
        "wm_summary_run_minutes": None,
        "wm_summary_planned_minutes": None,
        "wm_summary_read_posts": None,
        "wm_summary_searched_topics": None,
        "wm_summary_opened_sources": None,
    }
    if not summary_text or not isinstance(summary_text, str):
        return res

    m = re.search(
        r'Phiên đã chạy\s+(\d+)/(\d+)\s+phút\.\s+Đã đọc\s+(\d+)\s+bài viết,\s+tìm kiếm\s+(\d+)\s+chủ đề,\s+mở\s+(\d+)\s+nguồn/trang',
        summary_text
    )
    if m:
        res["wm_summary_run_minutes"] = int(m.group(1))
        res["wm_summary_planned_minutes"] = int(m.group(2))
        res["wm_summary_read_posts"] = int(m.group(3))
        res["wm_summary_searched_topics"] = int(m.group(4))
        res["wm_summary_opened_sources"] = int(m.group(5))
    return res


def parse_action_summary(summary_text: Optional[str]) -> Dict[str, Any]:
    """Dùng regex bóc tách toàn bộ thông số vật lý và kỹ thuật trong recent_actions[].summary."""
    res = {
        "gesture_pace": None,
        "gesture_total_px": None,
        "gesture_ms": None,
        "gesture_direction": None,
        "landing_correction_px": None,
        "action_url": None,
        "url_type": None,
        "execution_mode": None,
    }
    if not summary_text or not isinstance(summary_text, str):
        return res

    m_p = re.search(r'pace=(\w+)', summary_text)
    m_t = re.search(r'total=(\d+)px', summary_text)
    m_g = re.search(r'gesture_ms=(\d+)', summary_text)
    m_d = re.search(r'direction=(\w+)', summary_text)
    m_l = re.search(r'landing_correction=(\d+)px', summary_text)
    m_u = re.search(r'(https?://[^\s;,\)]+)', summary_text)

    if m_p: res["gesture_pace"] = m_p.group(1)
    if m_t: res["gesture_total_px"] = int(m_t.group(1))
    if m_g: res["gesture_ms"] = int(m_g.group(1))
    if m_d: res["gesture_direction"] = m_d.group(1)
    if m_l: res["landing_correction_px"] = int(m_l.group(1))

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

    if "CDP fallback" in summary_text:
        res["execution_mode"] = "cdp_fallback"
    elif "native Cloak click" in summary_text:
        res["execution_mode"] = "native_click"
    elif "native Cloak smooth wheel" in summary_text:
        res["execution_mode"] = "smooth_wheel"
    elif "native Enter" in summary_text or "search entered" in summary_text:
        res["execution_mode"] = "native_search"
    elif "read visible post" in summary_text:
        res["execution_mode"] = "read_post"
    else:
        res["execution_mode"] = "other"

    return res


def parse_evidence_strings(evidence_list: List[str]) -> Tuple[List[Dict[str, str]], Dict[str, int], List[str]]:
    """Dùng regex bóc tách các chuỗi source:dimension=reason trong active_threads.evidence."""
    parsed: List[Dict[str, str]] = []
    source_counts: Dict[str, int] = {"persona": 0, "neutral_control": 0, "viewport": 0, "session_memory": 0, "other": 0}
    dimensions: List[str] = []

    for ev in evidence_list:
        if not isinstance(ev, str):
            continue
        m = re.match(r'^([^:=]+):([^=]+)=(.*)$', ev)
        if m:
            src = m.group(1).strip()
            dim = m.group(2).strip()
            reason = m.group(3).strip()
            parsed.append({"source": src, "dimension": dim, "reason": reason})
            dimensions.append(dim)
            if src in source_counts:
                source_counts[src] += 1
            else:
                source_counts["other"] += 1
        else:
            parsed.append({"source": "raw", "dimension": "raw", "reason": ev})
            source_counts["other"] += 1

    return parsed, source_counts, dimensions


def parse_dimension_evidence(dim_evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Bóc tách ma trận trọng số và vai trò nhận thức từ mảng dimension_evidence."""
    roles = []
    weights = []
    dims = []
    sources = []
    ref_ids = []
    primary_dim = None
    primary_val = None
    primary_ref = None

    role_counts = {"primary": 0, "supporting": 0, "situational": 0, "constraint": 0, "other": 0}

    for d in dim_evidence:
        if not isinstance(d, dict):
            continue
        r = d.get("role")
        w = d.get("weight")
        dim = d.get("dimension")
        src = d.get("source")
        val = d.get("value")
        ref = d.get("reference_id")

        if r:
            roles.append(r)
            if r in role_counts:
                role_counts[r] += 1
            else:
                role_counts["other"] += 1
        if w is not None and isinstance(w, (int, float)):
            weights.append(float(w))
        if dim:
            dims.append(dim)
        if src:
            sources.append(src)
        if ref:
            ref_ids.append(str(ref))

        if r == "primary" and primary_dim is None:
            primary_dim = dim
            primary_val = val
            primary_ref = ref

    if primary_dim is None and dim_evidence:
        first = dim_evidence[0]
        if isinstance(first, dict):
            primary_dim = first.get("dimension")
            primary_val = first.get("value")
            primary_ref = first.get("reference_id")

    return {
        "num_dimension_evidence": len(dim_evidence),
        "dimension_sources": ",".join(sorted(set(sources))) if sources else None,
        "dimensions": ",".join(sorted(set(dims))) if dims else None,
        "dim_evidence_primary_dimension": primary_dim,
        "dim_evidence_primary_value": primary_val,
        "dim_evidence_primary_ref_id": primary_ref,
        "dim_evidence_max_weight": max(weights) if weights else None,
        "dim_evidence_avg_weight": round(sum(weights) / len(weights), 2) if weights else None,
        "dim_evidence_roles": ",".join(sorted(set(roles))) if roles else None,
        "dim_evidence_reference_ids": ",".join(sorted(set(ref_ids))) if ref_ids else None,
        "num_dim_primary": role_counts["primary"],
        "num_dim_supporting": role_counts["supporting"],
        "num_dim_situational": role_counts["situational"],
        "num_dim_constraint": role_counts["constraint"],
    }


def parse_step_action_summary(summary_text: Optional[str]) -> Dict[str, Any]:
    """Bóc tách hành động và bề mặt mục tiêu từ action_summary của step record."""
    if not summary_text or not isinstance(summary_text, str):
        return {"action_summary_verb": None, "action_summary_target_surface": None}

    verb = None
    target_surf = None
    m_act = re.search(r'Hành động:\s*(\w+)(?:\s+trên\s+([^\s]+))?', summary_text)
    if m_act:
        verb = m_act.group(1)
        target_surf = m_act.group(2)
    elif "Quan sát màn hình" in summary_text:
        verb = "observe"

    return {"action_summary_verb": verb, "action_summary_target_surface": target_surf}


class PersonaActionLoader:
    """Class nạp và xử lý Action Logs từ các file benchmark_eda_*.json.
    
    Hỗ trợ nạp và bóc tách chuyên sâu toàn bộ step_records, session_context bằng Regex,
    bao gồm Working Memory, Dimension Evidences, Target Candidates, Cử chỉ cuộn chuột,
    Cơ chế cảnh báo phân tâm, Ký ức đa phiên và Ngân sách thời gian.
    """

    def __init__(
        self,
        persona_path: Optional[Union[str, Path]] = None,
        no_persona_path: Optional[Union[str, Path]] = None,
        fb_persona_path: Optional[Union[str, Path]] = None,
    ) -> None:
        self.persona_action_path = Path(persona_path) if persona_path else persona_action_path
        self.no_persona_action_path = Path(no_persona_path) if no_persona_path else no_persona_action_path
        self.fb_pf_persona_path = Path(fb_persona_path) if fb_persona_path else fb_pf_persona_path
        self._manifest_map: Optional[Dict[str, str]] = None
        self._persona_profiles_cache: Optional[Dict[str, Dict[str, Any]]] = None

    def _get_manifest_mappings(self) -> Dict[str, str]:
        """Đọc file manifest.json từ cả 2 nguồn để ánh xạ episode_id -> persona_id chuẩn."""
        if self._manifest_map is not None:
            return self._manifest_map

        manifest_map: Dict[str, str] = {}
        paths = [
            self.persona_action_path / "manifest.json",
            self.no_persona_action_path / "manifest.json",
        ]
        for p in paths:
            if p.is_file():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        m_data = json.load(f)
                    trials = m_data.get("trials", [])
                    for t in trials:
                        ep_id = t.get("episode_id")
                        p_id = t.get("persona_id")
                        is_neutral = t.get("neutral_control", False)
                        if ep_id:
                            manifest_map[ep_id] = None if is_neutral else p_id
                except Exception as e:
                    print(f"[!] Lỗi đọc manifest {p}: {e}")

        self._manifest_map = manifest_map
        return manifest_map

    def load_fb_pf_persona(self) -> pd.DataFrame:
        """Nạp danh sách Facebook Persona gốc thành DataFrame dạng bảng phẳng."""
        loader = PersonaDataLoader(self.fb_pf_persona_path)
        return loader.to_fb_dataframe(include_id=True)

    def load_persona_profiles(self) -> pd.DataFrame:
        """Bóc tách đầy đủ hồ sơ tâm lý và hành vi của Persona từ original_facebook_persona.json."""
        if not self.fb_pf_persona_path.is_file():
            return pd.DataFrame()

        with open(self.fb_pf_persona_path, "r", encoding="utf-8") as fp:
            raw_personas = json.load(fp)

        profiles: List[Dict[str, Any]] = []
        for item in raw_personas:
            pid = item.get("persona_id")
            fb_prof = item.get("facebook_behavior_profile") or {}
            fb_behavior = fb_prof.get("facebookBehavior") or {}
            usage = fb_prof.get("usage") or {}
            interests = fb_prof.get("interests") or {}
            persona_obj = item.get("persona") or {}

            strong_interests = interests.get("strong") or []
            avoid_interests = interests.get("avoid") or []

            row = {
                "persona_id": pid,
                "persona_name": persona_obj.get("name"),
                "persona_age": persona_obj.get("age"),
                "persona_gender": persona_obj.get("gender"),
                "persona_occupation": persona_obj.get("occupation"),
                
                # Thuộc tính hành vi điều hướng & nhịp độ
                "pace": fb_behavior.get("pace"),
                "restStyle": fb_behavior.get("restStyle"),
                "readingDepth": fb_behavior.get("readingDepth"),
                "discoveryStyle": fb_behavior.get("discoveryStyle"),
                "interactionStyle": fb_behavior.get("interactionStyle"),
                "preferredSurface": fb_behavior.get("preferredSurface"),
                
                # Thói quen sử dụng
                "attention": usage.get("attention"),
                "energy": usage.get("energy"),
                "facebookFrequency": usage.get("facebookFrequency"),
                
                # Sở thích
                "strong_interests_count": len(strong_interests),
                "strong_interests": ", ".join(strong_interests),
                "avoid_interests_count": len(avoid_interests),
                "avoid_interests": ", ".join(avoid_interests),
                "inferred_habits_count": len(fb_prof.get("inferredHabits") or []),
            }
            profiles.append(row)

        df_prof = pd.DataFrame(profiles)
        return df_prof

    def _get_persona_profiles_dict(self) -> Dict[str, Dict[str, Any]]:
        """Lấy dict hồ sơ persona theo persona_id để ánh xạ nhanh."""
        if self._persona_profiles_cache is not None:
            return self._persona_profiles_cache

        df_prof = self.load_persona_profiles()
        if df_prof.empty:
            self._persona_profiles_cache = {}
            return {}

        self._persona_profiles_cache = df_prof.set_index("persona_id").to_dict(orient="index")
        return self._persona_profiles_cache

    def _get_target_files(self, source: str = "all") -> List[tuple[Path, str]]:
        """Lấy danh sách các file benchmark_eda_*.json theo nguồn yêu cầu."""
        target_files: List[tuple[Path, str]] = []
        source_clean = source.lower()

        if source_clean in ("all", "persona"):
            if self.persona_action_path.is_dir():
                for f in sorted(self.persona_action_path.glob("benchmark_eda_*.json")):
                    target_files.append((f, "persona"))

        if source_clean in ("all", "no_persona", "without_persona"):
            if self.no_persona_action_path.is_dir():
                for f in sorted(self.no_persona_action_path.glob("benchmark_eda_*.json")):
                    target_files.append((f, "no_persona"))

        return target_files

    def load_action_logs(self, source: str = "all") -> pd.DataFrame:
        """Nạp tổng quan các action logs ở cấp độ Episode (Phiên chạy)."""
        target_files = self._get_target_files(source)
        manifest_map = self._get_manifest_mappings()
        profiles_map = self._get_persona_profiles_dict()
        records: List[Dict[str, Any]] = []

        for fpath, dataset_type in target_files:
            try:
                with open(fpath, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
            except Exception as e:
                print(f"[!] Lỗi đọc file {fpath.name}: {e}")
                continue

            metadata = data.get("metadata", {})
            summary_stats = metadata.get("summary_statistics", {})
            step_records = data.get("step_records", [])
            episode_id = metadata.get("episode_id")

            if dataset_type == "no_persona":
                persona_id = None
            else:
                persona_id = manifest_map.get(episode_id) or metadata.get("persona_id")
            prof_info = profiles_map.get(persona_id, {}) if persona_id else {}

            # Trích xuất trạng thái working memory và session context cuối phiên
            last_ctx_step = next((s for s in reversed(step_records) if isinstance(s.get("session_context"), dict)), None)
            if last_ctx_step:
                final_ctx = last_ctx_step["session_context"]
                final_wm = final_ctx.get("working_memory") or {}
                final_queries = final_wm.get("searched_topics") or []
                final_read_count = len(final_wm.get("read_posts") or [])
                final_opened_count = len(final_wm.get("opened_sources") or [])
                final_threads_count = len(final_wm.get("active_threads") or [])
                final_summary = final_wm.get("summary")

                parsed_wm_sum = parse_wm_summary(final_summary)

                final_rest = final_ctx.get("rest") or {}
                final_rest_sec = final_rest.get("accumulated_seconds", 0) if isinstance(final_rest, dict) else 0
                final_rest_count = final_rest.get("count", 0) if isinstance(final_rest, dict) else 0
                
                final_sc = final_ctx.get("search_context") or {}
                mem_queries = final_sc.get("recent_queries_from_memory", []) if isinstance(final_sc, dict) else []
                final_elapsed = final_ctx.get("elapsed_seconds")
                final_remaining = final_ctx.get("remaining_seconds")
                is_overtime = final_remaining is not None and final_remaining < 0
                completed_actions = final_ctx.get("completed_actions", 0)

                planned_sec = final_ctx.get("planned_active_seconds")
                planned_min_dict = final_ctx.get("planned_session_minutes") or {}
                planned_min_min = planned_min_dict.get("min") if isinstance(planned_min_dict, dict) else None
                planned_min_max = planned_min_dict.get("max") if isinstance(planned_min_dict, dict) else None
                final_surface = final_ctx.get("current_surface")
            else:
                final_queries = []
                final_read_count = 0
                final_opened_count = 0
                final_threads_count = 0
                final_summary = None
                parsed_wm_sum = parse_wm_summary(None)
                final_rest_sec = 0
                final_rest_count = 0
                mem_queries = []
                final_elapsed = None
                final_remaining = None
                is_overtime = False
                completed_actions = 0
                planned_sec = None
                planned_min_min = None
                planned_min_max = None
                final_surface = None

            surfaces_seq: List[str] = []
            max_situational_steps = 0
            has_novelty_warning = False
            warning_messages: List[str] = []

            all_paces: List[str] = []
            all_totals_px: List[int] = []
            all_gestures_ms: List[int] = []
            all_urls_found: List[str] = []
            execution_modes_counts = {"smooth_wheel": 0, "native_click": 0, "native_search": 0, "cdp_fallback": 0, "read_post": 0, "other": 0}
            seen_sequences = set()

            for step in step_records:
                ctx = step.get("session_context")
                if isinstance(ctx, dict):
                    s_surf = ctx.get("current_surface")
                    if s_surf and (not surfaces_seq or surfaces_seq[-1] != s_surf):
                        surfaces_seq.append(s_surf)

                    wm_step = ctx.get("working_memory")
                    if isinstance(wm_step, dict):
                        nov = wm_step.get("novelty")
                        if isinstance(nov, dict):
                            sit = nov.get("situational_steps", 0)
                            if sit > max_situational_steps:
                                max_situational_steps = sit
                            g = nov.get("guidance", "")
                            if "CẢNH BÁO TIẾT CHẾ" in g or "TIẾT CHẾ" in g:
                                has_novelty_warning = True
                                if g not in warning_messages:
                                    warning_messages.append(g)

                    ra_list = ctx.get("recent_actions") or []
                    for ra in ra_list:
                        if isinstance(ra, dict):
                            seq = ra.get("sequence")
                            if seq is not None and seq in seen_sequences:
                                continue
                            if seq is not None:
                                seen_sequences.add(seq)

                            summ = ra.get("summary", "")
                            parsed_act = parse_action_summary(summ)
                            if parsed_act["gesture_pace"]: all_paces.append(parsed_act["gesture_pace"])
                            if parsed_act["gesture_total_px"]: all_totals_px.append(parsed_act["gesture_total_px"])
                            if parsed_act["gesture_ms"]: all_gestures_ms.append(parsed_act["gesture_ms"])
                            if parsed_act["action_url"]: all_urls_found.append(parsed_act["action_url"])
                            em = parsed_act["execution_mode"]
                            if em in execution_modes_counts:
                                execution_modes_counts[em] += 1
                            else:
                                execution_modes_counts["other"] += 1

            primary_pace = max(set(all_paces), key=all_paces.count) if all_paces else None
            avg_px = sum(all_totals_px) / len(all_totals_px) if all_totals_px else None
            avg_ms = sum(all_gestures_ms) / len(all_gestures_ms) if all_gestures_ms else None
            velocity = (completed_actions / (final_elapsed / 60)) if final_elapsed and final_elapsed > 0 else 0

            row = {
                # 10 trường cốt lõi được yêu cầu
                "episode_id": episode_id,
                "persona_id": persona_id,
                "total_steps": metadata.get("total_steps") or summary_stats.get("total_steps"),
                "tool_distribution": summary_stats.get("tool_distribution", {}),
                "intent_distribution": summary_stats.get("intent_distribution", {}),
                "reaction_distribution": summary_stats.get("reaction_distribution", {}),
                "avg_model_latency_ms": summary_stats.get("avg_model_latency_ms"),
                "avg_tool_execution_ms": summary_stats.get("avg_tool_execution_ms"),
                "step_records": step_records,
                "episode_events": data.get("episode_events", []),
                
                # Thuộc tính Persona đối chiếu từ hồ sơ gốc
                "persona_pace": prof_info.get("pace"),
                "persona_rest_style": prof_info.get("restStyle"),
                "persona_reading_depth": prof_info.get("readingDepth"),
                "persona_discovery_style": prof_info.get("discoveryStyle"),
                "persona_interaction_style": prof_info.get("interactionStyle"),
                "persona_attention": prof_info.get("attention"),

                # Session Context: Cử chỉ đo đạc thực tế (Gesture Metrics)
                "gesture_pace_mode": primary_pace,
                "avg_gesture_px": round(avg_px, 1) if avg_px else None,
                "avg_gesture_ms": round(avg_ms, 1) if avg_ms else None,
                "total_scroll_actions_observed": len(all_totals_px),
                "execution_smooth_wheels": execution_modes_counts["smooth_wheel"],
                "execution_native_clicks": execution_modes_counts["native_click"],
                "execution_native_searches": execution_modes_counts["native_search"],
                "execution_cdp_fallbacks": execution_modes_counts["cdp_fallback"],
                "execution_reads": execution_modes_counts["read_post"],
                "total_unique_urls_interacted": len(set(all_urls_found)),

                # Session Context: Thời gian, Vận tốc & Bề mặt duyệt web
                "planned_active_seconds": planned_sec,
                "planned_session_min_minutes": planned_min_min,
                "planned_session_max_minutes": planned_min_max,
                "final_elapsed_seconds": final_elapsed,
                "final_remaining_seconds": final_remaining,
                "is_overtime": is_overtime,
                "action_velocity_per_minute": round(velocity, 2),
                "final_surface": final_surface,
                "surface_journey": " -> ".join(surfaces_seq),
                "surfaces_visited_count": len(set(surfaces_seq)),

                # Session Context: Dừng nghỉ & Ký ức đa phiên
                "final_rest_accumulated_seconds": final_rest_sec,
                "final_rest_count": final_rest_count,
                "has_rest": final_rest_count > 0,
                "recent_queries_from_memory": mem_queries,
                "has_memory_queries": bool(mem_queries),

                # Session Context: Cơ chế kiểm soát mới lạ (Novelty & Drift Warning)
                "max_situational_steps": max_situational_steps,
                "has_novelty_warning": has_novelty_warning,
                "novelty_warning_message": warning_messages[0] if warning_messages else None,

                # Working Memory tổng kết cuối phiên & Regex summary parse
                "final_searched_queries": final_queries,
                "final_read_posts_count": final_read_count,
                "final_opened_sources_count": final_opened_count,
                "final_active_threads_count": final_threads_count,
                "final_memory_summary": final_summary,
                "wm_summary_run_minutes": parsed_wm_sum["wm_summary_run_minutes"],
                "wm_summary_planned_minutes": parsed_wm_sum["wm_summary_planned_minutes"],
                "wm_summary_read_posts": parsed_wm_sum["wm_summary_read_posts"],
                "wm_summary_searched_topics": parsed_wm_sum["wm_summary_searched_topics"],
                "wm_summary_opened_sources": parsed_wm_sum["wm_summary_opened_sources"],

                # Các trường metadata mở rộng
                "dataset_type": dataset_type,
                "verified_rate": summary_stats.get("verified_rate"),
                "verified_count": summary_stats.get("verified_count"),
                "profile_id": metadata.get("profile_id"),
                "status": metadata.get("status"),
                "started_at": metadata.get("started_at"),
                "ended_at": metadata.get("ended_at"),
                "terminal_reason": metadata.get("terminal_reason"),
                "file_name": fpath.name,
                "file_path": str(fpath),
            }
            records.append(row)

        df = pd.DataFrame(records)
        return df

    def load_step_records(self, source: str = "all") -> pd.DataFrame:
        """Bóc tách và làm phẳng toàn bộ step_records từ các episode thành DataFrame dạng bảng.
        
        Mỗi dòng là một bước hành động (action step), kèm đầy đủ target_candidate,
        dimension_evidence trọng số & vai trò, latency ratio, session_context và working_memory.
        """
        df_episodes = self.load_action_logs(source=source)
        all_steps: List[Dict[str, Any]] = []

        for _, ep in df_episodes.iterrows():
            episode_id = ep["episode_id"]
            persona_id = ep["persona_id"]
            dataset_type = ep["dataset_type"]
            file_name = ep["file_name"]
            p_pace = ep.get("persona_pace")
            p_rest = ep.get("persona_rest_style")

            for step in ep["step_records"]:
                dim_evidence = step.get("dimension_evidence") or []
                parsed_dim_ev = parse_dimension_evidence(dim_evidence)

                target_cand = step.get("target_candidate") or {}
                has_tc = bool(target_cand and isinstance(target_cand, dict))
                tc_url = target_cand.get("url") if has_tc else None
                tc_kind = target_cand.get("kind") if has_tc else None
                tc_text = target_cand.get("text") if has_tc else None

                session_ctx = step.get("session_context") or {}
                has_ctx = bool(session_ctx and isinstance(session_ctx, dict))

                # Trích xuất Working Memory tại bước này
                wm = session_ctx.get("working_memory") or {} if has_ctx else {}
                has_wm = bool(wm and isinstance(wm, dict))

                current_thread = wm.get("current_thread") or {} if has_wm else {}
                active_threads = wm.get("active_threads") or [] if has_wm else []
                searched_topics = wm.get("searched_topics") or [] if has_wm else []
                read_posts = wm.get("read_posts") or [] if has_wm else []
                opened_sources = wm.get("opened_sources") or [] if has_wm else []
                novelty = wm.get("novelty") or {} if has_wm else {}
                wm_summary_text = wm.get("summary") if has_wm else None
                parsed_wm_sum = parse_wm_summary(wm_summary_text)

                persona_threads = [t for t in active_threads if isinstance(t, dict) and t.get("origin") == "persona"]
                situational_threads = [t for t in active_threads if isinstance(t, dict) and t.get("origin") != "persona"]

                # Trích xuất thông tin mạch hiện tại (Current Thread)
                ct_topic = current_thread.get("topic") if isinstance(current_thread, dict) else None
                ct_origin = current_thread.get("origin") if isinstance(current_thread, dict) else None
                ct_state = current_thread.get("state") if isinstance(current_thread, dict) else None
                if ct_state is None and ct_topic and active_threads:
                    for at in active_threads:
                        if isinstance(at, dict) and at.get("topic") == ct_topic:
                            ct_state = at.get("state")
                            break
                ct_verified = current_thread.get("verified_steps") if isinstance(current_thread, dict) else None

                # Trích xuất Rest & Search Context tại bước này
                rest_dict = session_ctx.get("rest") or {} if has_ctx else {}
                rest_sec = rest_dict.get("accumulated_seconds", 0) if isinstance(rest_dict, dict) else 0
                rest_cnt = rest_dict.get("count", 0) if isinstance(rest_dict, dict) else 0

                search_ctx = session_ctx.get("search_context") or {} if has_ctx else {}
                q_session = search_ctx.get("queries_this_session") or [] if isinstance(search_ctx, dict) else []
                q_mem = search_ctx.get("recent_queries_from_memory") or [] if isinstance(search_ctx, dict) else []
                search_rule = search_ctx.get("rule") if isinstance(search_ctx, dict) else None
                planner_rule = wm.get("planner_rule") if has_wm else None

                # Thời gian, Vận tốc & Latency
                elapsed_sec = session_ctx.get("elapsed_seconds") if has_ctx else None
                remaining_sec = session_ctx.get("remaining_seconds") if has_ctx else None
                completed_acts = session_ctx.get("completed_actions") if has_ctx else None
                curr_surf = session_ctx.get("current_surface") if has_ctx else None
                step_velocity = (completed_acts / (elapsed_sec / 60)) if elapsed_sec and elapsed_sec > 0 and completed_acts else 0
                is_ot = remaining_sec is not None and remaining_sec < 0

                m_lat = step.get("model_latency_ms")
                t_lat = step.get("tool_execution_ms")
                tot_lat = (m_lat or 0) + (t_lat or 0)
                cog_ratio = round(m_lat / tot_lat, 3) if tot_lat > 0 and m_lat is not None else None

                # Action summary & Reason
                action_summ_text = step.get("action_summary")
                parsed_act_summ = parse_step_action_summary(action_summ_text)
                reason_text = step.get("reason", "")

                # Trích xuất Cử chỉ & Hành động gần nhất (Gesture Pace & Metrics)
                recent_actions_list = session_ctx.get("recent_actions") or [] if has_ctx else []
                last_ra = recent_actions_list[-1] if recent_actions_list and isinstance(recent_actions_list[-1], dict) else {}
                last_summ = last_ra.get("summary", "") if last_ra else ""
                parsed_last_act = parse_action_summary(last_summ)

                # Novelty cảnh báo
                nov_guidance = novelty.get("guidance", "") if isinstance(novelty, dict) else ""
                nov_warning = bool("CẢNH BÁO TIẾT CHẾ" in nov_guidance or "TIẾT CHẾ" in nov_guidance)

                step_row = {
                    "episode_id": episode_id,
                    "persona_id": persona_id,
                    "persona_pace": p_pace,
                    "persona_rest_style": p_rest,
                    "dataset_type": dataset_type,
                    "file_name": file_name,
                    "step_index": step.get("step_index"),
                    "timestamp": step.get("timestamp"),
                    "tool": step.get("tool"),
                    "resolved_tool": step.get("resolved_tool"),
                    "intent": step.get("intent"),
                    "target_id": step.get("target_id"),
                    "reaction": step.get("reaction"),
                    "surface": step.get("surface"),
                    "current_surface": curr_surf,
                    "verified": step.get("verified"),
                    "reason": reason_text,
                    "reason_length": len(reason_text) if reason_text else 0,
                    "action_summary": action_summ_text,
                    "action_summary_verb": parsed_act_summ["action_summary_verb"],
                    "action_summary_target_surface": parsed_act_summ["action_summary_target_surface"],
                    "evidence": step.get("evidence"),
                    
                    # Latency & Cognitive Ratio
                    "model_latency_ms": m_lat,
                    "tool_execution_ms": t_lat,
                    "total_step_latency_ms": tot_lat if tot_lat > 0 else None,
                    "cognitive_latency_ratio": cog_ratio,
                    "llm_request_index": step.get("llm_request_index"),
                    
                    # Target Candidate chi tiết
                    "has_target_candidate": has_tc,
                    "target_candidate_kind": tc_kind,
                    "target_candidate_text": tc_text,
                    "target_candidate_url": tc_url,
                    
                    # Dimension Evidence bóc tách vai trò, trọng số & giá trị
                    "num_dimension_evidence": parsed_dim_ev["num_dimension_evidence"],
                    "dimension_sources": parsed_dim_ev["dimension_sources"],
                    "dimensions": parsed_dim_ev["dimensions"],
                    "dim_evidence_primary_dimension": parsed_dim_ev["dim_evidence_primary_dimension"],
                    "dim_evidence_primary_value": parsed_dim_ev["dim_evidence_primary_value"],
                    "dim_evidence_primary_ref_id": parsed_dim_ev["dim_evidence_primary_ref_id"],
                    "dim_evidence_max_weight": parsed_dim_ev["dim_evidence_max_weight"],
                    "dim_evidence_avg_weight": parsed_dim_ev["dim_evidence_avg_weight"],
                    "dim_evidence_roles": parsed_dim_ev["dim_evidence_roles"],
                    "dim_evidence_reference_ids": parsed_dim_ev["dim_evidence_reference_ids"],
                    "num_dim_primary": parsed_dim_ev["num_dim_primary"],
                    "num_dim_supporting": parsed_dim_ev["num_dim_supporting"],
                    "num_dim_situational": parsed_dim_ev["num_dim_situational"],
                    "num_dim_constraint": parsed_dim_ev["num_dim_constraint"],
                    
                    # Session context: Tiến độ thời gian & Vận tốc
                    "has_session_context": has_ctx,
                    "context_elapsed_seconds": elapsed_sec,
                    "context_remaining_seconds": remaining_sec,
                    "context_is_overtime": is_ot,
                    "context_completed_actions": completed_acts,
                    "context_action_velocity": round(step_velocity, 2),
                    
                    # Session context: Dừng nghỉ (Rest)
                    "context_rest_accumulated_seconds": rest_sec,
                    "context_rest_count": rest_cnt,

                    # Session context: Tìm kiếm & Ký ức đa phiên (Search & Memory)
                    "context_num_queries_this_session": len(q_session),
                    "context_queries_this_session": ", ".join(q_session) if q_session else None,
                    "context_num_memory_queries": len(q_mem),
                    "context_recent_queries_from_memory": ", ".join(q_mem) if q_mem else None,
                    "context_has_memory_queries": bool(q_mem),
                    "search_rule": search_rule,
                    "planner_rule": planner_rule,

                    # Session context: Cử chỉ gần nhất trích xuất bằng regex
                    "context_num_recent_actions": len(recent_actions_list),
                    "recent_last_intent": last_ra.get("intent") if last_ra else None,
                    "recent_last_surface": last_ra.get("surface") if last_ra else None,
                    "recent_last_tool": last_ra.get("resolved_tool") if last_ra else None,
                    "recent_last_gesture_pace": parsed_last_act["gesture_pace"],
                    "recent_last_gesture_px": parsed_last_act["gesture_total_px"],
                    "recent_last_gesture_ms": parsed_last_act["gesture_ms"],
                    "scroll_speed_px_s": (parsed_last_act["gesture_total_px"] / parsed_last_act["gesture_ms"] * 1000.0) if (parsed_last_act["gesture_total_px"] is not None and parsed_last_act["gesture_ms"] is not None and parsed_last_act["gesture_ms"] > 0) else None,
                    "recent_last_gesture_dir": parsed_last_act["gesture_direction"],
                    "recent_last_landing_correction": parsed_last_act["landing_correction_px"],
                    "recent_last_action_url": parsed_last_act["action_url"],
                    "recent_last_url_type": parsed_last_act["url_type"],
                    "recent_last_execution_mode": parsed_last_act["execution_mode"],

                    # Working Memory
                    "has_working_memory": has_wm,
                    "wm_current_thread_topic": ct_topic,
                    "wm_current_thread_origin": ct_origin,
                    "wm_current_thread_state": ct_state,
                    "wm_current_thread_verified_steps": ct_verified,
                    "wm_num_active_threads": len(active_threads) if has_wm else 0,
                    "wm_persona_threads_count": len(persona_threads) if has_wm else 0,
                    "wm_situational_threads_count": len(situational_threads) if has_wm else 0,
                    "wm_cumulative_searches": len(searched_topics) if has_wm else 0,
                    "wm_cumulative_reads": len(read_posts) if has_wm else 0,
                    "wm_cumulative_opened": len(opened_sources) if has_wm else 0,
                    
                    # Novelty & Cảnh báo tiết chế
                    "wm_situational_steps": novelty.get("situational_steps", 0) if isinstance(novelty, dict) else 0,
                    "wm_explored_evidence_share": novelty.get("explored_evidence_share", 0) if isinstance(novelty, dict) else 0,
                    "wm_explored_thread_count": novelty.get("explored_thread_count", 0) if isinstance(novelty, dict) else 0,
                    "wm_has_novelty_warning": nov_warning,
                    "wm_novelty_guidance": nov_guidance,

                    # Working Memory Regex parsed numbers
                    "wm_summary_run_minutes": parsed_wm_sum["wm_summary_run_minutes"],
                    "wm_summary_planned_minutes": parsed_wm_sum["wm_summary_planned_minutes"],
                    "wm_summary_read_posts": parsed_wm_sum["wm_summary_read_posts"],
                    "wm_summary_searched_topics": parsed_wm_sum["wm_summary_searched_topics"],
                    "wm_summary_opened_sources": parsed_wm_sum["wm_summary_opened_sources"],
                    "wm_summary_raw": wm_summary_text,
                }
                all_steps.append(step_row)

        return pd.DataFrame(all_steps)

    def load_dimension_evidences(self, source: str = "all") -> pd.DataFrame:
        """Bóc tách TOÀN BỘ các phần tử trong dimension_evidence thành DataFrame chuyên biệt.
        
        Mỗi dòng là một chiều nhận thức được viện dẫn (role, weight, source, dimension, value, reference_id).
        """
        df_episodes = self.load_action_logs(source=source)
        all_dims: List[Dict[str, Any]] = []

        for _, ep in df_episodes.iterrows():
            episode_id = ep["episode_id"]
            persona_id = ep["persona_id"]
            dataset_type = ep["dataset_type"]
            file_name = ep["file_name"]

            for step in ep["step_records"]:
                step_idx = step.get("step_index")
                intent = step.get("intent")
                resolved_tool = step.get("resolved_tool")
                dim_evidence = step.get("dimension_evidence") or []

                for item in dim_evidence:
                    if isinstance(item, dict):
                        all_dims.append({
                            "episode_id": episode_id,
                            "persona_id": persona_id,
                            "dataset_type": dataset_type,
                            "file_name": file_name,
                            "step_index": step_idx,
                            "intent": intent,
                            "resolved_tool": resolved_tool,
                            "dimension": item.get("dimension"),
                            "role": item.get("role"),
                            "weight": item.get("weight"),
                            "source": item.get("source"),
                            "reference_id": item.get("reference_id"),
                            "value": item.get("value"),
                        })

        return pd.DataFrame(all_dims)

    def load_target_candidates(self, source: str = "all") -> pd.DataFrame:
        """Bóc tách TOÀN BỘ các đối tượng mục tiêu (target_candidate) mà Agent đã tương tác."""
        df_episodes = self.load_action_logs(source=source)
        all_cands: List[Dict[str, Any]] = []

        for _, ep in df_episodes.iterrows():
            episode_id = ep["episode_id"]
            persona_id = ep["persona_id"]
            dataset_type = ep["dataset_type"]
            file_name = ep["file_name"]

            for step in ep["step_records"]:
                tc = step.get("target_candidate")
                if isinstance(tc, dict) and tc:
                    step_idx = step.get("step_index")
                    intent = step.get("intent")
                    resolved_tool = step.get("resolved_tool")
                    url = tc.get("url")

                    all_cands.append({
                        "episode_id": episode_id,
                        "persona_id": persona_id,
                        "dataset_type": dataset_type,
                        "file_name": file_name,
                        "step_index": step_idx,
                        "intent": intent,
                        "resolved_tool": resolved_tool,
                        "kind": tc.get("kind"),
                        "text": tc.get("text"),
                        "url": url,
                    })

        return pd.DataFrame(all_cands)

    def load_recent_actions(self, source: str = "all", deduplicate: bool = True) -> pd.DataFrame:
        """Bóc tách TOÀN BỘ mảng recent_actions trong session_context thành DataFrame.
        
        Trích xuất trực tiếp bằng regex: pace, total_px, gesture_ms, direction, landing_correction,
        action_url, url_type, và execution_mode.
        """
        df_episodes = self.load_action_logs(source=source)
        all_actions: List[Dict[str, Any]] = []

        for _, ep in df_episodes.iterrows():
            episode_id = ep["episode_id"]
            persona_id = ep["persona_id"]
            dataset_type = ep["dataset_type"]
            file_name = ep["file_name"]
            p_pace = ep.get("persona_pace")
            p_rest = ep.get("persona_rest_style")

            for step in ep["step_records"]:
                step_idx = step.get("step_index")
                ctx = step.get("session_context")
                if not isinstance(ctx, dict):
                    continue

                ra_list = ctx.get("recent_actions") or []
                for ra in ra_list:
                    if not isinstance(ra, dict):
                        continue

                    summ = ra.get("summary", "")
                    parsed_act = parse_action_summary(summ)

                    action_row = {
                        "episode_id": episode_id,
                        "persona_id": persona_id,
                        "persona_pace": p_pace,
                        "persona_rest_style": p_rest,
                        "dataset_type": dataset_type,
                        "file_name": file_name,
                        "recorded_step_index": step_idx,
                        "sequence": ra.get("sequence"),
                        "elapsed_seconds": ra.get("elapsed_seconds"),
                        "intent": ra.get("intent"),
                        "resolved_tool": ra.get("resolved_tool"),
                        "surface": ra.get("surface"),
                        "target_id": ra.get("target_id"),
                        "verified": ra.get("verified"),
                        "query": ra.get("query"),
                        "summary": summ,
                        
                        # Chỉ số cử chỉ & URL trích xuất trực tiếp bằng regex
                        "gesture_pace": parsed_act["gesture_pace"],
                        "gesture_total_px": parsed_act["gesture_total_px"],
                        "gesture_ms": parsed_act["gesture_ms"],
                        "gesture_direction": parsed_act["gesture_direction"],
                        "landing_correction_px": parsed_act["landing_correction_px"],
                        "action_url": parsed_act["action_url"],
                        "url_type": parsed_act["url_type"],
                        "execution_mode": parsed_act["execution_mode"],
                    }
                    all_actions.append(action_row)

        df = pd.DataFrame(all_actions)
        if df.empty:
            return df

        if deduplicate:
            # Giữ lại bản ghi đầu tiên của mỗi sequence trong episode
            df = df.sort_values(by=["episode_id", "sequence", "recorded_step_index"])
            df = df.drop_duplicates(subset=["episode_id", "sequence"], keep="first").reset_index(drop=True)

        return df

    def load_active_threads(self, source: str = "all") -> pd.DataFrame:
        """Bóc tách chi tiết các active_threads trong working_memory qua từng bước.
        
        Trích xuất trực tiếp bằng regex các chiều tâm lý: source:dimension=reason.
        """
        df_episodes = self.load_action_logs(source=source)
        all_threads: List[Dict[str, Any]] = []

        for _, ep in df_episodes.iterrows():
            episode_id = ep["episode_id"]
            persona_id = ep["persona_id"]
            dataset_type = ep["dataset_type"]

            for step in ep["step_records"]:
                step_idx = step.get("step_index")
                session_ctx = step.get("session_context") or {}
                wm = session_ctx.get("working_memory") or {} if isinstance(session_ctx, dict) else {}
                threads = wm.get("active_threads") or []

                for t in threads:
                    if isinstance(t, dict):
                        evidences = t.get("evidence") or []
                        parsed_ev, src_counts, dims = parse_evidence_strings(evidences)

                        all_threads.append({
                            "episode_id": episode_id,
                            "persona_id": persona_id,
                            "dataset_type": dataset_type,
                            "step_index": step_idx,
                            "key": t.get("key"),
                            "topic": t.get("topic"),
                            "origin": t.get("origin"),
                            "state": t.get("state"),
                            "last_intent": t.get("last_intent"),
                            "verified_steps": t.get("verified_steps"),
                            "num_evidences": len(evidences),
                            "evidence_list": evidences,
                            
                            # Regex bóc tách bằng chứng tâm lý
                            "evidence_sources": ",".join(sorted(set([e["source"] for e in parsed_ev]))),
                            "evidence_dimensions": ",".join(sorted(set(dims))),
                            "evidence_persona_count": src_counts["persona"],
                            "evidence_neutral_count": src_counts["neutral_control"],
                            "evidence_viewport_count": src_counts["viewport"],
                            "evidence_session_memory_count": src_counts["session_memory"],
                        })

        return pd.DataFrame(all_threads)

    def load_episode_events(self, source: str = "all") -> pd.DataFrame:
        """Bóc tách và làm phẳng toàn bộ episode_events từ các episode thành DataFrame dạng bảng."""
        df_episodes = self.load_action_logs(source=source)
        all_events: List[Dict[str, Any]] = []

        for _, ep in df_episodes.iterrows():
            episode_id = ep["episode_id"]
            persona_id = ep["persona_id"]
            dataset_type = ep["dataset_type"]
            file_name = ep["file_name"]

            for event in ep["episode_events"]:
                payload = event.get("payload") or {}
                affordances = payload.get("affordances") if isinstance(payload, dict) else []

                event_row = {
                    "episode_id": episode_id,
                    "persona_id": persona_id,
                    "dataset_type": dataset_type,
                    "file_name": file_name,
                    "timestamp": event.get("timestamp"),
                    "kind": event.get("kind"),
                    "surface": payload.get("surface") if isinstance(payload, dict) else None,
                    "verified": payload.get("verified") if isinstance(payload, dict) else None,
                    "affordances_count": len(affordances) if affordances else 0,
                    "reason": payload.get("reason") if isinstance(payload, dict) else None,
                    "payload": payload,
                }
                all_events.append(event_row)

        return pd.DataFrame(all_events)


if __name__ == "__main__":
    loader = PersonaActionLoader()
    print("=== 1. STEP LEVEL (ĐẦY ĐỦ 94 CỘT) ===")
    df_steps = loader.load_step_records()
    print(f"Shape: {df_steps.shape}")
    sample_cols = [
        "step_index", "intent", "dim_evidence_primary_dimension", 
        "dim_evidence_max_weight", "cognitive_latency_ratio", 
        "action_summary_verb", "target_candidate_kind"
    ]
    print(df_steps[df_steps["has_target_candidate"]][sample_cols].head(8).to_string())

    print("\n=== 2. DIMENSION EVIDENCES (CHUYÊN BIỆT) ===")
    df_dims = loader.load_dimension_evidences()
    print(f"Total dimension evidence records: {df_dims.shape[0]}")
    print(df_dims[["dimension", "role", "weight", "source"]].head(8).to_string())

    print("\n=== 3. TARGET CANDIDATES (CHUYÊN BIỆT) ===")
    df_cands = loader.load_target_candidates()
    print(f"Total target candidates: {df_cands.shape[0]}")
    print(df_cands[["kind", "text", "url"]].head(5).to_string())
