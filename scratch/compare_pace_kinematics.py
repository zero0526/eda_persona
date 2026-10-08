import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
from loaders.action_loader import ActionLoader

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)
df_gestures = df_actions[df_actions['gesture_total_px'].notnull()].copy()
df_gestures['scroll_speed_px_s'] = (
    df_gestures['gesture_total_px'] / (df_gestures['gesture_ms'] / 1000.0)
).astype(float).round(2)

print("=== Thống kê Cơ học theo từng nhãn gesture_pace ===")
stats_by_pace = df_gestures.groupby('gesture_pace').agg(
    n=('step_index', 'count'),
    mean_speed=('scroll_speed_px_s', 'mean'),
    median_speed=('scroll_speed_px_s', 'median'),
    mean_ms=('gesture_ms', 'mean'),
    median_ms=('gesture_ms', 'median'),
    mean_px=('gesture_total_px', 'mean'),
    median_px=('gesture_total_px', 'median')
).reset_index()
print(stats_by_pace.to_string())

print("\n=== Thống kê theo Nhóm Nhịp (Quick/Fast vs Balanced/Careful) ===")
df_gestures['pace_family'] = df_gestures['gesture_pace'].map({
    'fast': 'Nhóm Nhanh (Fast/Quick)',
    'quick': 'Nhóm Nhanh (Fast/Quick)',
    'careful': 'Nhóm Cân bằng/Chậm (Careful/Balanced)',
    'balanced': 'Nhóm Cân bằng/Chậm (Careful/Balanced)'
})
stats_by_family = df_gestures.groupby('pace_family').agg(
    n=('step_index', 'count'),
    median_speed=('scroll_speed_px_s', 'median'),
    median_ms=('gesture_ms', 'median'),
    median_px=('gesture_total_px', 'median')
).reset_index()
print(stats_by_family.to_string())
