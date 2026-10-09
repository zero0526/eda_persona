import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Ensure UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR = PROJECT_ROOT / "output" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Styling configuration
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI', 'Liberation Sans']
plt.rcParams['axes.edgecolor'] = '#7f8c8d'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.color'] = '#ecf0f1'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

# 1. Prepare Data
data = {
    'Comment': [1.00, 0.54, 4.90, 0.00, 5.66, 0.49],
    'Warmth (Love/Care)': [0.00, 3.80, 0.27, 0.00, 0.47, 0.00],
    'Reels (Watch/Next)': [0.33, 24.46, 21.53, 83.50, 0.00, 0.00]
}
persona_ids = ['vn_fb_001', 'vn_fb_002', 'vn_fb_003', 'vn_fb_004', 'vn_fb_005', 'vn_fb_006']
persona_display = {
    'vn_fb_001': 'vn_fb_001 (Thiết kế)',
    'vn_fb_002': 'vn_fb_002 (Nội trợ / Phật giáo)',
    'vn_fb_003': 'vn_fb_003 (Bảo vệ ca trực)',
    'vn_fb_004': 'vn_fb_004 (Phục vụ / Gen Z)',
    'vn_fb_005': 'vn_fb_005 (Thợ cơ khí)',
    'vn_fb_006': 'vn_fb_006 (Kinh doanh BĐS)'
}

archetypes = {
    'vn_fb_001': ('Chuẩn mực Baseline', '#2980b9'),
    'vn_fb_002': ('Cảm xúc ấm áp', '#e84393'),
    'vn_fb_003': ('Đàm luận xã hội', '#27ae60'),
    'vn_fb_004': ('Tiêu thụ Video ngắn', '#e67e22'),
    'vn_fb_005': ('Đàm luận xã hội', '#27ae60'),
    'vn_fb_006': ('Chuẩn mực Baseline', '#2980b9'),
}

df = pd.DataFrame(data, index=persona_ids)

# 2. Fit PCA
scaler = StandardScaler()
scaled = scaler.fit_transform(df)

pca = PCA(n_components=3)
coords = pca.fit_transform(scaled)
coords_df = pd.DataFrame(coords, index=persona_ids, columns=['PC1', 'PC2', 'PC3'])
loadings = pd.DataFrame(pca.components_.T, index=df.columns, columns=['PC1', 'PC2', 'PC3'])

# 3. Create Figure - Single Focused Plot
fig, ax = plt.subplots(figsize=(13.5, 8.2))

# Draw Quadrant axes
ax.axhline(0, color='#95a5a6', linestyle=':', linewidth=1.5, alpha=0.8)
ax.axvline(0, color='#95a5a6', linestyle=':', linewidth=1.5, alpha=0.8)

# Draw Loading vectors (mũi tên định hướng hành vi)
arrow_scale = 2.15
for feat in df.columns:
    lx = loadings.loc[feat, 'PC1'] * arrow_scale
    ly = loadings.loc[feat, 'PC2'] * arrow_scale
    ax.annotate(
        '', xy=(lx, ly), xytext=(0, 0),
        arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=2.6, mutation_scale=22, alpha=0.9)
    )
    
    # Offset label for loading
    if feat == 'Comment':
        tx, ty = lx + 0.08, ly - 0.12
    elif feat == 'Warmth (Love/Care)':
        tx, ty = lx - 0.05, ly + 0.16
    else: # Reels
        tx, ty = lx - 0.18, ly + 0.16
        
    ax.text(tx, ty, f"Hướng: {feat}", fontsize=11.5, fontweight='bold', color='#16a085',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#e8f8f5', edgecolor='#1abc9c', linewidth=1.5, alpha=0.95))

# Plot Persona Points
for pid in persona_ids:
    arch_label, color = archetypes[pid]
    x = coords_df.loc[pid, 'PC1']
    y = coords_df.loc[pid, 'PC2']
    ax.scatter(x, y, color=color, s=360, edgecolor='#2c3e50', linewidth=2.0, zorder=6)
    
    label = persona_display[pid]
    if pid == 'vn_fb_004':
        ax.annotate(label, xy=(x, y), xytext=(x - 0.05, y - 0.28), fontsize=11, fontweight='bold',
                    color='#d35400', ha='center',
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor='#e67e22', linewidth=1.2, alpha=0.95))
    elif pid == 'vn_fb_002':
        ax.annotate(label, xy=(x, y), xytext=(x - 0.15, y + 0.22), fontsize=11, fontweight='bold',
                    color='#8e44ad', ha='right',
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor='#9b59b6', linewidth=1.2, alpha=0.95))
    elif pid == 'vn_fb_005':
        ax.annotate(label, xy=(x, y), xytext=(x + 0.12, y + 0.14), fontsize=11, fontweight='bold',
                    color='#27ae60', ha='left',
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor='#2ecc71', linewidth=1.2, alpha=0.95))
    elif pid == 'vn_fb_003':
        ax.annotate(label, xy=(x, y), xytext=(x + 0.12, y - 0.22), fontsize=11, fontweight='bold',
                    color='#27ae60', ha='left',
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor='#2ecc71', linewidth=1.2, alpha=0.95))
    elif pid == 'vn_fb_001':
        ax.annotate(label, xy=(x, y), xytext=(x - 0.05, y + 0.22), fontsize=10.2, fontweight='bold',
                    color='#2980b9', ha='center',
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor='#3498db', linewidth=1.2, alpha=0.9))
    elif pid == 'vn_fb_006':
        ax.annotate(label, xy=(x, y), xytext=(x - 0.05, y - 0.32), fontsize=10.2, fontweight='bold',
                    color='#2980b9', ha='center',
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor='#3498db', linewidth=1.2, alpha=0.9))

