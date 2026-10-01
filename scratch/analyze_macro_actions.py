import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
import pandas as pd
import numpy as np

p_dir = Path('data/action_logs')
np_dir = Path('data/no_persona_Action')

# Define macro category mapping
def map_to_macro_cat(dim_name, src=''):
    dim = (dim_name or '').lower()
    # 1. Consumption
    if dim in ['reading_vs_watching', 'detail_orientation', 'content_consumption_format',
               'readingdepth', 'reading_depth', 'content', 'post_content', 'feed_content']:
        return 'Tiêu thụ nội dung (Consumption)'
    # 2. Social Engagement
    elif dim in ['social_engagement_style', 'emotional_expressiveness',
                 'interactionstyle', 'interaction_style', 'personality', 'interaction']:
        return 'Tương tác xã hội (Social / React)'
    # 3. Exploration & Search
    elif dim in ['curiosity', 'query_complexity',
                 'discoverystyle', 'discovery_style', 'interest', 'searched_topics', 'exploration_state']:
        return 'Khám phá & Tìm kiếm (Exploration)'
    # 4. Pacing & Control
    elif dim in ['attention_span', 'decision_speed', 'novelty_vs_familiarity',
                 'pace', 'behavior', 'session', 'time_remaining', 'context']:
        return 'Nhịp độ & Điều tiết (Pacing & Control)'
    elif dim == 'none':
        return 'Không neo nhận thức (None / Baseline)'
    else:
        return 'Khác / Ngữ cảnh thị giác (Other)'

def extract_macro_records(directory, group_name):
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
            dim_evidence = step.get('dimension_evidence') or []
            
            if not dim_evidence:
                records.append({
                    'group': group_name,
                    'episode_id': ep_id,
                    'step_index': step_idx,
                    'intent': intent,
                    'tool': tool,
                    'raw_dim': 'none',
                    'macro_cat': 'Không neo nhận thức (None / Baseline)'
                })
            else:
                for item in dim_evidence:
                    if isinstance(item, dict):
                        dim = item.get('dimension')
                        src = item.get('source')
                        records.append({
                            'group': group_name,
                            'episode_id': ep_id,
                            'step_index': step_idx,
                            'intent': intent,
                            'tool': tool,
                            'raw_dim': dim,
                            'macro_cat': map_to_macro_cat(dim, src)
                        })
    return pd.DataFrame(records)

df_p = extract_macro_records(p_dir, 'persona')
df_np = extract_macro_records(np_dir, 'no_persona')

# Group intents into major actions: scroll, read, react, search, open_explore, navigate_control, observe
def group_intent(intent):
    if intent in ['scroll', 'scroll_comments']:
        return 'scroll'
    elif intent in ['read', 'expand']:
        return 'read/expand'
    elif intent in ['react', 'like_page', 'share']:
        return 'react/engage'
    elif intent in ['search']:
        return 'search'
    elif intent in ['open', 'open_comments', 'open_reels']:
        return 'open/drill-down'
    elif intent in ['back', 'close', 'home']:
        return 'navigate/close'
    elif intent in ['observe']:
        return 'observe'
    return 'other'

df_p['action_group'] = df_p['intent'].apply(group_intent)
df_np['action_group'] = df_np['intent'].apply(group_intent)

print("=== NO PERSONA: Macro Category vs Action Group (Counts) ===")
ct_np = pd.crosstab(df_np['macro_cat'], df_np['action_group'])
print(ct_np)

print("\n=== NO PERSONA: Macro Category vs Action Group (Percentages %) ===")
pct_np = pd.crosstab(df_np['macro_cat'], df_np['action_group'], normalize='index') * 100
print(pct_np.round(1))

print("\n=== PERSONA: Macro Category vs Action Group (Counts) ===")
ct_p = pd.crosstab(df_p['macro_cat'], df_p['action_group'])
print(ct_p)

print("\n=== PERSONA: Macro Category vs Action Group (Percentages %) ===")
pct_p = pd.crosstab(df_p['macro_cat'], df_p['action_group'], normalize='index') * 100
print(pct_p.round(1))
