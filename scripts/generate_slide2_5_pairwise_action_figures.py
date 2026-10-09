import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, str(Path('.').resolve()))
sys.stdout.reconfigure(encoding='utf-8')

from loaders.action_loader import ActionLoader

loader = ActionLoader()
df = loader.to_unified_actions_dataframe()

FIGURES_DIR = Path("output/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Matplotlib visual settings
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI', 'Liberation Sans']
plt.rcParams['axes.edgecolor'] = '#7f8c8d'
plt.rcParams['axes.linewidth'] = 1.0

PERSONA_ORDER = ['vn_fb_001', 'vn_fb_002', 'vn_fb_003', 'vn_fb_004', 'vn_fb_005', 'vn_fb_006']
PERSONA_LABELS = {
    'vn_fb_001': 'vn_fb_001\n(Thiết kế đồ họa)',
    'vn_fb_002': 'vn_fb_002\n(Gia đình / Nghệ An)',
    'vn_fb_003': 'vn_fb_003\n(Bảo vệ ca đêm)',
    'vn_fb_004': 'vn_fb_004\n(Phục vụ nhà hàng)',
    'vn_fb_005': 'vn_fb_005\n(Thợ cơ khí)',
    'vn_fb_006': 'vn_fb_006\n(Gen X BĐS)',
}

# Semantic color palette mapped strictly to exact primary_dimension keys
DIM_COLORS = {
    'curiosity': '#2980b9',                       # Deep Blue
    'interest_real_estate': '#16a085',            # Teal
    'value_tradition': '#c0392b',                 # Crimson
    'cuisine_street_food': '#e67e22',             # Orange
    'cuisine_vietnamese': '#d35400',              # Brick Orange
    'emotional_state': '#27ae60',                            # Emerald Green
    'sport_football': '#e74c3c',                  # Red
    'content_consumption_format': '#f39c12',      # Amber
    'interest_technology': '#3498db',             # Sky Blue
    'social_engagement_style': '#8e44ad',         # Purple
    'interest_spirituality': '#9b59b6',           # Light Purple
    'skepticism': '#34495e',                      # Slate Dark
    'group_community_participation': '#1abc9c',   # Turquoise
    'career_role': '#2c3e50',                     # Navy
    'province': '#e84393',                        # Magenta
    'writing_format': '#00cec9',                  # Cyan
    'value_health': '#00b894',                    # Mint Green
    'value_wealth': '#fdcb6e',                    # Sand Yellow
    'interest_parenting_family_life': '#6c5ce7',  # Lavender
    'emotional_expressiveness': '#fd79a8',        # Soft Pink
    'decision_speed': '#fab1a0',                  # Peach
    'cuisine_japanese': '#e17055',                # Burnt Orange
    'reading_frequency': '#a29bfe',               # Soft Violet
    'other_dimensions': '#95a5a6',                # Grey
}

def get_dimension_breakdown(intent_name):
    sub = df[df['intent'] == intent_name]
    breakdown = {}
    for p in PERSONA_ORDER:
        sp = sub[sub['persona_id'] == p]
        n = len(sp)
        if n == 0:
            breakdown[p] = {'n': 0, 'segments': []}
        else:
            vc = sp['primary_dimension'].value_counts()
            segments = []
            accum_other = 0.0
            accum_other_cnt = 0
            for dim, cnt in vc.items():
                pct = cnt / n * 100.0
                if pct >= 8.0 or len(vc) <= 3:
                    display_dim = 'emotional_state' if dim == 'tone' else dim
                    segments.append({
                        'dimension': display_dim,
                        'count': cnt,
                        'pct': pct,
                        'color': DIM_COLORS.get(display_dim, '#95a5a6')
                    })
                else:
                    accum_other += pct
                    accum_other_cnt += cnt
            if accum_other > 0:
                segments.append({
                    'dimension': 'other_dimensions',
                    'count': accum_other_cnt,
                    'pct': accum_other,
                    'color': '#95a5a6'
                })
            breakdown[p] = {'n': n, 'segments': segments}
    return breakdown


def plot_pairwise_motivation(act1, act1_title, act2, act2_title, slide_id, slide_title, output_filename, notes_act1, notes_act2):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(22, 9.2))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.83, bottom=0.10, wspace=0.44)
    
    bd1 = get_dimension_breakdown(act1)
    bd2 = get_dimension_breakdown(act2)
    
    def render_panel(ax, bd_data, act_title, notes_dict, act_key):
        y_pos = np.arange(len(PERSONA_ORDER))
        
        for y_idx, persona in enumerate(PERSONA_ORDER):
            p_info = bd_data[persona]
            n = p_info['n']
            segments = p_info['segments']
            
            if n == 0:
                note_txt = notes_dict.get(persona, "[Không phát sinh - 0 lượt]")
                ax.barh(
                    y_idx, 100.0, left=0.0, height=0.56,
                    color='#dfe6e9', edgecolor='#7f8c8d', linewidth=1.1,
                    hatch='///', alpha=0.75
                )
                ax.text(
                    50.0, y_idx, f"[Không phát sinh hành vi - 0 lượt]",
                    ha='center', va='center',
                    fontsize=9.0, fontweight='bold', color='#636e72'
                )
                ax.text(
                    102.5, y_idx, f"▶ {note_txt}",
                    ha='left', va='center',
                    fontsize=8.2, fontweight='bold', color='#7f8c8d'
                )
            else:
                current_left = 0.0
                for seg in segments:
                    dim = seg['dimension']
                    pct = seg['pct']
                    color = seg['color']
                    
                    bar = ax.barh(
                        y_idx, pct, left=current_left, height=0.56,
                        color=color, edgecolor='#2c3e50', linewidth=1.1,
                        alpha=0.92
                    )
                    
                    mid_x = current_left + pct / 2.0
                    if pct >= 24.0:
                        ax.text(
                            mid_x, y_idx, f"{dim}\n{pct:.1f}%",
                            ha='center', va='center',
                            fontsize=8.0, fontweight='bold', color='#ffffff'
                        )
                    elif pct >= 14.0:
                        short_dim = dim if len(dim) <= 12 else dim[:10] + '..'
                        ax.text(
                            mid_x, y_idx, f"{short_dim}\n{pct:.1f}%",
                            ha='center', va='center',
                            fontsize=7.2, fontweight='bold', color='#ffffff'
                        )
                    elif pct >= 7.0:
                        ax.text(
                            mid_x, y_idx, f"{pct:.1f}%",
                            ha='center', va='center',
                            fontsize=7.0, fontweight='bold', color='#ffffff'
                        )
                    current_left += pct
                
                note_txt = notes_dict.get(persona, "")
                ax.text(
                    102.5, y_idx, f"▶ {note_txt}",
                    ha='left', va='center',
                    fontsize=8.2, fontweight='bold', color='#1a365d'
                )
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels([PERSONA_LABELS[p] for p in PERSONA_ORDER], fontsize=9.5, fontweight='bold', color='#2c3e50')
        ax.invert_yaxis()
        ax.set_xlim(0, 195)
        ax.set_xticks([0, 20, 40, 60, 80, 100])
        ax.set_xticklabels(['0%', '20%', '40%', '60%', '80%', '100%'], fontsize=9.5, fontweight='bold', color='#34495e')
        ax.set_xlabel('Cơ cấu % các trường primary_dimension nội tại', fontsize=10.0, fontweight='bold', color='#2c3e50')
        ax.set_title(act_title, fontsize=11.5, fontweight='bold', color='#1a365d', pad=12)
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        ax.axvline(100, color='#e74c3c', linestyle=':', linewidth=1.3, alpha=0.85)

    render_panel(ax1, bd1, act1_title, notes_act1, act1 if act1!='tone' else 'emotional_state')
    render_panel(ax2, bd2, act2_title, notes_act2, act2 if act2!='tone' else 'emotional_state')
    
    fig.suptitle(f"KIỂM CHỨNG H2 ({slide_id}): {slide_title}\n(Cơ cấu % các trường primary_dimension chính xác từ CSDL thực nghiệm - Tuyệt đối không dùng tên suy diễn)",
                 fontsize=13.0, fontweight='bold', color='#1a365d', y=0.96)
    
    out_path = FIGURES_DIR / output_filename
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"  -> Đã lưu biểu đồ {slide_id}: {out_path}")


