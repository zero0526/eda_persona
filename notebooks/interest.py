"""Phân tích các hành vi liên quan đến Sở thích (Interest) của 6 Persona Facebook.

Thực hiện 3 nhiệm vụ thống kê cốt lõi:
1. BẢNG 1: Tổng hợp các sở thích có mức độ quan tâm cao ("Rất đam mê", "Có hứng thú tìm hiểu")
   từ hồ sơ gốc `selected_6_facebook_personas_description.jsonl` và ánh xạ Subgroup từ `persona_Dimension_v2.csv`.
2. BẢNG 2: Thống kê tỷ lệ hành động (action steps) của từng Persona có viện dẫn ít nhất một bằng chứng
   thuộc trường sở thích (`interest_*`) trong SQLite `persona-runner.sqlite`.
3. BẢNG 3: Phân tích sự kết hợp đa chiều (Cognitive Fusion): Trong các hành động có viện dẫn sở thích,
   các bằng chứng đi kèm thuộc những trường nào và Subgroup nào từ `persona_Dimension_v2.csv`.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import sys
from collections import Counter, defaultdict
from typing import Any, Dict, List, Tuple

import pandas as pd

# Thiết lập hiển thị UTF-8 trên Windows Console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 100)
pd.set_option("display.width", 1000)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PERSONA_ORDER = ["vn_fb_001", "vn_fb_002", "vn_fb_003", "vn_fb_004", "vn_fb_005", "vn_fb_006"]
PERSONA_LABELS = {
    "vn_fb_001": "vn_fb_001 (Thiết kế đồ họa, 26t, Nữ)",
    "vn_fb_002": "vn_fb_002 (Nông nghiệp / Gia đình, 42t, Nữ)",
    "vn_fb_003": "vn_fb_003 (Bảo vệ ca trực, 28t, Nam)",
    "vn_fb_004": "vn_fb_004 (Nhân viên nhà hàng, 22t, Nam)",
    "vn_fb_005": "vn_fb_005 (Thợ cơ khí, 31t, Nam)",
    "vn_fb_006": "vn_fb_006 (Kinh doanh BĐS, 52t, Nam)",
}


def load_dimension_mappings(csv_path: Path) -> Dict[str, Tuple[str, str, str]]:
    """Xây dựng từ điển ánh xạ từ tên dimension (snake_case) sang (Subgroup, Group, Dimension Name)."""
    df_dim = pd.read_csv(csv_path)
    mapping: Dict[str, Tuple[str, str, str]] = {}

    for _, r in df_dim.iterrows():
        d_name = str(r["Dimension"]).strip()
        sg = str(r["Subgroup"]).strip()
        grp = str(r["Group"]).strip()
        lbl = str(r["Label"]).strip()

        # Tạo khóa chuẩn snake_case từ Dimension tiếng Anh
        clean_d = d_name.lower().replace(":", "").replace("&", "").replace("/", " ").replace("-", " ")
        k_d = "_".join(clean_d.split())
        mapping[k_d] = (sg, grp, d_name)

        # Tạo khóa chuẩn snake_case từ Label tiếng Việt
        clean_lbl = lbl.lower().replace(":", "").replace("&", "").replace("/", " ").replace("-", " ")
        k_lbl = "_".join(clean_lbl.split())
        mapping[k_lbl] = (sg, grp, d_name)

    # Bổ sung các quy tắc chuẩn hóa thủ công tương ứng với tên biến trong SQLite runner
    custom_rules = {
        "curiosity": ("Cognitive & Work Style", "Psychology & Cognition", "Curiosity"),
        "content_consumption_format": ("Social Engagement", "Behavior and Interaction", "Content consumption format"),
        "interest_real_estate": ("Interest", "Lifestyle", "Interest: Real estate"),
        "group_community_participation": ("Social Engagement", "Behavior and Interaction", "Group / community participation"),
        "cuisine_vietnamese": ("Food & Beverage", "Lifestyle", "Cuisine: Vietnamese"),
        "province": ("Demographics", "Background", "Province"),
        "sport_football": ("Interest", "Lifestyle", "Sport: Football"),
        "cuisine_street_food": ("Food & Beverage", "Lifestyle", "Cuisine: Street Food"),
        "interest_technology": ("Interest", "Lifestyle", "Interest: Technology & AI"),
        "interest_technology_ai": ("Interest", "Lifestyle", "Interest: Technology & AI"),
        "attention_span": ("Cognitive & Work Style", "Psychology & Cognition", "Attention span"),
        "value_tradition": ("Values & Worldview", "Psychology & Cognition", "Value: Tradition"),
        "skepticism": ("Cognitive & Work Style", "Psychology & Cognition", "Skepticism / critical verification"),
        "social_engagement_style": ("Social Engagement", "Behavior and Interaction", "Social engagement style"),
        "value_health": ("Values & Worldview", "Psychology & Cognition", "Value: Health"),
        "tone": ("Communication Style", "Behavior and Interaction", "Tone"),
        "reading_frequency": ("Daily Lifestyle", "Lifestyle", "Reading frequency"),
        "career_role": ("Career & Education", "Background", "Career role"),
        "interest_film": ("Interest", "Lifestyle", "Interest: Film"),
        "current_thread": ("Interaction State", "Behavior and Interaction", "Current thread / context"),
        "purpose": ("Interaction State", "Behavior and Interaction", "Session purpose"),
        "books_mystery": ("Interest", "Lifestyle", "Books: Mystery / Thriller"),
        "dialect_register": ("Language Profile", "Background", "Dialect / register"),
        "decision_speed": ("Cognitive & Work Style", "Psychology & Cognition", "Decision speed"),
        "facebook_frequency": ("Platform Presence", "Behavior and Interaction", "Platform frequency: Facebook"),
        "writing_format": ("Communication Style", "Behavior and Interaction", "Writing format"),
        "interest_travel": ("Interest", "Lifestyle", "Interest: Travel"),
        "energy_level": ("Interaction State", "Behavior and Interaction", "Energy level"),
        "value_wealth": ("Values & Worldview", "Psychology & Cognition", "Value: Wealth"),
        "attitude_new_technology": ("Values & Worldview", "Psychology & Cognition", "Attitude to new technology"),
        "value_family": ("Values & Worldview", "Psychology & Cognition", "Value: Family"),
        "interest_parenting_family_life": ("Interest", "Lifestyle", "Interest: Parenting & Family life"),
        "open_question": ("Communication Style", "Behavior and Interaction", "Open question tendency"),
        "humor_style": ("Communication Style", "Behavior and Interaction", "Humor style"),
        "extroversion": ("Personality", "Psychology & Cognition", "Extroversion"),
        "character_playfulness": ("Personality", "Psychology & Cognition", "Playfulness"),
        "music_indie": ("Interest", "Lifestyle", "Music: Indie"),
        "emotional_expressiveness": ("Communication Style", "Behavior and Interaction", "Emotional expressiveness"),
        "interest_pets": ("Interest", "Lifestyle", "Interest: Pets & Animals"),
        "attitude_advertising": ("Social Engagement", "Behavior and Interaction", "Pet peeve: Pop-up ads"),
        "interest_spirituality": ("Interest", "Lifestyle", "Interest: Spirituality & Mindfulness"),
        "big_picture_vs_detail": ("Cognitive & Work Style", "Psychology & Cognition", "Big picture vs detail"),
        "books_self_help": ("Interest", "Lifestyle", "Books: Self-help"),
        "storytelling_tendency": ("Communication Style", "Behavior and Interaction", "Storytelling tendency"),
        "film_animation": ("Interest", "Lifestyle", "Film: Animation"),
        "interest_investing": ("Interest", "Lifestyle", "Interest: Personal finance & Investing"),
        "emoji_emoticon_use": ("Communication Style", "Behavior and Interaction", "Emoji / emoticon usage"),
        "character_social_intelligence": ("Skills", "Capability", "Social intelligence"),
        "children": ("Demographics", "Background", "Children"),
        "state": ("Interaction State", "Behavior and Interaction", "Bot runtime state"),
        "logic_vs_intuition": ("Cognitive & Work Style", "Psychology & Cognition", "Logic vs intuition"),
        "tech_savviness": ("Skills", "Capability", "Tech savviness"),
        "sport_gym_calisthenics": ("Interest", "Lifestyle", "Sport: Gym & Calisthenic"),
        "sport_martial_arts": ("Interest", "Lifestyle", "Sport: Martial arts"),
        "attitude_online_reviews": ("Social Engagement", "Behavior and Interaction", "Review checking behavior"),
        "media_diet": ("Social Engagement", "Behavior and Interaction", "Media diet"),
        "directness": ("Communication Style", "Behavior and Interaction", "Directness"),
        "film_sci_fi_superhero": ("Interest", "Lifestyle", "Film: Sci-fi / Superhero"),
        "sport_badminton": ("Interest", "Lifestyle", "Sport: Badminton"),
        "film_horror_thriller": ("Interest", "Lifestyle", "Film: Horror / Thriller"),
        "verbosity": ("Communication Style", "Behavior and Interaction", "Verbosity"),
        "attitude_climate_action": ("Values & Worldview", "Psychology & Cognition", "Climate action attitude"),
        "interest_sports": ("Interest", "Lifestyle", "Interest: Sport"),
        "books_fantasy": ("Interest", "Lifestyle", "Books: Fantasy"),
        "books_romance": ("Interest", "Lifestyle", "Books: Romance"),
        "cuisine_japanese": ("Food & Beverage", "Lifestyle", "Cuisine: Japanese"),
        "music_pop": ("Interest", "Lifestyle", "Music: Pop"),
        "formality": ("Communication Style", "Behavior and Interaction", "Formality"),
        "language_english": ("Language Profile", "Background", "Language: English"),
        "location": ("Demographics", "Background", "Location"),
        "books_historical_fiction": ("Interest", "Lifestyle", "Books: Historical fiction"),
        "character_generosity": ("Personality", "Psychology & Cognition", "Generosity"),
        "current_surface": ("Interaction State", "Behavior and Interaction", "Current surface"),
        "film_television": ("Interest", "Lifestyle", "Film: Drama"),
        "post_title": ("Interaction State", "Behavior and Interaction", "Post title context"),
        "openness": ("Personality", "Psychology & Cognition", "Dominant personality trait: Openness"),
        "politeness": ("Communication Style", "Behavior and Interaction", "Politeness"),
        "sport_boxing": ("Interest", "Lifestyle", "Sport: Boxing"),
        "sport_table_tennis": ("Interest", "Lifestyle", "Sport: Table tennis"),
        "sport_running": ("Interest", "Lifestyle", "Sport: Running"),
        "sport_tennis": ("Interest", "Lifestyle", "Sport: Tennis"),
    }
    for k, v in custom_rules.items():
        mapping[k] = v

    return mapping


def build_table_4_prominent_attributes(
    jsonl_path: Path, csv_dim_path: Path
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Tạo BẢNG 4: Trích xuất các trường thuộc tính có giá trị nổi bật / cường độ cao:
    - 'Chuyên gia', 'Nâng cao' (Kỹ năng & Chuyên môn)
    - 'Rất cao', 'Cao' (Mức độ & Cường độ nhận thức / tâm lý)
    - 'Nhiều lần mỗi ngày', 'Hàng ngày' (Tần suất sinh hoạt & MXH)
    - 'Rất thích', 'Thích' (Mức độ yêu thích ẩm thực / giải trí)
    - 'Thường xuyên tham gia', 'Chủ yếu theo dõi' (Mức độ tham gia thể thao / hoạt động)
    - 'Rất đam mê', 'Có hứng thú tìm hiểu' (Mối quan tâm & Sở thích chuyên sâu)
    Phân loại chi tiết theo từng Group và Subgroup từ persona_Dimension_v2.csv.
    """
    target_value_groups = {
        "Chuyên gia": "Kỹ năng & Chuyên môn",
        "Nâng cao": "Kỹ năng & Chuyên môn",
        "Rất cao": "Mức độ / Cường độ cao",
        "Cao": "Mức độ / Cường độ cao",
        "Nhiều lần mỗi ngày": "Tần suất cao",
        "Hàng ngày": "Tần suất cao",
        "Rất thích": "Sở thích / Yêu thích",
        "Thích": "Sở thích / Yêu thích",
        "Thường xuyên tham gia": "Mức độ tham gia hoạt động",
        "Chủ yếu theo dõi": "Mức độ tham gia hoạt động",
        "Rất đam mê": "Mối quan tâm / Sở thích chuyên sâu",
        "Có hứng thú tìm hiểu": "Mối quan tâm / Sở thích chuyên sâu",
    }

    df_dim = pd.read_csv(csv_dim_path)
    lookup: Dict[str, Tuple[str, str, str, str]] = {}

    def norm_txt(s: str) -> str:
        return s.lower().replace(".", "").replace(":", "").replace("&", "").replace("/", " ").replace("-", " ").strip()

    for _, r in df_dim.iterrows():
        grp = str(r["Group"]).strip()
        sg = str(r["Subgroup"]).strip()
        dim = str(r["Dimension"]).strip()
        lbl = str(r["Label"]).strip()
        desc = str(r["Description"]).strip() if pd.notna(r["Description"]) else ""
        val_tuple = (grp, sg, dim, lbl)

        lookup[norm_txt(lbl)] = val_tuple
        lookup[norm_txt(dim)] = val_tuple
        if desc:
            lookup[norm_txt(desc)] = val_tuple

    records = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            p_id = data["persona_id"]
            attrs = data.get("attributes", {})

            for attr_name, val in attrs.items():
                val_clean = str(val).strip()
                if val_clean in target_value_groups:
                    val_type = target_value_groups[val_clean]
                    k_norm = norm_txt(attr_name)

                    if k_norm in lookup:
                        grp, sg, dim, lbl = lookup[k_norm]
                    else:
                        found = False
                        for l_k, l_v in lookup.items():
                            if l_k and (l_k in k_norm or k_norm in l_k):
                                grp, sg, dim, lbl = l_v
                                found = True
                                break
                        if not found:
                            grp, sg, dim, lbl = ("Khác", "Khác", attr_name, attr_name)

                    records.append({
                        "persona_id": p_id,
                        "persona_ten": PERSONA_LABELS.get(p_id, p_id),
                        "group": grp,
                        "subgroup": sg,
                        "dimension": dim,
                        "thuoc_tinh": attr_name,
                        "gia_tri": val_clean,
                        "nhom_gia_tri": val_type,
                    })

    df_detail = pd.DataFrame(records).sort_values(
        by=["persona_id", "group", "subgroup", "nhom_gia_tri", "thuoc_tinh"]
    )

    df_pivot = pd.crosstab(
        index=[df_detail["group"], df_detail["subgroup"]],
        columns=df_detail["persona_id"],
        margins=True,
        margins_name="Tong_cong",
    )
    for col in PERSONA_ORDER:
        if col not in df_pivot.columns:
            df_pivot[col] = 0
    df_pivot = df_pivot.reindex(columns=PERSONA_ORDER + ["Tong_cong"], fill_value=0)

    return df_detail, df_pivot


