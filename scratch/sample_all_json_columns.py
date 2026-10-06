import sys, os, sqlite3, json
sys.path.append(os.path.abspath('.'))
from loaders.episode_loader import get_sqlite_path

conn = sqlite3.connect(get_sqlite_path())
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = [r[0] for r in cur.fetchall()]

for table in tables:
    cur.execute(f"PRAGMA table_info(`{table}`);")
    cols = [dict(c) for c in cur.fetchall()]
    
    # Check each column for JSON content
    for col in cols:
        c_name = col['name']
        cur.execute(f"SELECT `{c_name}` FROM `{table}` WHERE `{c_name}` IS NOT NULL AND `{c_name}` != '' LIMIT 3;")
        rows = cur.fetchall()
        for r in rows:
            val = r[0]
            if isinstance(val, str) and (val.strip().startswith('{') or val.strip().startswith('[')):
                try:
                    parsed = json.loads(val)
                    print(f"=== {table}.{c_name} ({type(parsed).__name__}) ===")
                    if isinstance(parsed, dict):
                        print("  Keys:", list(parsed.keys()))
                        for k, v in list(parsed.items())[:6]:
                            print(f"    {k}: {type(v).__name__}")
                    elif isinstance(parsed, list):
                        print("  List len:", len(parsed))
                        if parsed and isinstance(parsed[0], dict):
                            print("  Item keys:", list(parsed[0].keys()))
                            for k, v in list(parsed[0].items())[:6]:
                                print(f"    {k}: {type(v).__name__}")
                        elif parsed:
                            print("  Item type:", type(parsed[0]).__name__)
                    print()
                    break
                except Exception:
                    pass
