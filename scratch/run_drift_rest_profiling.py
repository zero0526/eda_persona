import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from loaders.loaders.persona_action import PersonaActionLoader
from algorithms.drift_and_rest_statistical_profiler import (
    evaluate_temporal_drift_trajectory,
    evaluate_guardrail_warning_recovery,
    evaluate_rest_fatigue_dynamics,
    run_full_statistical_investigation
)

loader = PersonaActionLoader()
df_steps = loader.load_step_records()
df_ep = loader.load_action_logs()

tables_dir = project_root / "output" / "tables"
figures_dir = project_root / "output" / "figures"
tables_dir.mkdir(parents=True, exist_ok=True)
figures_dir.mkdir(parents=True, exist_ok=True)

# 1. Chạy thuật toán
results = run_full_statistical_investigation(df_steps, df_ep)

# 2. Xuất bảng kết quả CSV
df_drift_ep = results["drift_trajectory"]["episode_drift_table"]
df_drift_ep.to_csv(tables_dir / "step4_drift_trajectory_and_onset.csv", index=False, encoding="utf-8-sig")
print("Saved:", tables_dir / "step4_drift_trajectory_and_onset.csv")

df_warn_cross = results["guardrail_recovery"]["crosstab_warning_recovery"]
df_warn_cross.to_csv(tables_dir / "step4_guardrail_recovery_matrix.csv", encoding="utf-8-sig")
print("Saved:", tables_dir / "step4_guardrail_recovery_matrix.csv")

df_pre_post = results["rest_dynamics"]["pre_post_table"]
df_pre_post.to_csv(tables_dir / "step4_rest_dynamics_pre_post_evaluation.csv", index=False, encoding="utf-8-sig")
print("Saved:", tables_dir / "step4_rest_dynamics_pre_post_evaluation.csv")

# 3. Vẽ biểu đồ trực quan hóa
sns.set_theme(style="whitegrid", font_scale=1.0)
fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# Subplot 1: Drift Trajectory & Guardrail Warnings
ax1 = axes[0]
palette = {"no_persona": "#d9534f", "persona": "#2b6cb0"}

for ep_id, ep_df in df_steps.groupby("episode_id"):
    sub = ep_df.sort_values("step_index")
    dtype = sub["dataset_type"].iloc[0]
    color = palette[dtype]
    label = f"No-Persona ({ep_id[:6]})" if dtype == "no_persona" else ("Persona (6 episodes)" if ep_id == df_steps[df_steps["dataset_type"]=="persona"]["episode_id"].iloc[0] else None)
    ax1.plot(sub["step_index"], sub["wm_situational_steps"], marker="o", markersize=4, alpha=0.7, color=color, label=label, linewidth=1.8 if dtype=="no_persona" else 1.0)

# Đánh dấu các bước có Warning
warn_steps = df_steps[(df_steps["wm_has_novelty_warning"] == True) & (df_steps["dataset_type"] == "no_persona")]
ax1.scatter(warn_steps["step_index"], warn_steps["wm_situational_steps"] + 0.15, marker="^", color="#d9534f", s=80, zorder=5, label="Guardrail Warning (Cảnh báo tiết chế)")

ax1.set_title("Quỹ đạo Thời gian của Sa đà Nhận thức (Cognitive Drift) & Hiệu lực Guardrail", fontsize=13, fontweight="bold", pad=10)
ax1.set_xlabel("Chỉ số bước hành động (step_index)", fontsize=11)
ax1.set_ylabel("Số bước sa đà (wm_situational_steps)", fontsize=11)
ax1.set_ylim(-0.5, 7.0)
ax1.axhline(6, color="#c0392b", linestyle="--", alpha=0.5, label="Ngưỡng sa đà bão hòa tối đa (6 bước)")
ax1.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.9)

# Subplot 2: Rest & Fatigue in Persona Episode
ax2 = axes[1]
p_ep_rest = df_steps[df_steps["episode_id"] == "2cbcde75-15d8-4223-a1a3-22c69aca9b6d"].sort_values("step_index")
ax2.plot(p_ep_rest["step_index"], p_ep_rest["context_action_velocity"], color="#2b6cb0", marker="s", markersize=4, label="Vận tốc thao tác (hành động/phút)", linewidth=2)
ax2.axvline(30, color="#27ae60", linestyle="--", linewidth=2, label="Thời điểm nghỉ 120s (Step 30, t = 436s)")

# Fill vùng nghỉ
ax2.axvspan(30, 53, color="#2ecc71", alpha=0.15, label="Giai đoạn sau nghỉ (Vận tốc ổn định hơn, p=4.08e-06)")

ax2.set_title("Động lực học Dừng nghỉ (Rest & Fatigue Dynamics) trong Phiên Persona vn_000081", fontsize=13, fontweight="bold", pad=10)
ax2.set_xlabel("Chỉ số bước hành động (step_index)", fontsize=11)
ax2.set_ylabel("Vận tốc hành động (hành động/phút)", fontsize=11)
ax2.legend(loc="lower right", frameon=True, facecolor="white", framealpha=0.9)

plt.tight_layout()
fig_path = figures_dir / "step4_drift_and_rest_deep_dive.png"
plt.savefig(fig_path, dpi=300)
plt.close()
print("Saved Figure:", fig_path)

print("\n--- TỔNG KẾT KẾT QUẢ THỐNG KÊ ---")
print("1. Drift Trajectory:")
for k, v in results["drift_trajectory"]["summary_statistics"].items():
    print(f"  {k}: {v}")

print("\n2. Guardrail Recovery:")
for k, v in results["guardrail_recovery"]["summary"].items():
    print(f"  {k}: {v}")

print("\n3. Rest Dynamics:")
for k, v in results["rest_dynamics"]["summary"].items():
    print(f"  {k}: {v}")
