import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

PERSONA_ORDER = ['vn_fb_001', 'vn_fb_002', 'vn_fb_003', 'vn_fb_004', 'vn_fb_005', 'vn_fb_006']
PERSONA_LABELS = {
    'vn_fb_001': 'vn_fb_001\n(Thiết kế đồ họa)',
    'vn_fb_002': 'vn_fb_002\n(Lao động / Gia đình)',
    'vn_fb_003': 'vn_fb_003\n(Bảo vệ trực ca)',
    'vn_fb_004': 'vn_fb_004\n(Nhân viên nhà hàng)',
    'vn_fb_005': 'vn_fb_005\n(Thợ cơ khí)',
    'vn_fb_006': 'vn_fb_006\n(Gen X Kinh doanh)',
}

print("1. Nạp dữ liệu actions...")
from loaders.action_loader import ActionLoader
loader = ActionLoader()
df_actions = loader.to_unified_actions_dataframe()

focused_intents = ['read', 'comment', 'react', 'expand', 'search', 'share']
sub = df_actions[df_actions['intent'].isin(focused_intents)].copy()
print(f"  -> Tổng số hành động tập trung cao: {len(sub)} actions")

pillar_map = {
    # Trụ cột 1: Tò mò & Khám phá tri thức (Cognitive & Intellectual Needs)
    'curiosity': 'Tò mò',
    'interest_technology': 'Tò mò',
    'books_self_help': 'Tò mò',
    'reading_frequency': 'Tò mò',
    'books_fantasy': 'Tò mò',
    'books_romance': 'Tò mò',
    'books_science_fiction': 'Tò mò',
    'attitude_new_technology': 'Tò mò',
    'decision_speed': 'Tò mò',
    'extroversion': 'Tò mò',
    'logic_vs_intuition': 'Tò mò',
    'tech_savviness': 'Tò mò',
    'skepticism': 'Tò mò',
    'attention_span': 'Tò mò',
    'language_english': 'Tò mò',
    'discoveryStyle': 'Tò mò',
    
    # Trụ cột 2: Thực dụng & Chuyên môn (Utilitarian & Professional Needs)
    'interest_real_estate': 'Thực dụng & Chuyên môn',
    'career_role': 'Thực dụng & Chuyên môn',
    'value_wealth': 'Thực dụng & Chuyên môn',
    'province': 'Thực dụng & Chuyên môn',
    'writing_format': 'Thực dụng & Chuyên môn',
    'attitude_advertising': 'Thực dụng & Chuyên môn',
    'current_thread': 'Thực dụng & Chuyên môn',
    'interest_investing': 'Thực dụng & Chuyên môn',

    # Trụ cột 3: Truyền thống & Tâm linh (Cultural & Spiritual Identity)
    'value_tradition': 'Truyền thống & Tâm linh',
    'interest_spirituality': 'Truyền thống & Tâm linh',
    'religion': 'Truyền thống & Tâm linh',
    'books_history_philosophy': 'Truyền thống & Tâm linh',
    'books_historical_fiction': 'Truyền thống & Tâm linh',

    # Trụ cột 4: Đời sống & Giải trí (Affective, Social & Daily Leisure)
    'cuisine_vietnamese': 'Đời sống & Giải trí',
    'cuisine_street_food': 'Đời sống & Giải trí',
    'cuisine_japanese': 'Đời sống & Giải trí',
    'sport_football': 'Đời sống & Giải trí',
    'sport_badminton': 'Đời sống & Giải trí',
    'sport_table_tennis': 'Đời sống & Giải trí',
    'sport_boxing': 'Đời sống & Giải trí',
    'tone': 'Đời sống & Giải trí',
    'content_consumption_format': 'Đời sống & Giải trí',
    'emotional_expressiveness': 'Đời sống & Giải trí',
    'interest_parenting_family_life': 'Đời sống & Giải trí',
    'social_engagement_style': 'Đời sống & Giải trí',
    'group_community_participation': 'Đời sống & Giải trí',
    'value_health': 'Đời sống & Giải trí',
    'value_family': 'Đời sống & Giải trí',
    'facebook_frequency': 'Đời sống & Giải trí',
    'dialect_register': 'Đời sống & Giải trí',
    'interest_film': 'Đời sống & Giải trí',
    'film_animation': 'Đời sống & Giải trí',
    'interest_pets': 'Đời sống & Giải trí',
    'interest_travel': 'Đời sống & Giải trí',
    'music_indie': 'Đời sống & Giải trí',
    'humor_style': 'Đời sống & Giải trí',
    'directness': 'Đời sống & Giải trí',
    'children': 'Đời sống & Giải trí',
    'emoji_emoticon_use': 'Đời sống & Giải trí',
}

