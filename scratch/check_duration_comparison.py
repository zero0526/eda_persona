import sqlite3, pandas as pd, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

conn = sqlite3.connect('data/persona-runner.sqlite')

df = pd.read_sql_query('''
    SELECT 
        b.persona_id,
        e.id as ep_id,
        e.status as ep_status,
        e.terminal_reason,
        e.started_at as ep_started,
        e.ended_at as ep_ended,
        w.id as win_id,
        w.start_at as win_start,
        w.end_at as win_end
    FROM episodes e
    JOIN bots b ON e.bot_id = b.id
    LEFT JOIN activity_windows w ON e.window_id = w.id
    ORDER BY b.persona_id, e.id
''', conn)

df['t_ep_start'] = pd.to_datetime(df['ep_started'])
df['t_ep_end'] = pd.to_datetime(df['ep_ended'])
df['actual_duration_min'] = (df['t_ep_end'] - df['t_ep_start']).dt.total_seconds() / 60.0

df['t_win_start'] = pd.to_datetime(df['win_start'])
df['t_win_end'] = pd.to_datetime(df['win_end'])
df['planned_duration_min'] = (df['t_win_end'] - df['t_win_start']).dt.total_seconds() / 60.0

df['diff_min'] = df['actual_duration_min'] - df['planned_duration_min']
df['diff_pct'] = (df['diff_min'] / df['planned_duration_min']) * 100

cols = ['persona_id', 'ep_id', 'ep_status', 'terminal_reason', 'planned_duration_min', 'actual_duration_min', 'diff_min', 'diff_pct']
res = df[cols].copy()
res['ep_id'] = res['ep_id'].str[:8]
print("=== BẢNG ĐỐI CHIẾU CHI TIẾT 15 SESSIONS: KẾ HOẠCH VS THỰC TẾ ===")
print(res.round(2).to_string(index=False))

print("\n=== THỐNG KÊ THEO TERMINAL_REASON ===")
print(res.groupby('terminal_reason')[['planned_duration_min', 'actual_duration_min', 'diff_min', 'diff_pct']].agg(['count', 'mean']).round(2))

print("\n=== ĐỐI VỚI CÁC PHIÊN HOÀN THÀNH TỰ NHIÊN (agent_stop) ===")
stop_df = res[res['terminal_reason'] == 'agent_stop']
print(stop_df[['persona_id', 'ep_id', 'planned_duration_min', 'actual_duration_min', 'diff_min', 'diff_pct']].to_string(index=False))
