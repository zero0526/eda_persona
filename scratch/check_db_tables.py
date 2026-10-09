import sys
from pathlib import Path
import sqlite3
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from loaders.episode_loader import DEFAULT_SQLITE_PATH

print("Using DB path:", DEFAULT_SQLITE_PATH)
conn = sqlite3.connect(DEFAULT_SQLITE_PATH)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in SQLite:", [t[0] for t in tables])

for t in [tab[0] for tab in tables]:
    cursor.execute(f"SELECT count(*) FROM {t}")
    cnt = cursor.fetchone()[0]
    cursor.execute(f"PRAGMA table_info({t});")
    cols = [col[1] for col in cursor.fetchall()]
    print(f"\nTable '{t}' ({cnt} rows):")
    print(f"  Columns: {cols}")

conn.close()
