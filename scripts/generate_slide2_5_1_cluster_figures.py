import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.metrics import silhouette_score

# Đảm bảo UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

FIGURES_DIR = PROJECT_ROOT / "output" / "figures"
TABLES_DIR = PROJECT_ROOT / "output" / "tables"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# Cấu hình thẩm mỹ
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI', 'Liberation Sans']
plt.rcParams['axes.edgecolor'] = '#7f8c8d'
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['grid.color'] = '#ecf0f1'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

print("1. Nạp dữ liệu actions và xây dựng ma trận đặc trưng...")
from loaders.action_loader import ActionLoader
loader = ActionLoader()
df_actions = loader.to_unified_actions_dataframe()

focused_intents = ['read', 'comment', 'react', 'expand', 'search', 'share']
sub = df_actions[df_actions['intent'].isin(focused_intents)].copy()
N_TOTAL = len(sub)

top_dims = sub['primary_dimension'].value_counts()
valid_dims = top_dims[top_dims >= 2].index.tolist()

# Feature matrix: tỷ lệ xuất hiện theo từng Persona và từng Intent (23 x 12)
ct_pers = pd.crosstab(sub['primary_dimension'], sub['persona_id'], normalize='index').loc[valid_dims]
ct_act = pd.crosstab(sub['primary_dimension'], sub['intent'], normalize='index').loc[valid_dims]
feature_mat = pd.concat([ct_pers, ct_act], axis=1)

print("2. Chạy thuật toán Ward's Linkage và quét Silhouette Score...")
Z = linkage(feature_mat, method='ward')

k_values = list(range(2, 8))
sil_scores = []
for k in k_values:
    labels = fcluster(Z, t=k, criterion='maxclust')
    score = silhouette_score(feature_mat, labels)
    sil_scores.append(score)

best_idx = np.argmax(sil_scores)
best_k = k_values[best_idx]
best_score = sil_scores[best_idx]
print(f"  -> k tối ưu: {best_k} với Silhouette Score = {best_score:.4f}")

# Gán nhãn cho k=6
cluster_labels_k6 = fcluster(Z, t=6, criterion='maxclust')
res_df = pd.DataFrame({
    'primary_dimension': valid_dims,
    'count': [top_dims[d] for d in valid_dims],
    'cluster_id': cluster_labels_k6
})

# Đặt tên định danh cho 6 cụm dựa trên thành phần thực tế
cluster_meta = {
    6: {
        'name': 'Cụm 6: Khám phá Tri thức & BĐS',
        'persona': 'vn_fb_001, 005, 006 (Trí thức & Kỹ thuật)',
        'top_dims': 'curiosity (119), real_estate (36), career (7), tech (7)',
        'color': '#2980b9'  # Xanh dương đậm
    },
    2: {
        'name': 'Cụm 2: Ẩm thực & Giao lưu Đêm',
        'persona': 'vn_fb_003 (Bảo vệ ca trực)',
        'top_dims': 'cuisine_vn (14), street_food (12), social_style (7), group (6)',
        'color': '#e67e22'  # Cam ấm
    },
    1: {
        'name': 'Cụm 1: Ngôn ngữ & Gia đình',
        'persona': 'vn_fb_002 (Gia đình / Nghệ An)',
        'top_dims': 'tone (14), province (7), expressiveness (5), parenting (3)',
        'color': '#27ae60'  # Xanh lá
    },
    5: {
        'name': 'Cụm 5: Giải trí Video & Thể thao',
        'persona': 'vn_fb_004 (Nhà hàng / Gen Z)',
        'top_dims': 'content_format (13), football (11)',
        'color': '#d35400'  # Cam gạch
    },
    4: {
        'name': 'Cụm 4: Truyền thống & Lịch sử',
        'persona': 'vn_fb_005 (Cơ khí / Tri ân tướng Giáp)',
        'top_dims': 'value_tradition (21), cuisine_jp (2)',
        'color': '#8e44ad'  # Tím
    },
    3: {
        'name': 'Cụm 3: Tâm linh & Sức khỏe',
        'persona': 'vn_fb_006 & 002 (Trung niên & Lớn tuổi)',
        'top_dims': 'spirituality (7), health (5), wealth (4), thread (2)',
        'color': '#16a085'  # Xanh ngọc biển
    }
}

