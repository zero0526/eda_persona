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
    # Trụ cột 1: Tò mò & Khám phá tri thức
    'curiosity': 'Tò mò & Khám phá tri thức',
    'interest_technology': 'Tò mò & Khám phá tri thức',
    'books_self_help': 'Tò mò & Khám phá tri thức',
    'reading_frequency': 'Tò mò & Khám phá tri thức',
    'books_fantasy': 'Tò mò & Khám phá tri thức',
    'books_romance': 'Tò mò & Khám phá tri thức',
    'attitude_new_technology': 'Tò mò & Khám phá tri thức',
    'decision_speed': 'Tò mò & Khám phá tri thức',
    'extroversion': 'Tò mò & Khám phá tri thức',
    'logic_vs_intuition': 'Tò mò & Khám phá tri thức',
    'tech_savviness': 'Tò mò & Khám phá tri thức',
    
    # Trụ cột 2: Thực dụng, Chuyên môn & Đầu tư
    'interest_real_estate': 'Thực dụng & Chuyên môn đầu tư',
    'career_role': 'Thực dụng & Chuyên môn đầu tư',
    'value_wealth': 'Thực dụng & Chuyên môn đầu tư',
    'province': 'Thực dụng & Chuyên môn đầu tư',
    'writing_format': 'Thực dụng & Chuyên môn đầu tư',
    'attitude_advertising': 'Thực dụng & Chuyên môn đầu tư',
    'current_thread': 'Thực dụng & Chuyên môn đầu tư',

    # Trụ cột 3: Truyền thống, Bản sắc & Tâm linh
    'value_tradition': 'Truyền thống & Tâm linh',
    'interest_spirituality': 'Truyền thống & Tâm linh',
    'religion': 'Truyền thống & Tâm linh',

    # Trụ cột 4: Đời sống, Cảm xúc & Giải trí
    'cuisine_vietnamese': 'Đời sống, Cảm xúc & Giải trí',
    'cuisine_street_food': 'Đời sống, Cảm xúc & Giải trí',
    'cuisine_japanese': 'Đời sống, Cảm xúc & Giải trí',
    'sport_football': 'Đời sống, Cảm xúc & Giải trí',
    'sport_badminton': 'Đời sống, Cảm xúc & Giải trí',
    'tone': 'Đời sống, Cảm xúc & Giải trí',
    'content_consumption_format': 'Đời sống, Cảm xúc & Giải trí',
    'emotional_expressiveness': 'Đời sống, Cảm xúc & Giải trí',
    'interest_parenting_family_life': 'Đời sống, Cảm xúc & Giải trí',
    'social_engagement_style': 'Đời sống, Cảm xúc & Giải trí',
    'group_community_participation': 'Đời sống, Cảm xúc & Giải trí',
    'value_health': 'Đời sống, Cảm xúc & Giải trí',
    'value_family': 'Đời sống, Cảm xúc & Giải trí',
    'facebook_frequency': 'Đời sống, Cảm xúc & Giải trí',
    'dialect_register': 'Đời sống, Cảm xúc & Giải trí',
    'interest_film': 'Đời sống, Cảm xúc & Giải trí',
    'interest_pets': 'Đời sống, Cảm xúc & Giải trí',
    'interest_travel': 'Đời sống, Cảm xúc & Giải trí',
}

sub['macro_pillar'] = sub['primary_dimension'].map(pillar_map).fillna('Khác')

PILLAR_ORDER = [
    'Tò mò & Khám phá tri thức',
    'Đời sống, Cảm xúc & Giải trí',
    'Thực dụng & Chuyên môn đầu tư',
    'Truyền thống & Tâm linh'
]

PILLAR_COLORS = {
    'Tò mò & Khám phá tri thức': '#2980b9',      # Xanh lam
    'Đời sống, Cảm xúc & Giải trí': '#e67e22',   # Cam ấm
    'Thực dụng & Chuyên môn đầu tư': '#27ae60',  # Xanh ngọc
    'Truyền thống & Tâm linh': '#8e44ad'        # Tím
}