# ==============================================================================
# 2. XÁC ĐỊNH 2 NHÓM BẢN SẮC NHẬN THỨC THEO BẢN CHẤT MỤC TIÊU HÀNH VI
# ==============================================================================
GROUP_1_IDS = ['vn_fb_001', 'vn_fb_005', 'vn_fb_006']
GROUP_2_IDS = ['vn_fb_002', 'vn_fb_003', 'vn_fb_004']

GROUP_NAMES = [
    'Nhóm 1: Tri thức & Thực dụng',
    'Nhóm 2: Đời sống & Giải trí'
]

GROUP_COLORS = {
    'Nhóm 1: Tri thức & Thực dụng': '#2980b9',  # Xanh lam duy lý
    'Nhóm 2: Đời sống & Giải trí': '#e67e22'   # Cam ấm đời thường
}

sub['persona_group'] = sub['persona_id'].apply(
    lambda x: 'Nhóm 1: Tri thức & Thực dụng' if x in GROUP_1_IDS else 'Nhóm 2: Đời sống & Giải trí'
)

print("2. Tính toán bảng thống kê 2 nhóm nhận thức...")
group_counts = sub['persona_group'].value_counts().reindex(GROUP_NAMES).fillna(0)
group_pcts = (group_counts / len(sub) * 100).round(1)

# Ma trận 2 Nhóm x 6 Hành vi
ACTION_ORDER = ['read', 'react', 'comment', 'expand', 'search', 'share']
ACTION_LABELS = ['Đọc sâu\n(read)', 'Thả cảm xúc\n(react)', 'Bình luận\n(comment)', 'Mở rộng\n(expand)', 'Tìm kiếm\n(search)', 'Chia sẻ\n(share)']
ct_group_action = pd.crosstab(sub['persona_group'], sub['intent']).reindex(index=GROUP_NAMES, columns=ACTION_ORDER, fill_value=0)

df_macro_dist = pd.DataFrame({
    'nhom_nhan_thuc': GROUP_NAMES,
    'so_luot_kich_hoat': group_counts.values.astype(int),
    'ty_le_phan_tram': group_pcts.values,
})

print("3. Vẽ biểu đồ Tổng quan Vĩ mô 2 Nhóm (Slide 2.5)...")
fig = plt.figure(figsize=(16, 7.8), facecolor='#ffffff')
gs = fig.add_gridspec(1, 2, width_ratios=[1.1, 1.3], wspace=0.30, left=0.12, right=0.96, top=0.88, bottom=0.18)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# PANEL A: Phân bổ 2 Nhóm Bản Sắc Nhận Thức
y_pos = np.arange(len(GROUP_NAMES))
bars = ax1.barh(y_pos, group_counts.values, height=0.48, color=[GROUP_COLORS[g] for g in GROUP_NAMES], edgecolor='#2c3e50', linewidth=1.2, alpha=0.9)

ax1.set_yticks(y_pos)
ax1.set_yticklabels(GROUP_NAMES, fontsize=11, fontweight='bold', color='#2c3e50')
ax1.invert_yaxis()
ax1.set_xlabel('Số lượng hành vi tập trung được kích hoạt (actions)', fontsize=10.5, fontweight='bold', color='#34495e', labelpad=8)
ax1.set_title('A. Phân Bổ Quyết Định Giữa 2 Nhóm Bản Sắc Nhận Thức\n(Tổng số: N = 325 hành vi tập trung)', fontsize=12, fontweight='bold', color='#2c3e50', pad=12)
ax1.set_xlim(0, max(group_counts.values) * 1.35)
ax1.grid(axis='x', linestyle='--', alpha=0.6)

