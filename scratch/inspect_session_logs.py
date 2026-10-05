import json
from pathlib import Path
import pandas as pd

logs_dir = Path('data/action_logs')

rows = []
for b_file in sorted(logs_dir.glob('benchmark_eda_*.json')):
    with open(b_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    meta = data.get('metadata', {})
    pid = meta.get('persona_id')
    stats = meta.get('summary_statistics', {})
    steps = data.get('step_records', [])
    
    # Analyze steps
    tools = [s.get('resolved_tool') or s.get('tool') for s in steps]
    intents = [s.get('intent') for s in steps]
    surfaces = [s.get('surface') for s in steps]
    latencies = [s.get('model_latency_ms') for s in steps if s.get('model_latency_ms') is not None]
    reactions = [s.get('reaction') for s in steps if s.get('reaction')]
    
    rows.append({
        'file': b_file.name,
        'persona_id': pid,
        'total_steps': meta.get('total_steps'),
        'terminal_reason': meta.get('terminal_reason'),
        'mean_latency': round(sum(latencies)/len(latencies), 1) if latencies else 0,
        'median_latency': pd.Series(latencies).median() if latencies else 0,
        'n_reads': sum(1 for i in intents if i == 'read'),
        'n_scrolls': sum(1 for i in intents if i == 'scroll'),
        'n_searches': sum(1 for i in intents if i == 'search'),
        'n_reacts': sum(1 for i in intents if i == 'react'),
        'n_shares': sum(1 for i in intents if i == 'share'),
        'n_observes': sum(1 for i in intents if i == 'observe'),
        'n_reactions': len(reactions),
        'feed_pct': round(sum(1 for s in surfaces if s == 'feed') / len(surfaces) * 100, 1) if surfaces else 0,
        'mixed_surface_pct': round(sum(1 for s in surfaces if s in ('group', 'page', 'search', 'detail')) / len(surfaces) * 100, 1) if surfaces else 0,
        'summary_stats': stats
    })

df = pd.DataFrame(rows)
print(df[['persona_id', 'total_steps', 'terminal_reason', 'mean_latency', 'n_reads', 'n_scrolls', 'n_searches', 'n_reacts', 'n_shares', 'feed_pct', 'mixed_surface_pct']].to_string())