print("2. Tính toán bảng thống kê vĩ mô...")
pillar_counts = sub['macro_pillar'].value_counts().reindex(PILLAR_ORDER).fillna(0)
pillar_pcts = (pillar_counts / len(sub) * 100).round(1)

df_macro_dist = pd.DataFrame({
    'tru_cot_nhan_thuc': PILLAR_ORDER,
    'so_luot_kich_hoat': pillar_counts.values.astype(int),
    'ty_le_phan_tram': pillar_pcts.values,
})

# Thống kê top dimensions theo trụ cột
top_dims_per_pillar = []
for p in PILLAR_ORDER:
    p_dims = sub[sub['macro_pillar'] == p]['primary_dimension'].value_counts().head(3)
    p_str = ", ".join([f"{k} ({v})" for k, v in p_dims.items()])
    top_dims_per_pillar.append(p_str)
df_macro_dist['top_dimensions'] = top_dims_per_pillar

# Ma trận Trụ cột x Hành vi
ACTION_ORDER = ['read', 'react', 'comment', 'expand', 'search', 'share']
ct_pillar_action = pd.crosstab(sub['macro_pillar'], sub['intent']).reindex(index=PILLAR_ORDER, columns=ACTION_ORDER, fill_value=0)
df_matrix_export = ct_pillar_action.copy()
df_matrix_export['TOTAL'] = df_matrix_export.sum(axis=1)

print("3. Vẽ biểu đồ Tổng quan Vĩ mô (Slide 2.5)...")
fig = plt.figure(figsize=(16, 7.8), facecolor='#ffffff')
gs = fig.add_gridspec(1, 2, width_ratios=[1.1, 1.3], wspace=0.28, left=0.07, right=0.96, top=0.88, bottom=0.18)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# PANEL A: Phân bổ 4 trụ cột nhận thức
y_pos = np.arange(len(PILLAR_ORDER))
bars = ax1.barh(y_pos, pillar_counts.values, height=0.58, color=[PILLAR_COLORS[p] for p in PILLAR_ORDER], edgecolor='#2c3e50', linewidth=1.2, alpha=0.9)

ax1.set_yticks(y_pos)
ax1.set_yticklabels(PILLAR_ORDER, fontsize=10.5, fontweight='bold', color='#2c3e50')
ax1.invert_yaxis()  # Trụ cột lớn nhất lên trên
ax1.set_xlabel('Số lượng hành vi tập trung được kích hoạt (actions)', fontsize=10, fontweight='bold', color='#34495e', labelpad=8)
ax1.set_title('A. Phân Bổ 4 Trụ Cột Căn Cứ Nhận Thức Toàn Hệ Thống\n(Tổng số: N = 313 hành động có chủ đích)', fontsize=12, fontweight='bold', color='#2c3e50', pad=12)
ax1.set_xlim(0, max(pillar_counts.values) * 1.25)
ax1.grid(axis='x', linestyle='--', alpha=0.6)

# Ghi chú giá trị trên thanh bar
for bar, count, pct, p in zip(bars, pillar_counts.values, pillar_pcts.values, PILLAR_ORDER):
    w = bar.get_width()
    y = bar.get_y() + bar.get_height() / 2
    top_dim_txt = sub[sub['macro_pillar'] == p]['primary_dimension'].value_counts().index[0]
    ax1.text(w + 3, y, f"{count} lượt ({pct}%)\n[chủ đạo: {top_dim_txt}]", va='center', ha='left', fontsize=9.2, fontweight='bold', color='#2c3e50')

# PANEL B: Heatmap liên kết Trụ cột Nhận thức -> Hành vi tập trung cao
sns.heatmap(
    ct_pillar_action,
    annot=True,
    fmt='d',
    cmap='Blues',
    cbar=True,
    cbar_kws={'label': 'Số lượt kích hoạt hành vi', 'shrink': 0.8},
    linewidths=1.5,
    linecolor='#ffffff',
    ax=ax2,
    annot_kws={'fontsize': 11, 'fontweight': 'bold', 'color': '#1a252f'}
)

