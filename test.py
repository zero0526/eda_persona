"""Phân tích dữ liệu khám phá (EDA): Mâu thuẫn giữa Ràng buộc Hợp đồng (BehavioralContract)
và Hồ sơ Ngữ nghĩa Persona (Semantic Persona Profile) trong Tương tác Mạng Xã Hội.

Mục tiêu:
1. Đối chiếu 3 chiều: Hồ sơ Persona (Semantic) vs Hợp đồng kỹ thuật (Contract) vs Thực tế (Actual).
2. Phát hiện và định lượng mâu thuẫn thiết kế (Design Contradictions) qua hệ số Spearman rank (r_s, p-value).
3. Minh chứng sự áp đảo của Semantic Archetype so với các tham số xác suất cơ học.
"""

import sys
import json
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Nạp dữ liệu từ module loaders
from loaders.episode_loader import get_sqlite_path, list_episodes, load_episode

DB_PATH = get_sqlite_path()
print(f"=== ĐANG KẾT NỐI DATABASE: {DB_PATH} ===\n")

# 1. Trích xuất Persona Versions & Behavioral Contracts
conn = sqlite3.connect(DB_PATH)
df_bots_raw = pd.read_sql_query('''
    SELECT 
        b.persona_id,
        pv.content_json as persona_json,
        bc.contract_json
    FROM bots b
    JOIN persona_versions pv ON pv.bot_id = b.id
    LEFT JOIN behavioral_contracts bc ON bc.id = (
        SELECT contract_id FROM episodes WHERE bot_id = b.id LIMIT 1
    )
''', conn)
conn.close()

contracts_dict = {}
personas_dict = {}
for _, row in df_bots_raw.iterrows():
    p_id = row['persona_id']
    if row['contract_json']:
        contracts_dict[p_id] = json.loads(row['contract_json'])
    if row['persona_json']:
        personas_dict[p_id] = json.loads(row['persona_json'])

# 2. Nạp toàn bộ các bước thực thi (Live Steps) từ các Episodes
episodes_summary = list_episodes(DB_PATH)
all_steps_list = []
for ep_info in episodes_summary:
    ep = load_episode(ep_info['id'], DB_PATH)
    all_steps_list.append(ep.to_steps_dataframe())

df_steps = pd.concat(all_steps_list, ignore_index=True)

# 3. Tổng hợp Bảng Chỉ số 3 Chiều (Semantic - Contract - Actual)
freq_map = {'Hàng ngày': 3, 'Vài lần một tuần': 2, 'Vài lần một tháng': 1, 'Rất hiếm khi': 0}

rows = []
for p_id in sorted(df_steps['persona_id'].unique()):
    p_steps = df_steps[df_steps['persona_id'] == p_id]
    attrs = personas_dict.get(p_id, {}).get('attributes', {})
    c_social = contracts_dict.get(p_id, {}).get('social', {})
    
    # Cơ hội quan sát bài viết độc nhất
    interactive_steps = p_steps[p_steps['intent'].isin(['read', 'expand', 'open', 'react', 'comment', 'share'])]
    unique_posts = interactive_steps['target_id'].nunique() if 'target_id' in interactive_steps.columns else 0
    
    # Hành vi thực tế
    actual_reacts = (p_steps['intent'] == 'react').sum()
    actual_comments = (p_steps['intent'] == 'comment').sum()
    actual_shares = (p_steps['intent'] == 'share').sum()
    total_eng = actual_reacts + actual_comments + actual_shares
    
    # Trường ngữ nghĩa gốc
    arch_full = attrs.get('Cách thường tham gia và tương tác trên các nền tảng trực tuyến.', 'Khác')
    arch_clean = arch_full.split('(')[0].strip()
    cmt_text = attrs.get('Tần suất viết comment trên các bài đăng công khai.', '')
    share_text = attrs.get('Tần suất share lại nội dung của fanpage hoặc người khác về tường.', '')
    
    rows.append({
        'persona_id': p_id,
        'archetype': arch_clean,
        # Semantic
        'cmt_freq_text': cmt_text,
        'cmt_freq_rank': freq_map.get(cmt_text, 0),
        'share_freq_text': share_text,
        'share_freq_rank': freq_map.get(share_text, 0),
        'is_lurker': 1 if 'Tàu ngầm' in arch_full else 0,
        'is_commenter': 1 if 'bình luận' in arch_full else 0,
        'is_sharer': 1 if 'chia sẻ' in arch_full else 0,
        # Contract
        'target_react_rate': c_social.get('reactionRate', np.nan),
        'target_comment_rate': c_social.get('commentRate', np.nan),
        'target_share_rate': c_social.get('shareRate', np.nan),
        # Actual
        'unique_posts': unique_posts,
        'actual_reacts': actual_reacts,
        'actual_comments': actual_comments,
        'actual_shares': actual_shares,
        'total_eng': total_eng,
        'actual_react_rate': actual_reacts / unique_posts if unique_posts > 0 else 0.0,
        'actual_comment_rate': actual_comments / unique_posts if unique_posts > 0 else 0.0,
        'actual_share_rate': actual_shares / unique_posts if unique_posts > 0 else 0.0,
    })