# Ghi chú chi tiết trên thanh bar
top_reasons_txt = [
    "Đại diện: 001, 005, 006 (66.5%)\nTop lý do: curiosity (107), real_estate (36), tradition (21)",
    "Đại diện: 002, 003, 004 (33.5%)\nTop lý do: cuisine (24), tone (14), format (13), football (10)"
]

for bar, count, pct, txt in zip(bars, group_counts.values, group_pcts.values, top_reasons_txt):
    w = bar.get_width()
    y = bar.get_y() + bar.get_height() / 2
    ax1.text(w + 4, y, f"{count} lượt ({pct}%)\n{txt}", va='center', ha='left', fontsize=9.2, fontweight='bold', color='#2c3e50')

# PANEL B: Heatmap liên kết 2 Nhóm -> 6 Hành vi tập trung
# Tạo ma trận chuỗi định dạng count (pct%)
annot_matrix = np.empty(ct_group_action.shape, dtype=object)
for i in range(ct_group_action.shape[0]):
    row_sum = ct_group_action.iloc[i].sum()
    for j in range(ct_group_action.shape[1]):
        val = ct_group_action.iloc[i, j]
        pct = (val / row_sum * 100).round(1) if row_sum > 0 else 0
        annot_matrix[i, j] = f"{val}\n({pct}%)"

sns.heatmap(
    ct_group_action,
    annot=annot_matrix,
    fmt='',
    cmap='Blues',
    cbar=True,
    cbar_kws={'label': 'Số lượt kích hoạt hành vi', 'shrink': 0.8},
    linewidths=1.5,
    linecolor='#ffffff',
    ax=ax2,
    annot_kws={'fontsize': 10.5, 'fontweight': 'bold', 'color': '#1a252f'}
)

ax2.set_title('B. Ma Trận Đối Sánh: 2 Nhóm Nhận Thức ➔ 6 Hành Vi Tập Trung\n(Cột: Hành vi thực hiện | Hàng: Nhóm động lực nhận thức)', fontsize=12, fontweight='bold', color='#2c3e50', pad=12)
ax2.set_xlabel('Hành vi tập trung cao (Action Intent)', fontsize=10.5, fontweight='bold', color='#34495e', labelpad=8)
ax2.set_ylabel('')
ax2.set_xticklabels(ACTION_LABELS, fontsize=9.5, fontweight='bold', color='#2c3e50')
ax2.set_yticklabels(GROUP_NAMES, fontsize=10.5, fontweight='bold', color='#2c3e50', rotation=0)

# Tiêu đề toàn slide
fig.suptitle(
    "KIỂM CHỨNG H2 (SLIDE 2.5): CƠ CHẾ CĂN CỨ NHẬN THỨC & SỰ PHÂN HÓA 2 NHÓM BẢN SẮC HÀNH VI",
    fontsize=14,
    fontweight='bold',
    color='#1a365d',
    y=0.97
)

fig_path = FIGURES_DIR / "slide2_5_macro_decision_evidence_overview.png"
plt.savefig(fig_path, dpi=300)
plt.close()
print(f"  -> Đã lưu biểu đồ: {fig_path}")

print("4. Xuất các bảng CSV chi tiết...")
csv_macro_dist = TABLES_DIR / "h2_macro_evidence_distribution.csv"
df_macro_dist.to_csv(csv_macro_dist, index=False, encoding='utf-8-sig')
print(f"  -> Đã lưu: {csv_macro_dist}")

df_matrix_export = ct_group_action.copy()
df_matrix_export['TOTAL'] = df_matrix_export.sum(axis=1)
csv_macro_matrix = TABLES_DIR / "h2_macro_evidence_action_matrix.csv"
df_matrix_export.to_csv(csv_macro_matrix, encoding='utf-8-sig')
print(f"  -> Đã lưu: {csv_macro_matrix}")