def build_table_1_persona_interests(df_table_4: pd.DataFrame) -> pd.DataFrame:
    """Tạo BẢNG 1: Sử dụng Bảng 4 làm mốc, lọc ra các trường thuộc Sở thích (Interest)
    và Ẩm thực (Food & Beverage) có mức độ cao ('Rất thích', 'Thích', 'Rất đam mê',
    'Có hứng thú tìm hiểu', 'Thường xuyên tham gia', 'Chủ yếu theo dõi').
    """
    df_t1 = df_table_4[df_table_4["subgroup"].isin(["Interest", "Food & Beverage"])].copy()
    df_t1 = df_t1.sort_values(by=["persona_id", "subgroup", "nhom_gia_tri", "thuoc_tinh"])
    return df_t1


def load_decision_actions_from_sqlite(db_path: Path) -> Dict[Tuple[str, int], Dict[str, Any]]:
    """Nạp toàn bộ các bước hành động (action step) kèm danh sách evidence từ SQLite."""
    conn = sqlite3.connect(db_path)
    query = """
        SELECT de.id as evidence_id, de.episode_id, b.persona_id, de.step_index,
               de.action, de.evidence_json
        FROM decision_evidence de
        JOIN episodes e ON de.episode_id = e.id
        JOIN bots b ON e.bot_id = b.id
        ORDER BY b.persona_id, de.step_index
    """
    df_raw = pd.read_sql_query(query, conn)
    conn.close()

    actions: Dict[Tuple[str, int], Dict[str, Any]] = defaultdict(lambda: {"persona_id": "", "action": "", "items": []})
    for _, r in df_raw.iterrows():
        act_key = (r["episode_id"], r["step_index"])
        actions[act_key]["persona_id"] = r["persona_id"]
        actions[act_key]["action"] = r["action"]
        try:
            items = json.loads(r["evidence_json"])
            if isinstance(items, list):
                for item in items:
                    actions[act_key]["items"].append(item)
        except Exception:
            pass

    return actions


