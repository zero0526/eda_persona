import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')
from loaders.episode_loader import get_sqlite_path

conn = sqlite3.connect(get_sqlite_path())
cur = conn.cursor()
cur.execute('SELECT pv.content_json FROM persona_versions pv LIMIT 1')
row = cur.fetchone()
data = json.loads(row[0])
attrs = data.get('attributes', {})

print("=== SEARCHING KEYS ===")
for k in attrs.keys():
    k_lower = k.lower()
    if any(w in k_lower for w in ['giới tính', 'định dạng', 'video', 'nội dung', 'format', 'tương tác', 'hành vi']):
        print(f"Key: {k} -> Value: {attrs[k]}")
