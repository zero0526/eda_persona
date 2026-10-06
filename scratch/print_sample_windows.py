import sqlite3
import json
import sys
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

conn = sqlite3.connect(r"D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("""
    SELECT w.id, b.persona_id, w.start_at, w.end_at, w.surface_bias, w.reason
    FROM activity_windows w
    JOIN bots b ON b.id = w.bot_id
    LIMIT 3
""")

rows = [dict(r) for r in cur.fetchall()]
for r in rows:
    start_utc = pd.to_datetime(r["start_at"])
    end_utc = pd.to_datetime(r["end_at"])
    start_vn = start_utc.tz_convert("Asia/Ho_Chi_Minh")
    dur_min = (end_utc - start_utc).total_seconds() / 60.0
    bias = json.loads(r["surface_bias"]) if r["surface_bias"] else {}
    print(f"Persona: {r['persona_id']}")
    print(f"  - start_at (UTC): {r['start_at']} -> Giờ VN (UTC+7): {start_vn.strftime('%Y-%m-%d %H:%M')} (Hour: {start_vn.hour})")
    print(f"  - duration_min: {dur_min:.1f} phút")
    print(f"  - surface_bias: {bias} (bias_feed={bias.get('feed')}, bias_reels={bias.get('reels')})")
    print(f"  - is_late_night (>=21h): {int(start_vn.hour >= 21)}")
    print(f"  - is_early_morning (<=8h): {int(start_vn.hour <= 8)}")
    print(f"  - Reason: {r['reason']}\n")

conn.close()
