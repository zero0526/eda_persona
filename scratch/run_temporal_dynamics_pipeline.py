import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from loaders.loaders.persona_action import PersonaActionLoader
from algorithms.temporal_velocity_and_behavior_profiler import (
    compute_temporal_velocity_by_pace,
    compute_temporal_behavior_distribution,
)
from viz.temporal_dynamics_viz import plot_velocity_and_behavior_dynamics

# 1. Load data
loader = PersonaActionLoader()
df_steps = loader.load_step_records()

# 2. Compute velocity by pace dynamics
res_vel = compute_temporal_velocity_by_pace(df_steps)
df_processed = res_vel["df_processed"]
vel_by_group = res_vel["vel_by_group"]
vel_by_pace = res_vel["vel_by_pace"]
df_kw = res_vel["kruskal_wallis_by_phase"]
df_internal = res_vel["internal_pace_evolution"]

# 3. Compute behavior distribution dynamics
res_beh = compute_temporal_behavior_distribution(df_processed)
ct_p = res_beh["crosstab_persona"]
ct_np = res_beh["crosstab_nopersona"]
df_beh_comp = res_beh["behavior_comparison_table"]

# 4. Save tables
table_dir = project_root / "output" / "tables"
table_dir.mkdir(parents=True, exist_ok=True)

vel_by_pace.to_csv(table_dir / "step5_velocity_trajectory_by_pace.csv", index=False, encoding="utf-8-sig")
df_kw.to_csv(table_dir / "step5_velocity_kruskal_wallis_by_phase.csv", index=False, encoding="utf-8-sig")
df_internal.to_csv(table_dir / "step5_velocity_internal_pace_evolution.csv", index=False, encoding="utf-8-sig")
df_beh_comp.to_csv(table_dir / "step5_behavior_distribution_over_time.csv", index=False, encoding="utf-8-sig")
ct_p.to_csv(table_dir / "step5_behavior_crosstab_persona.csv", encoding="utf-8-sig")
ct_np.to_csv(table_dir / "step5_behavior_crosstab_nopersona.csv", encoding="utf-8-sig")

print("[✓] Đã xuất các bảng CSV phân tích thời gian vào output/tables/!")

# 5. Render figure
fig_dir = project_root / "output" / "figures"
fig_dir.mkdir(parents=True, exist_ok=True)
fig_path = fig_dir / "step5_velocity_and_behavior_temporal_dynamics.png"

plot_velocity_and_behavior_dynamics(
    df_processed=df_processed,
    vel_by_pace=vel_by_pace,
    ct_p=ct_p,
    ct_np=ct_np,
    output_path=fig_path
)

print(f"[✓] Đã lưu biểu đồ động lực học thời gian tại: {fig_path}")
