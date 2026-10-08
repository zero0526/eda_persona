import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
from loaders.action_loader import ActionLoader

loader = ActionLoader()
histories = loader.load_all_personas()
df_actions = loader.to_unified_actions_dataframe(histories)

# 1. Lọc toàn bộ bước thực thi cuộn chuột Playwright
df_gestures = df_actions[df_actions['gesture_total_px'].notnull()].copy()
df_gestures['scroll_speed_px_s'] = (
    df_gestures['gesture_total_px'] / (df_gestures['gesture_ms'] / 1000.0)
).astype(float).round(2)

# Chuẩn hóa nhãn nhịp độ theo đúng hợp đồng hành vi (Quick vs Balanced)
pace_map = {
    'fast': 'quick',
    'quick': 'quick',
    'careful': 'balanced',
    'balanced': 'balanced'
}
df_gestures['gesture_pace_std'] = df_gestures['gesture_pace'].map(pace_map).fillna(df_gestures['gesture_pace'])

# 2. Thống kê cơ học cử chỉ theo Persona
kin_stats = df_gestures.groupby('persona_id').agg(
    n_gestures=('step_index', 'count'),
    pct_quick=('gesture_pace_std', lambda x: (x == 'quick').mean() * 100),
    median_scroll_px=('gesture_total_px', 'median'),
    median_gesture_ms=('gesture_ms', 'median'),
    median_speed_px_s=('scroll_speed_px_s', 'median')
).round(2).reset_index()

kin_stats.columns = [
    'Persona ID', 'Số lần cuộn (N)', 'Tỷ lệ Quick (%)', 
    'Median Cự ly Cuộn (px)', 'Median Thời gian (ms)', 'Median Vận tốc (px/s)'
]
print("=== BẢNG KIN_STATS ĐÃ CHUẨN HÓA ===")
print(kin_stats.to_string())

# Panel B crosstab
pace_ct = pd.crosstab(df_gestures['persona_id'], df_gestures['gesture_pace_std'], normalize='index') * 100
cols_order = [c for c in ['quick', 'balanced'] if c in pace_ct.columns]
pace_ct = pace_ct[cols_order].round(1)
print("\n=== CROSSTAB PANEL B ĐÃ CHUẨN HÓA (%) ===")
print(pace_ct.to_string())
