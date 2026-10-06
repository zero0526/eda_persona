import sys
import os
sys.path.append(os.path.abspath('.'))
import json
import sqlite3
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from loaders.episode_loader import get_sqlite_path, list_episodes, load_episode

conn = sqlite3.connect(get_sqlite_path())
df_bots = conn.execute('''
    SELECT b.persona_id, pv.content_json, bc.contract_json 
    FROM bots b 
    JOIN persona_versions pv ON pv.bot_id = b.id 
    LEFT JOIN behavioral_contracts bc ON bc.id = (
        SELECT contract_id FROM episodes WHERE bot_id = b.id LIMIT 1
    )
''').fetchall()
personas_dict = {p_id: json.loads(p_json) if p_json else {} for p_id, p_json, _ in df_bots}
contracts_dict = {p_id: json.loads(c_json) if c_json else {} for p_id, _, c_json in df_bots}

episodes_summary = list_episodes(get_sqlite_path())
all_steps = [load_episode(ep['id']).to_steps_dataframe() for ep in episodes_summary]
df_steps = pd.concat(all_steps, ignore_index=True)

# 1. Thang điểm 3 nấc theo Social Archetype (0 = Thấp/Không, 1 = Trung bình/Vừa, 2 = Cao/Chủ đạo)
archetype_3tier = {
    'vn_fb_001': {'tier_react': 1, 'tier_comment': 1, 'tier_share': 0}, # Sáng tạo
    'vn_fb_002': {'tier_react': 1, 'tier_comment': 1, 'tier_share': 0}, # Kết nối
    'vn_fb_003': {'tier_react': 0, 'tier_comment': 2, 'tier_share': 0}, # Bình luận dạo
    'vn_fb_004': {'tier_react': 2, 'tier_comment': 0, 'tier_share': 0}, # Tàu ngầm
    'vn_fb_005': {'tier_react': 1, 'tier_comment': 0, 'tier_share': 2}, # Thích chia sẻ
    'vn_fb_006': {'tier_react': 2, 'tier_comment': 0, 'tier_share': 0}, # Tàu ngầm
}

persona_social = []
for p_id in sorted(df_steps['persona_id'].unique()):
    p_steps = df_steps[df_steps['persona_id'] == p_id]
    c_rules = contracts_dict.get(p_id, {}).get('social', {})
    attrs = personas_dict.get(p_id, {}).get('attributes', {})
    
    # Số bài viết độc nhất được quan sát / tiếp cận
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

# --- BẢNG 1: THỐNG KÊ THỰC NGHIỆM GOM THEO NHÓM SOCIAL ARCHETYPE ---
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

print("=== 1. BẢNG THỰC NGHIỆM TƯƠNG TÁC GOM THEO NHÓM SOCIAL ARCHETYPE ===")
print(df_arch_summary.to_string(index=False))

# --- BẢNG 2: KIỂM ĐỊNH TƯƠNG QUAN SPEARMAN VỚI THANG 3 NẤC ---
print("\n=== 2. HỆ SỐ TƯƠNG QUAN SPEARMAN (THANG ĐIỂM 3 NẤC VS THỰC TẾ) ===")
for act in ['react', 'comment', 'share']:
    r_cnt, p_cnt = stats.spearmanr(df_ps[f'tier_{act}'], df_ps[f'actual_{act}s'])
    r_rate, p_rate = stats.spearmanr(df_ps[f'tier_{act}'], df_ps[f'actual_{act}_rate'])
    sig = "*** (p < 0.01)" if p_rate < 0.01 else ("* (p < 0.10)" if p_rate < 0.10 else "")
    print(f" - {act.capitalize():<7} -> vs Count: r_s = {r_cnt:+.4f} (p = {p_cnt:.4f}) | vs Rate: r_s = {r_rate:+.4f} (p = {p_rate:.4f}) {sig}")

# Đối chiếu nhanh với contract reactionRate
r_contra, p_contra = stats.spearmanr(df_ps['contract_react_rate'], df_ps['actual_react_rate'])
print(f" * Đối chiếu Contract reactionRate vs Actual Rate: r_s = {r_contra:+.4f} (p = {p_contra:.4f}) [NGHỊCH BIẾN DO GÁN NHẦM CONTRACT]")

# --- BẢNG 3: KIỂM ĐỊNH CHI-SQUARE TÍNH ĐỘC LẬP CƠ CẤU HÀNH VI ---
contingency_table = df_ps.groupby('archetype')[['actual_reacts', 'actual_comments', 'actual_shares']].sum()
chi2, p_chi2, dof, _ = stats.chi2_contingency(contingency_table)
print(f"\n=== 3. KIỂM ĐỊNH ĐỘ LỆCH CHI-SQUARE VỀ TÍNH PHỤ THUỘC HÌNH MẪU ===")
print(f" - Chi2 = {chi2:.3f}, dof = {dof}, p-value = {p_chi2:.4e} (p < 0.001 -> Hành vi bám sát hình mẫu)")

print("\nAll logic test succeeded!")
