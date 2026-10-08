import sqlite3, pandas as pd, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('data/persona-runner.sqlite')
query = '''
SELECT b.persona_id, aw.local_date, aw.start_at, aw.end_at, aw.reason
FROM activity_windows aw
JOIN bots b ON aw.bot_id = b.id
WHERE b.persona_id IN ('vn_fb_001', 'vn_fb_002')
ORDER BY b.persona_id, aw.start_at
'''
df = pd.read_sql_query(query, conn)
df['start_dt'] = pd.to_datetime(df['start_at'])
df['end_dt'] = pd.to_datetime(df['end_at'])
df['dur_min'] = (df['end_dt'] - df['start_dt']).dt.total_seconds() / 60.0
df['start_local'] = df['start_dt'] + pd.Timedelta(hours=7)

for pid, group in df.groupby('persona_id'):
    print(f"==================== {pid} (Total windows: {len(group)}) ====================")
    for idx, row in group.iterrows():
        t_str = row['start_local'].strftime('%Y-%m-%d %H:%M')
        print(f"[{t_str} | {row['dur_min']:.0f}m]: {row['reason']}")
