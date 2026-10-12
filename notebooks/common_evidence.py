"""
Phân tích Pointwise Mutual Information (PMI) cho Evidence có nguồn gốc từ Persona (source == 'persona').
- Không dịch nghĩa nhãn (sử dụng tên dimension gốc).
- Thống kê trên toàn bộ các hành động có evidence khởi nguồn từ Persona.
- Điều kiện lọc: Bắt buộc số lần đồng xuất hiện > 1 (count >= 2).
- Thống kê vào 1 bảng duy nhất: Mỗi Persona lấy đúng 3 nhóm evidence.
- Thứ tự ưu tiên: Ưu tiên nhóm 3 (3-itemsets) trước, sau đó bổ sung bằng nhóm 2 (2-itemsets).
"""

import sys
import json
import math
import sqlite3
import itertools
from collections import defaultdict, Counter
from pathlib import Path
import pandas as pd

# Đảm bảo in tiếng Việt chuẩn trên Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "persona-runner.sqlite"
OUTPUT_DIR = PROJECT_ROOT / "output" / "tables"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PERSONA_ORDER = [
    "vn_fb_001",
    "vn_fb_002",
    "vn_fb_003",
    "vn_fb_004",
    "vn_fb_005",
    "vn_fb_006",
]

PERSONA_LABELS = {
    "vn_fb_001": "vn_fb_001 (Thiết kế đồ họa, 26t, Nữ)",
    "vn_fb_002": "vn_fb_002 (Nông nghiệp/Gia đình, 42t, Nữ)",
    "vn_fb_003": "vn_fb_003 (Bảo vệ ca trực, 28t, Nam)",
    "vn_fb_004": "vn_fb_004 (Nhân viên nhà hàng, 22t, Nam)",
    "vn_fb_005": "vn_fb_005 (Thợ cơ khí, 31t, Nam)",
    "vn_fb_006": "vn_fb_006 (Kinh doanh BĐS, 52t, Nam)",
}


JSONL_PATH = PROJECT_ROOT / "data" / "selected_6_facebook_personas_description.jsonl"
DIM_CSV_PATH = PROJECT_ROOT / "data" / "persona_Dimension_v2.csv"


DIMENSION_MANUAL_DESCRIPTIONS = {
    "big_picture_vs_detail": "Xu hướng nhìn nhận tổng thể chiến lược hay soi xét chi tiết cụ thể.",
    "character_playfulness": "Tính cách tinh nghịch, hóm hỉnh, thích đùa vui.",
    "dialect_register": "Phương ngữ vùng miền và phong cách ngôn ngữ giao tiếp.",
    "emoji_emoticon_use": "Thói quen và tần suất sử dụng biểu tượng cảm xúc (emoji / emoticon).",
    "logic_vs_intuition": "Xu hướng ra quyết định dựa trên logic/dữ liệu hay trực giác cá nhân.",
    "tone": "Sắc thái giọng điệu ngôn từ khi bình luận hoặc đăng bài.",
    "writing_format": "Định dạng và hình thức cấu trúc bài viết/bình luận.",
}


def load_jsonl_persona_attributes(jsonl_path: Path):
    """Nạp trực tiếp toàn bộ thuộc tính của 6 Persona từ selected_6_facebook_personas_description.jsonl."""
    profiles = {}
    if not jsonl_path.exists():
        return profiles
    try:
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    pid = data.get("persona_id")
                    if pid:
                        profiles[pid] = data.get("attributes", {})
    except Exception:
        pass
    return profiles


def load_dimension_key_mappings(csv_path: Path):
    """Xây dựng từ điển ánh xạ từ dimension code (snake_case) sang key thuộc tính trong JSONL và mô tả."""
    dim_to_key = {}
    if not csv_path.exists():
        return dim_to_key
    try:
        df_dim = pd.read_csv(csv_path)
        for _, r in df_dim.iterrows():
            d_name = str(r["Dimension"]).strip()
            desc = str(r["Description"]).strip()
            clean_d = d_name.lower().replace(":", "").replace("&", "").replace("/", " ").replace("-", " ")
            k_d = "_".join(clean_d.split())
            dim_to_key[k_d] = desc
            dim_to_key[d_name] = desc
            parts = k_d.split("_")
            if len(parts) >= 2:
                prefix_2 = f"{parts[0]}_{parts[1]}"
                if prefix_2 not in dim_to_key:
                    dim_to_key[prefix_2] = desc
            if parts[0] == "skepticism":
                dim_to_key["skepticism"] = desc
    except Exception:
        pass
    return dim_to_key


