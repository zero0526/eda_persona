import sys, os
sys.path.append(os.path.abspath('.'))
import json, sqlite3, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')
from loaders.episode_loader import get_sqlite_path, list_episodes, load_episode

conn = sqlite3.connect(get_sqlite_path())
df_bots = conn.execute('SELECT b.persona_id, pv.content_json FROM bots b JOIN persona_versions pv ON pv.bot_id = b.id').fetchall()
personas_dict = {p_id: json.loads(p_json) if p_json else {} for p_id, p_json in df_bots}

episodes_summary = list_episodes(get_sqlite_path())
all_steps = [load_episode(ep['id']).to_steps_dataframe() for ep in episodes_summary]
df_steps = pd.concat(all_steps, ignore_index=True)

ct = pd.crosstab(df_steps['persona_id'], df_steps['surface'].fillna('unknown'), normalize='index') * 100

rows = []
for p_id in ct.index:
    attrs = personas_dict.get(p_id, {}).get('attributes', {})
    age = attrs.get('Nhóm tuổi', '')
    gen = attrs.get('Nhóm thế hệ dựa trên thời kỳ họ sinh ra, thường được dùng để mô tả những trải nghiệm xã hội và công nghệ chung.', '')
    fmt = attrs.get('Loại hình nội dung yêu thích nhất', '')
    grp = attrs.get('Mức độ sinh hoạt trong các hội nhóm và cộng đồng mạng xã hội.', '')
    arch = attrs.get('Cách thường tham gia và tương tác trên các nền tảng trực tuyến.', '').split('(')[0].strip()
    
    rows.append({
        'persona_id': p_id,
        'Demographics': f"{age} ({gen})",
        'Nội dung yêu thích': fmt,
        'Sinh hoạt Group': grp,
        'Archetype': arch,
        'Feed (%)': f"{ct.loc[p_id, 'feed']:.1f}%",
        'Reels (%)': f"{ct.loc[p_id, 'reels']:.1f}%" if 'reels' in ct.columns else '0.0%',
        'Group (%)': f"{ct.loc[p_id, 'group']:.1f}%" if 'group' in ct.columns else '0.0%',
        'Detail (%)': f"{ct.loc[p_id, 'detail']:.1f}%" if 'detail' in ct.columns else '0.0%',
        'Search (%)': f"{ct.loc[p_id, 'search']:.1f}%" if 'search' in ct.columns else '0.0%',
    })

df_res = pd.DataFrame(rows)
print(df_res.to_string(index=False))
