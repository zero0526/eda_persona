import sqlite3
import json
import re
import pandas as pd
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect("data/persona-runner.sqlite")
cursor = conn.cursor()

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
        })
    except Exception as e:
        pass

df_p = pd.DataFrame(parsed_posts)

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("=== 1. TẤT CẢ TÁC GIẢ / FANPAGE / USER XUẤT HIỆN XUYÊN CÁC PHIÊN ===")
author_summary = df_p.groupby('author').agg(
    total_interactions=('url', 'count'),
    distinct_personas=('persona_id', lambda s: sorted(s.unique())),
    distinct_sessions=('session_order', lambda s: sorted(s.unique())),
    sessions_count=('session_order', 'nunique'),
    personas_count=('persona_id', 'nunique'),
    sample_snippet=('snippet', 'first')
).reset_index()

cross_authors = author_summary[author_summary['sessions_count'] > 1].sort_values('total_interactions', ascending=False)
for idx, r in cross_authors.iterrows():
    print(f"\n* Tác giả: [{r['author']}]")
    print(f"  - Tổng tương tác: {r['total_interactions']} lần")
    print(f"  - Các Persona: {r['distinct_personas']} (Số lượng: {r['personas_count']})")
    print(f"  - Các Phiên: {r['distinct_sessions']} (Số phiên: {r['sessions_count']})")
    print(f"  - Trích đoạn: {r['sample_snippet'][:100]}")

print("\n=== 2. TÁC GIẢ ĐƯỢC CÙNG 1 PERSONA TƯƠNG TÁC LẠI Ở PHIÊN TIẾP THEO (INTRA-PERSONA RETENTION) ===")
p_author = df_p.groupby(['persona_id', 'author']).agg(
    sessions=('session_order', lambda s: sorted(s.unique())),
    n_sessions=('session_order', 'nunique'),
    total_actions=('url', 'count'),
    sample_snippet=('snippet', 'first')
).reset_index()
cross_p = p_author[p_author['n_sessions'] > 1]
for idx, r in cross_p.iterrows():
    print(f"\n* Persona {r['persona_id']} -> Tác giả [{r['author']}]:")
    print(f"  - Xuất hiện ở các Phiên: S{r['sessions']}")
    print(f"  - Tổng số thao tác: {r['total_actions']}")
    print(f"  - Nội dung: {r['sample_snippet'][:100]}")

print("\n=== 3. HỘI NHÓM (GROUPS) ĐƯỢC TƯƠNG TÁC XUYÊN CÁC PHIÊN ===")
group_names = {
    '2133631560242753': 'Bất Động Sản Cần Thơ - Batdongsancantho.vn (63K thành viên)',
    '306716320482601': 'Măm Măm Đà Nẵng (296K thành viên)',
    'groupcovua': 'Cờ Vua đam mê (46K thành viên)'
}
group_summary = df_p[df_p['group'].notna()].groupby('group').agg(
    total_interactions=('url', 'count'),
    distinct_personas=('persona_id', lambda s: sorted(s.unique())),
    distinct_sessions=('session_order', lambda s: sorted(s.unique())),
    n_sessions=('session_order', 'nunique'),
).reset_index()
for idx, r in group_summary.iterrows():
    g_name = group_names.get(r['group'], r['group'])
    print(f"\n* Nhóm: [{g_name}] (ID: {r['group']})")
    print(f"  - Tổng tương tác: {r['total_interactions']}")
    print(f"  - Personas tham gia: {r['distinct_personas']}")
    print(f"  - Các Phiên: S{r['distinct_sessions']} ({r['n_sessions']} phiên)")

print("\n=== 4. CÙNG 1 BÀI VIẾT (EXACT POST / URL) ĐƯỢC TƯƠNG TÁC LẠI XUYÊN PHIÊN ===")
url_summary = df_p.groupby('url').agg(
    total_interactions=('author', 'count'),
    distinct_personas=('persona_id', lambda s: sorted(s.unique())),
    distinct_sessions=('session_order', lambda s: sorted(s.unique())),
    sessions_count=('session_order', 'nunique'),
    sample_author=('author', 'first'),
    sample_snippet=('snippet', 'first')
).reset_index()
cross_urls = url_summary[url_summary['sessions_count'] > 1]
for idx, r in cross_urls.iterrows():
    print(f"\n* URL: {r['url']}")
    print(f"  - Tác giả: {r['sample_author']}")
    print(f"  - Personas: {r['distinct_personas']}")
    print(f"  - Các Phiên: S{r['distinct_sessions']}")
    print(f"  - Nội dung: {r['sample_snippet'][:100]}")

conn.close()