def load_persona_evidence_transactions(db_path: Path):
    """Nạp toàn bộ dữ liệu decision_evidence, lọc các evidence có source == 'persona'."""
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

    persona_transactions = defaultdict(list)
    all_transactions = []
    item_counts_global = Counter()
    item_counts_by_persona = defaultdict(Counter)
    persona_dim_values = defaultdict(dict)

    for _, row in df_raw.iterrows():
        p_id = row["persona_id"]
        act = str(row["action"]).strip()
        try:
            items = json.loads(row["evidence_json"])
            p_dims = set()
            for it in items:
                if str(it.get("source", "")).strip().lower() == "persona":
                    d = str(it.get("dimension", "")).strip()
                    val = it.get("value")
                    if d:
                        p_dims.add(d)
                        if val is not None and d not in persona_dim_values[p_id]:
                            persona_dim_values[p_id][d] = str(val)

            if p_dims:
                persona_transactions[p_id].append((act, p_dims))
                all_transactions.append((p_id, p_dims))
                for d in p_dims:
                    item_counts_global[d] += 1
                    item_counts_by_persona[p_id][d] += 1
        except Exception:
            pass

    return persona_transactions, all_transactions, item_counts_global, item_counts_by_persona, persona_dim_values


def compute_top_combined_itemsets(
    persona_transactions: dict,
    item_counts_global: Counter,
    total_transactions: int,
    top_k: int = 5,
    min_count: int = 2,
):
    """
    Tính toán Pointwise Mutual Information (PMI) và chọn ra đúng `top_k` tập evidence cho mỗi Persona:
    - Điều kiện lọc: Số lần đồng xuất hiện >= min_count (mặc định min_count = 2, tức là số lần > 1).
    - Thứ tự ưu tiên: Nhóm 3 (3-itemsets) trước -> Nhóm 2 (2-itemsets) sau.
    - Sắp xếp: Theo điểm PMI giảm dần, ưu tiên số lần đồng xuất hiện nếu PMI bằng nhau.
    - Kèm Top 2 hành động (actions) được kích hoạt nhiều nhất khi tập evidence này cùng xuất hiện.
    """
    N = total_transactions
    all_combined_results = []

    for p_id in PERSONA_ORDER:
        t_list = persona_transactions.get(p_id, [])
        n_p = len(t_list)

        pair_counts = Counter()
        pair_actions = defaultdict(Counter)
        triplet_counts = Counter()
        triplet_actions = defaultdict(Counter)

        for act, t_items in t_list:
            sorted_items = sorted(list(t_items))
            for pair in itertools.combinations(sorted_items, 2):
                pair_counts[pair] += 1
                pair_actions[pair][act] += 1
            for trip in itertools.combinations(sorted_items, 3):
                triplet_counts[trip] += 1
                triplet_actions[trip][act] += 1

        # 1. Tập hợp các 3-itemsets thỏa mãn số lần >= min_count
        triplet_scored = []
        for (item_a, item_b, item_c), cnt_abc in triplet_counts.items():
            if cnt_abc < min_count:
                continue

            cnt_a = item_counts_global[item_a]
            cnt_b = item_counts_global[item_b]
            cnt_c = item_counts_global[item_c]

            prob_abc = cnt_abc / N
            prob_indep = (cnt_a / N) * (cnt_b / N) * (cnt_c / N)

            if prob_indep > 0 and prob_abc > 0:
                pmi = math.log2(prob_abc / prob_indep)
                npmi = pmi / (-math.log2(prob_abc))
            else:
                pmi = 0.0
                npmi = 0.0

            top_acts = triplet_actions[(item_a, item_b, item_c)].most_common(2)
            top_acts_str = ", ".join([f"{a} ({c})" for a, c in top_acts])

            triplet_scored.append({
                "persona_id": p_id,
                "persona_ten": PERSONA_LABELS.get(p_id, p_id),
                "loai_tap": "Nhóm 3 (3-itemset)",
                "evidence_set": f"{item_a}  +  {item_b}  +  {item_c}",
                "evidence_1": item_a,
                "evidence_2": item_b,
                "evidence_3": item_c,
                "dims_list": [item_a, item_b, item_c],
                "so_lan_dong_xuat_hien": cnt_abc,
                "support_%": round(prob_abc * 100, 2),
                "support_persona_%": round((cnt_abc / n_p) * 100, 2) if n_p > 0 else 0.0,
                "pmi_score": round(pmi, 3),
                "npmi_score": round(npmi, 3),
                "top_2_actions": top_acts_str,
                "tan_suat_toan_cuc_ev1": cnt_a,
                "tan_suat_toan_cuc_ev2": cnt_b,
                "tan_suat_toan_cuc_ev3": cnt_c,
            })

        triplet_scored.sort(
            key=lambda x: (x["pmi_score"], x["so_lan_dong_xuat_hien"]),
            reverse=True,
        )

        # 2. Tập hợp các 2-itemsets thỏa mãn số lần >= min_count
        pair_scored = []
        for (item_a, item_b), cnt_ab in pair_counts.items():
            if cnt_ab < min_count:
                continue

            cnt_a = item_counts_global[item_a]
            cnt_b = item_counts_global[item_b]

            prob_ab = cnt_ab / N
            prob_indep = (cnt_a / N) * (cnt_b / N)

            if prob_indep > 0 and prob_ab > 0:
                pmi = math.log2(prob_ab / prob_indep)
                npmi = pmi / (-math.log2(prob_ab))
            else:
                pmi = 0.0
                npmi = 0.0

            top_acts = pair_actions[(item_a, item_b)].most_common(2)
            top_acts_str = ", ".join([f"{a} ({c})" for a, c in top_acts])

            pair_scored.append({
                "persona_id": p_id,
                "persona_ten": PERSONA_LABELS.get(p_id, p_id),
                "loai_tap": "Nhóm 2 (2-itemset)",
                "evidence_set": f"{item_a}  +  {item_b}",
                "evidence_1": item_a,
                "evidence_2": item_b,
                "evidence_3": "-",
                "dims_list": [item_a, item_b],
                "so_lan_dong_xuat_hien": cnt_ab,
                "support_%": round(prob_ab * 100, 2),
                "support_persona_%": round((cnt_ab / n_p) * 100, 2) if n_p > 0 else 0.0,
                "pmi_score": round(pmi, 3),
                "npmi_score": round(npmi, 3),
                "top_2_actions": top_acts_str,
                "tan_suat_toan_cuc_ev1": cnt_a,
                "tan_suat_toan_cuc_ev2": cnt_b,
                "tan_suat_toan_cuc_ev3": 0,
            })

        pair_scored.sort(
            key=lambda x: (x["pmi_score"], x["so_lan_dong_xuat_hien"]),
            reverse=True,
        )

        # 3. Kết hợp ưu tiên: Nhóm 3 trước -> Nhóm 2 sau
        chosen = triplet_scored[:top_k]
        if len(chosen) < top_k:
            needed = top_k - len(chosen)
            chosen.extend(pair_scored[:needed])

        for rank, item in enumerate(chosen, 1):
            item["hang_rank"] = rank
            all_combined_results.append(item)

    return pd.DataFrame(all_combined_results)