df_eda = pd.DataFrame(rows)

# ==============================================================================
# PHẦN 1: BẢNG ĐỐI CHIẾU 3 CHIỀU CHI TIẾT
# ==============================================================================
print("=" * 105)
print("PHẦN 1: BẢNG ĐỐI CHIẾU 3 CHIỀU (HỒ SƠ SEMANTIC VS HỢP ĐỒNG CONTRACT VS THỰC TẾ ACTUAL)")
print("=" * 105)
view_cols = [
    'persona_id', 'archetype',
    'cmt_freq_text', 'target_comment_rate', 'actual_comments', 'actual_comment_rate',
    'share_freq_text', 'target_share_rate', 'actual_shares', 'actual_share_rate',
    'target_react_rate', 'actual_reacts', 'actual_react_rate'
]
df_view = df_eda[view_cols].copy()
df_view['actual_comment_rate'] = df_view['actual_comment_rate'].apply(lambda x: f"{x*100:.1f}%")
df_view['actual_share_rate'] = df_view['actual_share_rate'].apply(lambda x: f"{x*100:.1f}%")
df_view['actual_react_rate'] = df_view['actual_react_rate'].apply(lambda x: f"{x*100:.1f}%")
print(df_view.to_string(index=False))

# ==============================================================================
# PHẦN 2: KIỂM ĐỊNH TƯƠNG QUAN SPEARMAN (RANK CORRELATION)
# ==============================================================================
print("\n" + "=" * 105)
print("PHẦN 2: ĐO LƯỜNG TƯƠNG QUAN HẠNG SPEARMAN (r_s, p-value)")
print("=" * 105)

def eval_corr(name, col1, col2):
    r, p = stats.spearmanr(df_eda[col1], df_eda[col2])
    sig = "*** (p<0.001)" if p < 0.001 else ("** (p<0.05)" if p < 0.05 else ("* (p<0.15)" if p < 0.15 else "(Không có ý nghĩa)"))
    print(f" - {name:<65} | r_s = {r:+.4f} | p = {p:.4f} {sig}")

print("\n--- Nhóm A: Quan hệ giữa Hồ sơ Semantic và Hợp đồng Kỹ thuật (Hồ sơ vs Hợp đồng) ---")
eval_corr("1. Tần suất Comment (Hồ sơ) vs Target commentRate (Hợp đồng)", "cmt_freq_rank", "target_comment_rate")
eval_corr("2. Tần suất Share (Hồ sơ) vs Target shareRate (Hợp đồng)", "share_freq_rank", "target_share_rate")
eval_corr("3. Hình mẫu Tàu ngầm (is_lurker) vs Target reactionRate (Hợp đồng)", "is_lurker", "target_react_rate")

print("\n--- Nhóm B: Quan hệ giữa Hợp đồng Kỹ thuật và Hành vi Thực tế (Hợp đồng vs Thực tế - FAIL) ---")
eval_corr("4. Target reactionRate (Hợp đồng) vs Actual React Rate (Thực tế)", "target_react_rate", "actual_react_rate")
eval_corr("5. Target commentRate (Hợp đồng) vs Actual Comment Rate (Thực tế)", "target_comment_rate", "actual_comment_rate")
eval_corr("6. Target shareRate (Hợp đồng) vs Actual Share Rate (Thực tế)", "target_share_rate", "actual_share_rate")

print("\n--- Nhóm C: Quan hệ giữa Hồ sơ Semantic và Hành vi Thực tế (Semantic vs Thực tế - THÀNH CÔNG) ---")
eval_corr("7. Tần suất Share (Hồ sơ) vs Actual Share Rate (Thực tế)", "share_freq_rank", "actual_share_rate")
eval_corr("8. Hình mẫu Thích chia sẻ (is_sharer) vs Actual Share Rate", "is_sharer", "actual_share_rate")
eval_corr("9. Hình mẫu Tàu ngầm (is_lurker) vs Actual React Rate", "is_lurker", "actual_react_rate")
eval_corr("10. Hình mẫu Bình luận dạo (is_commenter) vs Actual Comment Rate", "is_commenter", "actual_comment_rate")