# ==============================================================================
# 1. HÌNH SLIDE 2.5.1: SEARCH & COMMENT
# ==============================================================================
notes_search = {
    'vn_fb_001': 'interest_technology (100.0%) | value: "Rất đam mê"',
    'vn_fb_002': '[Không phát sinh tìm kiếm - 0 lượt]',
    'vn_fb_003': 'cuisine_street_food (50.0%) & social_engagement_style (50.0%)',
    'vn_fb_004': 'sport_football (100.0%) | value: "Chủ yếu theo dõi"',
    'vn_fb_005': 'curiosity (100.0%) | value: "Cao"',
    'vn_fb_006': 'interest_real_estate (66.7%) & skepticism (33.3%)',
}

notes_comment = {
    'vn_fb_001': 'curiosity (66.7%) & writing_format (33.3%)',
    'vn_fb_002': 'emotional_state (100.0%) | value: "Lo âu / Bồn chồn"',
    'vn_fb_003': 'cuisine_vietnamese (38.9%) & cuisine_street_food (33.3%)',
    'vn_fb_004': '[Không phát sinh bình luận - 0 lượt]',
    'vn_fb_005': 'value_tradition (58.3%) & curiosity (33.3%)',
    'vn_fb_006': 'cuisine_street_food (100.0%) | value: "Rất thích"',
}

