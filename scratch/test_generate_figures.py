import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import linkage, dendrogram, cophenet, fcluster
from scipy.spatial.distance import pdist

sys.stdout.reconfigure(encoding='utf-8')

# Style config
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI']
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['grid.color'] = '#f1f5f9'

# 1. Load data
json_path = Path("data/original_facebook_persona.json")
with open(json_path, "r", encoding="utf-8") as f:
    raw_personas = json.load(f)

extracted_rows = []
for p in raw_personas:
    pid = p.get("persona_id") or p.get("id")
    fb = p.get("facebook_behavior_profile", {})
    comm = fb.get("communication", {})
    beh = fb.get("facebookBehavior", {})
    usage = fb.get("usage", {})
    inte = fb.get("interests", {})
    
    extracted_rows.append({
        "persona_id": pid,
        "directness": comm.get("directness"),
        "emoji_use": comm.get("emojiUse"),
        "register": comm.get("register"),
        "tone": comm.get("tone"),
        "pace": beh.get("pace"),
        "reading_depth": beh.get("readingDepth"),
        "preferred_surface": beh.get("preferredSurface"),
        "rest_style": beh.get("restStyle"),
        "discovery_style": beh.get("discoveryStyle"),
        "attention": usage.get("attention"),
        "energy": usage.get("energy"),
        "engagement_style": usage.get("engagementStyle"),
        "fb_frequency": usage.get("facebookFrequency"),
        "num_strong_interests": len(inte.get("strong", [])),
        "num_avoid_interests": len(inte.get("avoid", [])),
    })

df_extracted = pd.DataFrame(extracted_rows)

pace_map = {'slow': 1, 'balanced': 2, 'quick': 3}
att_map = {'Very short': 1, 'Short': 2, 'medium': 3, 'Long': 4, 'Very long': 5}
depth_map = {'skim': 1, 'selective': 2}
freq_map = {'Rarely': 1, 'Monthly': 2, 'Weekly': 3, 'Daily': 4}
surf_map = {'feed': 0, 'mixed': 1}
energy_map = {'Low': 1, 'medium': 2}
rest_map = {'continuous': 1, 'occasional': 2, 'periodic': 3}

df_num = pd.DataFrame({
    'persona_id': df_extracted['persona_id'],
    'Pace': df_extracted['pace'].map(pace_map),
    'Attention_Span': df_extracted['attention'].map(att_map),
    'Reading_Depth': df_extracted['reading_depth'].map(depth_map),
    'FB_Frequency': df_extracted['fb_frequency'].map(freq_map),
    'Mixed_Surface': df_extracted['preferred_surface'].map(surf_map),
    'Energy_Level': df_extracted['energy'].map(energy_map),
    'Rest_Style': df_extracted['rest_style'].map(rest_map)
}).set_index('persona_id')

out_figs = Path("output/figures")
out_figs.mkdir(parents=True, exist_ok=True)

# Figure 1: Correlation Heatmap
corr = df_num.corr()
fig, ax = plt.subplots(figsize=(8, 6.5), dpi=300)
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
cmap = sns.diverging_palette(230, 20, as_cmap=True)
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1,
            center=0, square=True, linewidths=1.2, cbar_kws={"shrink": .8, "label": "Hệ số tương quan Pearson (r)"}, ax=ax)
ax.set_title("Ma trận Tương quan Tuyến tính giữa các Thuộc tính Hồ sơ Hành vi", fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
fig.savefig(out_figs / "step6_persona_correlation_heatmap.png", bbox_inches='tight')
plt.close(fig)
print("Fig 1 saved.")

# PCA & Ward Linkage
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_num)
pca = PCA()
X_pca = pca.fit_transform(X_scaled)
var_exp = pca.explained_variance_ratio_
cum_var = np.cumsum(var_exp)

dist_matrix = pdist(X_scaled, metric='euclidean')
Z = linkage(dist_matrix, method='ward')
coph_corr, _ = cophenet(Z, dist_matrix)
clusters = fcluster(Z, t=3, criterion='maxclust')

# Figure 2: Scree Plot & PCA Biplot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

# Panel A: Scree Plot
bars = ax1.bar(range(1, len(var_exp)+1), var_exp * 100, color='#3b82f6', alpha=0.85, label='Phương sai từng thành phần (%)', edgecolor='#1d4ed8')
line = ax1.plot(range(1, len(cum_var)+1), cum_var * 100, color='#ef4444', marker='o', linewidth=2.5, label='Phương sai tích lũy (%)')
ax1.axhline(80, color='#10b981', linestyle='--', linewidth=1.5, label='Ngưỡng thông tin 80%')
ax1.set_xlabel('Thành phần chính (Principal Component)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Tỷ lệ phương sai (%)', fontsize=11, fontweight='bold')
ax1.set_title('A. Scree Plot: Tỷ lệ Phương sai Giải thích (PCA)', fontsize=12, fontweight='bold', pad=10)
ax1.set_xticks(range(1, len(var_exp)+1))
ax1.set_xticklabels([f'PC{i}' for i in range(1, len(var_exp)+1)])
ax1.set_ylim(0, 110)
for bar in bars:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, yval + 1.5, f"{yval:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')
for i, val in enumerate(cum_var):
    ax1.text(i+1, val*100 + 2.5, f"{val*100:.1f}%", ha='center', va='bottom', fontsize=9, color='#b91c1c', fontweight='bold')