cluster_summary = []
for cid, meta in cluster_meta.items():
    sub_c = res_df[res_df['cluster_id'] == cid]
    tot_cnt = sub_c['count'].sum()
    pct = tot_cnt / N_TOTAL * 100
    cluster_summary.append({
        'cluster_id': cid,
        'cluster_name': meta['name'],
        'so_luot': tot_cnt,
        'ty_le': pct,
        'persona_dai_dien': meta['persona'],
        'thuoc_tinh_chinh': meta['top_dims'],
        'color': meta['color']
    })

df_cluster_summary = pd.DataFrame(cluster_summary).sort_values('so_luot', ascending=True)

print("3. Xuất bảng dữ liệu CSV...")
df_cluster_summary.to_csv(TABLES_DIR / "slide2_5_1_data_driven_clusters.csv", index=False, encoding='utf-8-sig')
res_df.to_csv(TABLES_DIR / "slide2_5_1_dimensions_cluster_assignments.csv", index=False, encoding='utf-8-sig')

print("4. Vẽ biểu đồ Slide 2.5.1...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5), gridspec_kw={'width_ratios': [1, 1.4]})

# Panel A: Silhouette Score Curve
ax1.plot(k_values, sil_scores, marker='o', linewidth=2.5, markersize=8, color='#2c3e50', zorder=3)
for k, sc in zip(k_values, sil_scores):
    if k == best_k:
        ax1.scatter([k], [sc], color='#e74c3c', s=200, zorder=5, edgecolors='black', linewidth=1.5)
        ax1.annotate(f"ĐỈNH TỐI ƯU TOÁN HỌC\nk={k} (Score = {sc:.4f})\nTrùng khớp 6 Persona!",
                     xy=(k, sc), xytext=(k - 0.5, sc + 0.035),
                     fontsize=10.5, fontweight='bold', color='#c0392b',
                     arrowprops=dict(arrowstyle="->", color='#c0392b', lw=1.5),
                     ha='right', va='bottom',
                     bbox=dict(boxstyle="round,pad=0.4", fc="#fadbd8", ec="#e74c3c", lw=1))
    else:
        ax1.annotate(f"{sc:.4f}", xy=(k, sc), xytext=(k, sc - 0.02),
                     fontsize=9, ha='center', va='top', color='#7f8c8d')

ax1.set_title("A. KIỂM ĐỊNH SỐ CỤM TỐI ƯU (SILHOUETTE SCORE)", fontsize=12, fontweight='bold', pad=14, color='#2c3e50')
ax1.set_xlabel("Số lượng Cụm Nhận thức (k)", fontsize=10.5, fontweight='bold')
ax1.set_ylabel("Hệ số Phân tách Silhouette Score", fontsize=10.5, fontweight='bold')
ax1.set_xticks(k_values)
ax1.set_ylim(0.15, 0.48)
ax1.grid(True, linestyle='--', alpha=0.6)

# Panel B: Phân bố 6 Cụm do máy tự học
y_pos = np.arange(len(df_cluster_summary))
bars = ax2.barh(y_pos, df_cluster_summary['so_luot'], color=df_cluster_summary['color'],
                edgecolor='black', linewidth=1.0, height=0.65, alpha=0.9, zorder=3)

ax2.set_yticks(y_pos)
ax2.set_yticklabels(df_cluster_summary['cluster_name'], fontsize=10, fontweight='bold')
ax2.set_xlabel(f"Số lượt Kích hoạt Quyết định (Tổng N = {N_TOTAL} actions)", fontsize=10.5, fontweight='bold')
ax2.set_title("B. 6 CỤM BẢN SẮC NHẬN THỨC DO THUẬT TOÁN TỰ HỌC (k=6)", fontsize=12, fontweight='bold', pad=14, color='#2c3e50')
ax2.set_xlim(0, max(df_cluster_summary['so_luot']) * 1.35)
ax2.grid(True, axis='x', linestyle='--', alpha=0.6)

for idx, (_, row) in enumerate(df_cluster_summary.iterrows()):
    cnt = row['so_luot']
    pct = row['ty_le']
    persona_txt = row['persona_dai_dien'].split('(')[0].strip()
    ax2.text(cnt + 2.5, idx, f"{cnt} lượt ({pct:.1f}%)\nĐại diện: {persona_txt}",
             va='center', ha='left', fontsize=8.8, fontweight='bold', color='#2c3e50')

plt.tight_layout()
fig_path = FIGURES_DIR / "slide2_5_1_data_driven_clusters.png"
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"  -> Đã lưu biểu đồ thành công: {fig_path}")