def build_table_2_action_interest_rates(
    actions: Dict[Tuple[str, int], Dict[str, Any]],
    df_t1: pd.DataFrame,
    mapping: Dict[str, Tuple[str, str, str]],
) -> pd.DataFrame:
    """Tạo BẢNG 2: Tỉ lệ hành động của Persona có viện dẫn evidence từ các trường trong BẢNG 1 (Sở thích & Ẩm thực)."""
    # Tập hợp các trường mốc của từng Persona từ Bảng 1
    t1_dims_by_p: Dict[str, set] = defaultdict(set)
    for _, r in df_t1.iterrows():
        p_id = r["persona_id"]
        dim_clean = str(r["dimension"]).lower().strip()
        t1_dims_by_p[p_id].add(dim_clean)
        clean_dim_k = "_".join(dim_clean.replace(":", "").replace("&", "").replace("/", " ").replace("-", " ").split())
        t1_dims_by_p[p_id].add(clean_dim_k)

    stats = defaultdict(lambda: {
        "tong_hanh_dong": 0,
        "hanh_dong_co_so_thich": 0,
        "tong_evidence_so_thich": 0,
    })

    for act_key, data in actions.items():
        p_id = data["persona_id"]
        items = data["items"]
        stats[p_id]["tong_hanh_dong"] += 1
        p_valid_dims = t1_dims_by_p[p_id]

        matched_count_in_step = 0
        for it in items:
            dim_raw = str(it.get("dimension", "")).strip().lower()
            sg, grp, std_dim = mapping.get(dim_raw, ("Khác", "Khác", dim_raw))
            std_dim_clean = std_dim.lower().strip()

            # Kiểm tra evidence có thuộc bộ trường Bảng 1 của persona này không
            if std_dim_clean in p_valid_dims or dim_raw in p_valid_dims:
                matched_count_in_step += 1

        if matched_count_in_step > 0:
            stats[p_id]["hanh_dong_co_so_thich"] += 1
            stats[p_id]["tong_evidence_so_thich"] += matched_count_in_step

    rows = []
    tot_actions_all = 0
    tot_matched_actions_all = 0
    tot_matched_evidence_all = 0

    for p_id in PERSONA_ORDER:
        d = stats[p_id]
        tot = d["tong_hanh_dong"]
        n_act = d["hanh_dong_co_so_thich"]
        n_ev = d["tong_evidence_so_thich"]
        pct = round(n_act / tot * 100, 2) if tot > 0 else 0.0

        tot_actions_all += tot
        tot_matched_actions_all += n_act
        tot_matched_evidence_all += n_ev

        rows.append({
            "persona_id": p_id,
            "persona_ten": PERSONA_LABELS.get(p_id, p_id),
            "tong_so_hanh_dong": tot,
            "so_hanh_dong_co_so_thich": n_act,
            "ty_le_hanh_dong_so_thich_%": pct,
            "tong_evidence_so_thich_vien_dan": n_ev,
        })

    # Dòng tổng cộng toàn mạng
    pct_all = round(tot_matched_actions_all / tot_actions_all * 100, 2) if tot_actions_all > 0 else 0.0
    rows.append({
        "persona_id": "TOAN_HE_THONG",
        "persona_ten": "Toàn bộ 6 Persona Facebook",
        "tong_so_hanh_dong": tot_actions_all,
        "so_hanh_dong_co_so_thich": tot_matched_actions_all,
        "ty_le_hanh_dong_so_thich_%": pct_all,
        "tong_evidence_so_thich_vien_dan": tot_matched_evidence_all,
    })

    return pd.DataFrame(rows)


