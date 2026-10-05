import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
db_path = r'D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite'
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = [t[0] for t in c.fetchall()]

episode_tables = []
for t in tables:
    c.execute(f"PRAGMA table_info({t});")
    cols = [col[1] for col in c.fetchall()]
    if 'episode_id' in cols or t == 'episodes' or 'id' in cols and t.startswith('episode'):
        episode_tables.append((t, cols))

print(f"Tables with episode relation ({len(episode_tables)}):")
for t, cols in episode_tables:
    print(f"\nTable: {t}")
    for col in cols:
        print(f"   {col}")

# Check episodes table details
print("\n=== EPISODES TABLE COLUMNS & SAMPLE ===")
c.execute("PRAGMA table_info(episodes);")
for col in c.fetchall():
    print(col)

c.execute("SELECT * FROM episodes LIMIT 1;")
row = c.fetchone()
c.execute("PRAGMA table_info(episodes);")
colnames = [col[1] for col in c.fetchall()]
for k, v in zip(colnames, row):
    print(f"  {k}: {str(v)[:120]}")

conn.close()
