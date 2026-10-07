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

PERSONA_PALETTE = {
    'vn_fb_001': '#1f77b4',
    'vn_fb_002': '#ff7f0e',
    'vn_fb_003': '#2ca02c',
    'vn_fb_004': '#d62728',
    'vn_fb_005': '#9467bd',
    'vn_fb_006': '#8c564b',
}

fig, axes = plt.subplots(1, 3, figsize=(18, 5.2), dpi=120)

# --- Subplot 1: Giờ bắt đầu phiên (24h) ---
ax1 = axes[0]
sns.histplot(df_w['start_hour_local'], bins=16, kde=True, color='#2b5c8f', ax=ax1, stat='density', alpha=0.45)
# Phân vùng các ca
ax1.axvspan(6, 11, color='#ffeaa7', alpha=0.25, label='Sáng (6-11h)')
ax1.axvspan(11, 14, color='#fab1a0', alpha=0.25, label='Trưa (11-14h)')
ax1.axvspan(14, 18, color='#55efc4', alpha=0.2, label='Chiều (14-18h)')
ax1.axvspan(18, 23, color='#74b9ff', alpha=0.2, label='Tối (18-23h)')

ax1.axvline(df_w['start_hour_local'].median(), color='#d63031', linestyle='--', linewidth=1.8, label=f"Median ({df_w['start_hour_local'].median():.1f}h)")
ax1.set_title("Phân phối Giờ bắt đầu phiên (start_hour_local)\nKèm 4 ca sinh hoạt chính trong ngày (UTC+7)", fontsize=11, fontweight='bold')
ax1.set_xlabel("Giờ trong ngày (Local Hour UTC+7)", fontsize=10)
ax1.set_ylabel("Mật độ xác suất (Density)", fontsize=10)
ax1.set_xlim(5, 24)
ax1.legend(loc='upper right', fontsize=8.5)

# --- Subplot 2: Thời lượng phiên theo Persona (Boxplot) ---
ax2 = axes[1]
sns.boxplot(data=df_w, x='persona_id', y='duration_min', palette=PERSONA_PALETTE, ax=ax2, width=0.55, boxprops=dict(alpha=0.75))
sns.stripplot(data=df_w, x='persona_id', y='duration_min', color='#2d3436', size=4.5, jitter=0.2, ax=ax2, alpha=0.6)
ax2.axhline(8, color='#d63031', linestyle=':', linewidth=1.5, label='Biên dưới hợp đồng (8m)')
ax2.axhline(32, color='#d63031', linestyle='--', linewidth=1.5, label='Biên trên hợp đồng (32m)')
ax2.set_title("Phân phối Thời lượng phiên (duration_min)\nĐối soát giới hạn hợp đồng [8, 32] phút theo Persona", fontsize=11, fontweight='bold')
ax2.set_xlabel("Persona ID", fontsize=10)
ax2.set_ylabel("Thời lượng (Phút)", fontsize=10)
ax2.set_ylim(4, 38)
ax2.legend(loc='upper left', fontsize=8.5)

# --- Subplot 3: Tần suất phiên mỗi ngày ---
ax3 = axes[2]
sns.barplot(data=wpd, x='persona_id', y='daily_windows', palette=PERSONA_PALETTE, ax=ax3, ci=None, alpha=0.85)
# Thêm nhãn giá trị trung bình trên đầu cột
means = wpd.groupby('persona_id')['daily_windows'].mean()
for i, (pid, m) in enumerate(means.items()):
    ax3.text(i, m + 0.06, f"{m:.2f}", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#2d3436')

ax3.axhline(wpd['daily_windows'].mean(), color='#636e72', linestyle='--', linewidth=1.2, label=f"TB Toàn hệ thống ({wpd['daily_windows'].mean():.2f}/ngày)")
ax3.set_title("Tần suất phiên trung bình mỗi ngày\nSố lượng windows/ngày theo từng Persona", fontsize=11, fontweight='bold')
ax3.set_xlabel("Persona ID", fontsize=10)
ax3.set_ylabel("Số phiên / ngày", fontsize=10)
ax3.set_ylim(0, 3.5)
ax3.legend(loc='lower right', fontsize=8.5)

plt.tight_layout()
plt.savefig("scratch/temporal_distributions.png")
print("Saved plot to scratch/temporal_distributions.png successfully!")
