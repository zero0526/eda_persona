import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import json
from pathlib import Path
import pandas as pd
import numpy as np

from loaders.loaders.persona_action import PersonaActionLoader

# Cấu hình hiển thị của pandas
pd.set_option("display.max_columns", 30)
pd.set_option("display.max_rows", 100)
pd.set_option("display.width", 1000)
pd.set_option("display.float_format", lambda x: f"{x:.2f}")


def load_benchmark_action_logs(source: str = "all"):
    """Nạp dữ liệu action logs thông qua PersonaActionLoader."""
    loader = PersonaActionLoader()
    df = loader.load_step_records(source=source if source in ("all", "persona", "no_persona") else "all")
    print(f"\n[+] Tổng số records action nạp được: {len(df)} dòng, {df.shape[1]} cột.")
    return df

def run_eda(df: pd.DataFrame):
    """
    Tiến hành phân tích EDA nhanh:
    1. Tổng quan các trường, kiểu dữ liệu, missing value, số giá trị duy nhất.
    2. Tập giá trị và phân phối của từng trường phân loại (categorical fields).
    3. Phân phối và thống kê mô tả của các trường số (numerical metrics).
    4. Phân tích chéo (Cross-analysis) giữa các thuộc tính quan trọng.
    """
    sep = "=" * 80
    sub_sep = "-" * 80

    print("\n" + sep)
    print("                      1. TỔNG QUAN VỀ DỮ LIỆU & CÁC TRƯỜNG")
    print(sep)
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"Phân bố dataset_type:\n{df['dataset_type'].value_counts().to_string()}")
    print(f"\nSố file: {df['file_name'].nunique()} | Số episode: {df['episode_id'].nunique()} | Số persona: {df['persona_id'].nunique()}")

    # Bảng tổng quan thông tin các trường
    field_summary = []
    for col in df.columns:
        null_count = df[col].isnull().sum()
        null_pct = (null_count / len(df)) * 100
        nunique = df[col].nunique(dropna=False)
        dtype = str(df[col].dtype)
        
        # Mẫu một vài giá trị đặc trưng
        sample_vals = df[col].dropna().unique()[:4].tolist()
        sample_str = str(sample_vals)
        if len(sample_str) > 45:
            sample_str = sample_str[:42] + "..."
            
        field_summary.append({
            "Field": col,
            "Type": dtype,
            "Non-Null": len(df) - null_count,
            "Null Count": null_count,
            "Null %": null_pct,
            "Unique": nunique,
            "Sample Values": sample_str
        })
    
    df_field_summary = pd.DataFrame(field_summary)
    print("\n[BẢNG TỔNG QUAN TẤT CẢ CÁC TRƯỜNG TRONG STEP RECORDS]:")
    print(df_field_summary.to_string(index=False))

    print("\n" + sep)
    print("             2. TẬP GIÁ TRỊ VÀ PHÂN PHỐI CÁC TRƯỜNG PHÂN LOẠI (CATEGORICAL)")
    print(sep)

    categorical_cols = [
        "tool",
        "resolved_tool",
        "intent",
        "surface",
        "reaction",
        "verified",
        "target_candidate_kind",
        "dimension_sources"
    ]

    for col in categorical_cols:
        print(f"\n>>> Trường '{col}' (Số lượng non-null: {df[col].notnull().sum()}, Missing: {df[col].isnull().sum()}):")
        counts = df[col].value_counts(dropna=False)
        pcts = df[col].value_counts(dropna=False, normalize=True) * 100
        dist_df = pd.DataFrame({"Count": counts, "Percent (%)": pcts})
        print(dist_df.to_string())

    print("\n" + sep)
    print("             3. PHÂN PHỐI CÁC TRƯỜNG SỐ ĐO (NUMERICAL METRICS)")
    print(sep)

    num_cols = ["model_latency_ms", "tool_execution_ms", "num_dimension_evidence", "step_index"]
    desc_df = df[num_cols].describe(percentiles=[0.25, 0.5, 0.75, 0.9, 0.95]).T
    desc_df["median"] = df[num_cols].median()
    print(desc_df[["count", "mean", "std", "min", "25%", "50%", "75%", "90%", "95%", "max"]].to_string())

    print("\n" + sep)
    print("             4. PHÂN TÍCH CHÉO & TƯƠNG QUAN HÀNH VI (CROSS ANALYSIS)")
    print(sep)

    print("\n>>> (A) Ma trận Tool vs Resolved Tool:")
    tool_ct = pd.crosstab(df["tool"].fillna("NULL"), df["resolved_tool"].fillna("NULL"), margins=True)
    print(tool_ct.to_string())

    print("\n>>> (B) Ma trận Intent vs Tool:")
    intent_tool_ct = pd.crosstab(df["intent"].fillna("NULL"), df["tool"].fillna("NULL"), margins=True)
    print(intent_tool_ct.to_string())

    print("\n>>> (C) Tỉ lệ Verified (thành công) theo từng Intent:")
    verified_intent = df.groupby("intent", dropna=False)["verified"].agg(
        total="count",
        verified_count=lambda x: (x == True).sum(),
        verified_rate=lambda x: (x == True).mean() * 100
    ).sort_values("total", ascending=False)
    print(verified_intent.to_string())

    print("\n>>> (D) So sánh Persona vs No-Persona về phân bố Intent:")
    dataset_intent = pd.crosstab(
        df["intent"].fillna("NULL"), 
        df["dataset_type"], 
        normalize="columns"
    ) * 100
    dataset_intent["Diff (P - NP)"] = dataset_intent.get("persona", 0) - dataset_intent.get("no_persona", 0)
    print(dataset_intent.sort_values("persona", ascending=False).to_string())

    print("\n>>> (E) So sánh Persona vs No-Persona về Tỉ lệ Verified & Latency trung bình:")
    comp_df = df.groupby("dataset_type").agg(
        total_steps=("step_index", "count"),
        verified_rate=("verified", lambda x: (x == True).mean() * 100),
        avg_model_latency_ms=("model_latency_ms", "mean"),
        median_model_latency_ms=("model_latency_ms", "median"),
        avg_tool_exec_ms=("tool_execution_ms", "mean"),
        median_tool_exec_ms=("tool_execution_ms", "median"),
        steps_with_dim=("num_dimension_evidence", lambda x: (x > 0).mean() * 100)
    )
    print(comp_df.to_string())

    print("\n" + sep)
    print("             5. PHÂN TÍCH CÁC TRƯỜNG TEXT (REASON & ACTION SUMMARY)")
    print(sep)
    print(f"Tổng số reason có nội dung: {df['reason'].notnull().sum()}")
    print("\nTop 5 lý do (reason) phổ biến nhất:")
    top_reasons = df["reason"].value_counts().head(5)
    for r, c in top_reasons.items():
        print(f"  [{c} lần] {r}")

    print("\nTop 5 action_summary phổ biến nhất:")
    top_summaries = df["action_summary"].value_counts().head(5)
    for s, c in top_summaries.items():
        print(f"  [{c} lần] {s}")

    print("\n" + sep)
    print("             6. PHÂN TÍCH BỘ NHỚ LÀM VIỆC (WORKING MEMORY DYNAMICS)")
    print(sep)
    wm_steps = df[df["has_working_memory"]]
    print(f"Số bước có working memory: {len(wm_steps)}/{len(df)} ({len(wm_steps)/len(df)*100:.1f}%)")

    print("\n>>> (A) Phân bố nguồn gốc mạch hiện tại (Current Thread Origin):")
    print(wm_steps["wm_current_thread_origin"].value_counts(dropna=False).to_string())

    print("\n>>> (B) Top 5 chủ đề đang tập trung nhiều nhất (Top Current Threads):")
    top_threads = wm_steps["wm_current_thread_topic"].value_counts().head(5)
    for th, c in top_threads.items():
        print(f"  [{c} steps] {th}")

    print("\n>>> (C) Thống kê tích luỹ nhận thức (Cumulative Reads / Searches / Opened):")
    wm_metrics = ["wm_num_active_threads", "wm_cumulative_searches", "wm_cumulative_reads", "wm_cumulative_opened"]
    print(wm_steps[wm_metrics].describe().T[["mean", "std", "min", "50%", "max"]].to_string())

    print("\n" + sep)
    print("   7. ĐỐI CHIẾU HỒ SƠ PERSONA VS HÀNH VI SESSION CONTEXT (REST, MEMORY, GESTURE)")
    print(sep)

    # 7.1 Dừng nghỉ (Rest)
    print("\n>>> (A) Phân tích Dừng Nghỉ (Rest) qua các Episode:")
    rest_summary = df.groupby(["episode_id", "persona_id", "persona_rest_style", "dataset_type"]).agg(
        total_steps=("step_index", "count"),
        steps_with_rest=("context_rest_count", lambda x: (x > 0).sum()),
        max_accumulated_rest_sec=("context_rest_accumulated_seconds", "max"),
        max_rest_count=("context_rest_count", "max")
    ).reset_index()
    print(rest_summary.to_string(index=False))

    # 7.2 Ký ức đa phiên (Cross-session Memory Queries)
    print("\n>>> (B) Khám phá Ký ức Đa Phiên (Cross-session Memory Queries):")
    mem_steps = df[df["context_has_memory_queries"]]
    print(f"Tổng số bước ghi nhận memory queries: {len(mem_steps)}/{len(df)} bước")
    if not mem_steps.empty:
        print(mem_steps[["episode_id", "persona_id", "step_index", "context_recent_queries_from_memory"]].head(10).to_string(index=False))
        unique_mem_queries = mem_steps["context_recent_queries_from_memory"].unique()
        print(f"Các queries từ ký ức phiên trước: {unique_mem_queries}")

    # 7.3 Cử chỉ cuộn chuột thực tế (Gesture Pacing)
    print("\n>>> (C) Đối chiếu Tốc độ Persona (pace) với Cử chỉ cuộn chuột thực tế:")
    loader = PersonaActionLoader()
    df_ra = loader.load_recent_actions(deduplicate=True)
    scroll_ra = df_ra[df_ra["intent"] == "scroll"].copy()

    if not scroll_ra.empty:
        gesture_comp = scroll_ra.groupby(["persona_id", "persona_pace", "gesture_pace"]).agg(
            total_scrolls=("sequence", "count"),
            avg_scroll_px=("gesture_total_px", "mean"),
            min_scroll_px=("gesture_total_px", "min"),
            max_scroll_px=("gesture_total_px", "max"),
            avg_gesture_ms=("gesture_ms", "mean"),
            min_gesture_ms=("gesture_ms", "min"),
            max_gesture_ms=("gesture_ms", "max")
        ).reset_index()
        print("\nBảng đối chiếu Persona Profile Pace vs Browser Scroll Gesture Metrics:")
        print(gesture_comp.to_string(index=False))

    print("\n" + sep)
    print("   8. VÉT SẠCH THÔNG TIN SESSION CONTEXT (REGEX: NOVELTY, VELOCITY, URL, MODES)")
    print(sep)

    df_ep = loader.load_action_logs()
    print("\n>>> (A) Vận tốc hành động (Action Velocity) & Cảnh báo phân tâm (Novelty Warning):")
    cols_ep = [
        "episode_id", "persona_id", "dataset_type", "action_velocity_per_minute",
        "max_situational_steps", "has_novelty_warning", "surfaces_visited_count",
        "wm_summary_run_minutes", "wm_summary_read_posts"
    ]
    print(df_ep[cols_ep].to_string(index=False))

    print("\n>>> (B) Phân phối các chế độ thực thi trên trình duyệt (Browser Execution Modes):")
    print(df_ra["execution_mode"].value_counts().to_string())

    print("\n>>> (C) Phân phối các loại URL được truy cập (URL Types extracted via Regex):")
    print(df_ra["url_type"].value_counts(dropna=False).to_string())

    print("\n>>> (D) Hành trình di chuyển bề mặt (Surface Journey) của từng phiên:")
    for _, r in df_ep.iterrows():
        pid_label = r['persona_id'] if pd.notnull(r['persona_id']) else "Neutral"
        print(f"  [{r['dataset_type']}] {pid_label} ({r['episode_id'][:8]}): {r['surface_journey']}")

    print("\n" + sep)
    print("   9. PHÂN TÍCH MA TRẬN NHẬN THỨC (DIMENSION EVIDENCE) & ĐỐI TƯỢNG ĐÍCH (TARGETS)")
    print(sep)

    df_dims = loader.load_dimension_evidences()
    print(f"\n>>> (A) Tổng số bản ghi bằng chứng nhận thức (Dimension Evidences): {len(df_dims)}")
    dim_role_ct = pd.crosstab(df_dims["dimension"], df_dims["role"], margins=True)
    print(dim_role_ct.to_string())

    print("\n>>> (B) Phân phối Trọng số (Weight) theo vai trò (Role):")
    print(df_dims.groupby("role")["weight"].describe()[["count", "mean", "std", "min", "50%", "max"]].to_string())

    df_cands = loader.load_target_candidates()
    print(f"\n>>> (C) Tổng số đối tượng mục tiêu tương tác (Target Candidates): {len(df_cands)}")
    print("Phân bố theo loại đối tượng (kind):")
    print(df_cands["kind"].value_counts().to_string())
    print("\nTop 5 đối tượng tương tác nổi bật nhất:")
    for idx, r in df_cands.head(5).iterrows():
        t_clean = r['text'].replace('\n', ' ') if pd.notnull(r['text']) else "None"
        if len(t_clean) > 80: t_clean = t_clean[:77] + "..."
        print(f"  [{r['kind']} | {r['intent']}] {t_clean} -> {r['url']}")

    print("\n>>> (D) Tỷ số Nhận thức (Cognitive Latency Ratio) giữa Persona vs No-Persona:")
    cog_comp = df.groupby("dataset_type").agg(
        avg_cog_ratio=("cognitive_latency_ratio", "mean"),
        median_cog_ratio=("cognitive_latency_ratio", "median"),
        avg_total_latency=("total_step_latency_ms", "mean")
    )
    print(cog_comp.to_string())

    print("\n" + sep)
    print("EDA HOÀN TẤT.")
    print(sep)

if __name__ == "__main__":
    df_actions = load_benchmark_action_logs("./data")
    run_eda(df_actions)