# 5. Xuất bảng ma trận chi tiết theo Persona (Cột = Hành vi, Hàng = Dimension)
detailed_persona_rows = []
for pid in PERSONA_ORDER:
    psub = sub[sub['persona_id'] == pid]
    group_name = "Nhóm 1 (Tri thức & Chuyên môn)" if pid in ['vn_fb_001', 'vn_fb_005', 'vn_fb_006'] else "Nhóm 2 (Đời sống & Giải trí)"
    ct = pd.crosstab(psub['primary_dimension'], psub['intent']).reindex(columns=ACTION_ORDER, fill_value=0)
    ct['TOTAL'] = ct.sum(axis=1)
    ct = ct.sort_values(by='TOTAL', ascending=False)
    
    for dim, row in ct.iterrows():
        sample_reason = ""
        dim_sub = psub[psub['primary_dimension'] == dim]
        if not dim_sub.empty:
            sample_reason = str(dim_sub.iloc[0]['reason']).replace('\n', ' ')
        
        entry = {
            'persona_id': pid,
            'persona_group': group_name,
            'primary_dimension': dim,
            'macro_pillar': pillar_map.get(dim, 'Khác'),
            'read': int(row.get('read', 0)),
            'react': int(row.get('react', 0)),
            'comment': int(row.get('comment', 0)),
            'expand': int(row.get('expand', 0)),
            'search': int(row.get('search', 0)),
            'share': int(row.get('share', 0)),
            'TOTAL': int(row['TOTAL']),
            'representative_reason': sample_reason
        }
        detailed_persona_rows.append(entry)

df_detailed_persona = pd.DataFrame(detailed_persona_rows)
csv_detailed_path = TABLES_DIR / "h2_persona_evidence_matrices_detailed.csv"
df_detailed_persona.to_csv(csv_detailed_path, index=False, encoding='utf-8-sig')
print(f"  -> Đã lưu bảng chi tiết 6 Persona: {csv_detailed_path}")

# ==============================================================================
# 6. TẠO HÌNH VẼ SLIDE 2.5.1: PHÂN BỔ NHẬN THỨC NHÓM 1 (001, 005, 006)
# ==============================================================================
print("5. Vẽ biểu đồ Chi tiết Nhóm 1 (Slide 2.5.1)...")
group1_pids = ['vn_fb_001', 'vn_fb_005', 'vn_fb_006']
fig_g1, axes_g1 = plt.subplots(1, 3, figsize=(19, 7.2), facecolor='#ffffff')
fig_g1.subplots_adjust(left=0.15, right=0.96, top=0.80, bottom=0.16, wspace=0.45)

g1_colors = ['#2980b9', '#8e44ad', '#27ae60']

DIM_LABEL_SHORT = {
    'content_consumption_format': 'content_format',
    'emotional_expressiveness': 'emotional_express',
    'group_community_participation': 'group_community',
    'interest_parenting_family_life': 'parenting_family',
    'attitude_new_technology': 'attitude_new_tech',
    'interest_real_estate': 'real_estate',
    'interest_technology': 'technology',
    'interest_spirituality': 'spirituality',
    'social_engagement_style': 'social_engagement',
    'cuisine_vietnamese': 'cuisine_vietnam',
    'cuisine_street_food': 'street_food',
    'cuisine_japanese': 'cuisine_japan',
}

for idx, (pid, ax) in enumerate(zip(group1_pids, axes_g1)):
    psub = df_detailed_persona[df_detailed_persona['persona_id'] == pid].copy()
    top_psub = psub.head(5).sort_values(by='TOTAL', ascending=True)
    
    y_pos = np.arange(len(top_psub))
    bars = ax.barh(y_pos, top_psub['TOTAL'], height=0.55, color=g1_colors[idx], edgecolor='#2c3e50', alpha=0.85)
    ax.set_yticks(y_pos)
    labels = [DIM_LABEL_SHORT.get(d, d) for d in top_psub['primary_dimension']]
    ax.set_yticklabels(labels, fontsize=10.5, fontweight='bold', color='#2c3e50')
    
    total_actions_pid = psub['TOTAL'].sum()
    ax.set_title(f"{PERSONA_LABELS[pid]}\n(Tổng: {total_actions_pid} hành vi)", fontsize=11.5, fontweight='bold', color='#1a365d', pad=12)
    ax.set_xlabel('Số lượt kích hoạt', fontsize=10.5, fontweight='bold', color='#34495e', labelpad=8)
    ax.set_xlim(0, max(top_psub['TOTAL']) * 1.35)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    
    for bar, val in zip(bars, top_psub['TOTAL']):
        pct = (val / total_actions_pid * 100).round(1)
        ax.text(val + max(top_psub['TOTAL']) * 0.03, bar.get_y() + bar.get_height()/2, f"{val} ({pct}%)", va='center', ha='left', fontsize=9.2, fontweight='bold', color='#2c3e50')

