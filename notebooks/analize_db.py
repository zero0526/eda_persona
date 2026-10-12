"""Thống kê Top 30 trường Bằng chứng nhận thức (decision_evidence) của từng Persona riêng biệt.

Kéo phẳng toàn bộ decision_evidence từ SQLite và lập bảng Top 30 trường (dimension)
cho mỗi Persona (vn_fb_001 -> vn_fb_006), hiển thị số lần, tỷ trọng %, và giá trị thường gặp.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import sys
import pandas as pd

# Thiết lập UTF-8 Console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 50)
pd.set_option("display.width", 1000)

PERSONA_LABELS = {
    "vn_fb_001": "vn_fb_001 (Thiết kế đồ họa, 26t, Nữ, Hybrid)",
    "vn_fb_002": "vn_fb_002 (Lao động phổ thông / Nông nghiệp, 42t, Nữ)",
    "vn_fb_003": "vn_fb_003 (Bảo vệ ca trực, 28t, Nam)",
    "vn_fb_004": "vn_fb_004 (Nhân viên nhà hàng, 22t, Nam)",
    "vn_fb_005": "vn_fb_005 (Thợ cơ khí, 31t, Nam)",
    "vn_fb_006": "vn_fb_006 (Kinh doanh BĐS, 52t, Nam)",
}

PERSONA_ORDER = ["vn_fb_001", "vn_fb_002", "vn_fb_003", "vn_fb_004", "vn_fb_005", "vn_fb_006"]


def find_database_path() -> Path:
    """Tìm đường dẫn SQLite database trong dự án."""
    candidates = [
        Path(__file__).resolve().parent.parent / "data" / "persona-runner.sqlite",
        Path("data/persona-runner.sqlite"),
        Path("persona-runner.sqlite"),
    ]
    for p in candidates:
        if p.is_file():
            return p.resolve()
    raise FileNotFoundError("Không tìm thấy cơ sở dữ liệu SQLite persona-runner.sqlite!")


def load_flattened_evidence(db_path: Path) -> pd.DataFrame:
    """Kéo phẳng toàn bộ evidence từ decision_evidence trong SQLite."""
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

    records = []
    for _, row in df_raw.iterrows():
        try:
            ev_list = json.loads(row["evidence_json"])
            if isinstance(ev_list, list):
                for item in ev_list:
                    dim = item.get("dimension")
                    if dim:
                        records.append({
                            "evidence_id": row["evidence_id"],
                            "episode_id": row["episode_id"],
                            "persona_id": row["persona_id"],
                            "step_index": row["step_index"],
                            "action": row["action"],
                            "dimension": str(dim).strip(),
                            "value": str(item.get("value", "")),
                            "weight": float(item.get("weight", 0.0)),
                            "role": str(item.get("role", "unknown"))
                        })
        except Exception:
            continue

    return pd.DataFrame(records)


def get_top_dimensions_for_persona(df_p: pd.DataFrame, top_n: int = 30) -> pd.DataFrame:
    """Thống kê top N trường evidence của riêng một persona."""
    total_p = len(df_p)
    if total_p == 0:
        return pd.DataFrame()

    def get_mode_val(s: pd.Series) -> str:
        s_clean = s[s != ""]
        if s_clean.empty:
            return ""
        mode = s_clean.mode()
        return mode.iloc[0] if not mode.empty else ""

    grouped = (
        df_p.groupby("dimension")
        .agg(
            so_lan=("dimension", "count"),
            ty_le_primary=("role", lambda r: round((r == "primary").mean() * 100, 1)),
            trong_so_tb=("weight", lambda w: round(w.mean(), 2)),
            gia_tri_thuong_gap=("value", get_mode_val),
        )
        .sort_values(by="so_lan", ascending=False)
    )

    grouped["ty_trong_%"] = (grouped["so_lan"] / total_p * 100).round(2)
    grouped["thu_hang"] = range(1, len(grouped) + 1)

    top_df = grouped.head(top_n).reset_index()
    top_df = top_df[[
        "thu_hang",
        "dimension",
        "so_lan",
        "ty_trong_%",
        "gia_tri_thuong_gap",
        "ty_le_primary",
        "trong_so_tb",
    ]]
    return top_df


def main():
    db_path = find_database_path()
    print(f"[*] Đang nạp cơ sở dữ liệu: {db_path}")

    df_evidence = load_flattened_evidence(db_path)
    output_dir = Path(__file__).resolve().parent.parent / "output" / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)

    all_top_dfs = []

    for p_id in PERSONA_ORDER:
        label = PERSONA_LABELS.get(p_id, p_id)
        df_p = df_evidence[df_evidence["persona_id"] == p_id]
        tot_p = len(df_p)
        n_dims = df_p["dimension"].nunique()

        print("\n" + "=" * 105)
        print(f" TOP 30 TRƯỜNG EVIDENCE CỦA {label.upper()} (TỔNG EVIDENCE: {tot_p} | SỐ TRƯỜNG: {n_dims})")
        print("=" * 105)

        top30_p = get_top_dimensions_for_persona(df_p, top_n=30)
        print(top30_p.to_string(index=False))

        # Lưu CSV từng persona
        csv_p = output_dir / f"top30_evidence_{p_id}.csv"
        top30_p.to_csv(csv_p, index=False, encoding="utf-8-sig")
        print(f"[✓] Đã lưu file: {csv_p}")

        # Thêm cột persona_id để lưu bảng tổng hợp
        top30_p_copy = top30_p.copy()
        top30_p_copy.insert(0, "persona_id", p_id)
        all_top_dfs.append(top30_p_copy)

    # Lưu bảng tổng hợp tất cả top 30
    df_combined = pd.concat(all_top_dfs, ignore_index=True)
    combined_csv = output_dir / "top30_evidence_all_personas.csv"
    df_combined.to_csv(combined_csv, index=False, encoding="utf-8-sig")
    print(f"\n[✓] Đã lưu file tổng hợp tất cả Persona: {combined_csv}")


if __name__ == "__main__":
    main()
