import sys, os
sys.path.append(os.path.abspath('.'))
import json, sqlite3, pandas as pd, numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from loaders.episode_loader import get_sqlite_path, list_episodes, load_episode

conn = sqlite3.connect(get_sqlite_path())
df_bots = conn.execute('SELECT b.persona_id, pv.content_json, bc.contract_json FROM bots b JOIN persona_versions pv ON pv.bot_id = b.id LEFT JOIN behavioral_contracts bc ON bc.id = (SELECT contract_id FROM episodes WHERE bot_id = b.id LIMIT 1)').fetchall()
personas_dict = {p_id: json.loads(p_json) if p_json else {} for p_id, p_json, _ in df_bots}
contracts_dict = {p_id: json.loads(c_json) if c_json else {} for p_id, _, c_json in df_bots}

episodes_summary = list_episodes(get_sqlite_path())
all_steps = [load_episode(ep['id']).to_steps_dataframe() for ep in episodes_summary]
df_steps = pd.concat(all_steps, ignore_index=True)

archetype_3tier = {
    'vn_fb_001': {'tier_react': 1, 'tier_comment': 1, 'tier_share': 0},
    'vn_fb_002': {'tier_react': 1, 'tier_comment': 1, 'tier_share': 0},
    'vn_fb_003': {'tier_react': 0, 'tier_comment': 2, 'tier_share': 0},
    'vn_fb_004': {'tier_react': 2, 'tier_comment': 0, 'tier_share': 0},
    'vn_fb_005': {'tier_react': 1, 'tier_comment': 0, 'tier_share': 2},
    'vn_fb_006': {'tier_react': 2, 'tier_comment': 0, 'tier_share': 0},
}

data = []
for p_id in sorted(df_steps['persona_id'].unique()):
    p_steps = df_steps[df_steps['persona_id'] == p_id]
    c_rules = contracts_dict.get(p_id, {}).get('social', {})
    attrs = personas_dict.get(p_id, {}).get('attributes', {})
    tier = archetype_3tier.get(p_id, {})
    
    interactive_steps = p_steps[p_steps['intent'].isin(['read', 'expand', 'open', 'react', 'comment', 'share'])]
    unique_posts = interactive_steps['target_id'].nunique() if 'target_id' in interactive_steps.columns else 0
    
    reacts = (p_steps['intent'] == 'react').sum()
    comments = (p_steps['intent'] == 'comment').sum()
    shares = (p_steps['intent'] == 'share').sum()
    total_eng = reacts + comments + shares
    arch_clean = attrs.get('Cách thường tham gia và tương tác trên các nền tảng trực tuyến.', 'Khác').split('(')[0].strip()
    
    data.append({
        'persona_id': p_id,
        'archetype': arch_clean,
        'tier_react': tier['tier_react'],
        'tier_comment': tier['tier_comment'],
        'tier_share': tier['tier_share'],
        'contract_react': c_rules.get('reactionRate', np.nan),
        'contract_comment': c_rules.get('commentRate', np.nan),
        'contract_share': c_rules.get('shareRate', np.nan),
        'actual_reacts': reacts,
        'actual_react_rate': reacts / unique_posts if unique_posts > 0 else 0,
        'actual_comments': comments,
        'actual_comment_rate': comments / unique_posts if unique_posts > 0 else 0,
        'actual_shares': shares,
        'actual_share_rate': shares / unique_posts if unique_posts > 0 else 0,
        'total_eng': total_eng
    })

df = pd.DataFrame(data)

# Ma trận Heatmap
rows_list = [
    ('Reaction (Thang 3 Nấc Archetype)', 'tier_react', 'actual_reacts', 'actual_react_rate'),
    ('Comment (Thang 3 Nấc Archetype)', 'tier_comment', 'actual_comments', 'actual_comment_rate'),
    ('Share (Thang 3 Nấc Archetype)', 'tier_share', 'actual_shares', 'actual_share_rate'),
    ('Đối chiếu: Reaction (Hợp đồng Contract)', 'contract_react', 'actual_reacts', 'actual_react_rate'),
    ('Đối chiếu: Comment (Hợp đồng Contract)', 'contract_comment', 'actual_comments', 'actual_comment_rate'),
    ('Đối chiếu: Share (Hợp đồng Contract)', 'contract_share', 'actual_shares', 'actual_share_rate'),
]

matrix_r = []
matrix_labels = []
row_names = []

for label, pred_col, cnt_col, rate_col in rows_list:
    r_cnt, p_cnt = stats.spearmanr(df[pred_col], df[cnt_col])
    r_rate, p_rate = stats.spearmanr(df[pred_col], df[rate_col])
    row_names.append(label)
    matrix_r.append([r_cnt, r_rate])
    
    sig_cnt = "***" if p_cnt < 0.01 else ("**" if p_cnt < 0.05 else ("*" if p_cnt < 0.1 else ""))
    sig_rate = "***" if p_rate < 0.01 else ("**" if p_rate < 0.05 else ("*" if p_rate < 0.1 else ""))
    lbl_cnt = f"r = {r_cnt:+.2f}\\n(p = {p_cnt:.3f}){sig_cnt}"
    lbl_rate = f"r = {r_rate:+.2f}\\n(p = {p_rate:.3f}){sig_rate}"
    matrix_labels.append([lbl_cnt, lbl_rate])

df_r = pd.DataFrame(matrix_r, index=row_names, columns=['vs Số lượng thực tế (Count)', 'vs Tỷ lệ chuẩn hóa (Rate)'])
annot_matrix = np.array(matrix_labels)

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Panel 1: Cơ cấu tương tác theo Nhóm Archetype
contingency_table = df.groupby('archetype')[['actual_reacts', 'actual_comments', 'actual_shares']].sum()
df_norm_pct = contingency_table.div(contingency_table.sum(axis=1), axis=0).fillna(0) * 100
df_norm_pct.columns = ['React (%)', 'Comment (%)', 'Share (%)']
df_norm_pct.plot(kind='barh', stacked=True, color=['#1f77b4', '#2ca02c', '#d62728'], edgecolor='black', ax=axes[0])
axes[0].set_title("Cơ Cấu Tương Tác Xã Hội (%) Theo Nhóm Social Archetype\\n(Chiến thần cmt 100% comment | Tàu ngầm >85% like | Thích chia sẻ độc quyền share)", fontsize=11, fontweight='bold')
axes[0].set_xlabel("Tỷ trọng tương tác (%)")
axes[0].set_ylabel("Nhóm Social Archetype")
axes[0].legend(loc='lower right')

# Panel 2: Heatmap Spearman
sns.heatmap(
    df_r,
    annot=annot_matrix,
    fmt="",
    cmap="RdYlGn",
    vmin=-1.0,
    vmax=1.0,
    center=0.0,
    cbar_kws={'label': 'Hệ số tương quan Spearman (r_s)'},
    linewidths=1.5,
    linecolor='white',
    ax=axes[1]
)
axes[1].set_title("Ma Trận Nhiệt (Heatmap) Tương Quan Spearman\\nThang 3 Nấc Archetype vs Hợp Đồng Contract", fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('scratch/combined_layout_test.png', dpi=120)
print('Saved combined layout test successfully!')
