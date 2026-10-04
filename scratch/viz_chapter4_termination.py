import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.stdout.reconfigure(encoding='utf-8')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Segoe UI', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

# Ensure sys.path includes project root
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from loaders.loaders.persona_action import PersonaActionLoader
loader = PersonaActionLoader()

df_ep = pd.read_csv(project_root / "output" / "tables" / "step4_termination_profile.csv")
df_steps = loader.load_step_records()

df_steps['timestamp_dt'] = pd.to_datetime(df_steps['timestamp'])
df_steps['step_delta_sec'] = df_steps.groupby('episode_id')['timestamp_dt'].diff().dt.total_seconds()

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 1. Termination Causes (Subplot 1)
ax1 = axes[0]
ct_cause = pd.crosstab(df_ep['group'], df_ep['termination_cause'], normalize='index') * 100
colors_cause = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981']
ct_cause.plot(kind='bar', ax=ax1, color=colors_cause, edgecolor='black', linewidth=0.8)
ax1.set_title("1. Phân Phối Nguyên Nhân Kết Thúc Phiên (% Phiên)\n[Persona: 50% Tự dừng chủ động vs No-Persona: 100% Bế tắc]", fontsize=11, fontweight='bold', pad=10)
ax1.set_ylabel("Tỷ lệ phiên (%)", fontsize=10, fontweight='bold')
ax1.set_xlabel("")
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0, fontweight='bold')
ax1.legend(title="Nguyên nhân dừng", loc='upper right', frameon=True, fontsize=9)
ax1.grid(axis='y', linestyle='--', alpha=0.5)

# 2. Step Delta Seconds - Inter-action Latency (Subplot 2)
ax2 = axes[1]
valid_delta = df_steps.dropna(subset=['step_delta_sec'])
palette = {'persona': '#2b5c8f', 'no_persona': '#d95f02'}
sns.boxplot(
    data=valid_delta,
    x='dataset_type',
    y='step_delta_sec',
    hue='dataset_type',
    palette=palette,
    legend=False,
    ax=ax2,
    showmeans=True,
    meanprops={'marker': 'o', 'markerfacecolor': 'white', 'markeredgecolor': 'black', 'markersize': 8}
)
ax2.set_title("2. Nhịp Độ Thao Tác Giữa Hai Bước (Step Delta Seconds)\n[Persona: Ổn định ~8.9s vs No-Persona: Giật cục 4s hoặc đơ kẹt 24-63s]", fontsize=11, fontweight='bold', pad=10)
ax2.set_ylabel("Khoảng cách thời gian giữa 2 bước (giây)", fontsize=10, fontweight='bold')
ax2.set_xlabel("Nhóm khảo sát", fontsize=10, fontweight='bold')
ax2.set_xticks([0, 1])
ax2.set_xticklabels(['Persona (N=343 bước)', 'No-Persona (N=86 bước)'], fontweight='bold')
ax2.set_ylim(0, 70)
ax2.grid(axis='y', linestyle='--', alpha=0.5)

plt.suptitle("HỒ SƠ CẤP PHIÊN (CHƯƠNG 4.3): NGUYÊN NHÂN THOÁT PHIÊN & NHỊP ĐỘ TƯƠNG TÁC THỜI GIAN", fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()

out_fig = project_root / 'output' / 'figures' / 'step4_univariate_termination_and_surfaces.png'
plt.savefig(out_fig, dpi=300, bbox_inches='tight')
plt.close()
print("Saved 2-subplot termination profile figure to:", out_fig)