ax2.set_title('B. Ma Trận Liên Kết: Trụ Cột Nhận Thức ➔ Hành Vi Tập Trung\n(Cột: Hành vi thực hiện | Hàng: Trụ cột lý do viện dẫn)', fontsize=12, fontweight='bold', color='#2c3e50', pad=12)
ax2.set_xlabel('Hành vi tập trung cao (Action Intent)', fontsize=10.5, fontweight='bold', color='#34495e', labelpad=8)
ax2.set_ylabel('')
ax2.set_xticklabels(['Đọc sâu\n(read)', 'Thả cảm xúc\n(react)', 'Bình luận\n(comment)', 'Mở rộng bài\n(expand)', 'Tìm kiếm\n(search)', 'Chia sẻ\n(share)'], fontsize=9.5, fontweight='bold', color='#2c3e50')
ax2.set_yticklabels(PILLAR_ORDER, fontsize=10, fontweight='bold', color='#2c3e50', rotation=0)

# Tiêu đề toàn slide
fig.suptitle(
    "KIỂM CHỨNG H2 (SLIDE 2.5): TỔNG QUAN CĂN CỨ NHẬN THỨC (DECISION EVIDENCE) & MA TRẬN LIÊN KẾT HÀNH HÀNH ĐỘNG",
    fontsize=14,
    fontweight='bold',
    color='#1a365d',
    y=0.97
)

# CALLOUT BOX DƯỚI CHÂN HÌNH
fig.text(
    0.5, 0.035,
    "★ NHẬN ĐỊNH THỰC NGHIỆM VỀ MỐI LIÊN HỆ GIỮA CĂN CỨ NHẬN THỨC VÀ HÀNH VI CÓ CHỦ ĐÍCH (H2) ★\n"
    "• Trụ cột 'Tò mò & Khám phá tri thức' chi phối mạnh nhất (40.6%, 127 lượt), là động lực chính kích hoạt hành vi Đọc sâu (72 lượt) và Tìm kiếm (11 lượt).\n"
    "• Trụ cột 'Đời sống, Cảm xúc & Giải trí' (30.4%, 95 lượt) kích hoạt tỷ lệ Bình luận (17 lượt) và Thả cảm xúc (29 lượt) cao nhất trong các nhóm căn cứ.\n"
    "• Trụ cột 'Thực dụng & Chuyên môn đầu tư' (19.8%, 62 lượt) liên kết chủ đạo với Đọc sâu khảo sát (38 lượt) và Thả cảm xúc lưu bài (16 lượt).\n"
    "• Trụ cột 'Truyền thống & Tâm linh' (9.3%, 29 lượt) có tần suất khiêm tốn nhưng kích hoạt tỷ lệ Bình luận thảo luận và Mở rộng bài đọc cao tương đối.",
    ha='center',
    fontsize=9.4,
    fontweight='bold',
    color='#196f3d',
    bbox=dict(boxstyle='round,pad=0.7', facecolor='#eafaf1', edgecolor='#27ae60', linewidth=1.2)
)

fig_path = FIGURES_DIR / "slide2_5_macro_decision_evidence_overview.png"
plt.savefig(fig_path, dpi=300)
plt.close()
print(f"  -> Đã lưu biểu đồ: {fig_path}")

print("4. Xuất các bảng CSV chi tiết...")
csv_macro_dist = TABLES_DIR / "h2_macro_evidence_distribution.csv"
df_macro_dist.to_csv(csv_macro_dist, index=False, encoding='utf-8-sig')
print(f"  -> Đã lưu: {csv_macro_dist}")

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
        # Lấy sample reason
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

print("Hoàn tất tạo hình và dữ liệu Slide 2.5!")