def print_single_summary_table(
    df_result: pd.DataFrame,
    persona_dim_values: dict,
    jsonl_profiles: dict,
    dim_to_key: dict,
):
    """In bảng thống kê với cột Top 2 hành động và liệt kê toàn bộ giá trị thuộc tính bên dưới mỗi bảng."""
    print("\n" + "=" * 155)
    print(" BẢNG THỐNG KÊ TOP TẬP EVIDENCE ĐI CÙNG NHAU (SỐ LẦN > 1 | ƯU TIÊN NHÓM 3 TRƯỚC RỒI ĐẾN NHÓM 2 | TOP 2 HÀNH ĐỘNG)")
    print("=" * 155)

    for p_id in PERSONA_ORDER:
        sub = df_result[df_result["persona_id"] == p_id]
        print(f"\n▶ {PERSONA_LABELS.get(p_id, p_id)}:")
        if sub.empty:
            print("   [!] Không có tập hợp evidence nào thỏa mãn (số lần xuất hiện > 1).")
            continue

        display_cols = [
            "hang_rank",
            "loai_tap",
            "evidence_set",
            "so_lan_dong_xuat_hien",
            "support_persona_%",
            "pmi_score",
            "npmi_score",
            "top_2_actions",
        ]
        sub_display = sub[display_cols].rename(columns={
            "hang_rank": "Top",
            "loai_tap": "Phân loại",
            "evidence_set": "Tập Evidence Đi Cùng Nhau",
            "so_lan_dong_xuat_hien": "Số lần (>1)",
            "support_persona_%": "% Persona",
            "pmi_score": "PMI (bits)",
            "npmi_score": "NPMI",
            "top_2_actions": "Top 2 Hành Động Sử Dụng Nhiều Nhất",
        })
        print(sub_display.to_string(index=False))

        # Liệt kê toàn bộ các giá trị của các thuộc tính được nhắc đến trong bảng
        used_dims = set()
        for dims in sub["dims_list"]:
            for d in dims:
                used_dims.add(d)

        print(f"\n   📋 [GIÁ TRỊ CẤU HÌNH TỪ HỒ SƠ PERSONA ({len(used_dims)} THUỘC TÍNH)]:")
        p_attrs = jsonl_profiles.get(p_id, {})

        for d in sorted(used_dims):
            # 1. Lấy trực tiếp từ log thực thi decision_evidence
            val_vi = persona_dim_values.get(p_id, {}).get(d)

            # 2. Tra cứu từ hồ sơ selected_6_facebook_personas_description.jsonl
            if not val_vi:
                attr_key = dim_to_key.get(d)
                if attr_key and attr_key in p_attrs:
                    val_vi = p_attrs[attr_key]
                else:
                    # Tra cứu gần đúng theo tên thuộc tính
                    for k, v in p_attrs.items():
                        if d.lower() in k.lower():
                            val_vi = v
                            break

            if not val_vi:
                val_vi = "Không có thông tin"

            # 3. Lấy mô tả thuộc tính
            desc = dim_to_key.get(d, "")
            if not desc or desc == d:
                desc = DIMENSION_MANUAL_DESCRIPTIONS.get(d, "")

            print(f"      • {d:<32}: {val_vi}")


