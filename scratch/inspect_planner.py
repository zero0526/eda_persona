import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')
from loaders.episode_loader import get_sqlite_path

conn = sqlite3.connect(get_sqlite_path())
cur = conn.cursor()
cur.execute("SELECT b.persona_id, p.request_json, p.response_json FROM planning_attempts p JOIN bots b ON p.bot_id = b.id WHERE b.persona_id = 'vn_fb_004' LIMIT 1")
row = cur.fetchone()
if row:
    req = json.loads(row[1])
    print("inferred_habits:", json.dumps(req.get('inferred_habits'), ensure_ascii=False, indent=2))
    print("identity:", json.dumps(req.get('identity'), ensure_ascii=False, indent=2))
    p = req.get('persona', {})
    print("persona habits/limits:", {k: v for k, v in p.items() if 'habit' in k or 'limit' in k or 'time' in k or 'session' in k})
