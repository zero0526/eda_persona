import sqlite3
import json
import sys
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

db_path = r"D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

cur = conn.cursor()
cur.execute("""
    SELECT b.id as bot_id, b.persona_id, pv.content_json
    FROM bots b
    JOIN persona_versions pv ON pv.bot_id = b.id
    ORDER BY b.persona_id
""")

personas_info = []
for r in cur.fetchall():
    d = json.loads(r["content_json"]) if r["content_json"] else {}
    attrs = d.get("attributes", {})
    personas_info.append({
        "persona_id": r["persona_id"],
        "name": d.get("persona_name", r["persona_id"]),
        "age": attrs.get("Độ tuổi", attrs.get("age")),
        "gender": attrs.get("Bản dạng giới", attrs.get("gender")),
        "marital": attrs.get("Tình trạng hôn nhân", attrs.get("marital_status")),
        "children": attrs.get("Tình trạng con cái", attrs.get("children")),
        "employment": attrs.get("Tình trạng việc làm"),
        "work_arr": attrs.get("Hình thức làm việc hiện tại"),
        "industry": attrs.get("Ngành nghề chính"),
        "streaming": attrs.get("Tổng thời gian xem phim, video và livestream hàng tuần."),
    })

print("=== 6 PERSONAS PROFILE ATTRIBUTES ===")
df_p = pd.DataFrame(personas_info)
print(df_p.to_string())

# Now inspect activity_windows per persona
df_w = pd.read_sql_query("""
    SELECT 
        b.persona_id,
        w.start_at,
        w.end_at,
        w.surface_bias
    FROM activity_windows w
    JOIN bots b ON b.id = w.bot_id
""", conn)

df_w['start_dt'] = pd.to_datetime(df_w['start_at'])
df_w['end_dt'] = pd.to_datetime(df_w['end_at'])
df_w['start_local'] = df_w['start_dt'].dt.tz_convert('Asia/Ho_Chi_Minh')
df_w['start_hour_local'] = df_w['start_local'].dt.hour
df_w['is_late_night'] = (df_w['start_hour_local'] >= 21).astype(int)
df_w['is_early_morning'] = (df_w['start_hour_local'] <= 8).astype(int)
df_w['duration_min'] = (df_w['end_dt'] - df_w['start_dt']).dt.total_seconds() / 60.0

def parse_surface_bias(b):
    if not b:
        return {'bias_feed': 0.0, 'bias_reels': 0.0}
    try:
        data = json.loads(b) if isinstance(b, str) else b
        return {
            'bias_feed': float(data.get('feed', 0.0)),
            'bias_reels': float(data.get('reels', 0.0)),
        }
    except Exception:
        return {'bias_feed': 0.0, 'bias_reels': 0.0}

bias_df = pd.DataFrame(df_w['surface_bias'].apply(parse_surface_bias).tolist())
df_w = pd.concat([df_w, bias_df], axis=1)

agg = df_w.groupby('persona_id').agg(
    total_windows=('start_at', 'count'),
    mean_duration=('duration_min', 'mean'),
    pct_early_morning=('is_early_morning', lambda x: x.mean() * 100),
    pct_late_night=('is_late_night', lambda x: x.mean() * 100),
    mean_bias_reels=('bias_reels', 'mean'),
    mean_bias_feed=('bias_feed', 'mean'),
).round(2)

print("\n=== AGGREGATED WINDOW METRICS PER PERSONA ===")
print(agg.to_string())

conn.close()
