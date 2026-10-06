import sqlite3, json
import pandas as pd
from loaders.episode_loader import get_sqlite_path

conn = sqlite3.connect(get_sqlite_path())
df_bots = pd.read_sql_query('''
    SELECT b.persona_id, pv.content_json
    FROM bots b
    JOIN persona_versions pv ON pv.bot_id = b.id
''', conn)
conn.close()

all_attrs = {}
for _, row in df_bots.iterrows():
    p_id = row['persona_id']
    content = json.loads(row['content_json'])
    all_attrs[p_id] = content.get('attributes', {})

p_ids = sorted(all_attrs.keys())

# Find relevant fields
keywords = ['video', 'nhóm', 'group', 'cộng đồng', 'nội dung', 'tìm', 'thông tin', 'tin tức', 'đọc', 'xem', 'lướt', 'chi tiết', 'thảo luận', 'tham gia', 'mạng xã hội', 'chú ý', 'thói quen']

matched_keys = set()
for k in all_attrs[p_ids[0]].keys():
    k_lower = k.lower()
    if any(w in k_lower for w in keywords):
        matched_keys.add(k)

print(f"Matched {len(matched_keys)} fields:")
for k in sorted(matched_keys):
    # check if values vary across personas
    vals = [all_attrs[pid].get(k, '') for pid in p_ids]
    print(f"\n--- [TRƯỜNG] {k} ---")
    for pid, v in zip(p_ids, vals):
        print(f"  {pid}: {v}")
