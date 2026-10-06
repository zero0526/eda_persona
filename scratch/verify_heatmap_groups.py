import sqlite3
import json
import sys
import pandas as pd
from scipy import stats

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

db_path = r"D:\source_code\agent_in_works\claw-master\data\persona-runner.sqlite"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

# Load activity_windows
df_windows = pd.read_sql_query('''
    SELECT 
        w.id as window_id,
        b.persona_id,
        w.start_at,
        w.end_at,
        w.surface_bias
    FROM activity_windows w
    JOIN bots b ON b.id = w.bot_id
''', conn)

df_windows['start_dt'] = pd.to_datetime(df_windows['start_at'])
df_windows['start_local'] = df_windows['start_dt'].dt.tz_convert('Asia/Ho_Chi_Minh')
df_windows['start_hour_local'] = df_windows['start_local'].dt.hour
df_windows['is_late_night'] = (df_windows['start_hour_local'] >= 21).astype(int)
df_windows['is_early_morning'] = (df_windows['start_hour_local'] <= 8).astype(int)

# Check dummy for vn_fb_004 (F&B / freelance)
df_windows['is_fb_004'] = (df_windows['persona_id'] == 'vn_fb_004').astype(int)
# Check dummy for vn_fb_006 (Gen X 55-64)
df_windows['is_fb_006'] = (df_windows['persona_id'] == 'vn_fb_006').astype(int)

r_004, p_004 = stats.spearmanr(df_windows['is_fb_004'], df_windows['is_late_night'])
r_006, p_006 = stats.spearmanr(df_windows['is_fb_006'], df_windows['is_early_morning'])

print(f"Correlation is_fb_004 (F&B) vs is_late_night: r = {r_004:.4f}, p = {p_004:.4e}")
print(f"Correlation is_fb_006 (Gen X) vs is_early_morning: r = {r_006:.4f}, p = {p_006:.4e}")

# Check per persona rates
night_rates = df_windows.groupby('persona_id')['is_late_night'].mean() * 100
morning_rates = df_windows.groupby('persona_id')['is_early_morning'].mean() * 100

print("\n--- Tỷ lệ đêm muộn (>=21h) theo persona ---")
print(night_rates.round(1))

print("\n--- Tỷ lệ sáng sớm (<=8h) theo persona ---")
print(morning_rates.round(1))

conn.close()