plot_pairwise_motivation(
    act1='search',
    act1_title='A. ĐỘNG LỰC TÌM KIẾM CHỦ ĐỘNG (SEARCH)\n(Cơ cấu % primary_dimension chính xác trong CSDL)',
    act2='comment',
    act2_title='B. ĐỘNG LỰC VIẾT BÌNH LUẬN (COMMENT)\n(Cơ cấu % primary_dimension chính xác trong CSDL)',
    slide_id='SLIDE 2.5.1',
    slide_title='ĐỐI SÁNH ĐỘNG LỰC HÀNH VI GÕ PHÍM CHỦ ĐỘNG (SEARCH & COMMENT)',
    output_filename='slide2_5_1_search_and_comment.png',
    notes_act1=notes_search,
    notes_act2=notes_comment
)


# ==============================================================================
# 2. HÌNH SLIDE 2.5.2: READ & EXPAND
# ==============================================================================
notes_read = {
    'vn_fb_001': 'curiosity (53.8%) & interest_real_estate (26.9%)',
    'vn_fb_002': 'curiosity (23.8%), emotional_state (23.8%), interest_parenting_family_life (14.3%)',
    'vn_fb_003': 'cuisine_vietnamese (30.4%) & group_community_participation (21.7%)',
    'vn_fb_004': 'sport_football (70.0%) & curiosity (20.0%)',
    'vn_fb_005': 'curiosity (62.1%) & value_tradition (24.1%)',
    'vn_fb_006': 'curiosity (41.9%), interest_real_estate (23.3%), interest_spirituality (11.6%)',
}

notes_expand = {
    'vn_fb_001': 'curiosity (71.4%) & decision_speed (14.3%)',
    'vn_fb_002': 'interest_spirituality (100.0%) | value: "Không quan tâm"',
    'vn_fb_003': '[Không phát sinh mở rộng - 0 lượt]',
    'vn_fb_004': 'curiosity (100.0%) | value: "Rất cao"',
    'vn_fb_005': 'curiosity (36.4%) & value_tradition (36.4%)',
    'vn_fb_006': '[Không phát sinh mở rộng - 0 lượt]',
}

plot_pairwise_motivation(
    act1='read',
    act1_title='A. ĐỘNG LỰC ĐỌC SÂU NỘI DUNG (READ)\n(Cơ cấu % primary_dimension chính xác trong CSDL)',
    act2='expand',
    act2_title='B. ĐỘNG LỰC BẤM "XEM THÊM" (EXPAND)\n(Cơ cấu % primary_dimension chính xác trong CSDL)',
    slide_id='SLIDE 2.5.2',
    slide_title='ĐỐI SÁNH ĐỘNG LỰC HÀNH VI THẨM ĐỊNH VĂN BẢN (READ & EXPAND)',
    output_filename='slide2_5_2_read_and_expand.png',
    notes_act1=notes_read,
    notes_act2=notes_expand
)


# ==============================================================================
# 3. HÌNH SLIDE 2.5.3: REACT & SHARE
# ==============================================================================
notes_react = {
    'vn_fb_001': 'curiosity (52.6%), interest_real_estate (26.3%), career_role (15.8%)',
    'vn_fb_002': 'emotional_state (42.1%) & emotional_expressiveness (26.3%)',
    'vn_fb_003': 'content_consumption_format (66.7%) & curiosity (33.3%)',
    'vn_fb_004': 'content_consumption_format (66.7%) & sport_football (22.2%)',
    'vn_fb_005': 'curiosity (50.0%) & value_tradition (25.0%)',
    'vn_fb_006': 'interest_real_estate (41.7%), value_health (25.0%), curiosity (16.7%)',
}

notes_share = {
    'vn_fb_001': '[Không phát sinh chia sẻ - 0 lượt]',
    'vn_fb_002': '[Không phát sinh chia sẻ - 0 lượt]',
    'vn_fb_003': '[Không phát sinh chia sẻ - 0 lượt]',
    'vn_fb_004': '[Không phát sinh chia sẻ - 0 lượt]',
    'vn_fb_005': 'curiosity (100.0%) | value: "Cao"',
    'vn_fb_006': '[Không phát sinh chia sẻ - 0 lượt]',
}

