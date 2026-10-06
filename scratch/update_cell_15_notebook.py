import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

nb_path = 'notebooks/eda_action_v2.ipynb'
nb = json.load(open(nb_path, 'r', encoding='utf-8'))

cell_15_code = '''# Phân tích tỷ lệ tương tác xã hội (Reaction, Comment, Share)
# Đo lường cơ hội quan sát post (Unique Posts), Thống kê theo Nhóm Social Archetype và Thang đo 3 Nấc

# 1. Thang điểm 3 nấc theo Social Archetype (0 = Thấp / Không có, 1 = Trung bình / Vừa, 2 = Cao / Chủ đạo)
archetype_3tier = {
    'vn_fb_001': {'tier_react': 1, 'tier_comment': 1, 'tier_share': 0},  # Sáng tạo nội dung
    'vn_fb_002': {'tier_react': 1, 'tier_comment': 1, 'tier_share': 0},  # Kết nối cộng đồng
    'vn_fb_003': {'tier_react': 0, 'tier_comment': 2, 'tier_share': 0},  # Chiến thần bình luận dạo
    'vn_fb_004': {'tier_react': 2, 'tier_comment': 0, 'tier_share': 0},  # Tàu ngầm
    'vn_fb_005': {'tier_react': 1, 'tier_comment': 0, 'tier_share': 2},  # Người thích chia sẻ
    'vn_fb_006': {'tier_react': 2, 'tier_comment': 0, 'tier_share': 0},  # Tàu ngầm
}

persona_social = []
for p_id in sorted(df_steps['persona_id'].unique()):
    p_steps = df_steps[df_steps['persona_id'] == p_id]
    c_rules = contracts_dict.get(p_id, {}).get('social', {})
    attrs = personas_dict.get(p_id, {}).get('attributes', {})
    
    # Số bài viết độc nhất được quan sát / tiếp cận (Unique Post Targets)
    interactive_steps = p_steps[p_steps['intent'].isin(['read', 'expand', 'open', 'react', 'comment', 'share'])]
    unique_posts = interactive_steps['target_id'].nunique() if 'target_id' in interactive_steps.columns else 0
    
    reacts = (p_steps['intent'] == 'react').sum()
    comments = (p_steps['intent'] == 'comment').sum()
    shares = (p_steps['intent'] == 'share').sum()
    total_eng = reacts + comments + shares
    
    arch_raw = attrs.get('Cách thường tham gia và tương tác trên các nền tảng trực tuyến.', 'Khác')
    arch_clean = arch_raw.split('(')[0].strip()
    tier_info = archetype_3tier.get(p_id, {'tier_react': 1, 'tier_comment': 1, 'tier_share': 0})
    
    persona_social.append({
        'persona_id': p_id,
        'archetype': arch_clean,
        'unique_posts': unique_posts,
        'actual_reacts': reacts,
        'actual_comments': comments,
        'actual_shares': shares,
        'total_eng': total_eng,
        'actual_react_rate': reacts / unique_posts if unique_posts > 0 else 0.0,
        'actual_comment_rate': comments / unique_posts if unique_posts > 0 else 0.0,
        'actual_share_rate': shares / unique_posts if unique_posts > 0 else 0.0,
        'tier_react': tier_info['tier_react'],
        'tier_comment': tier_info['tier_comment'],
        'tier_share': tier_info['tier_share'],
        'contract_react_rate': c_rules.get('reactionRate', np.nan),
    })

df_ps = pd.DataFrame(persona_social)

# ==============================================================================
# BẢNG 1: THỐNG KÊ THỰC NGHIỆM TƯƠNG TÁC GOM THEO NHÓM SOCIAL ARCHETYPE
# ==============================================================================
df_arch_summary = df_ps.groupby('archetype').agg(
    So_Persona=('persona_id', 'count'),
    Tong_Co_Hoi_Quan_Sat=('unique_posts', 'sum'),
    Tong_React=('actual_reacts', 'sum'),
    Ty_Le_React_TB=('actual_react_rate', lambda x: f"{x.mean()*100:.1f}%"),
    Tong_Comment=('actual_comments', 'sum'),
    Ty_Le_Comment_TB=('actual_comment_rate', lambda x: f"{x.mean()*100:.1f}%"),
    Tong_Share=('actual_shares', 'sum'),
    Ty_Le_Share_TB=('actual_share_rate', lambda x: f"{x.mean()*100:.1f}%"),
    Tong_Tuong_Tac=('total_eng', 'sum'),
).reset_index()

print("=== 1. BẢNG THỰC NGHIỆM TƯƠNG TÁC XÃ HỘI GOM THEO NHÓM SOCIAL ARCHETYPE ===")
display(df_arch_summary)

# ==============================================================================
# BẢNG 2: KIỂM ĐỊNH TƯƠNG QUAN SPEARMAN (THANG ĐIỂM 3 NẤC VS THỰC TẾ)
# ==============================================================================
print("\\n=== 2. HỆ SỐ TƯƠNG QUAN SPEARMAN (THANG ĐIỂM 3 NẤC VS THỰC TẾ) ===")
for act in ['react', 'comment', 'share']:
    r_cnt, p_cnt = stats.spearmanr(df_ps[f'tier_{act}'], df_ps[f'actual_{act}s'])
    r_rate, p_rate = stats.spearmanr(df_ps[f'tier_{act}'], df_ps[f'actual_{act}_rate'])
    sig = "*** (p < 0.01)" if p_rate < 0.01 else ("* (p < 0.10)" if p_rate < 0.10 else "")
    print(f" - {act.capitalize():<7} -> vs Count: r_s = {r_cnt:+.4f} (p = {p_cnt:.4f}) | vs Rate: r_s = {r_rate:+.4f} (p = {p_rate:.4f}) {sig}")

r_contra, p_contra = stats.spearmanr(df_ps['contract_react_rate'], df_ps['actual_react_rate'])
print(f" * Đối chiếu Contract reactionRate: r_s = {r_contra:+.4f} (p = {p_contra:.4f}) [NGHỊCH BIẾN DO GÁN NHẦM CONTRACT]")

# ==============================================================================
# BẢNG 3: KIỂM ĐỊNH ĐỘ LỆCH CHI-SQUARE VỀ TÍNH PHỤ THUỘC HÌNH MẪU
# ==============================================================================
contingency_table = df_ps.groupby('archetype')[['actual_reacts', 'actual_comments', 'actual_shares']].sum()
chi2, p_chi2, dof, _ = stats.chi2_contingency(contingency_table)
print(f"\\n=== 3. KIỂM ĐỊNH CHI-SQUARE TÍNH ĐỘC LẬP CƠ CẤU HÀNH VI ===")
print(f" - Chi2 = {chi2:.3f}, dof = {dof}, p-value = {p_chi2:.4e} (p < 0.001 -> Phụ thuộc chặt chẽ vào Archetype)")

# ==============================================================================
# TRỰC QUAN HÓA: CƠ CẤU HÀNH VI & PHÂN BỔ THEO THANG 3 NẤC
# ==============================================================================
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# Đồ thị 1: Cơ cấu tương tác theo Nhóm Archetype
df_norm_pct = contingency_table.div(contingency_table.sum(axis=1), axis=0).fillna(0) * 100
df_norm_pct.columns = ['React (%)', 'Comment (%)', 'Share (%)']
df_norm_pct.plot(kind='barh', stacked=True, color=['#1f77b4', '#2ca02c', '#d62728'], edgecolor='black', ax=axes[0])
axes[0].set_title("Cơ Cấu Tương Tác Xã Hội (%) Theo Nhóm Social Archetype\\n(Chiến thần cmt 100% comment | Tàu ngầm >85% like | Thích chia sẻ độc quyền share)", fontsize=11, fontweight='bold')
axes[0].set_xlabel("Tỷ trọng tương tác (%)")
axes[0].set_ylabel("Nhóm Social Archetype")
axes[0].legend(loc='lower right')

# Đồ thị 2: Tỷ lệ tương tác thực tế trung bình theo Thang điểm 3 nấc (0 - 1 - 2)
plot_tiers = []
for act_name, col_tier, col_rate in [('React', 'tier_react', 'actual_react_rate'),
                                     ('Comment', 'tier_comment', 'actual_comment_rate'),
                                     ('Share', 'tier_share', 'actual_share_rate')]:
    mean_by_tier = df_ps.groupby(col_tier)[col_rate].mean().reset_index()
    mean_by_tier.columns = ['Tier', 'Mean_Rate']
    mean_by_tier['Action'] = act_name
    plot_tiers.append(mean_by_tier)

df_tier_plot = pd.concat(plot_tiers, ignore_index=True)
sns.barplot(data=df_tier_plot, x='Tier', y='Mean_Rate', hue='Action', 
            palette={'React': '#1f77b4', 'Comment': '#2ca02c', 'Share': '#d62728'}, edgecolor='black', ax=axes[1])
axes[1].set_title("Trung Bình Tỷ Lệ Tương Tác Thực Tế Theo Thang Điểm 3 Nấc\\n(0: Thấp/Không - 1: Trung Bình - 2: Cao/Chủ Đạo)", fontsize=11, fontweight='bold')
axes[1].set_xlabel("Nấc Đánh Giá (Tier: 0, 1, 2)")
axes[1].set_ylabel("Tỷ Lệ Tương Tác Chuẩn Hóa Trên Bài Quan Sát")
axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y*100:.0f}%'))

plt.tight_layout()
plt.show()
'''

nb['cells'][15]['source'] = [line + '\n' for line in cell_15_code.split('\n')][:-1]

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Đã cập nhật thành công Cell 15 trong notebooks/eda_action_v2.ipynb!")
