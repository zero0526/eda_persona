import json
from pathlib import Path
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

logs_dir = Path('data/action_logs')
rows = []

for b_file in sorted(logs_dir.glob('benchmark_eda_*.json')):
    with open(b_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    meta = data.get('metadata', {})
    pid = meta.get('persona_id')
    steps = data.get('step_records', [])
    
    # Parse timestamps
    timestamps = [pd.to_datetime(s.get('timestamp')) for s in steps if s.get('timestamp')]
    step_intervals = []
    for i in range(1, len(timestamps)):
        delta = (timestamps[i] - timestamps[i-1]).total_seconds()
        if 0 <= delta <= 300: # filter out huge pauses if any
            step_intervals.append(delta)
            
    total_duration_sec = (timestamps[-1] - timestamps[0]).total_seconds() if len(timestamps) > 1 else 0
    duration_min = total_duration_sec / 60 if total_duration_sec > 0 else 1
    
    # Tool execution ms vs model latency ms
    model_lats = [s.get('model_latency_ms') for s in steps if s.get('model_latency_ms') is not None]
    tool_execs = [s.get('tool_execution_ms') for s in steps if s.get('tool_execution_ms') is not None]
    
    intents = [s.get('intent') for s in steps]
    n_scrolls = sum(1 for i in intents if i == 'scroll')
    n_reads = sum(1 for i in intents if i == 'read')
    
    rows.append({
        'persona_id': pid,
        'total_steps': len(steps),
        'duration_sec': round(total_duration_sec, 1),
        'action_velocity_per_min': round(len(steps) / duration_min, 2),
        'mean_step_interval_sec': round(float(np.mean(step_intervals)), 2) if step_intervals else 0,
        'median_step_interval_sec': round(float(np.median(step_intervals)), 2) if step_intervals else 0,
        'mean_model_latency_s': round(float(np.mean(model_lats))/1000, 2) if model_lats else 0,
        'mean_tool_exec_s': round(float(np.mean(tool_execs))/1000, 2) if tool_execs else 0,
        'n_scrolls': n_scrolls,
        'scroll_rate_per_min': round(n_scrolls / duration_min, 2),
        'n_reads': n_reads
    })

df = pd.DataFrame(rows).set_index('persona_id')

# Merge with profile pace
df_prof = pd.read_csv("output/tables/step6_facebook_behavior_extracted_profiles.csv").set_index('persona_id')
df_clusters = pd.read_csv("output/tables/step6_persona_cluster_assignments.csv").set_index('persona_id')

df_merged = df.join(df_prof[['pace', 'attention', 'reading_depth']]).join(df_clusters[['Cluster_Ward']])
print("=== SO SÁNH TỐC ĐỘ THAO TÁC THỰC TẾ (ACTION VELOCITY) vs PROFILE PACE ===")
cols_print = ['Cluster_Ward', 'pace', 'total_steps', 'duration_sec', 'action_velocity_per_min', 'mean_step_interval_sec', 'scroll_rate_per_min', 'mean_model_latency_s', 'mean_tool_exec_s']
print(df_merged[cols_print].to_string())
