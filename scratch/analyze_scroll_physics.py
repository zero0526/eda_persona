import json
from pathlib import Path
import re
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

logs_dir = Path('data/action_logs')
cluster_map = {
    'vn_000077': 1, 'vn_000081': 1,
    'vn_000041': 2, 'vn_000049': 2,
    'vn_000019': 3, 'vn_000087': 3
}

rows = []
for b_file in sorted(logs_dir.glob('benchmark_eda_*.json')):
    with open(b_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    pid = data['metadata']['persona_id']
    cid = cluster_map.get(pid)
    steps = data.get('step_records', [])
    for s in steps:
        tool = s.get('tool') or s.get('resolved_tool')
        intent = s.get('intent')
        evidence = s.get('evidence') or ''
        
        px_match = re.search(r'total=(\d+)px', evidence)
        ms_match = re.search(r'gesture_ms=(\d+)', evidence)
        pace_match = re.search(r'pace=([a-zA-Z]+)', evidence)
        
        if px_match and ms_match:
            px = int(px_match.group(1))
            ms = int(ms_match.group(1))
            pace_mode = pace_match.group(1) if pace_match else 'unknown'
            speed_px_per_s = px / (ms / 1000)
            rows.append({
                'persona_id': pid,
                'cluster': cid,
                'scroll_px': px,
                'gesture_ms': ms,
                'scroll_speed_px_s': speed_px_per_s,
                'scroll_pace_mode': pace_mode
            })

df = pd.DataFrame(rows)

print("="*90)
print("THỐNG KÊ CƠ CHẾ CUỘN VẬT LÝ THỰC TẾ (PHYSICAL SCROLL MECHANICS)")
print("="*90)

print("\n1. Phân bổ chế độ cuộn (scroll_pace_mode) theo từng Persona:")
ct_mode = pd.crosstab(df['persona_id'], df['scroll_pace_mode'], margins=True)
print(ct_mode.to_string())

print("\n2. Quãng đường cuộn (Pixels) và Vận tốc cuộn (px/s) theo Persona:")
agg_p = df.groupby('persona_id')[['scroll_px', 'gesture_ms', 'scroll_speed_px_s']].agg(['count', 'mean', 'median']).round(1)
print(agg_p.to_string())

print("\n3. So sánh Cơ chế Cuộn theo 3 Cụm Archetype:")
agg_c = df.groupby('cluster')[['scroll_px', 'gesture_ms', 'scroll_speed_px_s']].agg(['count', 'mean', 'median']).round(1)
print(agg_c.to_string())
