import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
db_path = r'D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite'
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = c.fetchall()
print(f"Total tables: {len(tables)}")
for (t,) in tables:
    c.execute(f"SELECT COUNT(*) FROM {t};")
    cnt = c.fetchone()[0]
    print(f"{t:32s}: {cnt:6d} rows")
conn.close()