def export_persona_attributes_csvs(
    df_result: pd.DataFrame,
    persona_dim_values: dict,
    jsonl_profiles: dict,
    dim_to_key: dict,
    output_dir: Path,
):
    """
    Xuất file CSV riêng cho từng Persona và file tổng hợp ghi lại các giá trị thuộc tính
    của các dimension xuất hiện trong bảng phân tích Evidence.
    """
    all_records = []
    print("\n" + "=" * 155)
    print(" [XUẤT FILE CSV THUỘC TÍNH TỪ HỒ SƠ PERSONA CHO TỪNG PERSONA & TỔNG HỢP]")
    print("=" * 155)

    for p_id in PERSONA_ORDER:
        sub = df_result[df_result["persona_id"] == p_id]
        if sub.empty:
            continue

        dim_top_map = defaultdict(list)
        for _, row in sub.iterrows():
            rank = row["hang_rank"]
            for d in row["dims_list"]:
                dim_top_map[d].append(f"Top {rank}")

        p_attrs = jsonl_profiles.get(p_id, {})
        persona_records = []

        for d in sorted(dim_top_map.keys()):
            # 1. Lấy trực tiếp từ log thực thi decision_evidence
            val_vi = persona_dim_values.get(p_id, {}).get(d)

            # 2. Tra cứu từ hồ sơ JSONL
            if not val_vi:
                attr_key = dim_to_key.get(d)
                if attr_key and attr_key in p_attrs:
                    val_vi = p_attrs[attr_key]
                else:
                    for k, v in p_attrs.items():
                        if d.lower() in k.lower():
                            val_vi = v
                            break

            if not val_vi:
                val_vi = "Không có thông tin"

            # 3. Lấy mô tả thuộc tính
            desc = dim_to_key.get(d, "")
            if not desc or desc == d:
                desc = DIMENSION_MANUAL_DESCRIPTIONS.get(d, "")

            rec = {
                "persona_id": p_id,
                "persona_ten": PERSONA_LABELS.get(p_id, p_id),
                "dimension": d,
                "gia_tri_cau_hinh": val_vi,
                "mo_ta_thuoc_tinh": desc,
            }
            persona_records.append(rec)
            all_records.append(rec)

        # Xuất file CSV riêng cho từng persona
        df_p = pd.DataFrame(persona_records)
        p_csv_path = output_dir / f"pmi_persona_{p_id}_attributes.csv"
        df_p.to_csv(p_csv_path, index=False, encoding="utf-8-sig")
        print(f" [✓] Đã xuất file thuộc tính riêng cho {p_id} ({len(df_p)} thuộc tính): {p_csv_path.name}")

    # Xuất file CSV tổng hợp cả 6 Persona
    df_all = pd.DataFrame(all_records)
    all_csv_path = output_dir / "pmi_persona_top_attributes_values.csv"
    df_all.to_csv(all_csv_path, index=False, encoding="utf-8-sig")
    print(f" [✓] Đã xuất file tổng hợp thuộc tính của toàn bộ 6 Persona ({len(df_all)} dòng): {all_csv_path.name}")


