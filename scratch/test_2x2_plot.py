import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sys.stdout.reconfigure(encoding='utf-8')
from loaders.action_loader import ActionLoader

loader = ActionLoader()
df_w = loader.load_activity_windows()
wpd = df_w.groupby(['persona_id', 'local_date']).size().reset_index(name='daily_windows')

# Tính khoảng cách giữa các cửa sổ liên tiếp của cùng 1 Persona
df_w_sorted = df_w.sort_values(by=['persona_id', 'start_at']).copy()
df_w_sorted['start_dt'] = pd.to_datetime(df_w_sorted['start_at'])
df_w_sorted['gap_hours'] = df_w_sorted.groupby('persona_id')['start_dt'].diff().dt.total_seconds() / 3600.0

PERSONA_PALETTE = {
    'vn_fb_001': '#1f77b4',
    'vn_fb_002': '#ff7f0e',
    'vn_fb_003': '#2ca02c',
    'vn_fb_004': '#d62728',
    'vn_fb_005': '#9467bd',
    'vn_fb_006': '#8c564b',
}

fig, axes = plt.subplots(2, 2, figsize=(16, 9.5), dpi=120)

# --- (0,0): Giờ bắt đầu phiên ---
ax1 = axes[0, 0]
sns.histplot(df_w['start_hour_local'], bins=16, kde=True, color='#2b5c8f', ax=ax1, stat='density', alpha=0.45)
ax1.axvspan(6, 11, color='#ffeaa7', alpha=0.25, label='Sáng (6-11h)')
ax1.axvspan(11, 14, color='#fab1a0', alpha=0.25, label='Trưa (11-14h)')
ax1.axvspan(14, 18, color='#55efc4', alpha=0.2, label='Chiều (14-18h)')
ax1.axvspan(18, 23, color='#74b9ff', alpha=0.2, label='Tối (18-23h)')
med_h = float(df_w['start_hour_local'].median())
ax1.axvline(med_h, color='#d63031', linestyle='--', linewidth=1.8, label=f"Median ({med_h:.1f}h)")
ax1.set_title("1. Phân phối Giờ bắt đầu phiên (start_hour_local)\nKèm 4 ca sinh hoạt chính trong ngày (UTC+7)", fontsize=11, fontweight='bold')
ax1.set_xlabel("Giờ trong ngày (Local Hour UTC+7)", fontsize=10)
ax1.set_ylabel("Mật độ xác suất (Density)", fontsize=10)
ax1.set_xlim(5, 24)
ax1.legend(loc='upper right', fontsize=8.5)

# --- (0,1): Thời lượng phiên ---
ax2 = axes[0, 1]
sns.boxplot(data=df_w, x='persona_id', y='duration_min', hue='persona_id', palette=PERSONA_PALETTE, legend=False, ax=ax2, width=0.55, boxprops=dict(alpha=0.75))
sns.stripplot(data=df_w, x='persona_id', y='duration_min', color='#2d3436', size=4.5, jitter=0.2, ax=ax2, alpha=0.6)
ax2.axhline(8, color='#d63031', linestyle=':', linewidth=1.5, label='Biên dưới (8m)')
ax2.axhline(32, color='#d63031', linestyle='--', linewidth=1.5, label='Biên trên (32m)')
ax2.set_title("2. Phân phối Thời lượng phiên (duration_min)\nGiới hạn [8, 32] phút theo Persona", fontsize=11, fontweight='bold')
ax2.set_xlabel("Persona ID", fontsize=10)
ax2.set_ylabel("Thời lượng (Phút)", fontsize=10)
ax2.set_ylim(4, 38)
ax2.legend(loc='upper left', fontsize=8.5)

# --- (1,0): Tần suất phiên mỗi ngày ---
ax3 = axes[1, 0]
sns.barplot(data=wpd, x='persona_id', y='daily_windows', hue='persona_id', palette=PERSONA_PALETTE, legend=False, ax=ax3, errorbar=None, alpha=0.85)
means = wpd.groupby('persona_id')['daily_windows'].mean()
for i, (pid, m) in enumerate(means.items()):
    ax3.text(i, m + 0.06, f"{m:.2f}", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#2d3436')
mean_all = float(wpd['daily_windows'].mean())
ax3.axhline(mean_all, color='#636e72', linestyle='--', linewidth=1.2, label=f"TB Toàn hệ thống ({mean_all:.2f}/ngày)")
ax3.set_title("3. Tần suất phiên trung bình mỗi ngày\nSố lượng windows/ngày theo từng Persona", fontsize=11, fontweight='bold')
ax3.set_xlabel("Persona ID", fontsize=10)
ax3.set_ylabel("Số phiên / ngày", fontsize=10)
ax3.set_ylim(0, 3.5)
ax3.legend(loc='lower right', fontsize=8.5)

# --- (1,1): Khoảng cách giữa các lần thực thi liên tiếp ---
ax4 = axes[1, 1]
valid_gaps = df_w_sorted.dropna(subset=['gap_hours'])
sns.boxplot(data=valid_gaps, x='persona_id', y='gap_hours', hue='persona_id', palette=PERSONA_PALETTE, legend=False, ax=ax4, width=0.55, boxprops=dict(alpha=0.75))
sns.stripplot(data=valid_gaps, x='persona_id', y='gap_hours', color='#2d3436', size=4.5, jitter=0.2, ax=ax4, alpha=0.6)
med_gap = float(valid_gaps['gap_hours'].median())
mean_gap = float(valid_gaps['gap_hours'].mean())
ax4.axhline(med_gap, color='#e17055', linestyle='--', linewidth=1.5, label=f"Median toàn hệ thống ({med_gap:.1f}h)")
ax4.axhline(24, color='#b2bec3', linestyle=':', linewidth=1.2, label="Khoảng cách 24h (1 ngày)")
ax4.set_title("4. Khoảng cách giữa các lần thực thi liên tiếp (gap_hours)\nThời gian giữa 2 phiên kế tiếp của cùng Persona (Giờ)", fontsize=11, fontweight='bold')
ax4.set_xlabel("Persona ID", fontsize=10)
ax4.set_ylabel("Khoảng cách (Giờ)", fontsize=10)
ax4.set_ylim(-1, 40)
ax4.legend(loc='upper right', fontsize=8.5)

plt.tight_layout()
plt.savefig("scratch/temporal_2x2.png")
print("Saved 2x2 plot to scratch/temporal_2x2.png!")