ax1.legend(loc='center right', frameon=True, facecolor='white', framealpha=0.9)

# Panel B: Biplot
cluster_colors = {1: '#ef4444', 2: '#3b82f6', 3: '#10b981'}
cluster_names = {1: 'Cụm 1: Fast Skim / Daily', 2: 'Cụm 2: Deep Reader / Feed Focus', 3: 'Cụm 3: Deliberate / Infrequent'}

for c_id in [1, 2, 3]:
    mask = (clusters == c_id)
    ax2.scatter(X_pca[mask, 0], X_pca[mask, 1], c=cluster_colors[c_id], label=cluster_names[c_id], s=180, edgecolors='black', linewidth=1.5, zorder=5)

for i, pid in enumerate(df_num.index):
    offset_x = 0.15 if X_pca[i, 0] >= 0 else -0.15
    ha = 'left' if X_pca[i, 0] >= 0 else 'right'
    ax2.annotate(pid, (X_pca[i, 0] + offset_x, X_pca[i, 1] + 0.1), fontsize=10, fontweight='bold', color='#1e293b', ha=ha, zorder=6)

# Vector loadings
loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
scale_factor = 2.2
for j, feat in enumerate(df_num.columns):
    vx = loadings[j, 0] * scale_factor
    vy = loadings[j, 1] * scale_factor
    ax2.arrow(0, 0, vx, vy, color='#64748b', alpha=0.7, width=0.03, head_width=0.15, zorder=3)
    ax2.text(vx * 1.15, vy * 1.15, feat, color='#334155', fontsize=8.5, fontweight='semibold', ha='center', va='center', zorder=4)

ax2.axhline(0, color='#94a3b8', linestyle=':', linewidth=1)
ax2.axvline(0, color='#94a3b8', linestyle=':', linewidth=1)
ax2.set_xlabel(f'PC1 ({var_exp[0]*100:.1f}% Phương sai - Trục Nhận thức & Chiều sâu)', fontsize=11, fontweight='bold')
ax2.set_ylabel(f'PC2 ({var_exp[1]*100:.1f}% Phương sai - Trục Tần suất & Khám phá)', fontsize=11, fontweight='bold')
ax2.set_title('B. PCA Biplot: Chiếu 6 Persona & Vector Tải Thuộc tính', fontsize=12, fontweight='bold', pad=10)
ax2.legend(loc='lower left', frameon=True, facecolor='white', framealpha=0.9, fontsize=9)

plt.tight_layout()
fig.savefig(out_figs / "step6_persona_pca_scree_biplot.png", bbox_inches='tight')
plt.close(fig)
print("Fig 2 saved.")

# Figure 3: Dendrogram
fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
dend = dendrogram(
    Z,
    labels=df_num.index.tolist(),
    ax=ax,
    color_threshold=3.5,
    above_threshold_color='#64748b'
)
ax.axhline(3.5, color='#ef4444', linestyle='--', linewidth=1.5, label='Đường cắt 3 cụm tối ưu (Distance threshold = 3.5)')
ax.set_title(f'Cây Phân Cấp Hành Vi Persona (Ward Linkage - Cophenetic r = {coph_corr:.4f})', fontsize=12, fontweight='bold', pad=15)
ax.set_ylabel('Khoảng cách Euclidean Chuẩn hóa', fontsize=11, fontweight='bold')
ax.set_xlabel('Persona ID', fontsize=11, fontweight='bold')
ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
plt.tight_layout()
fig.savefig(out_figs / "step6_persona_hierarchical_dendrogram.png", bbox_inches='tight')
plt.close(fig)
print("Fig 3 saved.")

# Figure 4: Cluster Centroids Bar Chart
df_clustered = df_num.copy()
df_clustered['Cluster'] = clusters
centroids = df_clustered.groupby('Cluster').mean().T

fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
x = np.arange(len(centroids.index))
width = 0.25

rects1 = ax.bar(x - width, centroids[1], width, label='Cụm 1: Fast Skim / Daily (vn_000077, 81)', color='#ef4444', alpha=0.9, edgecolor='black', linewidth=0.8)
rects2 = ax.bar(x, centroids[2], width, label='Cụm 2: Deep Reader / Feed Focus (vn_000041, 49)', color='#3b82f6', alpha=0.9, edgecolor='black', linewidth=0.8)
rects3 = ax.bar(x + width, centroids[3], width, label='Cụm 3: Deliberate / Infrequent (vn_000019, 87)', color='#10b981', alpha=0.9, edgecolor='black', linewidth=0.8)

ax.set_ylabel('Giá trị Trung bình Số học (Mean Score)', fontsize=11, fontweight='bold')
ax.set_title('So sánh Trọng tâm Số học (Centroids) giữa 3 Cụm Hành vi Persona', fontsize=13, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(centroids.index, fontsize=10, fontweight='bold', rotation=15)
ax.legend(frameon=True, facecolor='white', framealpha=0.95, loc='upper right')
ax.set_ylim(0, 5.5)

def autolabel(rects):
    for rect in rects:
        h = rect.get_height()
        if h > 0:
            ax.annotate(f'{h:.1f}',
                        xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight='bold')

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

plt.tight_layout()
fig.savefig(out_figs / "step6_persona_cluster_centroids.png", bbox_inches='tight')
plt.close(fig)
print("Fig 4 saved.")
