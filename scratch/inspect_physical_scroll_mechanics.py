import json
from pathlib import Path
import re
import pandas as pd

logs_dir = Path('data/action_logs')

rows = []
for b_file in sorted(logs_dir.glob('benchmark_eda_*.json')):
    with open(b_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    pid = data['metadata']['persona_id']
    steps = data.get('step_records', [])
    for s in steps:
        tool = s.get('tool') or s.get('resolved_tool')
        intent = s.get('intent')
        evidence = s.get('evidence') or ''
        
        # Check if scroll evidence has gesture_ms, pixels, pace
        px_match = re.search(r'total=(\d+)px', evidence)
        ms_match = re.search(r'gesture_ms=(\d+)', evidence)
        pace_match = re.search(r'pace=([a-zA-Z]+)', evidence)
        
        rows.append({
            'persona_id': pid,
            'intent': intent,
            'tool': tool,
            'scroll_px': int(px_match.group(1)) if px_match else None,
            'gesture_ms': int(ms_match.group(1)) if ms_match else None,
            'scroll_pace': pace_match.group(1) if pace_match else None,
            'evidence': evidence[:80]
        })

df = pd.DataFrame(rows)
df_scroll = df[df['intent'] == 'scroll'].dropna(subset=['scroll_px'])
print("Sample scroll events with physical mechanics:")
print(df_scroll[['persona_id', 'scroll_px', 'gesture_ms', 'scroll_pace']].head(15).to_string())

print("\nThống kê cơ chế vật lý cuộn (Scroll Mechanics) theo Persona:")
agg = df_scroll.groupby('persona_id')[['scroll_px', 'gesture_ms']].agg(['count', 'mean', 'median'])
print(agg.to_string())