def build_table_3_cooccurrence(
    actions: Dict[Tuple[str, int], Dict[str, Any]],
    df_t1: pd.DataFrame,
    mapping: Dict[str, Tuple[str, str, str]],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Tạo BẢNG 3: Ma trận đồng xuất hiện giữa các trường Sở thích/Ẩm thực (BẢNG 1)
    và các trường / subgroup khác của từng Persona.
    """
    t1_dims_by_p: Dict[str, set] = defaultdict(set)
    for _, r in df_t1.iterrows():
        p_id = r["persona_id"]
        dim_clean = str(r["dimension"]).lower().strip()
        t1_dims_by_p[p_id].add(dim_clean)
        clean_dim_k = "_".join(dim_clean.replace(":", "").replace("&", "").replace("/", " ").replace("-", " ").split())
        t1_dims_by_p[p_id].add(clean_dim_k)

    subgroup_counts: Dict[str, Counter] = defaultdict(Counter)
    dim_counts: Dict[str, Counter] = defaultdict(Counter)
    interest_action_counts = Counter()

    for act_key, data in actions.items():
        p_id = data["persona_id"]
        items = data["items"]
        p_valid_dims = t1_dims_by_p[p_id]

        t1_ev_dims = []
        other_dims = []

        for it in items:
            dim_raw = str(it.get("dimension", "")).strip().lower()
            sg, grp, std_dim = mapping.get(dim_raw, ("Khác", "Khác", dim_raw))
            std_dim_clean = std_dim.lower().strip()

            if std_dim_clean in p_valid_dims or dim_raw in p_valid_dims:
                t1_ev_dims.append(dim_raw)
            else:
                other_dims.append(dim_raw)

        if t1_ev_dims:
            interest_action_counts[p_id] += 1
            for od in other_dims:
                sg_info = mapping.get(od.lower(), ("Khác", "Khác", od))
                sg = sg_info[0]
                std_d = sg_info[2]
                subgroup_counts[p_id][sg] += 1
                dim_counts[p_id][(std_d, sg)] += 1

    # Tạo bảng phẳng thống kê theo Subgroup
    sg_rows = []
    for p_id in PERSONA_ORDER:
        n_act = interest_action_counts[p_id]
        if n_act == 0:
            sg_rows.append({
                "persona_id": p_id,
                "persona_ten": PERSONA_LABELS.get(p_id, p_id),
                "so_hanh_dong_co_so_thich": 0,
                "subgroup_di_kem": "Không có hành động kích hoạt sở thích",
                "so_lan_dong_xuat_hien": 0,
                "ty_le_xuat_hien_moi_action_%": 0.0,
            })
            continue

        for sg, cnt in subgroup_counts[p_id].most_common():
            pct = round((cnt / n_act) * 100, 1)
            sg_rows.append({
                "persona_id": p_id,
                "persona_ten": PERSONA_LABELS.get(p_id, p_id),
                "so_hanh_dong_co_so_thich": n_act,
                "subgroup_di_kem": sg,
                "so_lan_dong_xuat_hien": cnt,
                "ty_le_xuat_hien_moi_action_%": pct,
            })

    # Tạo bảng chi tiết theo Dimension cụ thể
    dim_rows = []
    for p_id in PERSONA_ORDER:
        n_act = interest_action_counts[p_id]
        if n_act == 0:
            continue
        for (d, sg), cnt in dim_counts[p_id].most_common(10):
            dim_rows.append({
                "persona_id": p_id,
                "persona_ten": PERSONA_LABELS.get(p_id, p_id),
                "so_hanh_dong_co_so_thich": n_act,
                "truong_evidence_di_kem": d,
                "subgroup": sg,
                "so_lan_dong_xuat_hien": cnt,
                "ty_le_xuat_hien_moi_action_%": round((cnt / n_act) * 100, 1),
            })

    return pd.DataFrame(sg_rows), pd.DataFrame(dim_rows)


def build_table_visited_prominent_attributes(
    actions: Dict[Tuple[str, int], Dict[str, Any]],
    df_table_4: pd.DataFrame,
    mapping: Dict[str, Tuple[str, str, str]],
) -> pd.DataFrame:
    """Thống kê các thuộc tính trong Bảng 4 được thăm ít nhất 1 lần bởi evidence."""
    dim_aliases = {
        "interest_technology": "interest: technology & ai",
        "interest_investing": "interest: personal finance & investing",
        "books_mystery": "books: mystery / thriller",
        "books_biography": "books: biography / memoir",
        "books_fantasy": "books: fantasy",
        "books_romance": "books: romance",
        "books_historical_fiction": "books: historical fiction",
        "books_self_help": "books: self-help",
        "film_sci_fi_superhero": "film: sci-fi / superhero",
        "film_television": "film: drama",
        "film_horror_thriller": "film: horror / thriller",
        "film_animation": "film: animation",
        "sport_table_tennis": "sport: table tennis",
        "sport_gym_calisthenics": "sport: gym & calisthenic",
        "sport_martial_arts": "sport: martial arts",
        "interest_pets": "interest: pets & animals",
        "interest_spirituality": "interest: spirituality & mindfulness",
        "interest_sports": "interest: sport",
        "value_health": "value: health & wellness",
        "value_wealth": "value: wealth & success",
        "value_tradition": "value: tradition & duty",
        "value_family": "value: family",
        "facebook_frequency": "facebook frequency",
        "reading_frequency": "reading frequency",
        "skepticism": "skepticism / critical verification",
        "group_community_participation": "group / community participation",
        "curiosity": "curiosity",
        "playfulness": "playfulness",
    }

    def to_snake(s: str) -> str:
        s_clean = s.lower().replace(":", "").replace("&", "").replace("/", " ").replace("-", " ").strip()
        return "_".join(s_clean.split())

    ev_counts_by_p = defaultdict(Counter)
    act_counts_by_p = defaultdict(Counter)

    for act_key, data in actions.items():
        p = data["persona_id"]
        items = data["items"]
        act_dims_seen = set()
        for it in items:
            d_raw = str(it.get("dimension", "")).strip().lower()
            sg, grp, std_d = mapping.get(d_raw, ("Khác", "Khác", d_raw))
            canonical = dim_aliases.get(d_raw, std_d.lower().strip())
            c_snake = to_snake(canonical)
            ev_counts_by_p[p][c_snake] += 1
            act_dims_seen.add(c_snake)

        for c_s in act_dims_seen:
            act_counts_by_p[p][c_s] += 1

    visited_records = []
    for _, r in df_table_4.iterrows():
        p = r["persona_id"]
        dim = r["dimension"]
        dim_snake = to_snake(dim)
        ev_cnt = ev_counts_by_p[p].get(dim_snake, 0)
        act_cnt = act_counts_by_p[p].get(dim_snake, 0)
        if ev_cnt > 0:
            visited_records.append({
                "persona_id": p,
                "persona_ten": r["persona_ten"],
                "group": r["group"],
                "subgroup": r["subgroup"],
                "dimension": dim,
                "thuoc_tinh": r["thuoc_tinh"],
                "gia_tri": r["gia_tri"],
                "nhom_gia_tri": r["nhom_gia_tri"],
                "so_lan_evidence": ev_cnt,
                "so_hanh_dong": act_cnt,
            })

    df_visited = pd.DataFrame(visited_records)
    return df_visited.sort_values(by=["persona_id", "subgroup", "so_hanh_dong"], ascending=[True, True, False])


def build_table_category_distribution(
    actions: Dict[Tuple[str, int], Dict[str, Any]],
    csv_dim_path: Path,
) -> pd.DataFrame:
    """Tạo BẢNG PHÂN BỔ VIỆN DẪN EVIDENCE THEO TRƯỜNG CATEGORY CHO TỪNG PERSONA."""
    df_dim = pd.read_csv(csv_dim_path)
    dim_lookup = {}
    for _, r in df_dim.iterrows():
        d = str(r["Dimension"]).strip()
        lbl = str(r["Label"]).strip()
        sg = str(r["Subgroup"]).strip()
        grp = str(r["Group"]).strip()
        cat = str(r["Category"]).strip()

        clean_d = "_".join(d.lower().replace(":", "").replace("&", "").replace("/", " ").replace("-", " ").split())
        clean_lbl = "_".join(lbl.lower().replace(":", "").replace("&", "").replace("/", " ").replace("-", " ").split())

        info = (grp, sg, cat, d)
        dim_lookup[clean_d] = info
        dim_lookup[clean_lbl] = info

    custom_rules = {
        "curiosity": ("Psychology & Cognition", "Cognitive & Work Style", "Thinking & Decision Making", "Curiosity"),
        "content_consumption_format": ("Behavior and Interaction", "Social Engagement", "Interaction Habits", "Content consumption format"),
        "interest_real_estate": ("Lifestyle", "Interest", "Areas of Interest", "Interest: Real estate"),
        "group_community_participation": ("Behavior and Interaction", "Social Engagement", "Interaction Habits", "Group / community participation"),
        "cuisine_vietnamese": ("Lifestyle", "Food & Beverage", "Culinary Preferences", "Cuisine: Vietnamese"),
        "province": ("Background", "Demographics", "Demographics", "Province"),
        "sport_football": ("Lifestyle", "Interest", "Sports", "Sport: Football"),
        "cuisine_street_food": ("Lifestyle", "Food & Beverage", "Culinary Preferences", "Cuisine: Street Food"),
        "interest_technology": ("Lifestyle", "Interest", "Areas of Interest", "Interest: Technology & AI"),
        "interest_technology_ai": ("Lifestyle", "Interest", "Areas of Interest", "Interest: Technology & AI"),
        "attention_span": ("Psychology & Cognition", "Cognitive & Work Style", "Thinking & Decision Making", "Attention span"),
        "value_tradition": ("Psychology & Cognition", "Values & Worldview", "Life Priorities & Values", "Value: Tradition"),
        "skepticism": ("Psychology & Cognition", "Cognitive & Work Style", "Thinking & Decision Making", "Skepticism / critical verification"),
        "social_engagement_style": ("Behavior and Interaction", "Social Engagement", "Interaction Habits", "Social engagement style"),
        "value_health": ("Psychology & Cognition", "Values & Worldview", "Life Priorities & Values", "Value: Health"),
        "tone": ("Behavior and Interaction", "Communication Style", "Tone & Manner", "Tone"),
        "reading_frequency": ("Lifestyle", "Daily Lifestyle", "Habits", "Reading frequency"),
        "career_role": ("Background", "Career & Education", "Employment & Occupation", "Career role"),
        "interest_film": ("Lifestyle", "Interest", "Creative & Cultural Tastes", "Interest: Film"),
        "current_thread": ("Behavior and Interaction", "Interaction State", "Emotional & Energy State", "Current thread / context"),
        "purpose": ("Behavior and Interaction", "Interaction State", "Emotional & Energy State", "Session purpose"),
        "books_mystery": ("Lifestyle", "Interest", "Creative & Cultural Tastes", "Books: Mystery / Thriller"),
        "dialect_register": ("Background", "Language Profile", "Language Competency", "Dialect / register"),
        "decision_speed": ("Psychology & Cognition", "Cognitive & Work Style", "Thinking & Decision Making", "Decision speed"),
        "facebook_frequency": ("Behavior and Interaction", "Platform Presence", "Social Media Platforms", "Platform frequency: Facebook"),
        "writing_format": ("Behavior and Interaction", "Communication Style", "Tone & Manner", "Writing format"),
        "interest_travel": ("Lifestyle", "Interest", "Areas of Interest", "Interest: Travel"),
        "energy_level": ("Behavior and Interaction", "Interaction State", "Emotional & Energy State", "Energy level"),
        "value_wealth": ("Psychology & Cognition", "Values & Worldview", "Life Priorities & Values", "Value: Wealth"),
        "attitude_new_technology": ("Psychology & Cognition", "Values & Worldview", "Social Perspectives", "Attitude to new technology"),
        "value_family": ("Psychology & Cognition", "Values & Worldview", "Life Priorities & Values", "Value: Family"),
        "interest_parenting_family_life": ("Lifestyle", "Interest", "Areas of Interest", "Interest: Parenting & Family life"),
        "open_question": ("Behavior and Interaction", "Communication Style", "Tone & Manner", "Open question tendency"),
        "humor_style": ("Behavior and Interaction", "Communication Style", "Tone & Manner", "Humor style"),
        "extroversion": ("Psychology & Cognition", "Personality", "Core Personality", "Extroversion"),
        "character_playfulness": ("Psychology & Cognition", "Personality", "Core Personality", "Playfulness"),
        "music_indie": ("Lifestyle", "Interest", "Creative & Cultural Tastes", "Music: Indie"),
        "emotional_expressiveness": ("Behavior and Interaction", "Communication Style", "Tone & Manner", "Emotional expressiveness"),
        "interest_pets": ("Lifestyle", "Interest", "Areas of Interest", "Interest: Pets & Animals"),
        "attitude_advertising": ("Behavior and Interaction", "Social Engagement", "Interaction Habits", "Pet peeve: Pop-up ads"),
        "interest_spirituality": ("Lifestyle", "Interest", "Areas of Interest", "Interest: Spirituality & Mindfulness"),
        "big_picture_vs_detail": ("Psychology & Cognition", "Cognitive & Work Style", "Thinking & Decision Making", "Big picture vs detail"),
        "books_self_help": ("Lifestyle", "Interest", "Creative & Cultural Tastes", "Books: Self-help"),
        "storytelling_tendency": ("Behavior and Interaction", "Communication Style", "Tone & Manner", "Storytelling tendency"),
        "film_animation": ("Lifestyle", "Interest", "Creative & Cultural Tastes", "Film: Animation"),
        "interest_investing": ("Lifestyle", "Interest", "Areas of Interest", "Interest: Personal finance & Investing"),
        "emoji_emoticon_use": ("Behavior and Interaction", "Communication Style", "Tone & Manner", "Emoji / emoticon usage"),
        "character_social_intelligence": ("Capability", "Skills", "General Skills", "Social intelligence"),
        "children": ("Background", "Demographics", "Demographics", "Children"),
        "state": ("Behavior and Interaction", "Interaction State", "Emotional & Energy State", "Bot runtime state"),
        "logic_vs_intuition": ("Psychology & Cognition", "Cognitive & Work Style", "Thinking & Decision Making", "Logic vs intuition"),
        "tech_savviness": ("Capability", "Skills", "General Skills", "Tech savviness"),
        "sport_gym_calisthenics": ("Lifestyle", "Interest", "Sports", "Sport: Gym & Calisthenic"),
        "sport_martial_arts": ("Lifestyle", "Interest", "Sports", "Sport: Martial arts"),
        "attitude_online_reviews": ("Behavior and Interaction", "Social Engagement", "Interaction Habits", "Review checking behavior"),
        "media_diet": ("Behavior and Interaction", "Social Engagement", "Interaction Habits", "Media diet"),
        "directness": ("Behavior and Interaction", "Communication Style", "Tone & Manner", "Directness"),
        "film_sci_fi_superhero": ("Lifestyle", "Interest", "Creative & Cultural Tastes", "Film: Sci-fi / Superhero"),
        "sport_badminton": ("Lifestyle", "Interest", "Sports", "Sport: Badminton"),
        "film_horror_thriller": ("Lifestyle", "Interest", "Creative & Cultural Tastes", "Film: Horror / Thriller"),
        "verbosity": ("Behavior and Interaction", "Communication Style", "Tone & Manner", "Verbosity"),
        "attitude_climate_action": ("Psychology & Cognition", "Values & Worldview", "Social Perspectives", "Climate action attitude"),
        "interest_sports": ("Lifestyle", "Interest", "Sports", "Interest: Sport"),
        "books_fantasy": ("Lifestyle", "Interest", "Creative & Cultural Tastes", "Books: Fantasy"),
        "books_romance": ("Lifestyle", "Interest", "Creative & Cultural Tastes", "Books: Romance"),
        "cuisine_japanese": ("Lifestyle", "Food & Beverage", "Culinary Preferences", "Cuisine: Japanese"),
        "music_pop": ("Lifestyle", "Interest", "Creative & Cultural Tastes", "Music: Pop"),
        "formality": ("Behavior and Interaction", "Communication Style", "Tone & Manner", "Formality"),
        "language_english": ("Background", "Language Profile", "Language Competency", "Language: English"),
        "location": ("Background", "Demographics", "Demographics", "Location"),
        "books_historical_fiction": ("Lifestyle", "Interest", "Creative & Cultural Tastes", "Books: Historical fiction"),
        "character_generosity": ("Psychology & Cognition", "Personality", "Core Personality", "Generosity"),
        "current_surface": ("Behavior and Interaction", "Interaction State", "Emotional & Energy State", "Current surface"),
        "film_television": ("Lifestyle", "Interest", "Creative & Cultural Tastes", "Film: Drama"),
        "post_title": ("Behavior and Interaction", "Interaction State", "Emotional & Energy State", "Post title context"),
        "openness": ("Psychology & Cognition", "Personality", "Core Personality", "Dominant personality trait: Openness"),
        "politeness": ("Behavior and Interaction", "Communication Style", "Tone & Manner", "Politeness"),
        "sport_boxing": ("Lifestyle", "Interest", "Sports", "Sport: Boxing"),
        "sport_table_tennis": ("Lifestyle", "Interest", "Sports", "Sport: Table tennis"),
        "sport_running": ("Lifestyle", "Interest", "Sports", "Sport: Running"),
        "sport_tennis": ("Lifestyle", "Interest", "Sports", "Sport: Tennis"),
    }
    for k, v in custom_rules.items():
        dim_lookup[k] = v

    cat_counts = defaultdict(Counter)
    cat_meta = {}

    for act_key, data in actions.items():
        p = data["persona_id"]
        for it in data["items"]:
            d_raw = str(it.get("dimension", "")).strip()
            d_clean = "_".join(d_raw.lower().replace(":", "").replace("&", "").replace("/", " ").replace("-", " ").split())
            info = dim_lookup.get(d_clean)
            if not info:
                info = ("Khác", "Khác", "Khác", d_raw)
            grp, sg, cat, std_d = info
            cat_counts[p][cat] += 1
            if cat not in cat_meta:
                cat_meta[cat] = (grp, sg)

    cats = sorted(list(cat_meta.keys()))
    rows = []
    for c in cats:
        grp, sg = cat_meta[c]
        row = {"Group": grp, "Subgroup": sg, "Category": c}
        tot = 0
        for p in PERSONA_ORDER:
            cnt = cat_counts[p][c]
            row[p] = cnt
            tot += cnt
        row["Tong_cong"] = tot
        rows.append(row)

    df_cat = pd.DataFrame(rows).sort_values(by="Tong_cong", ascending=False)
    return df_cat


def main():
    jsonl_path = PROJECT_ROOT / "data" / "selected_6_facebook_personas_description.jsonl"
    csv_dim_path = PROJECT_ROOT / "data" / "persona_Dimension_v2.csv"
    db_path = PROJECT_ROOT / "data" / "persona-runner.sqlite"
    output_dir = PROJECT_ROOT / "output" / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 110)
    print(" KHỞI ĐỘNG PHÂN TÍCH HÀNH VI SỞ THÍCH & ẨM THỰC VÀ KHẢ NĂNG KẾT HỢP ĐA CHIỀU CỦA AGENT")
    print("=" * 110)

    # Nạp ánh xạ Subgroup từ CSV
    print(f"[*] Đang nạp danh mục thuộc tính từ: {csv_dim_path}")
    mapping = load_dimension_mappings(csv_dim_path)

    # 4. BẢNG 4: DANH MỤC THUỘC TÍNH NỔI BẬT THEO GROUP & SUBGROUP CHO MỖI PERSONA
    print("\n" + "=" * 110)
    print(" BẢNG 4: THỐNG KÊ CÁC TRƯỜNG NỔI BẬT TOÀN DIỆN THEO GROUP VÀ SUBGROUP CỦA MỖI PERSONA")
    print(" (BAO GỒM: CHUYÊN GIA/NÂNG CAO, RẤT CAO/CAO, NHIỀU LẦN MỖI NGÀY/HÀNG NGÀY, RẤT THÍCH/THÍCH, THƯỜNG XUYÊN/CHỦ YẾU THEO DÕI)")
    print("=" * 110)
    t4_detail, t4_pivot = build_table_4_prominent_attributes(jsonl_path, csv_dim_path)

    print("\n>>> TỔNG HỢP SỐ LƯỢNG THUỘC TÍNH NỔI BẬT THEO GROUP & SUBGROUP (BẢNG 4):")
    print(t4_pivot.to_string())

    csv_t4_detail = output_dir / "interest_table4_high_affinity_attributes.csv"
    t4_detail.to_csv(csv_t4_detail, index=False, encoding="utf-8-sig")
    print(f"\n[✓] Đã xuất Bảng 4 (Chi tiết) ra: {csv_t4_detail}")

    csv_t4_pivot = output_dir / "interest_table4_summary_by_subgroup.csv"
    t4_pivot.to_csv(csv_t4_pivot, encoding="utf-8-sig")
    print(f"[✓] Đã xuất Bảng 4 (Tổng hợp Group/Subgroup) ra: {csv_t4_pivot}")

    # 1. BẢNG 1: DÙNG BẢNG 4 LẤY CÁC TRƯỜNG YÊU THÍCH (INTEREST) & ẨM THỰC (FOOD & BEVERAGE) LÀM MỐC
    print("\n" + "=" * 110)
    print(" BẢNG 1: TỔNG HỢP CÁC TRƯỜNG SỞ THÍCH & ẨM THỰC LÀM MỐC (LẤY TỪ BẢNG 4: SUBGROUP INTEREST & FOOD & BEVERAGE)")
    print("=" * 110)
    t1 = build_table_1_persona_interests(t4_detail)
    print(t1[["persona_id", "subgroup", "thuoc_tinh", "gia_tri", "nhom_gia_tri"]].to_string(index=False))
    csv_t1 = output_dir / "interest_table1_persona_profiles.csv"
    t1.to_csv(csv_t1, index=False, encoding="utf-8-sig")
    print(f"[✓] Đã xuất Bảng 1 ra: {csv_t1} (Tổng {len(t1)} thuộc tính mốc)")

    # Nạp danh sách hành động từ SQLite
    actions = load_decision_actions_from_sqlite(db_path)

    # 2. BẢNG 2: TỈ LỆ HÀNH ĐỘNG CÓ VIỆN DẪN SỞ THÍCH & ẨM THỰC (THEO CÁC TRƯỜNG TRONG BẢNG 1)
    print("\n" + "=" * 110)
    print(" BẢNG 2: TỈ LỆ HÀNH ĐỘNG CỦA PERSONA CÓ VIỆN DẪN EVIDENCE TỪ CÁC TRƯỜNG TRONG BẢNG 1")
    print("=" * 110)
    t2 = build_table_2_action_interest_rates(actions, t1, mapping)
    print(t2[["persona_id", "tong_so_hanh_dong", "so_hanh_dong_co_so_thich", "ty_le_hanh_dong_so_thich_%", "tong_evidence_so_thich_vien_dan"]].to_string(index=False))
    csv_t2 = output_dir / "interest_table2_action_rates.csv"
    t2.to_csv(csv_t2, index=False, encoding="utf-8-sig")
    print(f"[✓] Đã xuất Bảng 2 ra: {csv_t2}")

    # 3. BẢNG 3: MA TRẬN ĐỒNG XUẤT HIỆN SUBGROUP & TRƯỜNG ĐI KÈM (THEO CÁC HÀNH ĐỘNG CÓ BẢNG 1)
    print("\n" + "=" * 110)
    print(" BẢNG 3: PHÂN TÍCH SỰ KẾT HỢP ĐA CHIỀU (KHI CÓ EVIDENCE BẢNG 1 THÌ THƯỜNG KẾT HỢP VỚI SUBGROUP VÀ TRƯỜNG NÀO)")
    print("=" * 110)
    t3_sg, t3_dim = build_table_3_cooccurrence(actions, t1, mapping)
    print(t3_sg.to_string(index=False))

    csv_t3_sg = output_dir / "interest_table3_subgroup_cooccurrence.csv"
    t3_sg.to_csv(csv_t3_sg, index=False, encoding="utf-8-sig")
    print(f"[✓] Đã xuất Bảng 3 (Subgroup) ra: {csv_t3_sg}")

    csv_t3_dim = output_dir / "interest_table3_dimension_cooccurrence.csv"
    t3_dim.to_csv(csv_t3_dim, index=False, encoding="utf-8-sig")
    print(f"[✓] Đã xuất Bảng 3 (Chi tiết Dimension) ra: {csv_t3_dim}")

    # 5. BẢNG THỐNG KÊ CÁC THUỘC TÍNH BẢNG 4 ĐƯỢC THĂM ÍT NHẤT 1 LẦN BỞI EVIDENCE
    print("\n" + "=" * 110)
    print(" BẢNG MỞ RỘNG: CÁC SỞ THÍCH VÀ THUỘC TÍNH TẠI BẢNG 4 ĐƯỢC THĂM ÍT NHẤT 1 LẦN BỞI EVIDENCE")
    print("=" * 110)
    df_visited = build_table_visited_prominent_attributes(actions, t4_detail, mapping)
    
    # Lọc riêng các thuộc tính thuộc Sở thích & Ẩm thực (Interest & Food & Beverage)
    df_visited_interests = df_visited[df_visited["subgroup"].isin(["Interest", "Food & Beverage"])].copy()
    print(f"\n>>> CÁC SỞ THÍCH & ẨM THỰC TẠI BẢNG 4 ĐƯỢC THĂM ÍT NHẤT 1 LẦN (TỔNG {len(df_visited_interests)} SỞ THÍCH):")
    print(df_visited_interests[["persona_id", "subgroup", "dimension", "gia_tri", "so_lan_evidence", "so_hanh_dong"]].to_string(index=False))

    csv_visited_interests = output_dir / "interest_table4_visited_interests_only.csv"
    df_visited_interests.to_csv(csv_visited_interests, index=False, encoding="utf-8-sig")
    print(f"\n[✓] Đã xuất Bảng các sở thích được thăm ra: {csv_visited_interests}")

    csv_visited_all = output_dir / "interest_table4_visited_all_attributes.csv"
    df_visited.to_csv(csv_visited_all, index=False, encoding="utf-8-sig")
    print(f"[✓] Đã xuất Toàn bộ thuộc tính Bảng 4 được thăm ({len(df_visited)} thuộc tính) ra: {csv_visited_all}")

    # 6. BẢNG PHÂN BỔ VIỆN DẪN EVIDENCE THEO TRƯỜNG CATEGORY CHO TỪNG PERSONA
    print("\n" + "=" * 110)
    print(" BẢNG PHÂN BỔ VIỆN DẪN EVIDENCE THEO TRƯỜNG CATEGORY CHO TỪNG PERSONA")
    print("=" * 110)
    df_cat = build_table_category_distribution(actions, csv_dim_path)
    print(df_cat[["Group", "Subgroup", "Category", "vn_fb_001", "vn_fb_002", "vn_fb_003", "vn_fb_004", "vn_fb_005", "vn_fb_006", "Tong_cong"]].to_string(index=False))

    csv_cat = output_dir / "interest_category_distribution.csv"
    df_cat.to_csv(csv_cat, index=False, encoding="utf-8-sig")
    print(f"\n[✓] Đã xuất Bảng phân bổ Category ra: {csv_cat}")

    print("\n" + "=" * 110)
    print(" [HOÀN TẤT] TẤT CẢ CÁC BẢNG ĐÃ ĐƯỢC TÍNH TOÁN VÀ XUẤT THÀNH CÔNG RA THƯ MỤC OUTPUT/TABLES!")
    print("=" * 110)


if __name__ == "__main__":
    main()