# Callout cluster boxes positioned cleanly without overlapping anything
# ax.text(1.8, 1.8, "CỤM 1: ĐÀM LUẬN XÃ HỘI\n(003: Bảo vệ, 005: Cơ khí)", fontsize=11, fontweight='bold', color='#27ae60',
#         ha='center', va='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#eafaf1', edgecolor='#2ecc71', linewidth=1.5, alpha=0.9))

# ax.text(-1.75, 1.3, "CỤM 2: CẢM XÚC ẤM ÁP\n(002: Chị nội trợ)", fontsize=11, fontweight='bold', color='#8e44ad',
#         ha='center', va='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#f4ecf7', edgecolor='#9b59b6', linewidth=1.5, alpha=0.9))

# ax.text(-1.5, -1.95, "CỤM 3: TIÊU THỤ REELS\n(004: Cậu phục vụ)", fontsize=11, fontweight='bold', color='#d35400',
#         ha='center', va='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#fef5e7', edgecolor='#e67e22', linewidth=1.5, alpha=0.9))

# ax.text(0.35, -0.68, "GỐC TỌA ĐỘ: CHUẨN MỰC BASELINE\n(001: Thiết kế, 006: Kinh doanh)", fontsize=10.5, fontweight='bold', color='#2980b9',
#         ha='left', va='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#ebf5fb', edgecolor='#3498db', linewidth=1.5, alpha=0.9))

ax.set_title("Bản đồ Chiếu Không gian Hành vi: Trực quan hóa Sự Phân tách 4 Nhóm Persona", fontsize=14, fontweight='bold', pad=16)
ax.set_xlabel("Trục Ngang: Xu hướng Đàm luận Xã hội (Gõ phím Comment & Share)", fontsize=12, fontweight='bold', labelpad=8)
ax.set_ylabel("Trục Dọc: Xu hướng Cảm xúc Ấm áp (Thả tim & Thương thương)", fontsize=12, fontweight='bold', labelpad=8)
ax.set_xlim(-2.5, 2.7)
ax.set_ylim(-2.3, 2.5)
ax.grid(True, alpha=0.45)

# Custom legend for Archetypes (Placed at top center/left where it's 100% free)
custom_handles = [
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#27ae60', markersize=11, label='Cụm Đàm luận xã hội (003, 005)'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#e84393', markersize=11, label='Cụm Cảm xúc ấm áp (002)'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#e67e22', markersize=11, label='Cụm Video ngắn Reels (004)'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#2980b9', markersize=11, label='Gốc tọa độ Chuẩn mực Baseline (001, 006)'),
]
ax.legend(handles=custom_handles, loc='upper center', bbox_to_anchor=(0.5, -0.10), frameon=True,
          facecolor='#ffffff', edgecolor='#bdc3c7', fontsize=10.2, ncol=2)

plt.tight_layout()
out_path = FIGURES_DIR / "slide2_2_2_pca_behavioral_space.png"
fig.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"Regenerated 100% clean plot: {out_path}")