fig_g1.suptitle(
    "KIỂM CHỨNG H2 (SLIDE 2.5.1): CƠ CẤU CĂN CỨ NHẬN THỨC CHI TIẾT NHÓM 1 — TRI THỨC, KỸ THUẬT & THỰC DỤNG",
    fontsize=14, fontweight='bold', color='#1a365d', y=0.95
)
fig_g1_path = FIGURES_DIR / "slide2_5_1_group1_evidence_breakdown.png"
fig_g1.savefig(fig_g1_path, dpi=300)
plt.close(fig_g1)
print(f"  -> Đã lưu biểu đồ Nhóm 1: {fig_g1_path}")

# ==============================================================================
# 7. TẠO HÌNH VẼ SLIDE 2.5.2: PHÂN BỔ NHẬN THỨC NHÓM 2 (002, 003, 004)
# ==============================================================================
print("6. Vẽ biểu đồ Chi tiết Nhóm 2 (Slide 2.5.2)...")
group2_pids = ['vn_fb_002', 'vn_fb_003', 'vn_fb_004']
fig_g2, axes_g2 = plt.subplots(1, 3, figsize=(19, 7.2), facecolor='#ffffff')
fig_g2.subplots_adjust(left=0.15, right=0.96, top=0.80, bottom=0.16, wspace=0.45)

g2_colors = ['#16a085', '#d35400', '#c0392b']

for idx, (pid, ax) in enumerate(zip(group2_pids, axes_g2)):
    psub = df_detailed_persona[df_detailed_persona['persona_id'] == pid].copy()
    top_psub = psub.head(5).sort_values(by='TOTAL', ascending=True)
    
    y_pos = np.arange(len(top_psub))
    bars = ax.barh(y_pos, top_psub['TOTAL'], height=0.55, color=g2_colors[idx], edgecolor='#2c3e50', alpha=0.85)
    ax.set_yticks(y_pos)
    labels = [DIM_LABEL_SHORT.get(d, d) for d in top_psub['primary_dimension']]
    ax.set_yticklabels(labels, fontsize=10.5, fontweight='bold', color='#2c3e50')
    
    total_actions_pid = psub['TOTAL'].sum()
    ax.set_title(f"{PERSONA_LABELS[pid]}\n(Tổng: {total_actions_pid} hành vi)", fontsize=11.5, fontweight='bold', color='#1a365d', pad=12)
    ax.set_xlabel('Số lượt kích hoạt', fontsize=10.5, fontweight='bold', color='#34495e', labelpad=8)
    ax.set_xlim(0, max(top_psub['TOTAL']) * 1.35)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    
    for bar, val in zip(bars, top_psub['TOTAL']):
        pct = (val / total_actions_pid * 100).round(1)
        ax.text(val + max(top_psub['TOTAL']) * 0.03, bar.get_y() + bar.get_height()/2, f"{val} ({pct}%)", va='center', ha='left', fontsize=9.2, fontweight='bold', color='#2c3e50')

fig_g2.suptitle(
    "KIỂM CHỨNG H2 (SLIDE 2.5.2): CƠ CẤU CĂN CỨ NHẬN THỨC CHI TIẾT NHÓM 2 — ĐỜI SỐNG THƯỜNG NHẬT, CẢM XÚC & GIẢI TRÍ",
    fontsize=14, fontweight='bold', color='#1a365d', y=0.95
)
fig_g2_path = FIGURES_DIR / "slide2_5_2_group2_evidence_breakdown.png"
fig_g2.savefig(fig_g2_path, dpi=300)
plt.close(fig_g2)
print(f"  -> Đã lưu biểu đồ Nhóm 2: {fig_g2_path}")

print("Hoàn tất toàn bộ hình vẽ và dữ liệu Slide 2.5, 2.5.1, 2.5.2!")