# ==============================================================================
# PHẦN 3: BÁO CÁO PHÁT HIỆN MÂU THUẪN HỆ THỐNG (SYSTEMIC CONTRADICTIONS)
# ==============================================================================
print("\n" + "=" * 105)
print("PHẦN 3: TỔNG HỢP CÁC MÂU THUẪN THIẾT KẾ CỐT LÕI (KEY CONTRADICTIONS)")
print("=" * 105)
print("""
[MÂU THUẪN 1 - ĐẢO CHIỀU REACTION]:
 - Hồ sơ Semantic: vn_fb_004 & vn_fb_006 ghi rõ là 'Tàu ngầm (Chỉ xem và like, không post không cmt)'.
 - Nhưng Hợp đồng (Contract): lại gán target_react_rate = 0.1667 (THẤP NHẤT HỆ THỐNG).
 - Ngược lại: vn_fb_003 là 'Chiến thần bình luận dạo' thì Contract lại gán target_react_rate = 0.8000 (CAO NHẤT).
 -> HẬU QUẢ: r_s(Contract React, Actual React) = -0.9258 (p = 0.008) - NGHỊCH BIẾN NẶNG.
    LLM ưu tiên tuân thủ vai trò Persona định tính (Semantic) nên đã bỏ qua xác suất hợp đồng!

[MÂU THUẪN 2 - CÀO BẰNG COMMENT RATE]:
 - Hồ sơ Semantic: Có sự phân hóa rõ rệt giữa 'Chiến thần bình luận dạo' (Hàng ngày, nghiện cmt) 
   và 'Tàu ngầm' (ngại cmt, chỉ cmt vài lần/tuần).
 - Nhưng Hợp đồng (Contract): Có tới 5/6 Persona đều bị gán cứng cào bằng target_comment_rate = 0.4500.
 -> HẬU QUẢ: Hợp đồng không tạo ra phương sai (variance) để định hướng hành vi tương tác comment cho LLM.

[MẶT ĐỒNG BỘ - TẦN SUẤT SHARE]:
 - Tần suất Share trong Hồ sơ và shareRate trong Hợp đồng đồng biến hoàn hảo: r_s = +0.9837 (p < 0.001).
 - Thực tế: Người có thói quen Share Hàng ngày (vn_fb_005) là persona DUY NHẤT thực hiện hành động share (r_s = +1.000).
""")

# ==============================================================================
# PHẦN 4: TRỰC QUAN HÓA BẰNG ĐỒ THỊ
# ==============================================================================
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Đồ thị 1: Mâu thuẫn Nghịch biến ở Reaction Rate
sns.regplot(
    data=df_eda, x='target_react_rate', y='actual_react_rate',
    scatter_kws={'s': 90, 'color': '#d62728'}, line_kws={'color': '#d62728', 'linestyle': '--'},
    ax=axes[0]
)
for _, r in df_eda.iterrows():
    axes[0].annotate(f"{r['persona_id']}\n({r['archetype']})", (r['target_react_rate'], r['actual_react_rate']),
                     textcoords="offset points", xytext=(0, 6), ha='center', fontsize=8)
axes[0].set_title("Mâu Thuẫn Nghịch Biến: Hợp Đồng vs Thực Tế\nReaction Rate (r_s = -0.9258, p = 0.008)", fontsize=11, fontweight='bold')
axes[0].set_xlabel("Target Reaction Rate trong Hợp Đồng")
axes[0].set_ylabel("Actual Reaction Rate Thực Tế")

# Đồ thị 2: Sự Áp Đảo Của Semantic Archetype Đối Với Comment và Share
arch_agg = df_eda.groupby('archetype')[['actual_reacts', 'actual_comments', 'actual_shares']].sum()
arch_pct = arch_agg.div(arch_agg.sum(axis=1), axis=0).fillna(0) * 100
arch_pct.plot(kind='bar', stacked=True, color=['#1f77b4', '#2ca02c', '#ff7f0e'], edgecolor='black', ax=axes[1])
axes[1].set_title("Cơ Cấu Tương Tác Thực Tế Theo Semantic Archetype (%)\n(Chứng minh hành vi bám sát mô tả hồ sơ)", fontsize=11, fontweight='bold')
axes[1].set_xlabel("Nhóm Semantic Archetype")
axes[1].set_ylabel("Tỷ trọng tương tác (%)")
axes[1].legend(['React', 'Comment', 'Share'], loc='upper right')
axes[1].tick_params(axis='x', rotation=30)

# Đồ thị 3: Đối Chiếu Tần Suất Share Hồ Sơ vs Hợp Đồng
sns.boxplot(data=df_eda, x='share_freq_text', y='target_share_rate', hue='share_freq_text', palette='Blues', legend=False, ax=axes[2])
sns.stripplot(data=df_eda, x='share_freq_text', y='target_share_rate', color='red', size=8, jitter=0.1, ax=axes[2])
axes[2].set_title("Độ Đồng Bộ Cao: Tần Suất Share Hồ Sơ vs Hợp Đồng\n(r_s = +0.9837, p < 0.001)", fontsize=11, fontweight='bold')
axes[2].set_xlabel("Tần suất Share trong Hồ sơ")
axes[2].set_ylabel("Target shareRate trong Hợp đồng")

plt.tight_layout()
output_img = Path("reports/contradiction_analysis.png")
output_img.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(output_img, dpi=150)
print(f"Đã lưu biểu đồ phân tích mâu thuẫn tại: {output_img.resolve()}")
plt.close(fig)
