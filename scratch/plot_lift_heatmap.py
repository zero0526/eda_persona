import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Load tables
lift_p = pd.read_csv('output/tables/step5_behavior_lift_persona.csv', index_col=0)
lift_np = pd.read_csv('output/tables/step5_behavior_lift_nopersona.csv', index_col=0)

# Shorten column names for clean display
cols_short = [c.split('. ')[-1] for c in lift_p.columns]
phases_short = ['Q1 (Early)', 'Q2 (Mid-Early)', 'Q3 (Mid-Late)', 'Q4 (Late)']

df_p_plot = lift_p.copy()
df_p_plot.columns = cols_short
df_p_plot.index = phases_short

df_np_plot = lift_np.copy()
df_np_plot.columns = cols_short
df_np_plot.index = phases_short

# Set aesthetic styling
sns.set_theme(style='white', font='sans-serif')
fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

# Panel 1: Persona
sns.heatmap(
    df_p_plot,
    ax=axes[0],
    annot=True,
    fmt='.2f',
    cmap='Blues',
    vmin=0.0,
    vmax=3.5,
    cbar_kws={'label': 'Chỉ số Lift (Baseline = 1.0x)'},
    linewidths=1,
    linecolor='white'
)
axes[0].set_title('A. Heatmap Hệ số Vượt trội (Lift Ratio) theo Giai đoạn - Nhóm Có Persona', fontsize=13, fontweight='bold', pad=12)
axes[0].set_ylabel('Giai đoạn', fontsize=11, fontweight='bold')

# Panel 2: No-Persona
sns.heatmap(
    df_np_plot,
    ax=axes[1],
    annot=True,
    fmt='.2f',
    cmap='Reds',
    vmin=0.0,
    vmax=3.5,
    cbar_kws={'label': 'Chỉ số Lift (Baseline = 1.0x)'},
    linewidths=1,
    linecolor='white'
)
axes[1].set_title('B. Heatmap Hệ số Vượt trội (Lift Ratio) theo Giai đoạn - Nhóm Không Có Persona', fontsize=13, fontweight='bold', pad=12)
axes[1].set_ylabel('Giai đoạn', fontsize=11, fontweight='bold')
axes[1].set_xlabel('Nhóm Hành vi Cốt lõi (Macro-Behaviors)', fontsize=11, fontweight='bold')

plt.xticks(rotation=15, ha='right', fontsize=10)
plt.tight_layout()

out_fig = 'output/figures/step5_behavior_lift_heatmap.png'
plt.savefig(out_fig, dpi=300)
plt.close()
print(f'Successfully exported {out_fig}!')