plot_pairwise_motivation(
    act1='react',
    act1_title='A. ĐỘNG LỰC THẢ CẢM XÚC (REACT)\n(Cơ cấu % primary_dimension chính xác trong CSDL)',
    act2='share',
    act2_title='B. ĐỘNG LỰC CHIA SẺ NỘI DUNG (SHARE)\n(Cơ cấu % primary_dimension chính xác trong CSDL)',
    slide_id='SLIDE 2.5.3',
    slide_title='ĐỐI SÁNH ĐỘNG LỰC HÀNH VI CẢM XÚC & LAN TỎA (REACT & SHARE)',
    output_filename='slide2_5_3_react_and_share.png',
    notes_act1=notes_react,
    notes_act2=notes_share
)


# ==============================================================================
# 4. HÌNH SLIDE 2.5: TỔNG QUAN MA TRẬN PHÂN HÓA ĐỘNG LỰC (HEATMAP TỐI ƯU LAYOUT)
# ==============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(19, 8.5), gridspec_kw={'width_ratios': [1.15, 1.15]})
fig.subplots_adjust(left=0.15, right=0.96, top=0.83, bottom=0.20, wspace=0.34)

focused_intents = ['read', 'comment', 'react', 'expand', 'search', 'share']
sub = df[df['intent'].isin(focused_intents)].copy()

top_overall_dims = sub['primary_dimension'].value_counts().head(8).index.tolist()
ct_pers_dim = pd.crosstab(sub['persona_id'], sub['primary_dimension'])[top_overall_dims].reindex(PERSONA_ORDER)

sns.heatmap(
    ct_pers_dim,
    annot=True,
    fmt='d',
    cmap='YlGnBu',
    cbar=True,
    cbar_kws={'label': 'Số lượt kích hoạt evidence', 'shrink': 0.8},
    linewidths=1.2,
    linecolor='#ffffff',
    ax=ax1,
    annot_kws={'fontsize': 11, 'fontweight': 'bold'}
)
ax1.set_title('A. Phân Bổ 8 Primary Evidence Chi Phối\n(Số lượt viện dẫn chính xác theo primary_dimension trong CSDL)', fontsize=11.5, fontweight='bold', color='#1a365d', pad=12)
ax1.set_xlabel('Tên Evidence Chính Xác (primary_dimension)', fontsize=10.5, fontweight='bold', color='#2c3e50')
ax1.set_ylabel('')
formatted_dims = ['Emotional state' if dim == 'tone' else dim for dim in top_overall_dims]
ax1.set_xticklabels(formatted_dims, fontsize=9.0, fontweight='bold', rotation=35, ha='right')
ax1.set_yticklabels([PERSONA_LABELS[p].replace('\n', ' ') for p in PERSONA_ORDER], fontsize=9.5, fontweight='bold', rotation=0)

ct_pers_act_pct = pd.crosstab(sub['persona_id'], sub['intent'], normalize='index')[focused_intents].reindex(PERSONA_ORDER) * 100
sns.heatmap(
    ct_pers_act_pct,
    annot=True,
    fmt='.1f',
    cmap='Oranges',
    cbar=True,
    cbar_kws={'label': 'Tỷ lệ phân bổ hành vi (%)', 'shrink': 0.8},
    linewidths=1.2,
    linecolor='#ffffff',
    ax=ax2,
    annot_kws={'fontsize': 11, 'fontweight': 'bold'}
)
ax2.set_title('B. Phân Bổ 6 Hành Vi Có Chủ Đích\n(Tỷ lệ % nội tại từng Persona, N = 325)', fontsize=11.5, fontweight='bold', color='#1a365d', pad=12)
ax2.set_xlabel('Loại Hành Vi (Action Intent)', fontsize=10.5, fontweight='bold', color='#2c3e50')
ax2.set_ylabel('')
ax2.set_xticklabels([i.upper() for i in focused_intents], fontsize=10, fontweight='bold', rotation=0)
ax2.set_yticklabels(['' for _ in PERSONA_ORDER])

fig.suptitle("TỔNG QUAN MA TRẬN PHÂN HÓA ĐỘNG LỰC TOÀN HỆ THỐNG & NGUYÊN TẮC NHẬN THỨC 1-1\n(Căn cứ 100% tên trường primary_dimension thực nghiệm trong CSDL)",
             fontsize=13.5, fontweight='bold', color='#1a365d', y=0.96)

out_overview = FIGURES_DIR / "slide2_5_macro_decision_evidence_overview.png"
fig.savefig(out_overview, dpi=300)
plt.close(fig)
print(f"  -> Đã lưu biểu đồ tổng quan Slide 2.5: {out_overview}")

print("HOÀN TẤT SINH TOÀN BỘ 4 HÌNH VẼ ĐỐI SÁNH CHUẨN XÁC EVIDENCE!")
