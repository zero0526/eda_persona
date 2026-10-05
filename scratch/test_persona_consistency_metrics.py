import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load profiles (from extracted CSV or JSON)
df_prof = pd.read_csv("output/tables/step6_facebook_behavior_extracted_profiles.csv").set_index('persona_id')
df_clusters = pd.read_csv("output/tables/step6_persona_cluster_assignments.csv").set_index('persona_id')
df_prof['Cluster'] = df_clusters['Cluster_Ward']

# 2. Extract actual metrics from logs
logs_dir = Path('data/action_logs')
actual_records = []

for b_file in sorted(logs_dir.glob('benchmark_eda_*.json')):
    with open(b_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    meta = data.get('metadata', {})
    pid = meta.get('persona_id')
    steps = data.get('step_records', [])
    
    intents = [s.get('intent') for s in steps]
    surfaces = [s.get('surface') for s in steps]
    latencies = [s.get('model_latency_ms') for s in steps if s.get('model_latency_ms') is not None]
    
    n_total = len(steps)
    n_reads = sum(1 for i in intents if i == 'read')
    n_scrolls = sum(1 for i in intents if i == 'scroll')
    n_searches = sum(1 for i in intents if i == 'search')
    n_reacts = sum(1 for i in intents if i == 'react')
    n_shares = sum(1 for i in intents if i == 'share')
    
    feed_count = sum(1 for s in surfaces if s == 'feed')
    mixed_count = sum(1 for s in surfaces if s in ('group', 'page', 'search', 'detail'))
    
    actual_records.append({
        'persona_id': pid,
        'total_steps': n_total,
        'mean_latency_ms': round(float(np.mean(latencies)), 1) if latencies else 0,
        'median_latency_ms': round(float(np.median(latencies)), 1) if latencies else 0,
        'n_reads': n_reads,
        'n_scrolls': n_scrolls,
        'n_searches': n_searches,
        'n_reacts': n_reacts,
        'n_shares': n_shares,
        'read_ratio_pct': round(n_reads / n_total * 100, 2),
        'deep_consumption_ratio': round((n_reads + n_searches) / (n_scrolls + n_reacts + 1e-5), 3),
        'feed_surface_pct': round(feed_count / n_total * 100, 2),
        'mixed_surface_pct': round(mixed_count / n_total * 100, 2)
    })

df_actual = pd.DataFrame(actual_records).set_index('persona_id')

# Merge profile & actual
df_eval = df_prof.join(df_actual)

print("="*90)
print("1. BẢNG ĐỐI CHIẾU CHỈ SỐ PROFILE vs HÀNH VI LOG THỰC TẾ")
print("="*90)
cols_show = ['Cluster', 'pace', 'reading_depth', 'preferred_surface', 'mean_latency_ms', 'n_reads', 'deep_consumption_ratio', 'mixed_surface_pct', 'n_shares', 'n_reacts']
print(df_eval[cols_show].to_string())

# 3. Tính toán tương quan định lượng giữa biến Profile và biến Log
pace_map = {'slow': 1, 'balanced': 2, 'quick': 3}
depth_map = {'skim': 1, 'selective': 2}
surf_map = {'feed': 0, 'mixed': 1}

prof_pace = df_eval['pace'].map(pace_map)
prof_depth = df_eval['reading_depth'].map(depth_map)
prof_surf = df_eval['preferred_surface'].map(surf_map)

# Spearman correlation
r_pace_lat, p_pace_lat = spearmanr(prof_pace, df_eval['mean_latency_ms'])
r_depth_read, p_depth_read = spearmanr(prof_depth, df_eval['read_ratio_pct'])
r_depth_dci, p_depth_dci = spearmanr(prof_depth, df_eval['deep_consumption_ratio'])
r_surf_mix, p_surf_mix = spearmanr(prof_surf, df_eval['mixed_surface_pct'])

print("\n" + "="*90)
print("2. HỆ SỐ TƯƠNG QUAN SPEARMAN (r_s) KIỂM ĐỊNH TÍNH NHẤT QUÁN")
print("="*90)
print(f"1. Profile Pace <---> Log Model Latency:      r_s = {r_pace_lat:+.3f} (p = {p_pace_lat:.4f}) [Pace nhanh -> Latency thấp]")
print(f"2. Profile Reading Depth <---> Log Read Ratio: r_s = {r_depth_read:+.3f} (p = {p_depth_read:.4f}) [Selective -> Tỷ lệ Read cao]")
print(f"3. Profile Reading Depth <---> Log DCI Ratio:  r_s = {r_depth_dci:+.3f} (p = {p_depth_dci:.4f}) [Selective -> Tỷ lệ Deep/Skim cao]")
print(f"4. Profile Surface <---> Log Mixed Surface %:  r_s = {r_surf_mix:+.3f} (p = {p_surf_mix:.4f})")

# 4. So sánh theo Cụm
print("\n" + "="*90)
print("3. SO SÁNH GIÁ TRỊ TRUNG BÌNH THEO 3 CỤM ARCHETYPE TRONG ACTION LOG")
print("="*90)
cluster_comp = df_eval.groupby('Cluster')[['mean_latency_ms', 'n_reads', 'read_ratio_pct', 'deep_consumption_ratio', 'n_shares', 'n_reacts', 'mixed_surface_pct']].mean().round(2)
print(cluster_comp.to_string())
