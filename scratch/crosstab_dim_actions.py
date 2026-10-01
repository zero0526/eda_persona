import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from collections import Counter, defaultdict
import pandas as pd

p_dir = Path('data/action_logs')
np_dir = Path('data/no_persona_Action')

def extract_step_dim_actions(directory, group_name):
    records = []
    for f in sorted(directory.glob('benchmark_eda_*.json')):
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
        ep = data if isinstance(data, dict) else data[0]
        ep_id = ep.get('episode_id')
        for step in ep.get('step_records', []):
            intent = step.get('intent')
            tool = step.get('resolved_tool')
            step_idx = step.get('step_index')
            
            # 1. From step-level dimension_evidence
            dim_evidence = step.get('dimension_evidence') or []
            for item in dim_evidence:
                if isinstance(item, dict):
                    dim = item.get('dimension')
                    src = item.get('source')
                    role = item.get('role')
                    weight = item.get('weight')
                    val = item.get('value')
                    records.append({
                        'group': group_name,
                        'level': 'step_dim_evidence',
                        'episode_id': ep_id,
                        'step_index': step_idx,
                        'intent': intent,
                        'tool': tool,
                        'source': src,
                        'dimension': dim,
                        'weight': weight,
                        'value': val
                    })
            
            # 2. Also track if no dim_evidence (empty)
            if not dim_evidence:
                records.append({
                    'group': group_name,
                    'level': 'step_dim_evidence',
                    'episode_id': ep_id,
                    'step_index': step_idx,
                    'intent': intent,
                    'tool': tool,
                    'source': 'none',
                    'dimension': 'none',
                    'weight': None,
                    'value': None
                })
    return pd.DataFrame(records)

df_p = extract_step_dim_actions(p_dir, 'persona')
df_np = extract_step_dim_actions(np_dir, 'no_persona')

print("=== NO PERSONA: Intent by Dimension in step_records ===")
ct_np = pd.crosstab(df_np['dimension'], df_np['intent'], margins=True)
print(ct_np)

print("\n=== PERSONA: Intent by Top Dimensions in step_records ===")
top_p_dims = df_p['dimension'].value_counts().head(12).index
df_p_top = df_p[df_p['dimension'].isin(top_p_dims)]
ct_p = pd.crosstab(df_p_top['dimension'], df_p_top['intent'], margins=True)
print(ct_p)
