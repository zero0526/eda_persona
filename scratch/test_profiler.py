import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from loaders.action_loader import ActionLoader
from loaders.episode_loader import get_sqlite_path
import sqlite3, json, re
import pandas as pd
import numpy as np

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)
df_sessions = loader.to_unified_sessions_dataframe(histories)

# Test extract_cross_session_entities dynamically
sqlite_file = get_sqlite_path()
conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()

# Get group affinities display names
cursor.execute("SELECT entity_type, entity_key, display_name, url FROM entity_affinities WHERE entity_type='group'")
group_affinities = cursor.fetchall()
group_map = {}
for g in group_affinities:
    # map both url and group id
    if g[3]:
        group_map[g[3]] = g[2]
        m = re.search(r'/groups/([^/]+)', g[3])
        if m:
            group_map[m.group(1)] = g[2]

# Get episodes to session order mapping
cursor.execute('''
    SELECT e.id, b.persona_id, w.start_at
    FROM episodes e
    JOIN bots b ON e.bot_id = b.id
    LEFT JOIN activity_windows w ON e.window_id = w.id
    ORDER BY b.persona_id, w.start_at;
''')
episodes_info = cursor.fetchall()
ep_map = {}
p_order = {}
for ep_id, p_id, start_at in episodes_info:
    p_order[p_id] = p_order.get(p_id, 0) + 1
    ep_map[ep_id] = {'persona_id': p_id, 'session_order': p_order[p_id]}

cursor.execute("SELECT episode_id, payload_json FROM episode_events WHERE kind = 'tool_result';")
events = cursor.fetchall()
conn.close()

parsed_entities = []
for ep_id, p_str in events:
    if not p_str or ep_id not in ep_map:
        continue
    info = ep_map[ep_id]
    try:
        p = json.loads(p_str)
        tc = p.get('target_candidate')
        if not tc or not isinstance(tc, dict):
            continue
        text = tc.get('text', '')
        url = tc.get('url', '')
        if not text and not url:
            continue
            
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        author = 'Unknown'
        if lines:
            if lines[0] in ['Chỉ báo trạng thái online', 'Đang hoạt động'] and len(lines) > 2:
                author = lines[2]
            else:
                author = lines[0]
                
        group_name = None
        group_id_match = re.search(r'/groups/([^/]+)', url)
        if group_id_match:
            gid = group_id_match.group(1)
            group_name = group_map.get(gid, group_map.get(url, f"Hội nhóm ({gid})"))
            
        parsed_entities.append({
            'persona_id': info['persona_id'],
            'session_order': info['session_order'],
            'author': author,
            'group_name': group_name,
            'url': url
        })
    except Exception:
        pass

df_ent = pd.DataFrame(parsed_entities)
cond_ent_13 = (df_ent['session_order'].isin([1, 2])) | ((df_ent['persona_id'] == 'vn_fb_006') & (df_ent['session_order'] == 3))
df_ent_13 = df_ent[cond_ent_13].copy()

# Dynamic entity continuity map
pairs = [
    ('vn_fb_001', 1, 2),
    ('vn_fb_002', 1, 2),
    ('vn_fb_003', 1, 2),
    ('vn_fb_004', 1, 2),
    ('vn_fb_005', 1, 2),
    ('vn_fb_006', 1, 2),
    ('vn_fb_006', 2, 3),
    ('vn_fb_006', 1, 3)
]

continuity_map = {}
for pid, s1, s2 in pairs:
    pair_label = f"S{s1} -> S{s2}"
    sub = df_ent_13[df_ent_13['persona_id'] == pid]
    
    auth_s1 = set(sub[sub['session_order'] == s1]['author'].dropna().unique()) - {'Unknown'}
    auth_s2 = set(sub[sub['session_order'] == s2]['author'].dropna().unique()) - {'Unknown'}
    common_auth = sorted(list(auth_s1 & auth_s2))
    
    grp_s1 = set(sub[sub['session_order'] == s1]['group_name'].dropna().unique())
    grp_s2 = set(sub[sub['session_order'] == s2]['group_name'].dropna().unique())
    common_grp = sorted(list(grp_s1 & grp_s2))
    
    parts = []
    if common_auth:
        parts.append(f"{len(common_auth)} trang ({', '.join(common_auth)})")
    if common_grp:
        parts.append(f"{len(common_grp)} nhóm ({', '.join(common_grp)})")
        
    continuity_map[(pid, pair_label)] = ' + '.join(parts) if parts else '0 (Không lặp lại)'

print("Dynamic continuity map:")
for k, v in continuity_map.items():
    print(k, "->", v)

# Repeated authors
p_author_stats = df_ent_13[df_ent_13['author'] != 'Unknown'].groupby(['persona_id', 'author'])['session_order'].agg(
    sessions=lambda s: sorted(list(s.unique())),
    n_sessions='nunique',
    total_actions='count'
).reset_index()
cross_authors_df = p_author_stats[p_author_stats['n_sessions'] > 1].sort_values('total_actions', ascending=False)
print("\nCross authors df count:", len(cross_authors_df))

# Repeated groups
p_group_stats = df_ent_13[df_ent_13['group_name'].notna()].groupby(['persona_id', 'group_name'])['session_order'].agg(
    sessions=lambda s: sorted(list(s.unique())),
    n_sessions='nunique',
    total_actions='count'
).reset_index()
cross_groups_df = p_group_stats[p_group_stats['n_sessions'] > 1].sort_values('total_actions', ascending=False)
print("Cross groups df count:", len(cross_groups_df))
print(cross_groups_df)