def main():
    print("==========================================================================================")
    print(" PHÂN TÍCH POINTWISE MUTUAL INFORMATION (PMI) CHO EVIDENCE CÓ NGUỒN GỐC TỪ PERSONA")
    print(" - Điều kiện lọc bắt buộc: Số lần đồng xuất hiện > 1 (count >= 2)")
    print(" - Cơ chế ưu tiên: Ưu tiên nhóm 3 (3-itemsets) trước, sau đó đến nhóm 2 (2-itemsets)")
    print(" - Bổ sung: Top 2 hành động sử dụng các evidence này & Tra cứu hồ sơ description.jsonl")
    print("==========================================================================================")

    # 1. Nạp và lọc dữ liệu
    (
        persona_transactions,
        all_transactions,
        item_counts_global,
        item_counts_by_persona,
        persona_dim_values,
    ) = load_persona_evidence_transactions(DB_PATH)

    # Nạp hồ sơ gốc từ selected_6_facebook_personas_description.jsonl
    jsonl_profiles = load_jsonl_persona_attributes(JSONL_PATH)
    dim_to_key = load_dimension_key_mappings(DIM_CSV_PATH)

    N_global = len(all_transactions)
    print(f"\n[+] Tổng số hành vi có evidence khởi nguồn từ Persona: N = {N_global} hành động.")
    print(f"[+] Tổng số loại dimension duy nhất có source='persona': {len(item_counts_global)} dimensions.")
    print(f"[+] Đã nạp hồ sơ thuộc tính 6 Persona từ: {JSONL_PATH.name}")

    for p_id in PERSONA_ORDER:
        cnt_act = len(persona_transactions[p_id])
        cnt_uniq_items = len(item_counts_by_persona[p_id])
        print(f"    - {p_id}: {cnt_act} hành động | {cnt_uniq_items} dimensions khởi nguồn từ persona.")

    # 2. Tính toán bảng kết quả (Top 5 nhóm per Persona, count >= 2, ưu tiên nhóm 3 trước nhóm 2)
    df_combined = compute_top_combined_itemsets(
        persona_transactions=persona_transactions,
        item_counts_global=item_counts_global,
        total_transactions=N_global,
        top_k=5,
        min_count=2,
    )

    # 3. In bảng kết quả kèm giá trị cấu hình thuộc tính
    print_single_summary_table(df_combined, persona_dim_values, jsonl_profiles, dim_to_key)

    # 4. Xuất file CSV phân tích PMI (bỏ cột danh sách tạm dims_list khi xuất file)
    csv_out_df = df_combined.drop(columns=["dims_list"]) if "dims_list" in df_combined.columns else df_combined
    csv_combined = OUTPUT_DIR / "pmi_persona_top_combined_evidence.csv"
    csv_out_df.to_csv(csv_combined, index=False, encoding="utf-8-sig")
    print(f"\n[✓] Đã xuất bảng kết quả hoàn chỉnh ra: {csv_combined}")

    # 5. Xuất file CSV giá trị thuộc tính riêng cho từng Persona và file tổng hợp
    export_persona_attributes_csvs(
        df_result=df_combined,
        persona_dim_values=persona_dim_values,
        jsonl_profiles=jsonl_profiles,
        dim_to_key=dim_to_key,
        output_dir=OUTPUT_DIR,
    )

    print("\n" + "=" * 155)
    print(" [HOÀN TẤT] BẢNG THỐNG KÊ KÈM TOP 2 HÀNH ĐỘNG VÀ CÁC FILE CSV THUỘC TÍNH ĐÃ ĐƯỢC TẠO THÀNH CÔNG!")
    print("=" * 155)


if __name__ == "__main__":
    main()
