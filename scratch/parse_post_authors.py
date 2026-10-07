import sqlite3
import json
import re
import pandas as pd
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect("data/persona-runner.sqlite")
cursor = conn.cursor()

# Map episode_id to persona_id and session_order
cursor.execute("""
    SELECT e.id, b.persona_id, w.start_at
    FROM episodes e
    JOIN bots b ON e.bot_id = b.id
    LEFT JOIN activity_windows w ON e.window_id = w.id
    ORDER BY b.persona_id, w.start_at;
""")
episodes_info = cursor.fetchall()
ep_map = {}
p_order = {}
for ep_id, p_id, start_at in episodes_info:
    p_order[p_id] = p_order.get(p_id, 0) + 1
    ep_map[ep_id] = {'persona_id': p_id, 'session_order': p_order[p_id]}

cursor.execute("SELECT episode_id, payload_json FROM episode_events WHERE kind = 'tool_result';")
events = cursor.fetchall()

parsed_posts = []
for ep_id, p_str in events:
    if not p_str:
        continue
    try:
        p = json.loads(p_str)
        info = ep_map.get(ep_id, {'persona_id': 'unknown', 'session_order': 0})
        tc = p.get('target_candidate')
        if not tc or not isinstance(tc, dict):
            continue
        
        kind = tc.get('kind', '')
        text = tc.get('text', '')
        url = tc.get('url', '')
        tool = p.get('resolved_tool', p.get('tool', ''))
        
        if not text and not url:
            continue
            
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        author = "Unknown"
        snippet = ""
        if lines:
            if lines[0] in ["Chỉ báo trạng thái online", "Đang hoạt động"] and len(lines) > 2:
                author = lines[2]
                snippet = " ".join(lines[3:6])
            else:
                author = lines[0]
                snippet = " ".join(lines[1:4])
        
        group_id_match = re.search(r'/groups/([^/]+)', url)
        group_name = group_id_match.group(1) if group_id_match else None
        
        parsed_posts.append({
            'persona_id': info['persona_id'],
            'session_order': info['session_order'],
            'episode_id': ep_id,
            'tool': tool,
            'author': author,
            'group': group_name,
            'url': url,
            'snippet': snippet[:120],
            'raw_text': text[:200]
        })
    except Exception as e:
        pass

df_p = pd.DataFrame(parsed_posts)
print(f"Total parsed post interactions: {len(df_p)}")
print("\nUnique authors found:", df_p['author'].nunique())
print("Unique URLs found:", df_p['url'].nunique())
print("Unique Groups found:", df_p['group'].dropna().nunique())

# 1. Authors across sessions
author_summary = df_p.groupby('author').agg(
    total_interactions=('url', 'count'),
    distinct_personas=('persona_id', lambda s: sorted(s.unique())),
    distinct_sessions=('session_order', lambda s: sorted(s.unique())),
    sessions_count=('session_order', 'nunique'),
    personas_count=('persona_id', 'nunique'),
    sample_url=('url', 'first'),
    sample_snippet=('snippet', 'first')
).reset_index()

cross_session_authors = author_summary[author_summary['sessions_count'] > 1].sort_values('total_interactions', ascending=False)
print("\n=== AUTHORS / PAGES INTERACTED ACROSS MULTIPLE SESSIONS ===")
print(cross_session_authors[['author', 'personas_count', 'sessions_count', 'total_interactions', 'distinct_personas', 'distinct_sessions']])

# 2. Same Persona, Multiple Sessions for same author
p_author = df_p.groupby(['persona_id', 'author']).agg(
    sessions=('session_order', lambda s: sorted(s.unique())),
    n_sessions=('session_order', 'nunique'),
    total_actions=('url', 'count')
).reset_index()
cross_p_authors = p_author[p_author['n_sessions'] > 1]
print("\n=== AUTHORS INTERACTED BY SAME PERSONA ACROSS MULTIPLE SESSIONS ===")
print(cross_p_authors)

# 3. Groups across sessions
group_summary = df_p[df_p['group'].notna()].groupby('group').agg(
    total_interactions=('url', 'count'),
    distinct_personas=('persona_id', lambda s: sorted(s.unique())),
    distinct_sessions=('session_order', lambda s: sorted(s.unique())),
    sessions_count=('session_order', 'nunique'),
    personas_count=('persona_id', 'nunique'),
    sample_author=('author', 'first'),
    sample_snippet=('snippet', 'first')
).reset_index()
print("\n=== GROUPS INTERACTED ACROSS SESSIONS ===")
print(group_summary)

# 4. Same exact post URL across sessions
url_summary = df_p.groupby('url').agg(
    total_interactions=('author', 'count'),
    distinct_personas=('persona_id', lambda s: sorted(s.unique())),
    distinct_sessions=('session_order', lambda s: sorted(s.unique())),
    sessions_count=('session_order', 'nunique'),
    sample_author=('author', 'first'),
    sample_snippet=('snippet', 'first')
).reset_index()
cross_posts = url_summary[url_summary['sessions_count'] > 1]
print("\n=== EXACT POST URLs INTERACTED ACROSS MULTIPLE SESSIONS ===")
print(cross_posts[['url', 'sample_author', 'sessions_count', 'distinct_personas', 'distinct_sessions', 'total_interactions']])

conn.close()
