import sys, os
sys.path.append(os.path.abspath('.'))
import sqlite3
from loaders.episode_loader import get_sqlite_path

conn = sqlite3.connect(get_sqlite_path())
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
all_tables = [r[0] for r in cursor.fetchall()]
print(f"Total tables in SQLite database ({len(all_tables)} tables):\n")

table_counts = {}
for t in all_tables:
    cursor.execute(f"SELECT count(*) FROM `{t}`;")
    cnt = cursor.fetchone()[0]
    table_counts[t] = cnt
    print(f" - {t:32s}: {cnt:6d} rows")
