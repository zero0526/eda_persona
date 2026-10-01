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

from scratch.compute_chapter4_profile import get_chapter4_univariate_tables

df_ep, df_st = get_chapter4_univariate_tables()

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Termination Causes (Subplot 1)
ax1 = axes[0, 0]
ct_cause = pd.crosstab(df_ep['group'], df_ep['termination_cause'], normalize='index') * 100
colors_cause = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6']
ct_cause.plot(kind='bar', ax=ax1, color=colors_cause, edgecolor='black', linewidth=0.8)
ax1.set_title("1. Phân Phối Nguyên Nhân Kết Thúc Phiên (%)", fontsize=12, fontweight='bold', pad=10)
ax1.set_ylabel("Tỷ lệ phiên (%)", fontsize=11, fontweight='bold')
ax1.set_xlabel("")
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0, fontweight='bold')
ax1.legend(title="Nguyên nhân", loc='upper right', frameon=True, fontsize=9)
ax1.grid(axis='y', linestyle='--', alpha=0.5)

# 2. Yield at Exit: Reads & Searches (Subplot 2)
ax2 = axes[0, 1]
yield_df = df_ep.groupby('group')[['reads_at_exit', 'searches_at_exit', 'opened_at_exit']].mean()
yield_df.columns = ['Số bài đọc', 'Số chủ đề tìm kiếm', 'Số nguồn mở']
yield_df.plot(kind='bar', ax=ax2, color=['#10b981', '#6366f1', '#ec4899'], edgecolor='black', linewidth=0.8)
ax2.set_title("2. Sản Lượng Tri Nhận Trung Bình Khi Thoát Phiên", fontsize=12, fontweight='bold', pad=10)
ax2.set_ylabel("Số lượng trung bình / phiên", fontsize=11, fontweight='bold')
ax2.set_xlabel("")
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0, fontweight='bold')
ax2.legend(loc='upper left', frameon=True, fontsize=10)
ax2.grid(axis='y', linestyle='--', alpha=0.5)

# 3. Surface Distribution (Subplot 3)
ax3 = axes[1, 0]
surf_order = ['feed', 'detail', 'group', 'page', 'search', 'unknown']
ct_surf = pd.crosstab(df_st['group'], df_st['surface'], normalize='index') * 100
for col in surf_order:
    if col not in ct_surf.columns:
        ct_surf[col] = 0.0
ct_surf = ct_surf[surf_order]
colors_surf = ['#3b82f6', '#f43f5e', '#8b5cf6', '#10b981', '#f59e0b', '#94a3b8']
ct_surf.plot(kind='bar', ax=ax3, color=colors_surf, edgecolor='black', linewidth=0.8)
ax3.set_title("3. Phân Phối Không Gian Giao Diện (Surface Distribution, %)", fontsize=12, fontweight='bold', pad=10)
ax3.set_ylabel("Tỷ lệ số bước (%)", fontsize=11, fontweight='bold')
ax3.set_xlabel("")
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=0, fontweight='bold')
ax3.legend(title="Surface", loc='upper right', frameon=True, fontsize=9)
ax3.grid(axis='y', linestyle='--', alpha=0.5)

# 4. Verified Action Status (Subplot 4)
ax4 = axes[1, 1]
ct_ver = pd.crosstab(df_st['group'], df_st['verified'], normalize='index') * 100
colors_ver = ['#ef4444', '#10b981']
ct_ver.columns = ['False (Thất bại / Lỗi)', 'True (Thành công)']
ct_ver.plot(kind='bar', stacked=True, ax=ax4, color=colors_ver, edgecolor='black', linewidth=0.8)
ax4.set_title("4. Tỷ Lệ Hành Động Được Kiểm Chứng Thành Công (Verified, %)", fontsize=12, fontweight='bold', pad=10)
ax4.set_ylabel("Tỷ lệ số bước (%)", fontsize=11, fontweight='bold')
ax4.set_xlabel("")
ax4.set_xticklabels(ax4.get_xticklabels(), rotation=0, fontweight='bold')
ax4.legend(loc='lower left', frameon=True, fontsize=10)
ax4.grid(axis='y', linestyle='--', alpha=0.5)

plt.suptitle("HỒ SƠ ĐƠN BIẾN MỞ RỘNG (CHƯƠNG 4): THOÁT PHIÊN, KHÔNG GIAN GIAO DIỆN & TÍNH KHẢ DỤNG", fontsize=14, fontweight='bold', y=0.99)
plt.tight_layout()

out_fig = Path('output/figures/step4_univariate_termination_and_surfaces.png')
plt.savefig(out_fig, dpi=300, bbox_inches='tight')
plt.close()
print("Saved figure to:", out_fig)
